"""
Boss RC-500 Tools (Unified GUI)
-------------------------------
A utility to Export, Import (Restore), and DELETE loops.

Features:
- Auto-detects ROLAND/WAVE drive.
- BACKUP: "All" or "Range". Extracts Name, BPM, Time Sig.
- RESTORE: Inject WAV files back into specific slots (Audio Only).
- DELETE: Preview Name/Number before deleting.

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

Boss RC-500 Tools (Unified GUI)
-------------------------------
A utility to Export, Import (Restore), and DELETE loops.

Features:
- Auto-detects ROLAND/WAVE drive.
- BACKUP: "All" or "Range". Extracts Name, BPM, Time Sig.
- RESTORE: Inject WAV files back into specific slots (Audio Only).
- DELETE: Preview Name/Number before deleting.

Copyright (C) 2026 [pmonk.com]
"""

import os
import shutil
import string
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import re
import webbrowser

# --- METADATA HELPERS ---

def get_time_signature_map(beat_val):
    beat_map = {
        0: "2/4", 1: "3/4", 2: "4/4", 3: "5/4", 4: "6/4",
        5: "7/4", 6: "5/8", 7: "6/8", 8: "7/8", 9: "8/8",
        10: "9/8", 11: "10/8", 12: "11/8", 13: "12/8",
        14: "13/8", 15: "14/8", 16: "15/8"
    }
    return beat_map.get(beat_val, "?")

def parse_metadata(boss_wave_path, logger_func):
    """Parses MEMORY1.RC0 for Name, BPM, Time Sig, and Context."""
    metadata = {}
    try:
        data_dir = os.path.abspath(os.path.join(boss_wave_path, "..", "DATA"))
        xml_path = os.path.join(data_dir, "MEMORY1.RC0")
        
        if not os.path.exists(xml_path):
            if logger_func: logger_func("Warning: MEMORY1.RC0 not found.")
            return {}

        if logger_func: logger_func("Reading metadata...")
        
        with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        mem_pattern = r'<mem id="(\d+)">(.*?)</mem>'
        mem_blocks = re.findall(mem_pattern, content, re.DOTALL)
        
        for mem_id_str, mem_content in mem_blocks:
            mem_id = int(mem_id_str) + 1
            data = {'name': '', 'bpm': '', 'ts': '', 'ts_raw': '', 'pattern': '', 'kit': ''}
            
            # Name
            name_codes = re.findall(r'<C(\d+)>(\d+)</C\d+>', mem_content)
            if name_codes:
                name_codes.sort(key=lambda x: int(x[0]))
                chars = [chr(int(c)) for _, c in name_codes]
                raw_name = "".join(chars).strip()
                data['name'] = "".join([c for c in raw_name if c.isalnum() or c in ('-', '_', ' ')])

            # BPM
            tempo = re.search(r'<Tempo>(\d+)</Tempo>', mem_content)
            if tempo:
                bpm = int(tempo.group(1)) / 10.0
                data['bpm'] = f"{int(bpm)}bpm" if bpm.is_integer() else f"{bpm}bpm"

            # Time Sig
            beat = re.search(r'<Beat>(\d+)</Beat>', mem_content)
            if beat:
                val = int(beat.group(1))
                data['ts_raw'] = val
                data['ts'] = get_time_signature_map(val)
            
            # Context
            pat = re.search(r'<Pattern>(\d+)</Pattern>', mem_content)
            if pat: data['pattern'] = pat.group(1)
            kit = re.search(r'<Kit>(\d+)</Kit>', mem_content)
            if kit: data['kit'] = kit.group(1)

            metadata[mem_id] = data
            
        return metadata
    except Exception as e:
        if logger_func: logger_func(f"Error parsing metadata: {str(e)}")
        return {}

