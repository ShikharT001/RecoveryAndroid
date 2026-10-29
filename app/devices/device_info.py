"""
RecoverX Device Information Model
"""

from pydantic import BaseModel, Field


class DeviceInfo(BaseModel):
    serial: str
    model: str = "Unknown Device"
    manufacturer: str = "Unknown"
    android_version: str = "Unknown"
    sdk_version: int = 0
    state: str = "device"  # "device", "unauthorized", "offline", "recovery"
    product: str = ""
    device: str = ""
    storage_total_bytes: int = 0
    storage_free_bytes: int = 0
    battery_level: int | None = None
    usb_configuration: str = ""
    is_authorized: bool = True

    @property
    def display_name(self) -> str:
        if self.manufacturer and self.manufacturer != "Unknown":
            return f"{self.manufacturer} {self.model} ({self.serial})"
        return f"{self.model} ({self.serial})"
