## Changes Report

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