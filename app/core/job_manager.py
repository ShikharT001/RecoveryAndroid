"""
RecoverX Job Manager & Worker
Provides multi-threaded execution for acquisition and recovery scans using PySide6 QThread.
"""

import time
from pathlib import Path
from PySide6.QtCore import QThread, Signal
import logging

from app.core.scan_manager import ScanConfiguration
from app.devices.adb_client import AdbClient
from app.devices.storage_browser import StorageBrowser
from app.devices.acquisition import AcquisitionEngine
from app.recovery.file_scanner import FileScanner
from app.recovery.recovery_classifier import RecoveryClassifier
from app.whatsapp.database_parser import WhatsAppDatabaseParser
from app.whatsapp.chat_export_parser import ChatExportParser
from app.whatsapp.media_indexer import MediaIndexer
from app.storage.secure_workspace import SecureWorkspace
from app.storage.repository import StorageRepository
from app.storage.models import ScanJobRecord, RecoveredItemRecord, ChatRecord
from app.core.evidence_manifest import EvidenceManifest

logger = logging.getLogger("recoverx.job_manager")


class ScanWorker(QThread):
    """Background worker executing device acquisition and forensic file analysis."""

    stage_changed = Signal(str)                          # e.g. "Discovering files..."
    progress_updated = Signal(int, int, str)             # discovered, acquired, current_item
    error_occurred = Signal(str, str)                    # error_type, message
    scan_completed = Signal(str, int, int, int)          # job_id, total_found, total_acquired, chats_count

    def __init__(
        self,
        config: ScanConfiguration,
        repository: StorageRepository,
        adb_client: AdbClient | None = None,
    ):
        super().__init__()
        self.config = config
        self.repo = repository
        self.adb = adb_client or AdbClient()
        self._is_cancelled = False
        self.acquisition_engine: AcquisitionEngine | None = None

    def cancel(self) -> None:
        """Safely stops acquisition between operations."""
        self._is_cancelled = True
        if self.acquisition_engine:
            self.acquisition_engine.cancel()
        logger.info("ScanWorker cancellation initiated.")

    def run(self) -> None:
        job_id = self.config.job_id
        workspace_base = self.config.workspace_dir or Path("workspaces")
        sec_workspace = SecureWorkspace(workspace_base, job_id=job_id)
        manifest = EvidenceManifest(sec_workspace.workspace_dir / "evidence_manifest.json")

        job_rec = ScanJobRecord(
            job_id=job_id,
            device_serial=self.config.device_serial,
            categories_selected=self.config.categories,
            workspace_path=str(sec_workspace.workspace_dir),
            status="RUNNING",
        )
        self.repo.create_scan_job(job_rec)

        discovered_count = 0
        acquired_count = 0
        chats_count = 0

        try:
            # -------------------------------------------------------------
            # Stage 1: Device / Local Source Discovery
            # -------------------------------------------------------------
            self.stage_changed.emit("Analyzing accessible storage paths...")

            target_files: list[tuple[str, str]] = []  # (source_path, category)

            if self.config.custom_source_dir and self.config.custom_source_dir.exists():
                # User-provided local backup / directory scan
                self.stage_changed.emit(f"Scanning local directory: {self.config.custom_source_dir.name}...")
                scanner = FileScanner()
                for item in scanner.scan_directory(
                    self.config.custom_source_dir,
                    job_id=job_id,
                    should_cancel=lambda: self._is_cancelled,
                ):
                    discovered_count += 1
                    acquired_count += 1
                    self.repo.add_recovered_item(item)
                    self.progress_updated.emit(discovered_count, acquired_count, item.filename)

                    # If SQLite database
                    if item.file_type in ("db", "sqlite") and self.config.parse_readable_databases:
                        try:
                            parser = WhatsAppDatabaseParser(Path(item.local_path))
                            if parser.is_readable():
                                chats = parser.extract_messages(job_id)
                                self.repo.add_chat_records_batch(chats)
                                chats_count += len(chats)
                        except Exception as e:
                            self.repo.record_scan_error(job_id, "DATABASE_PARSE_ERROR", str(e), item.source_path)

                    # If Chat export text
                    if item.file_type == "txt" and self.config.parse_chat_exports:
                        try:
                            chats = ChatExportParser.parse_file(Path(item.local_path), job_id)
                            if chats:
                                self.repo.add_chat_records_batch(chats)
                                chats_count += len(chats)
                        except Exception as e:
                            self.repo.record_scan_error(job_id, "EXPORT_PARSE_ERROR", str(e), item.source_path)

            elif self.config.device_serial:
                # Android ADB Device Scan
                browser = StorageBrowser(self.adb, self.config.device_serial)
                self.acquisition_engine = AcquisitionEngine(
                    self.adb,
                    serial=self.config.device_serial,
                    workspace=sec_workspace,
                    manifest=manifest,
                )

                # Locate WhatsApp directories
                wa_roots = browser.find_whatsapp_locations()
                search_roots = list(wa_roots) if wa_roots else ["/sdcard/WhatsApp", "/sdcard/Android/media/com.whatsapp/WhatsApp"]
                if "accessible_media" in self.config.categories:
                    search_roots.extend(["/sdcard/DCIM", "/sdcard/Pictures"])
                if "documents" in self.config.categories:
                    search_roots.extend(["/sdcard/Download", "/sdcard/Documents"])

                for root in search_roots:
                    if self._is_cancelled:
                        break
                    self.stage_changed.emit(f"Enumerating accessible files in {root}...")
                    files = browser.list_accessible_files_recursive(root, max_files=1000)
                    for f in files:
                        cat = RecoveryClassifier.categorize_by_path(f.path)
                        target_files.append((f.path, cat.value if hasattr(cat, 'value') else cat))
                        discovered_count += 1
                        self.progress_updated.emit(discovered_count, acquired_count, f.name)

                # ---------------------------------------------------------
                # Stage 2: Acquisition
                # ---------------------------------------------------------
                self.stage_changed.emit("Acquiring discovered files to secure workspace...")
                for src_path, cat in target_files:
                    if self._is_cancelled:
                        break

                    try:
                        record = self.acquisition_engine.acquire_file(
                            remote_source_path=src_path,
                            scan_id=job_id,
                            category=cat,
                        )
                        acquired_count += 1
                        local_path = str(sec_workspace.workspace_dir / record.workspace_relative_path)

                        item_rec = RecoveredItemRecord(
                            item_id=record.record_id,
                            job_id=job_id,
                            filename=Path(src_path).name,
                            file_type=Path(src_path).suffix.lstrip(".").lower() or "bin",
                            category=cat,
                            file_size_bytes=record.file_size_bytes,
                            source_path=src_path,
                            local_path=local_path,
                            sha256_hash=record.sha256_hash,
                        )
                        self.repo.add_recovered_item(item_rec)
                        self.progress_updated.emit(discovered_count, acquired_count, Path(src_path).name)

                        # Parse WhatsApp databases if unencrypted
                        if cat == "whatsapp_backup" and self.config.parse_readable_databases:
                            try:
                                parser = WhatsAppDatabaseParser(Path(local_path))
                                if parser.is_readable():
                                    chats = parser.extract_messages(job_id)
                                    self.repo.add_chat_records_batch(chats)
                                    chats_count += len(chats)
                            except Exception as e:
                                self.repo.record_scan_error(job_id, "DATABASE_PARSE_ERROR", str(e), src_path)

                    except Exception as e:
                        logger.warning(f"Failed to acquire {src_path}: {e}")
                        self.repo.record_scan_error(job_id, "ACQUISITION_ERROR", str(e), src_path)

            # Finalize Job Record
            job_rec.status = "CANCELLED" if self._is_cancelled else "COMPLETED"
            job_rec.files_discovered = discovered_count
            job_rec.files_acquired = acquired_count
            job_rec.chats_parsed = chats_count
            job_rec.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            self.repo.update_scan_job(job_rec)

            self.stage_changed.emit("Scan completed successfully." if not self._is_cancelled else "Scan cancelled by user.")
            self.scan_completed.emit(job_id, discovered_count, acquired_count, chats_count)

        except Exception as e:
            logger.error(f"Scan job {job_id} encountered critical error: {e}", exc_info=True)
            job_rec.status = "FAILED"
            job_rec.error_message = str(e)
            self.repo.update_scan_job(job_rec)
            self.error_occurred.emit("CRITICAL_ERROR", str(e))
            self.scan_completed.emit(job_id, discovered_count, acquired_count, chats_count)
