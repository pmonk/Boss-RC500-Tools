# Boss RC-500 Tools

A suite of Python utilities for musicians to manage their Boss RC-500 Loop Station. Back up all your loops instantly, restore audio to specific slots, or mass-delete unwanted tracks without the slow official software.

## Features
- **Auto-Detection:** Automatically scans drive letters to find the RC-500.
- **Smart Backup:** Extracts metadata (Name, BPM, Time Sig) and renames files automatically.
  - *Example:* `001_1.WAV` → `001_MySong_120bpm_4-4_Track_1.wav`
- **Range Support:** Backup or Delete specific ranges (e.g., "1-10, 15, 99").
- **Preview Mode:** "Scan Only" buttons let you verify what will happen before copying or deleting files.
- **Audio Restore:** Inject WAV files back into specific memory slots on the pedal.
- **HTML Reporting:** Generates a printable HTML/Markdown report of your entire library after backup.

---

## 🚀 Unified GUI
The tool is now a single, tabbed application handling all functions.

### 1. Connect & Run
1. **Connect your RC-500** via USB and ensure it is in **STORAGE** mode.
   *(Menu > Setup > USB > USB Mode > STORAGE)*
2. **Run the script**:
```bash
python BossRC500GUI.py
```
### 2. Tab: Backup / Export
- **Scope:** Choose "All Loops" or specify a "Range" (e.g., `90-99`).
- **Preview:** Click "Preview (Scan Only)" to see a list of detected loops in the log without copying anything.
- **Export:** Click "Start Backup" to copy files to your computer.
- **Report:** Once finished, click "View HTML Report" to see a table of your loops with names and BPMs.

### 3. Tab: Import / Restore
- **Audio Injection:** Select a folder containing your exported WAV files. The tool parses filenames (e.g., `Memory_01...`) and copies the audio back to the correct slot on the pedal.
- **⚠️ Limitation:** This restores **Audio Only**. The pedal does not allow external tools to write database metadata safely.
  - The pedal will play the new audio but may display the old song name.
  - You must manually rename the memory on the pedal to match.

### 4. Tab: Delete Loops
- **Mass Delete:** Enter a range (e.g., `10-20`) to wipe those slots from the pedal.
- **Safety First:** Always use the "Preview" button first to confirm which loops match your range.

---

## Requirements
- **Python 3.6+** (Standard installation usually includes `tkinter` for the GUI).
- A **Boss RC-500** Loop Station connected via USB.

## Why I made this
The default Boss Tone Studio software is slow and often requires handling tracks individually. This script leverages the RC-500's Mass Storage mode to grab everything at once, organizing it with useful filenames for immediate use in a DAW.

## ⚠️ Disclaimer
**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**
This tool performs file operations including **PERMANENT DELETION** of files on your pedal.
- The authors are not responsible for lost data.
- **ALWAYS BACKUP YOUR LOOPS** before using the delete function.
- Use at your own risk.

## License
GNU General Public License v3.0
