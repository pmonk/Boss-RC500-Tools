# Boss RC-500 Tools

A suite of Python utilities for musicians to manage their Boss RC-500 Loop Station. Back up all your loops instantly or mass-delete unwanted tracks without the slow official software.

## Features
- **Auto-Detection:** Automatically scans drive letters to find the RC-500.
- **One-Click Backup:** Runs instantly and saves all loops to a timestamped folder.
- **Readable Filenames:** Renames the obscure internal file structure (e.g., `001_1.WAV`) to human-readable names like `Memory_001_Track_1.wav`.
- **Mass Delete:** Quickly clear ranges of memory slots (e.g., delete slots 10-50 in one go).
- **Full Quality:** Preserves the original 32-bit float WAV files.

---

## 🚀 GUI Version (Recommended)
The easiest way to use these tools is the graphical interface.

1. **Connect your RC-500** via USB and ensure it is in **STORAGE** mode.
   *(Menu > Setup > USB > USB Mode > STORAGE)*
2. **Download** `BossRC500GUI.py`.
3. **Run the script** (double-click on Windows, or use terminal).

```bash
python BossRC500GUI.py
```
## Requirements
## Requirements
- **Python 3.6+** (Standard installation usually includes `tkinter` for the GUI).
- A **Boss RC-500** Loop Station connected via USB.

## Why I made this
The default Boss Tone Studio software requires importing/exporting tracks individually or uses a proprietary backup format. This script leverages the RC-500's Mass Storage mode to grab everything at once and organize it for immediate use in a DAW.

## ⚠️ Disclaimer
**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**
This tool performs file operations including **PERMANENT DELETION** of files on your pedal.
- The authors are not responsible for lost data.
- **ALWAYS BACKUP YOUR LOOPS** before using the delete function.
- Use at your own risk.

## License
GNU General Public License v3.0

