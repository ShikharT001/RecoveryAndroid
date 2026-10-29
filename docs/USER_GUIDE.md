# RecoveryAndroid — User Guide

## 1. Getting Started

### Prerequisites
- Windows 10 or Windows 11 (64-bit).
- USB Cable to connect your Android phone.
- Android SDK Platform-Tools (`adb.exe`).

### Enabling USB Debugging on Your Android Phone
1. Open **Settings** on your phone.
2. Scroll to **About Phone** (or **About Device**).
3. Find **Build Number** and tap it **7 times** until you see "You are now a developer!".
4. Go back to **Settings** → **System** → **Developer Options**.
5. Enable the toggle for **USB Debugging**.
6. Connect the phone to your Windows PC with a USB cable.
7. Look at your phone's screen: A prompt will appear: *"Allow USB debugging?"*. Check the box **"Always allow from this computer"** and tap **Allow**.

---

## 2. Connecting Your Phone in RecoverX

1. Launch RecoverX:
   ```powershell
   python main.py
   ```
2. Navigate to **Device Connection** on the left sidebar.
3. Click **Refresh Devices**!.
4. Select your phone from the dropdown list.
5. Verify that the status shows **`[AUTHORIZED]`**.
6. Click **Select & Confirm Device**.

---

## 3. Running a Recovery Scan

1. From the sidebar, click **Recovery Wizard**.
2. Choose your scan categories:
   - **WhatsApp Media**: Photos, videos, voice notes, stickers, audio.
   - **WhatsApp Backups**: Searches for historical databases and backup archives.
   - **Accessible Media**: Scans camera pictures (DCIM) and downloaded pictures.
   - **Documents**: Scans PDF attachments, documents, and transcripts.
3. Click **Start Recovery Scan**.
4. The application will transition to the **Scan Progress** view, showing live file counters, elapsed time, and an acquisition log.
5. You can click **Cancel Scan Safely** at any moment to stop acquisition while preserving all files acquired up to that point.

---

## 4. Viewing and Exporting Recovered Files

1. Go to **Recovered Files** in the sidebar.
2. Use the tabs (All, Images, Videos, Audio, Documents, Backups) or the search bar to locate specific files.
3. Double-click any file to open the **Forensic Preview** modal (supports images, text, and 512-byte hex view).
4. Select one or more files and click **Export Selected** to save them to any folder on your Windows computer.

---

## 5. WhatsApp Chat Inspection & Reports

1. Click **WhatsApp Chats** in the sidebar to review extracted message transcripts.
2. Messages found in older backups but absent in newer ones are highlighted with a red **`HISTORICAL/RECOVERED`** badge.
3. Click **Export HTML Transcript** or **Export CSV** to save the conversation.
4. Click **Forensic Reports** to generate an HTML chain-of-custody report containing SHA-256 hashes, device details, and evidence logs.
