"""
RecoverX Evidence Manifest
Maintains an immutable chain-of-custody audit manifest for all discovered and acquired evidence files.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from pydantic import BaseModel, Field


class ManifestRecord(BaseModel):
    record_id: str
    scan_id: str
    source_device_serial: str
    original_source_path: str
    workspace_relative_path: str
    file_size_bytes: int
    sha256_hash: str | None = None
    source_sha256: str | None = None
    hash_verified: bool = False
    acquired_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    category: str
    is_historical_or_deleted: bool = False
    recovery_classification: str = "existing_copied"
    notes: str = ""


class EvidenceManifest:
    """Manages the serialization and appending of evidence acquisition records."""

    def __init__(self, manifest_file: Path):
        self.manifest_file = manifest_file
        self.records: list[ManifestRecord] = []
        self._load()

    def _load(self) -> None:
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = [ManifestRecord(**item) for item in data]\n            except Exception:\n                self.records = []

    def add_record(self, record: ManifestRecord) -> None:
        self.records.append(record)
        self.save()

    def save(self) -> None:
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in self.records], f, indent=2)

    def get_by_hash(self, sha256_hash: str) -> list[ManifestRecord]:
        return [r for r in self.records if r.sha256_hash == sha256_hash]

    def total_bytes(self) -> int:
        return sum(r.file_size_bytes for r in self.records)
