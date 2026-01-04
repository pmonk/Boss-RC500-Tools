"""
Boss RC-500 Loop Deleter (CLI)
------------------------------
A utility to MASS DELETE loops from the Boss RC-500.
WARNING: This permanently removes files from the pedal.

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

WARNING:
This tool can PERMANENTLY DELETE files from your device.
The authors are not responsible for lost data.
ALWAYS BACKUP YOUR LOOPS BEFORE USING THE DELETE FUNCTION.
"""
import os
import shutil
import string

def find_boss_drive():
    available_drives = [f"{d}:/" for d in string.ascii_uppercase if os.path.exists(f"{d}:/")]
    for drive in available_drives:
        if os.path.exists(os.path.join(drive, "ROLAND", "WAVE")):
            return os.path.join(drive, "ROLAND", "WAVE")
    return None

def parse_range(range_str):
    ids = set()
    parts = range_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                ids.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                ids.add(int(part))
            except ValueError:
                continue
    return sorted(list(ids))

# --- MAIN ---
print("--- Boss RC-500 Mass Deleter ---")
source_dir = find_boss_drive()

if not source_dir:
    print("Error: Boss RC-500 not found.")
    input("Press Enter to exit...")
    exit()

print(f"Target: {source_dir}")

# Input Range
range_input = input("Enter memory slots to DELETE (e.g., '10-20' or '5, 8, 12'): ")
target_slots = parse_range(range_input)

if not target_slots:
    print("No valid slots selected.")
    exit()

# Scan for targets
folders_to_delete = []
print("\n--- Scanning for targets ---")

for root, dirs, files in os.walk(source_dir):
    folder_name = os.path.basename(root)
    # Folder format is "001_1", "001_2", etc.
    if "_" in folder_name:
        try:
            slot_str = folder_name.split("_")[0]
            slot_num = int(slot_str)
            
            if slot_num in target_slots:
                folders_to_delete.append(root)
                print(f"[FOUND] Memory {slot_num}: {folder_name}")
        except ValueError:
            pass

if not folders_to_delete:
    print("\nNo matching folders found on the pedal.")
    exit()

# --- CONFIRMATION ---
print(f"\nWARNING: You are about to DELETE {len(folders_to_delete)} folders/tracks.")
print("Make sure you have exported any loops you want to keep.")  # <--- NEW WARNING
print("This cannot be undone.")

confirm = input("Type 'DELETE' to confirm (or anything else to cancel): ")

if confirm == "DELETE":
    print("\nDeleting...")
    for folder in folders_to_delete:
        try:
            shutil.rmtree(folder) # PERMANENT DELETE
            print(f"Deleted: {folder}")
        except Exception as e:
            print(f"Error deleting {folder}: {e}")
    print("Deletion Complete.")
else:
    print("Cancelled.")
    
input("Press Enter to close...")
