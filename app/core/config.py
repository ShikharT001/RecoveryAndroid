"""
RecoverX Application Configuration
Manages platform-specific paths, environment defaults, and persistence using platformdirs.
"""

from pathlib import Path
import json
from pydantic import BaseModel, Field
from platformdirs import user_data_dir, user_log_dir, user_cache_dir, user_documents_dir

APP_NAME = "RecoveryAndroid"
APP_AUTHOR = "RecoveryAndroid"


class AppSettings(BaseModel):
    """User-configurable settings."""
    adb_path: str = ""
    default_export_dir: str = ""
    hash_chunk_size_kb: int = 64  # 64 KB chunk size for memory-safe hashing
    auto_refresh_devices_sec: int = 5
    max_preview_size_mb: int = 50
    enable_audit_logging: bool = True
    theme: str = "dark"


class ConfigManager:
    """Provides path resolution and settings persistence with sandbox & fallback support."""

    def __init__(self, custom_base_dir: Path | None = None):
        if custom_base_dir:
            self.base_dir = custom_base_dir
            self.data_dir = self.base_dir / "data"
            self.log_dir = self.base_dir / "logs"
            self.cache_dir = self.base_dir / "cache"
            self.exports_dir = self.base_dir / "exports"
        else:
            # Try system user directories, fallback to workspace app_data if restricted
            try:
                candidate_data = Path(user_data_dir(APP_NAME, APP_AUTHOR))
                candidate_data.mkdir(parents=True, exist_ok=True)
                self.data_dir = candidate_data
                self.log_dir = Path(user_log_dir(APP_NAME, APP_AUTHOR))
                self.cache_dir = Path(user_cache_dir(APP_NAME, APP_AUTHOR))
                self.exports_dir = Path(user_documents_dir()) / "RecoveryAndroid_Exports"
            except (PermissionError, OSError):
                # Fallback for sandbox / portable mode
                fallback_base = Path("app_data").resolve()
                self.data_dir = fallback_base / "data"
                self.log_dir = fallback_base / "logs"
                self.cache_dir = fallback_base / "cache"
                self.exports_dir = fallback_base / "exports"

        self.workspace_dir = self.data_dir / "workspaces"
        self.settings_file = self.data_dir / "settings.json"
        self.db_path = self.data_dir / "recoveryandroid_index.db"
        self.log_file = self.log_dir / "recoveryandroid.log"

        self._ensure_directories()
        self.settings = self._load_settings()

    def _ensure_directories(self) -> None:
        """Creates required app directories safely, falling back to local workspace on permission error."""
        for target_dir in [self.data_dir, self.log_dir, self.cache_dir, self.workspace_dir, self.exports_dir]:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError):
                # If a specific directory fails (e.g. exports in Documents), point to data_dir
                fallback = self.data_dir / target_dir.name
                fallback.mkdir(parents=True, exist_ok=True)
                if target_dir == self.exports_dir:
                    self.exports_dir = fallback

    def _load_settings(self) -> AppSettings:
        """Loads settings from JSON or creates defaults."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return AppSettings(**data)
            except Exception:
                pass
        
        default_settings = AppSettings(default_export_dir=str(self.exports_dir))
        self.save_settings(default_settings)
        return default_settings

    def save_settings(self, settings: AppSettings) -> None:
        """Persists settings to disk."""
        self.settings = settings
        with open(self.settings_file, "w", encoding="utf-8") as f:
            f.write(settings.model_dump_json(indent=2))


# Global default configuration instance
config = ConfigManager()
