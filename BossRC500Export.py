"""
Boss RC-500 Loop Exporter (CLI)
-------------------------------------
A Python utility to auto-detect a connected Boss RC-500 Loop Station
and backup all WAV loops into a flattened, readable directory structure.
Generates a Markdown library report with Time Signatures and Rhythm settings.

Copyright (C) 2026 [pmonk.com]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import os
import shutil
import string
import re
from datetime import datetime


def get_time_signature_map(beat_val):
    """
    Maps the RC-500 internal <Beat> integer to a readable string.
    """
    beat_map = {
        0: "2/4",
        1: "3/4",
        2: "4/4",
        3: "5/4",
        4: "6/4",
        5: "7/4",
        6: "5/8",
        7: "6/8",
        8: "7/8",
        9: "8/8",
        10: "9/8",
        11: "10/8",
        12: "11/8",
        13: "12/8",
        14: "13/8",
        15: "14/8",
        16: "15/8"
    }
    return beat_map.get(beat_val, "?")

def find_boss_drive():
    """
    Scans Windows drive letters to find the one containing the 
    Boss RC-500 directory structure (ROLAND/WAVE).
    """
    available_drives = [f"{d}:/" for d in string.ascii_uppercase if os.path.exists(f"{d}:/")]
    
    for drive in available_drives:
        candidate_path = os.path.join(drive, "ROLAND", "WAVE")
        if os.path.exists(candidate_path):
            return candidate_path
            
    return None

def get_memory_metadata(boss_wave_path):
    """
    Parses MEMORY1.RC0 using REGEX to extract Name, BPM, Time Sig, Pattern, and Kit.
    """
    metadata = {}
    
    try:
        data_dir = os.path.abspath(os.path.join(boss_wave_path, "..", "DATA"))
        xml_path = os.path.join(data_dir, "MEMORY1.RC0")
        
        if not os.path.exists(xml_path):
            print("Warning: Could not find metadata file (MEMORY1.RC0).")
            return {}

        print("Extracting metadata from MEMORY1.RC0...")
        
        with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find all <mem id="X"> blocks
        mem_pattern = r'<mem id="(\d+)">(.*?)</mem>'
        mem_blocks = re.findall(mem_pattern, content, re.DOTALL)
        
        print(f"Found {len(mem_blocks)} memory blocks.\n")
        
        for mem_id_str, mem_content in mem_blocks:
            mem_id = int(mem_id_str) + 1
            data = {
                'name': '', 
                'bpm': '', 
                'bpm_raw': 0,
                'ts': '', 
                'ts_raw': '', 
                'pattern': '', 
                'kit': ''
            }
            
            # 1. NAME
            name_pattern = r'<C(\d+)>(\d+)</C\d+>'
            name_codes = re.findall(name_pattern, mem_content)
            if name_codes:
                name_codes.sort(key=lambda x: int(x[0]))
                chars = []
                for idx, code_str in name_codes:
                    try:
                        chars.append(chr(int(code_str)))
                    except: pass
                raw_name = "".join(chars).strip()
                if raw_name:
                    data['name'] = "".join([c for c in raw_name if c.isalnum() or c in ('-', '_')])
            
            # 2. BPM
            tempo_match = re.search(r'<Tempo>(\d+)</Tempo>', mem_content)
            if tempo_match:
                try:
                    raw_bpm = int(tempo_match.group(1))
                    bpm = raw_bpm / 10.0
                    data['bpm_raw'] = bpm
                    data['bpm'] = f"{int(bpm)}bpm" if bpm.is_integer() else f"{bpm}bpm"
                except: pass

            # 3. Time Signature
            beat_match = re.search(r'<Beat>(\d+)</Beat>', mem_content)
            if beat_match:
                try:
                    beat_val = int(beat_match.group(1))
                    data['ts_raw'] = beat_val
                    data['ts'] = get_time_signature_map(beat_val)
                except: pass
            
            # 4. Pattern & Kit (Context)
            pat_match = re.search(r'<Pattern>(\d+)</Pattern>', mem_content)
            if pat_match: data['pattern'] = pat_match.group(1)
            
            kit_match = re.search(r'<Kit>(\d+)</Kit>', mem_content)
            if kit_match: data['kit'] = kit_match.group(1)

            metadata[mem_id] = data
        
        return metadata

    except Exception as e:
        print(f"Metadata extraction error: {e}\n")
        return {}

def generate_markdown_report(metadata, dest_dir):
    """
    Generates a README.md file with a table of all loop details.
    """
    report_path = os.path.join(dest_dir, "RC500_Library_Report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Boss RC-500 Library Report\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Table Header
        f.write("| Memory | Name | BPM | Beat Value (XML) | Time Signature | Context / Notes (Pattern/Kit) |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :--- |\n")
        
        # Sort by Memory ID
        sorted_ids = sorted(metadata.keys())
        
        for mem_id in sorted_ids:
            m = metadata[mem_id]
            # Format Context string
            context = []
            if m['pattern']: context.append(f"Pattern {m['pattern']}")
            if m['kit']: context.append(f"Kit {m['kit']}")
            context_str = ", ".join(context) if context else "-"

            # Format Row
            row = f"| {mem_id:02d} | {m['name'] or 'Empty'} | {m['bpm_raw']} | {m['ts_raw']} | {m['ts']} | {context_str} |\n"
            f.write(row)
            
    print(f"Report generated: {report_path}")

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    # 1. Auto-detect source directory
    print("Scanning for Boss RC-500...")
    source_dir = find_boss_drive()

    if not source_dir:
        print("Error: Could not find a drive with 'ROLAND/WAVE' folder.")
        print("Please ensure the RC-500 is in STORAGE mode and connected via USB.")
        input("Press Enter to exit...")
        exit()

    print(f"Found Boss RC-500 at: {source_dir}")

    # 2. Load metadata
    memory_metadata = get_memory_metadata(source_dir)

    # 3. Set dynamic destination directory
    script_location = os.path.dirname(os.path.abspath(__file__))
    current_date = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"Boss RC-500 Loop Backups {current_date}"
    dest_dir = os.path.join(script_location, folder_name)

    # 4. Create Directory
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created backup folder: {dest_dir}\n")
    else:
        print(f"Using existing backup folder: {dest_dir}\n")

    # 5. Generate Report
    if memory_metadata:
        generate_markdown_report(memory_metadata, dest_dir)
        print("")

    # 6. Backup Files
    count = 0
    print("Starting file backup...")
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.wav'):
                folder_name_raw = os.path.basename(root)
                try:
                    parts = folder_name_raw.split('_')
                    if len(parts) >= 2:
                        memory_slot = parts[0]
                        track_num = parts[1]
                        slot_int = int(memory_slot)
                        
                        # Build filename
                        base_name_parts = [f"Memory_{memory_slot}"]
                        if slot_int in memory_metadata:
                            meta = memory_metadata[slot_int]
                            if meta['name']:
                                base_name_parts[0] = f"{memory_slot}_{meta['name']}"
                            if meta['bpm']:
                                base_name_parts.append(meta['bpm'])
                            if meta['ts']:
                                # Replace slash with dash for filename safety
                                safe_ts = meta['ts'].replace('/', '-')
                                base_name_parts.append(safe_ts)

                        base_name = "_".join(base_name_parts)
                        new_filename = f"{base_name}_Track_{track_num}.wav"
                        
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
