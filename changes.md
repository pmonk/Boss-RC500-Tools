## Changes Report

### Version 1.1.3 - Selective Audio Restore & FAT32 / macOS Safety Hardening

**Summary:** Added selective file and slot-range restore options, FAT32 directory collision protection, and automatic macOS `dot_clean` sidecar cleanup to protect pedal storage integrity.

**Changes:**

* **Selective Import & Preview Mode**: Updated the **Import / Restore** tab in `BossRC500GUI.py` to default to picking **Specific WAV File(s)** directly, alongside a **Backup Folder** mode with an optional **Slot Filter** (e.g., `97` or `1-5`), a **Preview (Scan Only)** button, and explicit target slot summaries in the confirmation prompt.

* **FAT32 File-vs-Directory Collision Guard**: Added a check in `run_import()` to detect and remove any stray 0-byte file colliding with a target `ROLAND/WAVE/XXX_Y` directory path before creating the folder, preventing `Errno 20: Not a directory` errors.

* **Automatic macOS Sidecar Cleanup (`dot_clean`)**: Added `clean_macos_dotfiles()` to run `dot_clean -m` and remove `._*` AppleDouble files from `ROLAND` after import or delete operations on macOS, plus clean-eject reminders after USB writes.

* **Clearer Delete Boot-Sync Guidance**: Updated delete confirmation messaging to note that `MEMORY1.RC0` is not rewritten over USB and to use `WRITE -> CLEAR` on the pedal if a deleted slot is flagged on boot.

**Impact:**

* Prevents unintended multi-track overwrites when restoring from a folder containing multiple exported WAVs

* Protects the RC-500 FAT32 filesystem against `Errno 20` collisions and macOS AppleDouble artifacts

* Gives users a dry-run preview before writing restored audio to the pedal

**Files Modified:**

* `BossRC500GUI.py` - Selective file/slot restore, restore preview, FAT32 collision guard, and macOS `dot_clean` cleanup

* `README.md` - Documented selective restore, slot filtering, clean eject guidance, and delete `WRITE -> CLEAR` note

* `changes.md` - Added v1.1.3 release notes

### Version 1.1.2 - Cross-Platform Support & macOS Filesystem Hardening

**Summary:** Added cross-platform drive scanning for macOS, Windows, and Linux, hardened file operations against macOS AppleDouble resource forks, and updated repository documentation for direct `python3` execution.

**Changes:**

* **Cross-Platform Drive Auto-Detection**: Added `get_candidate_roots()` across the GUI and CLI utilities to automatically locate `ROLAND/WAVE` on Windows drive letters, macOS `/Volumes`, and Linux mount points (`/media`, `/run/media`, `/mnt`), along with manual path/browser fallback.

* **macOS Resource-Fork (`._*`) Filtering**: Excluded hidden AppleDouble sidecar files (`._*.WAV`) during backup previews, exports, and audio restores so Finder/Spotlight metadata files are never copied or parsed as audio tracks.

* **Top-Level Delete Directory Scanning**: Updated delete scanning in `BossRC500GUI.py` and `BossRC500Delete.py` to inspect direct `001_1`-style slot folders inside `ROLAND/WAVE` via `os.listdir()` rather than recursing through subdirectories.

* **Filename & CLI Parity**: Aligned exported filename sanitization between `BossRC500Export.py` and `BossRC500GUI.py`, and standardized CLI exit behavior using `sys.exit()`.

* **Documentation Refresh**: Updated `README.md` to reflect cross-platform `python3` usage, standalone CLI invocation, and `tkinter` setup notes.

**Impact:**

* Seamless plug-and-play usage on macOS, Windows, and Linux without pre-compiled `.exe` binaries

* Cleaner backup folders free of 4KB macOS `._*` sidecar artifacts

* Safer, faster slot targeting during bulk deletion

**Files Modified:**

* `BossRC500GUI.py` - Cross-platform scanning, `._*` filtering, and top-level delete scan

* `BossRC500Export.py` - Cross-platform scanning, `._*` filtering, filename parity, and `sys.exit()` cleanup

* `BossRC500Delete.py` - Cross-platform scanning, top-level delete scan, and `sys.exit()` cleanup

* `README.md` - Cross-platform instructions, CLI usage notes, and updated requirements

### Version 1.1.1 - Enhanced Metadata Parsing

**Summary:** Improved robustness of metadata extraction for Boss RC-500 loops.

**Changes:**

* **Enhanced Name Extraction**: Added `extract_name_from_codes()` function with better character code parsing that validates ASCII range (32-127) and handles malformed data more gracefully

* **Improved Error Handling**: More resilient parsing logic that prevents crashes on corrupted MEMORY1.RC0 files  

* **Backward Compatibility**: Maintained existing parsing methods as fallback for older data formats

* **GUI Robustness**: Applied same improvements to GUI metadata extraction to ensure consistent behavior between tools

**Impact:** 

* More reliable loop name extraction from RC-500 memory

* Better handling of edge cases and corrupted firmware data

* Consistent behavior between CLI export tool and GUI application

* No breaking changes to existing functionality

**Files Modified:**

* `BossRC500GUI.py` - Enhanced metadata parsing logic

* `BossRC500Export.py` - Enhanced metadata parsing logic stand alone

This update makes both tools more stable when working with different RC-500 firmware versions or data states.