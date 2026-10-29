"""
RecoverX Exceptions Hierarchy
Defines domain-specific exceptions for device communication, storage acquisition,
forensic parsing, and data validation.
"""


class RecoverXError(Exception):
    """Base class for all RecoverX exceptions."""
    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or ""

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} ({self.details})"
        return self.message


# ----------------------------------------------------------------------
# Device & ADB Errors
# ----------------------------------------------------------------------

class DeviceError(RecoverXError):
    """Base error for Android device and ADB issues."""
    pass


class AdbNotFoundError(DeviceError):
    """ADB executable could not be located in PATH or configured directory."""
    pass


class DeviceNotFoundError(DeviceError):
    """Target Android device could not be found or was unplugged."""
    pass


class DeviceUnauthorizedError(DeviceError):
    """Target Android device is present but USB debugging is unauthorized."""
    pass


class DeviceDisconnectedError(DeviceError):
    """Android device was disconnected unexpectedly during an operation."""
    pass


class DeviceCommandTimeoutError(DeviceError):
    """ADB command execution timed out."""
    pass


# ----------------------------------------------------------------------
# Acquisition & Storage Errors
# ----------------------------------------------------------------------

class AcquisitionError(RecoverXError):
    """Base error for evidence acquisition and file extraction."""
    pass


class PermissionDeniedError(AcquisitionError):
    """Access to target path or storage partition was denied."""
    pass


class InsufficientDiskSpaceError(AcquisitionError):
    """Destination disk does not have enough free space for acquisition."""
    pass


class HashMismatchError(AcquisitionError):
    """Calculated file hash does not match source or expected hash."""
    pass


class PathTraversalSecurityError(AcquisitionError):
    """Detected unsafe file path attempting directory traversal."""
    pass


# ----------------------------------------------------------------------
# Parsing & Analysis Errors
# ----------------------------------------------------------------------

class ParsingError(RecoverXError):
    """Base error for WhatsApp and file parsing operations."""
    pass


class DatabaseCorruptedError(ParsingError):
    """SQLite database file is corrupted or malformed."""
    pass


class UnsupportedSchemaError(ParsingError):
    """Database schema version or structure is not supported."""
    pass


class EncryptedBackupError(ParsingError):
    """Backup is encrypted and cannot be parsed without authorized keys."""
    pass


class ExportParseError(ParsingError):
    """Exported chat text or archive could not be parsed."""
    pass


# ----------------------------------------------------------------------
# Repository & Storage Errors
# ----------------------------------------------------------------------

class StorageRepositoryError(RecoverXError):
    """Local SQLite repository error."""
    pass


class DatabaseMigrationError(StorageRepositoryError):
    """Failure while executing schema migrations on local database."""
    pass
