"""
RecoverX Scan Manager
Coordinates scan parameters, category selection, and forensic execution planning.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScanConfiguration:
    job_id: str
    device_serial: str | None = None
    custom_source_dir: Path | None = None
    workspace_dir: Path | None = None
    categories: list[str] = field(default_factory=lambda: [
        "whatsapp_media",
        "whatsapp_backup",
        "accessible_media",
        "documents",
    ])
    calculate_source_hashes: bool = True
    parse_readable_databases: bool = True
    parse_chat_exports: bool = True
