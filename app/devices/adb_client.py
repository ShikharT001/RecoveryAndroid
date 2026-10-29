"""
RecoverX ADB Client
Defensive, subprocess-safe interface for the Android Debug Bridge.
Guarantees argument list execution, non-root compliance, explicit timeouts, and serial isolation.
"""

import subprocess
import shutil
import os
from pathlib import Path
from typing import Sequence
import logging

from app.core.exceptions import (
    AdbNotFoundError,
    DeviceNotFoundError,
    DeviceUnauthorizedError,
    DeviceDisconnectedError,
    DeviceCommandTimeoutError,
    PermissionDeniedError,
)

logger = logging.getLogger("recoverx.adb")


class AdbClient:
    """Manages execution of ADB commands with serial isolation and defensive error handling."""

    def __init__(self, adb_path: str = ""):
        self.adb_bin = self._resolve_adb_binary(adb_path)

    @classmethod
    def _resolve_adb_binary(cls, configured_path: str = "") -> str:
        """Locates adb.exe from configuration, PATH, or standard Android SDK directories."""
        if configured_path and Path(configured_path).is_file():
            return str(Path(configured_path).resolve())

        # Check standard PATH
        found_in_path = shutil.which("adb")
        if found_in_path:
            return found_in_path

        # Standard Windows locations
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            candidate = Path(local_app_data) / "Android" / "Sdk" / "platform-tools" / "adb.exe"
            if candidate.is_file():
                return str(candidate)

        # Check workspace tools
        workspace_tools = Path("platform-tools") / "adb.exe"
        if workspace_tools.is_file():
            return str(workspace_tools.resolve())

        return "adb"

    def is_available(self) -> bool:
        """Checks if ADB executable can be called."""
        try:
            res = subprocess.run(
                [self.adb_bin, "version"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return res.returncode == 0
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            return False

    def run_cmd(
        self,
        args: Sequence[str],
        serial: str | None = None,
        timeout: int = 30,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """
        Executes an ADB command safely using argument lists.
        Always prepends `-s <serial>` when serial is provided to prevent ambiguous execution.
        """
        cmd = [self.adb_bin]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except FileNotFoundError:
            raise AdbNotFoundError(f"ADB executable not found at '{self.adb_bin}'")
        except subprocess.TimeoutExpired:
            raise DeviceCommandTimeoutError(
                f"ADB command timed out after {timeout} seconds",
                details=" ".join(cmd)
            )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        # Check common ADB error patterns
        if "device unauthorized" in stderr.lower() or "device unauthorized" in stdout.lower():
            raise DeviceUnauthorizedError(
                "Target device is unauthorized. Please accept the USB debugging prompt on the phone screen.",
                details=serial or ""
            )

        if "device not found" in stderr.lower() or "device not found" in stdout.lower():
            raise DeviceNotFoundError(
                "Device disconnected or not found.",
                details=serial or ""
            )

        if "device offline" in stderr.lower():
            raise DeviceDisconnectedError(
                "Device is offline. Reconnect USB cable.",
                details=serial or ""
            )

        if check and proc.returncode != 0:
            if "permission denied" in stderr.lower():
                raise PermissionDeniedError(
                    f"Access denied to target Android resource: {stderr}",
                    details=" ".join(args)
                )

        return proc

    def run_shell(
        self,
        shell_args: Sequence[str],
        serial: str,
        timeout: int = 30,
    ) -> str:
        """Executes an `adb shell <args>` command on the specified device and returns stdout."""
        if not serial:
            raise ValueError("Serial number is required for device shell execution.")
        args = ["shell"] + list(shell_args)
        proc = self.run_cmd(args, serial=serial, timeout=timeout)
        return proc.stdout.strip()