def create_reports(metadata, dest_dir, logger_func):
    """Generates Markdown and HTML reports."""
    md_path = os.path.join(dest_dir, "RC500_Library_Report.md")
    html_path = os.path.join(dest_dir, "RC500_Library_Report.html")
    
    html_rows = ""
    md_rows = ""
    
    if not metadata:
        return None

    sorted_ids = sorted(metadata.keys())
    for mem_id in sorted_ids:
        m = metadata[mem_id]
        context_parts = []
        if m['pattern']: context_parts.append(f"Pattern {m['pattern']}")
        if m['kit']: context_parts.append(f"Kit {m['kit']}")
        context_str = ", ".join(context_parts) if context_parts else "-"
        
        name = m['name'] or "Empty"
        ts = m['ts'] or "-"
        ts_raw = m['ts_raw'] if m['ts_raw'] != '' else "-"
        bpm = m['bpm'] or "-"

        # Markdown Row
        md_rows += f"| {mem_id:02d} | {name} | {bpm} | {ts_raw} | {ts} | {context_str} |\n"
        
        # HTML Row
        html_rows += f"""
        <tr>
            <td>{mem_id:02d}</td>
            <td class="name">{name}</td>
            <td>{bpm}</td>
            <td>{ts_raw}</td>
            <td class="highlight">{ts}</td>
            <td class="context">{context_str}</td>
        </tr>"""

    # Write Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Boss RC-500 Library Report\n\n")
        f.write("| Memory | Name | BPM | Beat (XML) | Time Sig | Context |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :--- |\n")
        f.write(md_rows)
    
    # Write HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Boss RC-500 Library Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f4f9; color: #333; padding: 20px; }}
            h1 {{ color: #444; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #007bff; color: white; text-transform: uppercase; font-size: 0.85rem; }}
            tr:hover {{ background-color: #f1f1f1; }}
            .name {{ font-weight: bold; color: #2c3e50; }}
            .highlight {{ color: #d63031; font-weight: bold; }}
            .context {{ font-style: italic; color: #666; }}
            .footer {{ margin-top: 20px; font-size: 0.8rem; color: #777; }}
        </style>
    </head>
    <body>
        <h1>RC-500 Loop Library</h1>
        <table>
            <thead>
                <tr>
                    <th>#</th><th>Name</th><th>BPM</th><th>XML Beat</th><th>Time Sig</th><th>Context / Kit</th>
                </tr>
            </thead>
            <tbody>{html_rows}</tbody>
        </table>
        <div class="footer">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
    </body>
    </html>
    """
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    logger_func(f"Reports generated:\n -> {md_path}\n -> {html_path}")
    return html_path

# --- MAIN GUI ---

class BossRC500App:
    def __init__(self, root):
        self.root = root
        self.root.title("Boss RC-500 Tools")
        self.root.geometry("680x720")
        
        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        
        # --- Variables ---
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar(value=os.path.join(os.getcwd(), "Backups"))
        self.import_source_dir = tk.StringVar()
        
        self.status_msg = tk.StringVar(value="Ready to scan.")
        self.is_running = False
        self.html_report_path = None
        self.final_dest_dir = None
        
        # Backup Logic Vars
        self.backup_mode_var = tk.StringVar(value="all") # "all" or "range"
        self.backup_range_var = tk.StringVar()

        # Delete Logic Vars
        self.delete_range_var = tk.StringVar()

        # --- Layout ---
        self.create_widgets()
        self.scan_drive() # Auto-scan on startup

    def create_widgets(self):
        # 1. Connection Header
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Pedal Drive:").pack(side="left")
        ttk.Entry(conn_frame, textvariable=self.source_dir, width=40, state="readonly").pack(side="left", padx=5)
        ttk.Button(conn_frame, text="Rescan", command=self.scan_drive).pack(side="left")

        # 2. Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tab 1: Backup
        self.tab_backup = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_backup, text="Backup / Export")
        self.setup_backup_tab()

        # Tab 2: Import / Restore
        self.tab_import = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_import, text="Import / Restore")
        self.setup_import_tab()
        
        # Tab 3: Delete
        self.tab_delete = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_delete, text="Delete Loops")
        self.setup_delete_tab()

        # 3. Log
        log_frame = ttk.LabelFrame(self.root, text="Activity Log", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, state="disabled", font=("Consolas", 9))
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Status Bar
        ttk.Label(self.root, textvariable=self.status_msg, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def setup_backup_tab(self):
        # Scope Selection
        scope_frame = ttk.LabelFrame(self.tab_backup, text="Backup Scope", padding=10)
        scope_frame.pack(fill="x", pady=5)
        
        ttk.Radiobutton(scope_frame, text="Backup All Loops", variable=self.backup_mode_var, value="all", command=self.toggle_backup_range_state).pack(anchor="w")
        
        range_box = ttk.Frame(scope_frame)
        range_box.pack(fill="x", pady=5)
        ttk.Radiobutton(range_box, text="Backup Range:", variable=self.backup_mode_var, value="range", command=self.toggle_backup_range_state).pack(side="left")
        
        self.entry_backup_range = ttk.Entry(range_box, textvariable=self.backup_range_var, width=20, state="disabled")
        self.entry_backup_range.pack(side="left", padx=5)
        ttk.Label(range_box, text="(e.g. 1-10, 15)", font=("Arial", 9, "italic"), foreground="gray").pack(side="left")

        # Destination
        dest_frame = ttk.Frame(self.tab_backup)
        dest_frame.pack(fill="x", pady=5)
        ttk.Label(dest_frame, text="Destination Folder:").pack(anchor="w")
        
        hbox = ttk.Frame(dest_frame)
        hbox.pack(fill="x")
        ttk.Entry(hbox, textvariable=self.dest_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(hbox, text="Browse...", command=self.browse_dest).pack(side="right", padx=5)
        
        # Big Button
        btn_frame = ttk.Frame(self.tab_backup)
        btn_frame.pack(fill="x", pady=15)
        
        # Preview Button
        ttk.Button(btn_frame, text="Preview (Scan Only)", command=self.start_preview_backup).pack(side="left", fill="x", expand=True, padx=5)
        
        # Execute Button
        ttk.Button(btn_frame, text="START BACKUP & GENERATE REPORT", command=self.start_backup_thread).pack(side="right", fill="x", expand=True, padx=5)
        
        # Progress
        self.progress = ttk.Progressbar(self.tab_backup, orient="horizontal", mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 15))

        # Report Buttons
        action_frame = ttk.LabelFrame(self.tab_backup, text="Post-Backup Actions", padding=10)
        action_frame.pack(fill="x")
        
        self.btn_view_report = ttk.Button(action_frame, text="View HTML Report", command=self.open_html_report, state="disabled")
        self.btn_view_report.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_open_folder = ttk.Button(action_frame, text="Open Backup Folder", command=self.open_backup_folder, state="disabled")
        self.btn_open_folder.pack(side="left", fill="x", expand=True, padx=5)

    def setup_import_tab(self):
        ttk.Label(self.tab_import, text="Import WAV files back to the Boss RC-500", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Detailed Warning
        warn_frame = ttk.LabelFrame(self.tab_import, text="LIMITATIONS & WARNINGS", padding=15)
        warn_frame.pack(fill="x", pady=10)
        
        ttk.Label(warn_frame, text="This feature restores AUDIO ONLY.", foreground="red", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0,5))
        ttk.Label(warn_frame, text="1. Metadata (Loop Name, BPM, Pattern) is NOT restored.").pack(anchor="w")
        ttk.Label(warn_frame, text="2. The pedal will RETAIN whatever Name/Settings are currently in that slot.").pack(anchor="w")
        ttk.Label(warn_frame, text="3. Result: You may hear new audio while seeing an old song name.").pack(anchor="w")
        ttk.Label(warn_frame, text="4. You must rename the loop manually on the pedal to match the new audio.").pack(anchor="w", pady=(5,0))

        # Source
        src_frame = ttk.Frame(self.tab_import)
        src_frame.pack(fill="x", pady=10)
        ttk.Label(src_frame, text="Select Backup Folder (containing exported WAVs):").pack(anchor="w")
        
        hbox = ttk.Frame(src_frame)
        hbox.pack(fill="x")
        ttk.Entry(hbox, textvariable=self.import_source_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(hbox, text="Browse...", command=self.browse_import_source).pack(side="right", padx=5)

        ttk.Button(self.tab_import, text="RESTORE AUDIO TO PEDAL", command=self.start_import_thread).pack(fill="x", pady=20)

    def setup_delete_tab(self):
        ttk.Label(self.tab_delete, text="Delete Loops by Memory Number", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(self.tab_delete, text="Enter ranges like '10-20' or '5, 8, 12'").pack(anchor="w")
        
        ttk.Entry(self.tab_delete, textvariable=self.delete_range_var, width=50).pack(fill="x", pady=10)
        
        btn_frame = ttk.Frame(self.tab_delete)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Preview (Scan Only)", command=self.preview_delete).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(btn_frame, text="DELETE PERMANENTLY", command=self.confirm_delete).pack(side="right", fill="x", expand=True, padx=5)

    # --- SHARED HELPERS ---

    def log(self, message):
        def _append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, _append)

    def scan_drive(self):
        self.log("Scanning for Boss RC-500...")
        found = False
        available_drives = [f"{d}:/" for d in string.ascii_uppercase if os.path.exists(f"{d}:/")]
        
        for drive in available_drives:
            candidate = os.path.join(drive, "ROLAND", "WAVE")
            if os.path.exists(candidate):
                self.source_dir.set(candidate)
                self.log(f"Found pedal at: {candidate}")
                self.status_msg.set(f"Connected: {candidate}")
                found = True
                break
        
        if not found:
            self.source_dir.set("")
            self.log("Error: Pedal not found.")
            self.status_msg.set("Not Connected")

    def browse_dest(self):
        d = filedialog.askdirectory(initialdir=self.dest_dir.get())
        if d: self.dest_dir.set(d)

    def browse_import_source(self):
        d = filedialog.askdirectory()
        if d: self.import_source_dir.set(d)

    def toggle_backup_range_state(self):
        if self.backup_mode_var.get() == "range":
            self.entry_backup_range.config(state="normal")
        else:
            self.entry_backup_range.config(state="disabled")

    def parse_range(self, range_str):
        ids = set()
        parts = range_str.split(',')
        for part in parts:
            part = part.strip()
            if not part: continue
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    ids.update(range(start, end + 1))
                except ValueError: continue
            else:
                try:
                    ids.add(int(part))
                except ValueError: continue
        return sorted(list(ids))

    # --- BACKUP LOGIC ---

    def start_preview_backup(self):
        if not self.source_dir.get(): 
            messagebox.showerror("Error", "No Boss RC-500 detected.")
            return
        if self.is_running: return

        if self.backup_mode_var.get() == "range":
            r = self.backup_range_var.get()
            if not r or not self.parse_range(r):
                messagebox.showerror("Error", "Please enter a valid range (e.g. 1-10).")
                return
        
        self.is_running = True
        self.progress.start(10)
        threading.Thread(target=self.run_preview_backup, daemon=True).start()

    def run_preview_backup(self):
        try:
            source = self.source_dir.get()
            self.log("--- STARTING PREVIEW (NO FILES COPIED) ---")
            
            metadata = parse_metadata(source, self.log)
            
            mode = self.backup_mode_var.get()
            target_slots = None
            if mode == "range":
                target_slots = self.parse_range(self.backup_range_var.get())
                self.log(f"Previewing range: {target_slots}")
            else:
                self.log("Previewing ALL slots...")

            count = 0
            for root, dirs, files in os.walk(source):
                for file in files:
                    if file.lower().endswith('.wav'):
                        try:
                            folder_raw = os.path.basename(root)
                            parts = folder_raw.split('_')
                            if len(parts) >= 2:
                                mem_slot = parts[0]
                                track_num = parts[1]
                                mem_int = int(mem_slot)
                                
                                if mode == "range" and mem_int not in target_slots:
                                    continue 

                                fname_parts = [f"Memory_{mem_slot}"]
                                if mem_int in metadata:
                                    m = metadata[mem_int]
                                    if m['name']: fname_parts[0] = f"{mem_slot}_{m['name']}"
                                    if m['bpm']: fname_parts.append(m['bpm'])
                                    if m['ts']: fname_parts.append(m['ts'].replace('/', '-'))
                                
                                new_name = "_".join(fname_parts) + f"_Track_{track_num}.wav"
                                
                                self.log(f"[PREVIEW] Found: {new_name}")
                                count += 1
                        except Exception: pass
            
            self.log(f"--- PREVIEW COMPLETE: {count} loops found ---")

        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self.progress.stop)

    def start_backup_thread(self):
        if not self.source_dir.get(): 
            messagebox.showerror("Error", "No Boss RC-500 detected.")
            return
        if self.is_running: return
        
        if self.backup_mode_var.get() == "range":
            r = self.backup_range_var.get()
            if not r or not self.parse_range(r):
                messagebox.showerror("Error", "Please enter a valid range (e.g. 1-10).")
                return

        self.btn_view_report.config(state="disabled")
        self.btn_open_folder.config(state="disabled")
        
        self.is_running = True
        self.progress.start(10)
        threading.Thread(target=self.run_backup, daemon=True).start()

    def run_backup(self):
        try:
            source = self.source_dir.get()
            base_dest = self.dest_dir.get()
            folder_name = f"Boss RC-500 Backup {datetime.now().strftime('%Y-%m-%d')}"
            self.final_dest_dir = os.path.join(base_dest, folder_name)
            
            mode = self.backup_mode_var.get()
            target_slots = None
            if mode == "range":
                target_slots = self.parse_range(self.backup_range_var.get())
                self.log(f"Starting Backup for slots: {target_slots}")
            else:
                self.log("Starting Backup for ALL slots...")

            if not os.path.exists(self.final_dest_dir): 
                os.makedirs(self.final_dest_dir)
            
            metadata = parse_metadata(source, self.log)
            
            count = 0
            for root, dirs, files in os.walk(source):
                for file in files:
                    if file.lower().endswith('.wav'):
                        try:
                            folder_raw = os.path.basename(root)
                            parts = folder_raw.split('_')
                            if len(parts) >= 2:
                                mem_slot = parts[0]
                                track_num = parts[1]
                                mem_int = int(mem_slot)
                                
                                if mode == "range" and mem_int not in target_slots:
                                    continue 

                                fname_parts = [f"Memory_{mem_slot}"]
                                if mem_int in metadata:
                                    m = metadata[mem_int]
                                    if m['name']: fname_parts[0] = f"{mem_slot}_{m['name']}"
                                    if m['bpm']: fname_parts.append(m['bpm'])
                                    if m['ts']: fname_parts.append(m['ts'].replace('/', '-'))
                                
                                new_name = "_".join(fname_parts) + f"_Track_{track_num}.wav"
                                shutil.copy2(os.path.join(root, file), os.path.join(self.final_dest_dir, new_name))
                                self.log(f"Exported: {new_name}")
                                count += 1
                        except Exception: pass
            
            if mode == "range" and target_slots:
                report_metadata = {k: v for k, v in metadata.items() if k in target_slots}
            else:
                report_metadata = metadata

            self.html_report_path = create_reports(report_metadata, self.final_dest_dir, self.log)
            
            self.log(f"--- Backup Complete: {count} loops ---")
            
            self.root.after(0, lambda: self.btn_view_report.config(state="normal"))
            self.root.after(0, lambda: self.btn_open_folder.config(state="normal"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Backed up {count} loops.\nReport generated."))

        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self.progress.stop)

    def open_html_report(self):
        if self.html_report_path and os.path.exists(self.html_report_path):
            webbrowser.open(f"file://{self.html_report_path}")

    def open_backup_folder(self):
        if self.final_dest_dir and os.path.exists(self.final_dest_dir):
            os.startfile(self.final_dest_dir)

    # --- IMPORT LOGIC ---

    def start_import_thread(self):
        if not self.source_dir.get():
            messagebox.showerror("Error", "Pedal not connected.")
            return
        if not self.import_source_dir.get():
            messagebox.showerror("Error", "Please select a backup folder.")
            return

        if not messagebox.askyesno("Confirm Import", "This will overwrite any existing audio in the target memory slots.\n\nContinue?"):
            return

        self.is_running = True
        threading.Thread(target=self.run_import, daemon=True).start()

    def run_import(self):
        try:
            backup_folder = self.import_source_dir.get()
            pedal_wave_dir = self.source_dir.get() # ROLAND/WAVE
            
            self.log("--- STARTING IMPORT ---")
            
            files = [f for f in os.listdir(backup_folder) if f.lower().endswith('.wav')]
            if not files:
                self.log("No WAV files found in backup folder.")
                return

            count = 0
            
            for f in files:
                # Regex 1: "Memory_01_Name_Track_1.wav"
                match = re.match(r"Memory_(\d+)_.*Track_(\d+)\.wav", f, re.IGNORECASE)
                
                # Regex 2: "098_Memory98_...Track_1.wav" (Number first)
                if not match:
                    match = re.match(r"(\d+)_.*Track_(\d+)\.wav", f, re.IGNORECASE)
                
                # Regex 3: "Memory_01_Track_1.wav" (Simple)
                if not match:
                    match = re.match(r"Memory_(\d+)_Track_(\d+)\.wav", f, re.IGNORECASE)

                if match:
                    slot_str = match.group(1) 
                    track_str = match.group(2)
                    
                    # Normalize to Boss Format
                    slot_int = int(slot_str)
                    boss_folder_name = f"{slot_int:03d}_{track_str}" # "098_1"
                    boss_file_name = f"{slot_int:03d}_{track_str}.WAV" # "098_1.WAV"
                    
                    # Target Paths
                    target_folder = os.path.join(pedal_wave_dir, boss_folder_name)
                    target_file = os.path.join(target_folder, boss_file_name)
                    
                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)
                        
                    src_file = os.path.join(backup_folder, f)
                    shutil.copy2(src_file, target_file)
                    
                    self.log(f"Restored: #{slot_int} Trk {track_str}")
                    count += 1
                else:
                    self.log(f"Skipped unknown file format: {f}")

            self.log(f"--- IMPORT COMPLETE: {count} files restored ---")
            messagebox.showinfo("Import Complete", f"Restored {count} audio files.\n\nRemember to rename them on the pedal!")

        except Exception as e:
            self.log(f"Import Error: {e}")
        finally:
            self.is_running = False

    # --- DELETE LOGIC ---

    def get_delete_targets(self):
        source = self.source_dir.get()
        if not source: return []
        range_str = self.delete_range_var.get()
        if not range_str: return []
        
        targets = self.parse_range(range_str)
        folders_found = []
        for root, dirs, files in os.walk(source):
            folder_name = os.path.basename(root)
            if "_" in folder_name:
                try:
                    slot = int(folder_name.split("_")[0])
                    if slot in targets:
                        folders_found.append(root)
                except ValueError: pass
        return folders_found

    def preview_delete(self):
        targets = self.get_delete_targets()
        source = self.source_dir.get()
        
        self.log(f"--- PREVIEW DELETE ---")
        if not targets:
            self.log("No matching loops found for that range.")
            return

        self.log("Reading metadata to identify tracks...")
        metadata = parse_metadata(source, lambda x: None)

        for folder in targets:
            folder_name = os.path.basename(folder)
            try:
                slot = int(folder_name.split("_")[0])
                name = "Unknown"
                if slot in metadata and metadata[slot]['name']:
                    name = metadata[slot]['name']
                elif slot in metadata:
                    name = "No Name"
                
                self.log(f"[FOUND] #{slot} ({name}) -> {folder_name}")
            except:
                self.log(f"[FOUND] {folder_name}")
        
        self.log(f"Total found: {len(targets)}")

    def confirm_delete(self):
        targets = self.get_delete_targets()
        if not targets:
            messagebox.showinfo("Info", "No loops found to delete.")
            return

        msg = f"You are about to PERMANENTLY DELETE {len(targets)} loops from the pedal.\n\n"
        msg += "Make sure you have used the Backup tab first!\n\nContinue?"
        
        if not messagebox.askyesno("Confirm Delete", msg, icon='warning'):
            self.log("Delete cancelled.")
            return

        if not messagebox.askyesno("Final Warning", "This cannot be undone. Are you absolutely sure?"):
            self.log("Delete cancelled.")
            return

        self.log("--- STARTING DELETE ---")
        for folder in targets:
            try:
                shutil.rmtree(folder)
                self.log(f"Deleted: {os.path.basename(folder)}")
            except Exception as e:
                self.log(f"Error deleting {folder}: {e}")
        
        self.log("--- DELETE COMPLETE ---")
        messagebox.showinfo("Done", "Deletion complete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BossRC500App(root)
    root.mainloop()
