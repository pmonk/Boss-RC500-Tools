"""
Boss RC-500 Loop Tools (GUI)
----------------------------
A utility to Export and MASS DELETE loops from the Boss RC-500.

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
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime

class BossRC500App:
    def __init__(self, root):
        self.root = root
        self.root.title("Boss RC-500 Tools")
        self.root.geometry("650x500")
        
        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        
        # --- Variables ---
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar(value=os.path.join(os.getcwd(), "Backups"))
        self.status_msg = tk.StringVar(value="Ready to scan.")
        self.delete_range_var = tk.StringVar()
        self.is_running = False

        # --- Layout ---
        self.create_widgets()
        self.scan_drive() # Auto-scan on startup

    def create_widgets(self):
        # 1. Connection Header (Always visible)
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
        
        # Tab 2: Delete
        self.tab_delete = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_delete, text="Delete Loops")
        self.setup_delete_tab()

        # 3. Log (Shared)
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
        # Destination
        dest_frame = ttk.Frame(self.tab_backup)
        dest_frame.pack(fill="x", pady=5)
        ttk.Label(dest_frame, text="Backup To:").pack(anchor="w")
        
        hbox = ttk.Frame(dest_frame)
        hbox.pack(fill="x")
        ttk.Entry(hbox, textvariable=self.dest_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(hbox, text="Browse...", command=self.browse_dest).pack(side="right", padx=5)
        
        # Big Button
        ttk.Button(self.tab_backup, text="START BACKUP", command=self.start_backup_thread).pack(fill="x", pady=20)
        
        # Progress
        self.progress = ttk.Progressbar(self.tab_backup, orient="horizontal", mode="indeterminate")
        self.progress.pack(fill="x", pady=10)

    def setup_delete_tab(self):
        ttk.Label(self.tab_delete, text="Delete Loops by Memory Number", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(self.tab_delete, text="Enter ranges like '10-20' or '5, 8, 12'").pack(anchor="w")
        
        ttk.Entry(self.tab_delete, textvariable=self.delete_range_var, width=50).pack(fill="x", pady=10)
        
        btn_frame = ttk.Frame(self.tab_delete)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Preview (Scan Only)", command=self.preview_delete).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(btn_frame, text="DELETE PERMANENTLY", command=self.confirm_delete).pack(side="right", fill="x", expand=True, padx=5)

    # --- Logic ---

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

    # --- BACKUP LOGIC ---
    def start_backup_thread(self):
        if not self.source_dir.get(): return
        if self.is_running: return
        self.is_running = True
        self.progress.start(10)
        threading.Thread(target=self.run_backup, daemon=True).start()

    def run_backup(self):
        try:
            source = self.source_dir.get()
            base_dest = self.dest_dir.get()
            folder_name = f"Boss RC-500 Loop Backups {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
            final_dest = os.path.join(base_dest, folder_name)
            
            if not os.path.exists(final_dest): os.makedirs(final_dest)
            
            count = 0
            for root, dirs, files in os.walk(source):
                for file in files:
                    if file.lower().endswith('.wav'):
                        try:
                            folder_raw = os.path.basename(root)
                            parts = folder_raw.split('_')
                            if len(parts) >= 2:
                                slot, track = parts[0], parts[1]
                                new_name = f"Memory_{slot}_Track_{track}.wav"
                                shutil.copy2(os.path.join(root, file), os.path.join(final_dest, new_name))
                                self.log(f"Exported: {new_name}")
                                count += 1
                        except Exception: pass
            
            self.log(f"--- Backup Complete: {count} loops ---")
            messagebox.showinfo("Success", f"Backed up {count} loops.")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self.progress.stop)

    # --- DELETE LOGIC ---
    def parse_range(self, range_str):
        ids = set()
        parts = range_str.split(',')
        for part in parts:
            part = part.strip()
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
        self.log(f"--- PREVIEW DELETE ---")
        if not targets:
            self.log("No matching loops found for that range.")
        for folder in targets:
            self.log(f"[FOUND] {os.path.basename(folder)}")
        self.log(f"Total found: {len(targets)}")

    def confirm_delete(self):
        targets = self.get_delete_targets()
        if not targets:
            messagebox.showinfo("Info", "No loops found to delete.")
            return

        # Warning 1
        msg = f"You are about to delete {len(targets)} loops from the pedal.\n\n"
        msg += "Make sure you have exported any loops you want to keep.\n\n" # <--- YOUR MESSAGE
        msg += "Continue?"
        
        if not messagebox.askyesno("Confirm Delete", msg, icon='warning'):
            self.log("Delete cancelled.")
            return

        # Warning 2 (Double Check)
        if not messagebox.askyesno("Final Warning", "This cannot be undone. Are you absolutely sure?"):
            self.log("Delete cancelled.")
            return

        # Execute
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
