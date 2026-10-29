"""
RecoverX Android Permission & Scope Analyzer
Clarifies accessibility boundaries (shared storage vs protected app sandbox)
and enforces forensics principle of transparency.
"""

from enum import Enum
from pathlib import Path


class StorageScope(str, Enum):
    SHARED_STORAGE = "shared_storage"          # /sdcard, /storage/emulated/0
    APP_MEDIA = "app_media"                    # /sdcard/Android/media/com.whatsapp
    LEGACY_WHATSAPP = "legacy_whatsapp"        # /sdcard/WhatsApp
    USER_BACKUP = "user_backup"                # Local user directory or import
    APP_PRIVATE_SANDBOX = "app_private_sandbox"# /data/data/com.whatsapp (Restricted)
    SYSTEM_RESTRICTED = "system_restricted"    # /system, /data/local (Restricted)
    UNKNOWN = "unknown"


class StorageScopeEvaluator:
    """Evaluates whether a target Android path is accessible via standard authorized ADB."""

    ACCESSIBLE_PREFIXES = (
        "/sdcard",
        "/storage/emulated/0",
        "/mnt/sdcard",
        "/storage/self/primary",
    )

    RESTRICTED_PREFIXES = (
        "/data/data",
        "/data/user/0",
        "/data/system",
        "/sys",
        "/proc",
        "/root",
    )

    @classmethod
    def evaluate_scope(cls, path_str: str) -> StorageScope:
        norm = path_str.replace("\\", "/").rstrip("/")
        
        # Check private sandbox
        if any(norm.startswith(p) for p in cls.RESTRICTED_PREFIXES):
            if "com.whatsapp" in norm:
                return StorageScope.APP_PRIVATE_SANDBOX
            return StorageScope.SYSTEM_RESTRICTED

        # Check Android 11+ WhatsApp media storage
        if "Android/media/com.whatsapp" in norm:
            return StorageScope.APP_MEDIA

        # Check legacy WhatsApp storage
        if norm.endswith("/WhatsApp") or "/WhatsApp/" in norm:
            return StorageScope.LEGACY_WHATSAPP

        # Check shared storage
        if any(norm.startswith(p) for p in cls.ACCESSIBLE_PREFIXES):
            return StorageScope.SHARED_STORAGE

        return StorageScope.UNKNOWN

    @classmethod
    def is_accessible_without_root(cls, path_str: str) -> bool:
        scope = cls.evaluate_scope(path_str)
        return scope in (
            StorageScope.SHARED_STORAGE,
            StorageScope.APP_MEDIA,
            StorageScope.LEGACY_WHATSAPP,
            StorageScope.USER_BACKUP,
        )

    @classmethod
    def get_scope_explanation(cls, scope: StorageScope) -> str:
        explanations = {
            StorageScope.SHARED_STORAGE: "Accessible shared external storage partition.",
            StorageScope.APP_MEDIA: "Modern Android 11+ WhatsApp shared media folder (/Android/media/com.whatsapp). Accessible.",
            StorageScope.LEGACY_WHATSAPP: "Legacy Android WhatsApp folder (/sdcard/WhatsApp). Accessible.",
            StorageScope.USER_BACKUP: "Local PC folder or user-imported archive.",
            StorageScope.APP_PRIVATE_SANDBOX: (
                "Protected internal application sandbox (/data/data/com.whatsapp). "
                "Inaccessible via non-root ADB on standard production Android builds."
            ),
            StorageScope.SYSTEM_RESTRICTED: "System-protected partition inaccessible to standard ADB permissions.",
            StorageScope.UNKNOWN: "Unclassified storage location.",
        }
        return explanations.get(scope, "Unknown storage boundary.")
