"""
Boss RC-500 Loop Exporter
-------------------------
A Python utility to auto-detect a connected Boss RC-500 Loop Station
and backup all WAV loops into a flattened, readable directory structure.

Copyright (C) 2026 [pmonk.com]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

DISCLAIMER OF WARRANTY:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import shutil
import string
from datetime import datetime

def find_boss_drive():
    """
    Scans Windows drive letters to find the one containing the 
    Boss RC-500 directory structure (ROLAND/WAVE).
    """
    # Loop through standard Windows drive letters (A-Z)
    available_drives = [f"{d}:/" for d in string.ascii_uppercase if os.path.exists(f"{d}:/")]
    
    for drive in available_drives:
        # We look for the specific path that exists on Boss loopers
        candidate_path = os.path.join(drive, "ROLAND", "WAVE")
        if os.path.exists(candidate_path):
            return candidate_path
            
    return None

# --- MAIN CONFIGURATION ---

# 1. Auto-detect source directory
print("Scanning for Boss RC-500...")
source_dir = find_boss_drive()

if not source_dir:
    print("Error: Could not find a drive with 'ROLAND/WAVE' folder.")
    print("Please ensure the RC-500 is in STORAGE mode and connected via USB.")
    input("Press Enter to exit...")
    exit()

print(f"Found Boss RC-500 at: {source_dir}")

# 2. Set dynamic destination directory
# This gets the folder where THIS script is currently saved
script_location = os.path.dirname(os.path.abspath(__file__))
current_date = datetime.now().strftime("%Y-%m-%d")
folder_name = f"Boss RC-500 Loop Backups {current_date}"

dest_dir = os.path.join(script_location, folder_name)

# --- EXECUTION ---

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    print(f"Created backup folder: {dest_dir}\n")

count = 0

for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.lower().endswith('.wav'):
            # Parent folder name is like "001_1" (Memory_Track)
            folder_name_raw = os.path.basename(root)
            
            try:
                # Parse the folder name to get slot and track
                parts = folder_name_raw.split('_')
                if len(parts) >= 2:
                    memory_slot = parts[0]
                    track_num = parts[1]
                    
                    new_filename = f"Memory_{memory_slot}_Track_{track_num}.wav"
                    
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(dest_dir, new_filename)
                    
                    shutil.copy2(old_path, new_path)
                    print(f"Exported: {new_filename}")
                    count += 1
            except ValueError:
                print(f"Skipping weird folder: {folder_name_raw}")

print(f"\nSuccess! {count} loops backed up to:")
print(dest_dir)
input("Press Enter to close...")
