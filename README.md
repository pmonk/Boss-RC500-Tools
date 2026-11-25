# Boss RC-500 Tools

*Note: Pre-compiled `.exe` releases have been removed since Windows blocks unsigned executables without paid code signing—just run the Python scripts directly instead.*

A suite of cross-platform Python utilities for musicians to manage their Boss RC-500 Loop Station on Windows, macOS, and Linux. Back up all your loops instantly, restore audio to specific slots, or mass-delete unwanted tracks without the slow official software.

## Features
- **Cross-Platform Auto-Detection:** Automatically scans mounted drives and volumes across Windows, macOS, and Linux to find the RC-500 (with manual folder browsing/path override fallback).
- **Smart Backup:** Extracts metadata (Name, BPM, Time Sig) and renames files automatically.
  - *Example:* `001_1.WAV` → `001_MySong_120bpm_4-4_Track_1.wav`
- **Range Support:** Backup or Delete specific ranges (e.g., `"1-10, 15, 99"`).
- **Preview Mode:** "Scan Only" buttons let you verify what will happen before copying or deleting files.
- **Audio Restore:** Inject WAV files back into specific memory slots on the pedal.
- **HTML & Markdown Reporting:** Generates printable HTML and Markdown reports of your entire library after backup.

---

## Unified GUI
The main tool is a single, tabbed application handling all functions.

### 1. Connect & Run
1. **Connect your RC-500** via USB and ensure it is in **STORAGE** mode.
   *(MENU > GENERAL > STORAGE > CONNECTING... or Menu > Setup > USB > USB Mode > STORAGE depending on firmware)*
2. **Run the script**:
   - **macOS / Linux:**
     ```bash
     python3 BossRC500GUI.py
     ```
   - **Windows:**
     ```bash
     python BossRC500GUI.py
     ```

### 2. Tab: Backup / Export
- **Scope:** Choose "All Loops" or specify a "Range" (e.g., `90-99`).
- **Preview:** Click "Preview (Scan Only)" to see a list of detected loops in the log without copying anything.
- **Export:** Click "Start Backup" to copy files to your computer.
- **Report:** Once finished, click "View HTML Report" to see a table of your loops with names and BPMs.

### 3. Tab: Import / Restore
- **Audio Injection:** Select a folder containing your exported WAV files. The tool parses filenames (e.g., `Memory_01...` or `001_...`) and copies the audio back to the correct slot on the pedal.
- **Limitation:** This restores **Audio Only**. The pedal does not allow external tools to write database metadata safely.
  - The pedal will play the new audio but may display the old song name.
  - You must manually rename the memory on the pedal to match.

### 4. Tab: Delete Loops
- **Mass Delete:** Enter a range (e.g., `10-20`) to wipe those slots from the pedal.
- **Safety First:** Always use the "Preview (Scan Only)" button first to confirm which loops match your range.

---

## Standalone CLI Scripts (Optional)
If you prefer running headless scripts from the terminal, standalone CLI tools are also included (with optional manual mount path arguments):
```bash
python3 BossRC500Export.py [/Volumes/BOSS_RC-500]
python3 BossRC500Delete.py [/Volumes/BOSS_RC-500]
```

---

## Requirements
- **Python 3.6+** (Standard installations on Windows and macOS include `tkinter` for the GUI; on macOS via Homebrew, you may need `brew install python-tk`, and on Debian/Ubuntu Linux, `sudo apt install python3-tk`).
- A **Boss RC-500** Loop Station connected via USB.

## Why I made this
The default Boss Tone Studio software is slow and often requires handling tracks individually. This script leverages the RC-500's Mass Storage mode to grab everything at once, organizing it with useful filenames for immediate use in a DAW.

## Disclaimer
**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**
This tool performs file operations including **PERMANENT DELETION** of files on your pedal.
- The authors are not responsible for lost data.
- **ALWAYS BACKUP YOUR LOOPS** before using the delete function.
- Use at your own risk.

## License
GNU General Public License v3.0