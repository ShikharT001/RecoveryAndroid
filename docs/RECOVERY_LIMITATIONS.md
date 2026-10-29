# RecoveryAndroid — Recovery Capabilities & Limitations

## Forensic Transparency Principle
RecoveryAndroid adheres strictly to honest forensic reporting. It will never invent files, fabricate deleted counts, or misrepresent the physical boundaries of consumer Android devices.

## What RecoveryAndroid Can Recover
1. **Accessible WhatsApp Media**: Photos, videos, voice notes, audio files, and documents residing in accessible external shared storage (`/sdcard/WhatsApp/Media` and `/sdcard/Android/media/com.whatsapp/WhatsApp/Media`).
2. **WhatsApp Backups**: Locates `msgstore.db` and encrypted backup archives (`msgstore.db.crypt12/14/15`).
3. **Readable Message Databases**: Directly parses unencrypted SQLite databases (`msgstore.db`), extracting sender, timestamp, body text, and attachment references.
4. **Historical Messages via Differential Analysis**: When multiple backup snapshots are provided, RecoverX identifies messages that existed in older snapshots but were deleted before newer snapshots were taken.
5. **Exported Chat Transcripts**: Ingests user-exported `.txt` transcripts and zipped export bundles, reconstructing message threads with attachments.

## Technical Boundaries & What Is Not Possible
1. **Android App Sandbox (/data/data)**:
   - On standard, production Android devices running Android 10+, application private directories (`/data/data/com.whatsapp`) are protected by Linux kernel DAC (discretionary access control) and SELinux policies.
   - Non-root ADB cannot read `/data/data`. RecoverX does not exploit kernel vulnerabilities or bypass operating system security locks.
2. **Encrypted Backups Without Encryption Keys**:
   - Backups ending in `.crypt14` or `.crypt15` use AES-GCM encryption with keys stored inside the protected app sandbox or WhatsApp key servers.
   - Without the user's 64-digit end-to-end encryption key or device key file, encrypted backups cannot be decrypted. Renaming does not decrypt data.
3. **Overwritten Flash Storage (TRIM & Wear-Leveling)**:
   - Modern smartphones utilize UFS or eMMC flash memory. When a file is deleted and sectors are cleared via hardware TRIM/discard commands, raw unallocated blocks return zeroes.
   - Standard USB communication cannot perform physical block-level carving without chip-off hardware extraction.
