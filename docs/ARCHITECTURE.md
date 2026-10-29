# RecoveryAndroid — System Architecture

## Overview
RecoveryAndroid is engineered as a layered, modular desktop forensics and data-recovery application. It separates device communication, forensic analysis, persistence, and desktop presentation into decoupled subsystems.

```
+-------------------------------------------------------------------+
|                        PySide6 Desktop UI                         |
|   Dashboard | Device Panel | Wizard | Progress | Results | Chat   |
+---------------------------------+---------------------------------+
                                  | (Qt Signals / Slots)
+---------------------------------v---------------------------------+
|                       Core Job Manager                            |
|             ScanWorker (QThread) | ScanConfiguration              |
+---------------------------------+---------------------------------+
        |                         |                         |
+-------v-------+         +-------v-------+         +-------v-------+
| Device Engine |         | Recovery Core |         | WhatsApp Core |
|  - AdbClient  |         | - Signature   |         | - DbParser    |
|  - Detector   |         | - Integrity   |         | - ExportParser|
|  - Acquisition|         | - Classifier  |         | - BackupInfo  |
+-------+-------+         +-------+-------+         +-------+-------+
        |                         |                         |
+-------v-------------------------v-------------------------v-------+
|                     Storage & Manifest Layer                      |
|         DatabaseManager (SQLite) | StorageRepository              |
|         SecureWorkspace          | EvidenceManifest               |
+-------------------------------------------------------------------+
```

## Architectural Highlights
1. **Subprocess Isolation**: ADB commands are executed strictly through argument arrays (`["devices", "-l"]`) rather than shell string concatenation, mitigating command injection risks.
2. **Path Traversal Shield**: The `SecureWorkspace` enforces strict containment checks before creating any file, preventing directory traversal attacks from compromised backup files.
3. **Multi-Generation Database Support**: WhatsApp database structures vary across Android versions. RecoverX uses `SchemaDetector` to dynamically adapt SQL queries for legacy `messages`, modern `message`/`chat`, or view schemas.
4. **Differential Message Recovery**: When analyzing historical database backups alongside recent snapshots, messages present in the older snapshot but missing from the newer one are tagged as `HISTORICAL/RECOVERED`.
