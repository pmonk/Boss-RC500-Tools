# Boss RC-500 Loop Exporter

A simple Python utility for musicians who want to backup their Boss RC-500 loops without using the slow "one-by-one" official software.

## Features
- **Auto-Detection:** Automatically scans drive letters to find the RC-500 (no need to specify `D:` or `E:`).
- **One-Click Backup:** Runs instantly and saves all loops to a timestamped folder (e.g., `Boss RC-500 Loop Backups 2026-01-03`).
- **Readable Filenames:** Renames the obscure internal file structure (e.g., `001_1.WAV`) to human-readable names like `Memory_001_Track_1.wav`.
- **Full Quality:** Preserves the original 32-bit float WAV files.

## How to Use
1. **Connect your RC-500** via USB and ensure it is in **STORAGE** mode (Menu > Setup > USB > USB Mode > STORAGE).
2. **Download** the `BossRC500Export.py` script.
3. **Place the script** in the folder where you want your backups to live (e.g., `My Music/Backups`).
4. **Run the script** (double-click the file, or run via terminal with `python BossRC500Export.py`).

## GUI Version (New!)
Prefer a visual interface? Run `BossRC500GUI.py` instead!
- **Visual Log:** See exactly what is being copied.
- **Select Destination:** easy "Browse" button to pick where backups go.
- **Non-Freezing:** Runs in the background so you can keep working.

On Windows you can double-click the file and it will run or...

Run it with:
```bash
python BossRC500GUI.py
```
## Requirements
- Python 3.6+
- A Boss RC-500 Loop Station

## Why I made this
The default Boss Tone Studio software requires importing/exporting tracks individually or uses a proprietary backup format. This script leverages the RC-500's Mass Storage mode to grab everything at once and organize it for immediate use in a DAW.

## License
GNU General Public License v3.0
