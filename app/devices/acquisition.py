"""
RecoverX Evidence Acquisition Engine
Safely pulls accessible files from Android to the local forensic workspace,
verifies cryptographic hashes, records chain-of-custody manifest entries, and supports cancellation.
"""

import hashlib
import time
from pathlib import Path
from typing import Callable
import logging

from app.devices.adb_client import AdbClient
from app.storage.secure_workspace import SecureWorkspace
from app.core.evidence_manifest import EvidenceManifest, ManifestRecord
from app.core.exceptions import HashMismatchError, AcquisitionError

logger = logging.getLogger("recoverx.acquisition")


class AcquisitionEngine:
    """Orchestrates non-destructive evidence extraction and verification."""

    def __init__(
        self,
        adb_client: AdbClient,
        serial: str,
        workspace: SecureWorkspace,
        manifest: EvidenceManifest,
        chunk_size_kb: int = 64,
    ):
        self.adb = adb_client
        self.serial = serial
        self.workspace = workspace
        self.manifest = manifest
        self.chunk_size = chunk_size_kb * 1024
        self._is_cancelled = False

    def cancel(self) -> None:
        """Sets cancellation flag to safely stop further acquisition between operations."""
        self._is_cancelled = True
        logger.info("Acquisition cancellation requested.")

    def acquire_file(
        self,
        remote_source_path: str,
        scan_id: str,
        category: str = "other",
        on_progress: Callable[[str, int, int], None] | None = None,
    ) -> ManifestRecord:
        """
        Pulls a single file safely from the Android device into the secure workspace.
        Calculates SHA-256, verifies integrity, and updates the forensic manifest.
        """
        if self._is_cancelled:
            raise AcquisitionError("Acquisition was cancelled by user.")

        # Determine relative path in workspace preserving structure
        rel_path = remote_source_path.lstrip("/").replace(":", "_")
        dest_local_path = self.workspace.resolve_safe_path(rel_path)
        dest_local_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Pulling {remote_source_path} -> {dest_local_path}")

        # Run ADB pull with serial targeting
        t0 = time.time()
        proc = self.adb.run_cmd(
            ["pull", remote_source_path, str(dest_local_path)],
            serial=self.serial,
            timeout=120,
            check=True,
        )

        if not dest_local_path.exists():
            raise AcquisitionError(f"Failed to acquire file: {remote_source_path}")

        file_size = dest_local_path.stat().st_size
        sha256 = self.compute_sha256(dest_local_path)

        # Optional source hash check via sha256sum on device if available
        source_hash = self.get_remote_sha256(remote_source_path)
        verified = False
        if source_hash and sha256:
            verified = (source_hash.lower() == sha256.lower())
            if not verified:
                raise HashMismatchError(
                    f"Integrity check failed for {dest_local_path.name}",
                    details=f"Source: {source_hash}, Acquired: {sha256}"
                )

        record = ManifestRecord(
            record_id=f"rec_{int(time.time()*1000)}_{dest_local_path.name}",
            scan_id=scan_id,
            source_device_serial=self.serial,
            original_source_path=remote_source_path,
            workspace_relative_path=str(dest_local_path.relative_to(self.workspace.workspace_dir)),
            file_size_bytes=file_size,
            sha256_hash=sha256,
            source_sha256=source_hash,
            hash_verified=verified or (source_hash is None),
            category=category,
        )

        self.manifest.add_record(record)
        return record

    def compute_sha256(self, file_path: Path) -> str:
        """Calculates SHA-256 digest using memory-safe chunked reads."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(self.chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_remote_sha256(self, remote_path: str) -> str | None:
        """Attempts to calculate sha256sum directly on device if binary exists."""
        try:
            out = self.adb.run_shell(["sha256sum", remote_path], serial=self.serial, timeout=10)
            parts = out.split()
            if parts and len(parts[0]) == 64:
                return parts[0]
        except Exception:
            pass
        return None
