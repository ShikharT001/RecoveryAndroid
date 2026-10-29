"""
RecoverX Audit Log
Maintains an append-only audit trail of all forensic actions taken by the user and system.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str  # e.g. "DEVICE_CONNECT", "SCAN_START", "FILE_ACQUISITION", "EXPORT"
    scan_id: str | None = None
    target_identifier: str = ""  # Serial number, filename, or scan job ID
    action: str = ""
    status: str = "SUCCESS"  # "SUCCESS", "WARNING", "FAILED"
    details: str = ""


class AuditLog:
    """Appends forensic audit records to disk and notifies registered listeners."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event_type: str, action: str, scan_id: str | None = None,
            target_identifier: str = "", status: str = "SUCCESS", details: str = "") -> AuditEvent:
        event = AuditEvent(
            event_type=event_type,
            scan_id=scan_id,
            target_identifier=target_identifier,
            action=action,
            status=status,
            details=details,
        )
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
        except Exception:
            pass
        return event

    def read_events(self, limit: int = 500) -> list[AuditEvent]:
        events = []
        if not self.log_path.exists():
            return events
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    line = line.strip()
                    if line:
                        events.append(AuditEvent(**json.loads(line)))
        except Exception:
            pass
        return events
