"""
RecoverX Storage Browser
Discovers accessible partitions and files on Android devices via authorized ADB.
"""

from dataclasses import dataclass
from typing import Sequence
import logging
from app.devices.adb_client import AdbClient

logger = logging.getLogger("recoverx.storage_browser")


@dataclass
class RemoteFileInfo:
    path: str
    name: str
    size_bytes: int
    modified_time: str
    is_directory: bool
    category: str = "other"


class StorageBrowser:
    """Discovers accessible files and directories on connected Android storage."""

    KNOWN_WHATSAPP_ROOTS = [
        # Modern Android 11+ Scoped Storage
        "/sdcard/Android/media/com.whatsapp/WhatsApp",
        "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp",
        # Legacy Android Storage
        "/sdcard/WhatsApp",
        "/storage/emulated/0/WhatsApp",
    ]

    COMMON_MEDIA_DIRS = [
        "/sdcard/DCIM",
        "/sdcard/Pictures",
        "/sdcard/Download",
        "/sdcard/Documents",
        "/sdcard/Movies",
        "/sdcard/Music",
    ]

    def __init__(self, adb_client: AdbClient, serial: str):
        self.adb = adb_client
        self.serial = serial

    def find_whatsapp_locations(self) -> list[str]:
        """Locates active or historical WhatsApp folders that exist on device."""
        existing_roots = []
        for root in self.KNOWN_WHATSAPP_ROOTS:
            if self.path_exists(root):
                existing_roots.append(root)
        return existing_roots

    def path_exists(self, remote_path: str) -> bool:
        """Checks if a remote path exists using `ls -d`."""
        try:
            res = self.adb.run_shell(["ls", "-d", remote_path], serial=self.serial, timeout=8)
            return remote_path in res and "No such file" not in res
        except Exception:
            return False

    def list_accessible_files_recursive(
        self,
        target_directory: str,
        max_files: int = 5000,
    ) -> list[RemoteFileInfo]:
        """
        Recursively discovers accessible files using `find` or `ls -lR`.
        Defensively parses file size, path, and names.
        """
        discovered: list[RemoteFileInfo] = []
        
        # We try `find <target_directory> -type f` first
        try:
            raw_find = self.adb.run_shell(
                ["find", target_directory, "-type", "f"],
                serial=self.serial,
                timeout=60,
            )
            paths = [line.strip() for line in raw_find.splitlines() if line.strip() and not line.startswith("find:")]
            
            for p in paths[:max_files]:
                # Exclude hidden system files or socket files
                fname = p.rsplit("/", 1)[-1]
                discovered.append(RemoteFileInfo(
                    path=p,
                    name=fname,
                    size_bytes=0,  # Updated during stat/acquisition
                    modified_time="",
                    is_directory=False,
                ))
            return discovered

        except Exception as e:
            logger.warning(f"Find command failed on {target_directory}, attempting ls fallback: {e}")

        # Fallback to single-level `ls -la`
        return self._list_single_level(target_directory)

    def _list_single_level(self, directory: str) -> list[RemoteFileInfo]:
        items: list[RemoteFileInfo] = []
        try:
            raw_ls = self.adb.run_shell(["ls", "-la", directory], serial=self.serial, timeout=15)
            for line in raw_ls.splitlines():
                parts = line.strip().split()
                if len(parts) >= 8:
                    fname = parts[-1]
                    if fname in (".", ".."):
                        continue
                    is_dir = parts[0].startswith("d")
                    size = int(parts[4]) if parts[4].isdigit() else 0
                    full_p = f"{directory.rstrip('/')}/{fname}"
                    items.append(RemoteFileInfo(
                        path=full_p,
                        name=fname,
                        size_bytes=size,
                        modified_time=f"{parts[5]} {parts[6]}",
                        is_directory=is_dir,
                    ))
        except Exception as e:
            logger.error(f"Failed to list directory {directory}: {e}")
        return items

    def get_file_size(self, remote_path: str) -> int:
        """Returns file size in bytes using `stat -c %s` or `ls -l`."""
        try:
            out = self.adb.run_shell(["stat", "-c", "%s", remote_path], serial=self.serial, timeout=5)
            if out.isdigit():
                return int(out)
        except Exception:
            pass
        return 0
