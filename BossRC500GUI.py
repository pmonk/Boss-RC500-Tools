import os
import shutil
import string
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

class BossRC500App:
    def __init__(self, root):
        self.root = root
        self.root.title("Boss RC-500 Tools")
        self.root.geometry("600x450")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        
        # --- Variables ---
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar(value=os.path.join(os.getcwd(), "Backups"))
        self.status_msg = tk.StringVar(value="Ready to scan.")
        self.is_running = False

        # --- UI Layout ---
        self.create_widgets()
        
        # Auto-scan on startup (optional)
        self.scan_drive()

    def create_widgets(self):
        # 1. Connection Section
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Pedal Drive:").pack(side="left")
        ttk.Entry(conn_frame, textvariable=self.source_dir, width=40, state="readonly").pack(side="left", padx=5)
        ttk.Button(conn_frame, text="Rescan", command=self.scan_drive).pack(side="left")

        # 2. Destination Section
        dest_frame = ttk.LabelFrame(self.root, text="Backup Location", padding=10)
        dest_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Entry(dest_frame, textvariable=self.dest_dir, width=50).pack(side="left", fill="x", expand=True)
        ttk.Button(dest_frame, text="Browse...", command=self.browse_dest).pack(side="right", padx=5)

        # 3. Actions Section
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill="x", padx=10)
        
        self.btn_backup = ttk.Button(action_frame, text="Start Backup", command=self.start_backup_thread)
        self.btn_backup.pack(side="left", fill="x", expand=True)

        # 4. Progress & Log
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=(10, 0))
        
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, state="disabled", font=("Consolas", 9))
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Status Bar
        ttk.Label(self.root, textvariable=self.status_msg, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    # --- Logic Methods ---

    def log(self, message):
        """Thread-safe logging to the text widget"""
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
            self.log("Error: Pedal not found. Check USB connection and STORAGE mode.")
            self.status_msg.set("Not Connected")

    def browse_dest(self):
        directory = filedialog.askdirectory(initialdir=self.dest_dir.get())
        if directory:
            self.dest_dir.set(directory)

    def start_backup_thread(self):
        if not self.source_dir.get():
            messagebox.showerror("Error", "No pedal connected!")
            return
            
        if self.is_running:
            return

        self.is_running = True
        self.btn_backup.config(state="disabled")
        self.progress.start(10) # Start loading animation
        
        # Run backup in background thread
        threading.Thread(target=self.run_backup, daemon=True).start()

    def run_backup(self):
        try:
            source = self.source_dir.get()
            base_dest = self.dest_dir.get()
            
            # Create timestamped folder
            folder_name = f"Boss RC-500 Loop Backups {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
            final_dest = os.path.join(base_dest, folder_name)
            
            if not os.path.exists(final_dest):
                os.makedirs(final_dest)
                self.log(f"Created folder: {final_dest}")

            count = 0
            
            # Walk and Copy
            for root, dirs, files in os.walk(source):
                for file in files:
                    if file.lower().endswith('.wav'):
                        folder_name_raw = os.path.basename(root)
                        try:
                            parts = folder_name_raw.split('_')
                            if len(parts) >= 2:
                                slot, track = parts[0], parts[1]
                                new_name = f"Memory_{slot}_Track_{track}.wav"
                                
                                old_path = os.path.join(root, file)
                                new_path = os.path.join(final_dest, new_name)
                                
                                shutil.copy2(old_path, new_path)
                                self.log(f"Exported: {new_name}")
                                count += 1
                        except ValueError:
                            self.log(f"Skipping unknown folder: {folder_name_raw}")
            
            self.log(f"--- SUCCESS: {count} loops backed up! ---")
            self.status_msg.set("Backup Complete")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.status_msg.set("Error occurred")
            
        finally:
            self.is_running = False
            self.root.after(0, self.stop_progress)

    def stop_progress(self):
        self.progress.stop()
        self.btn_backup.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = BossRC500App(root)
    root.mainloop()
