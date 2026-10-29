# RecoveryAndroid — Automated Testing Guide

RecoveryAndroid includes a comprehensive automated test suite built with `pytest` and `pytest-qt`. In compliance with digital forensics safety guidelines, all tests run using synthetic fixtures without requiring a physical connected phone or private personal data.

## Running Tests

### Run Full Test Suite
```powershell
.\.venv\Scripts\pytest -v
```

### Run Specific Modules
```powershell
# Device detection tests (mocked subprocess)
.\.venv\Scripts\pytest tests\test_device_detection.py -v

# WhatsApp chat & database parser tests
.\.venv\Scripts\pytest tests\test_database_parser.py -v
.\.venv\Scripts\pytest tests\test_chat_export_parser.py -v

# Storage repository & secure workspace tests
.\.venv\Scripts\pytest tests\test_repository.py -v

# PySide6 desktop UI tests (offscreen Qt)
.\.venv\Scripts\pytest tests\test_ui.py -v
```

## Test Coverage Overview
- `test_device_detection.py`: Verifies `adb devices -l` parsing, unauthorized state detection, offline devices, and timeout exceptions.
- `test_acquisition.py`: Tests safe pulling, chunked SHA-256 calculation, hash mismatch exceptions, and cancellation responsiveness.
- `test_signature_detector.py`: Validates magic bytes for JPEG, PNG, SQLite, MP4, and flags spoofed file extensions.
- `test_integrity_checker.py`: Detects zero-byte files, valid image structures, and corrupted headers.
- `test_database_parser.py`: Evaluates legacy SQLite WhatsApp schemas and differential historical snapshot comparisons.
- `test_chat_export_parser.py`: Verifies international date formats, multiline message assembly, and attachment parsing.
- `test_repository.py`: Tests device upserts, scan jobs, deduplication, and secure workspace path traversal defenses.
- `test_export.py`: Validates file copies, CSV, JSON, and forensic HTML report generation.
- `test_ui.py`: Verifies PySide6 window initialization, sidebar navigation, card updates, and wizard routing.
