"""
RecoverX Device Detector
Enumerates connected devices via ADB, detects authorization states, and reads device hardware metrics.
"""

import re
import logging
from typing import Sequence
from app.devices.adb_client import AdbClient
from app.devices.device_info import DeviceInfo
from app.core.exceptions import AdbNotFoundError, DeviceUnauthorizedError, DeviceError

logger = logging.getLogger("recoverx.device_detector")


class DeviceDetector:
    """Discovers and inspects connected Android hardware over ADB."""

    def __init__(self, adb_client: AdbClient | None = None):
        self.adb = adb_client or AdbClient()

    def list_devices(self) -> list[DeviceInfo]:
        """
        Parses `adb devices -l` output defensively.
        Detects authorized, unauthorized, offline, and recovery states.
        """
        if not self.adb.is_available():
            raise AdbNotFoundError("Android SDK Platform-Tools (adb) not detected.")

        proc = self.adb.run_cmd(["devices", "-l"], check=False)
        lines = proc.stdout.splitlines()

        devices: list[DeviceInfo] = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("List of devices attached") or line.startswith("*"):
                continue

            parts = line.split()
            if not parts:
                continue

            serial = parts[0]
            state = parts[1] if len(parts) > 1 else "unknown"

            # Parse key-values like product:redfin model:Pixel_5 device:redfin
            props: dict[str, str] = {}
            for item in parts[2:]:
                if ":" in item:
                    k, v = item.split(":", 1)
                    props[k] = v

            dev = DeviceInfo(
                serial=serial,
                state=state,
                is_authorized=(state == "device"),
                product=props.get("product", ""),
                model=props.get("model", "Android Device").replace("_", " "),
                device=props.get("device", ""),
            )

            # If authorized, fetch detailed system properties
            if dev.is_authorized:
                self.populate_device_details(dev)

            devices.append(dev)

        return devices

    def populate_device_details(self, dev: DeviceInfo) -> None:
        """Fetches manufacturer, Android OS version, SDK level, and storage info."""
        try:
            # Batch property read
            props_raw = self.adb.run_shell(["getprop"], serial=dev.serial, timeout=10)
            props = self._parse_getprop(props_raw)

            dev.manufacturer = props.get("ro.product.manufacturer", dev.manufacturer).capitalize()
            dev.model = props.get("ro.product.model", dev.model).replace("_", " ")
            dev.android_version = props.get("ro.build.version.release", dev.android_version)
            
            sdk_str = props.get("ro.build.version.sdk", "")
            if sdk_str.isdigit():
                dev.sdk_version = int(sdk_str)

            # Storage capacity check via `df` on shared external storage
            df_out = self.adb.run_shell(["df", "/sdcard"], serial=dev.serial, timeout=8)
            total_b, free_b = self._parse_df(df_out)
            dev.storage_total_bytes = total_b
            dev.storage_free_bytes = free_b

        except Exception as e:
            logger.warning(f"Failed to fetch full properties for device {dev.serial}: {e}")

    @staticmethod
    def _parse_getprop(raw: str) -> dict[str, str]:
        """Extracts [key]: [value] pairs from `adb shell getprop` output."""
        pattern = re.compile(r'\[(.*?)\]:\s*\[(.*?)\]')
        props: dict[str, str] = {}
        for line in raw.splitlines():
            match = pattern.match(line.strip())
            if match:
                props[match.group(1)] = match.group(2)
        return props

    @staticmethod
    def _parse_df(df_output: str) -> tuple[int, int]:
        """
        Parses `df /sdcard` output.
        Standard format: Filesystem 1K-blocks Used Available Use% Mounted on
        Returns (total_bytes, free_bytes).
        """
        lines = [line.strip() for line in df_output.splitlines() if line.strip()]
        if len(lines) < 2:
            return 0, 0
        
        # Second line contains the numbers
        parts = lines[1].split()
        if len(parts) >= 4:
            try:
                # Typically in 1K blocks (or 512 bytes on older kernels)
                total_kb = int(parts[1])
                free_kb = int(parts[3])
                return total_kb * 1024, free_kb * 1024
            except ValueError:
                pass
        return 0, 0
