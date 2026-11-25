## Changes Report

### Version 1.1.2 - Cross-Platform Support & macOS Filesystem Hardening

**Summary:** Added cross-platform drive scanning for macOS, Windows, and Linux, hardened file operations against macOS AppleDouble resource forks, and updated repository documentation for direct `python3` execution.

**Changes:**
- **Cross-Platform Drive Auto-Detection**: Added `get_candidate_roots()` across the GUI and CLI utilities to automatically locate `ROLAND/WAVE` on Windows drive letters, macOS `/Volumes`, and Linux mount points (`/media`, `/run/media`, `/mnt`), along with manual path/browser fallback.
- **macOS Resource-Fork (`._*`) Filtering**: Excluded hidden AppleDouble sidecar files (`._*.WAV`) during backup previews, exports, and audio restores so Finder/Spotlight metadata files are never copied or parsed as audio tracks.
- **Top-Level Delete Directory Scanning**: Updated delete scanning in `BossRC500GUI.py` and `BossRC500Delete.py` to inspect direct `001_1`-style slot folders inside `ROLAND/WAVE` via `os.listdir()` rather than recursing through subdirectories.
- **Filename & CLI Parity**: Aligned exported filename sanitization between `BossRC500Export.py` and `BossRC500GUI.py`, and standardized CLI exit behavior using `sys.exit()`.
- **Documentation Refresh**: Updated `README.md` to reflect cross-platform `python3` usage, standalone CLI invocation, and `tkinter` setup notes.

**Impact:**
- Seamless plug-and-play usage on macOS, Windows, and Linux without pre-compiled `.exe` binaries
- Cleaner backup folders free of 4KB macOS `._*` sidecar artifacts
- Safer, faster slot targeting during bulk deletion

**Files Modified:**
- `BossRC500GUI.py` - Cross-platform scanning, `._*` filtering, and top-level delete scan
- `BossRC500Export.py` - Cross-platform scanning, `._*` filtering, filename parity, and `sys.exit()` cleanup
- `BossRC500Delete.py` - Cross-platform scanning, top-level delete scan, and `sys.exit()` cleanup
- `README.md` - Cross-platform instructions, CLI usage notes, and updated requirements

---

### Version 1.1.1 - Enhanced Metadata Parsing

**Summary:** Improved robustness of metadata extraction for Boss RC-500 loops.

**Changes:**
- **Enhanced Name Extraction**: Added `extract_name_from_codes()` function with better character code parsing that validates ASCII range (32-127) and handles malformed data more gracefully
- **Improved Error Handling**: More resilient parsing logic that prevents crashes on corrupted MEMORY1.RC0 files  
- **Backward Compatibility**: Maintained existing parsing methods as fallback for older data formats
- **GUI Robustness**: Applied same improvements to GUI metadata extraction to ensure consistent behavior between tools

**Impact:** 
- More reliable loop name extraction from RC-500 memory
- Better handling of edge cases and corrupted firmware data
- Consistent behavior between CLI export tool and GUI application
- No breaking changes to existing functionality

**Files Modified:**
- `BossRC500GUI.py` - Enhanced metadata parsing logic
- `BossRC500Export.py` - Enhanced metadata parsing logic stand alone

This update makes both tools more stable when working with different RC-500 firmware versions or data states.