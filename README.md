# RecoveryAndroid — Android & WhatsApp Data Recovery

> **Recover what is still recoverable.**

RecoveryAndroid is a digital-forensics and data recovery desktop application engineered for Windows (10/11) to discover, inspect, verify, and recover accessible WhatsApp data, media attachments, historical backups, and files from connected Android devices and local backup archives.

---

## 🌟 Key Features

- **USB & ADB Device Discovery**: Defensive Android discovery over standard USB debugging. Safely reads model, brand, Android version, battery, and accessible storage partitions.
- **WhatsApp Media Recovery**: Discovers accessible and historical WhatsApp photos, video attachments, audio, voice notes, documents, and stickers.
- **Backup & Snapshot Discovery**: Locates `msgstore.db.crypt*`, local SQLite databases, and user-provided backup snapshots.
- **Readable SQLite Chat Reconstruction**: Defensive parsing of unencrypted SQLite databases (`msgstore.db`), schema auto-detection, and differential historical message recovery.
- **Exported Chat Parser**: Defensive ingestion of exported `.txt` and `.zip` chat transcripts with multiline and varied timestamp support.
- **Cryptographic Integrity & SHA-256**: Chunked hashing, tamper-detection, duplicate identification, and signature/magic-byte classification.
- **Dark Charcoal & Neon Accent Forensic UI**: PySide6 dark UI with real-time responsive progress, background multi-threading, live search, and file previews.
- **Comprehensive Reporting**: Generates forensic audit logs, manifest records, and clean HTML/JSON/CSV recovery reports.

---

## 🔒 Forensic & Ethical Principles

RecoveryAndroid adheres strictly to digital forensics standards:
1. **Source Preservation**: Read-only source access. Never modifies, alters, or deletes data on the source Android device.
2. **Honest Recovery Classification**: Does not invent fake deleted files or simulate recovery statistics. Items are classified based on verifiable physical or metadata evidence.
3. **Privacy First**: Completely offline. No cloud telemetry, no analytics, no external servers. Sensitive fields are redacted from logs.
4. **No Vulnerability Exploits**: Operates via standard authorized ADB and user-selected storage. Does not circumvent device locks or execute hostile root exploits.

---

## 🛠️ Quick Start

### Prerequisites
- Windows 10 or 11 (64-bit).
- Python 3.12 (or a compatible maintained release).
- Android SDK Platform-Tools (`adb.exe` on PATH or specified in RecoveryAndroid Settings).
- USB Cable and Android device with **USB Debugging** enabled in Developer Options.

### Setup Development Environment
```powershell
# 1. Create virtual environment
uv venv --python 3.12 .venv
# or: python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\activate

# 3. Install dependencies
uv pip install -r requirements.txt
# or: pip install -r requirements.txt

# 4. Launch RecoveryAndroid
python main.py
```

### Run Tests
```powershell
.\.venv\Scripts\pytest -v
```

---

## 📦 Building Standalone Windows Executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```
The executable is produced in the `dist\RecoveryAndroid\` folder.

---

## 📖 License
MIT License. See [LICENSE](LICENSE) for details.
