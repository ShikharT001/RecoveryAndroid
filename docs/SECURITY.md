# RecoveryAndroid — Security, Privacy, and Forensics Policy

## Security Model

### 1. 100% Offline Processing
RecoveryAndroid operates entirely locally. There are no cloud servers, remote analytics, or telemetry pingbacks. All extracted databases, media files, and reports remain strictly on your local computer.

### 2. Privacy Redaction in Logs
The `RedactingFormatter` automatically scrubs sensitive personal details from all application log files:
- Phone numbers (+1..., +91...) are replaced with `[REDACTED-PHONE]`
- WhatsApp JIDs (`*@s.whatsapp.net`) are replaced with `[REDACTED-JID]`
- 32-character authentication keys or tokens are replaced with `[REDACTED-KEY]`

### 3. Source Preservation (Read-Only)
Digital forensic standards require evidence preservation:
- RecoverX performs only read operations on Android storage (`pull`, `ls`, `stat`, `find`).
- The application never executes write, delete, format, or truncate operations against connected Android storage devices.

### 4. Path Traversal & Disk Exhaustion Safeguards
- `SecureWorkspace` validates that every target file path resolves within the isolated job directory. Any attempt to traverse out (e.g. `../../Windows/System32`) raises a `PathTraversalSecurityError`.
- Available destination disk space is evaluated before large extractions to prevent system volume exhaustion.

### 5. Chain of Custody & Audit Logging
Every action (device connection, scan start, file acquisition, export) is recorded in an immutable audit ledger (`audit.jsonl`) and indexed with chunked SHA-256 hashes to guarantee data integrity.
