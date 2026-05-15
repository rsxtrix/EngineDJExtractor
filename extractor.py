import os
import shutil
import time
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def get_unique_path(dest_folder, filename):
    """
    If a file with the same name already exists, create a unique filename.
    Example: song.mp3 -> song_1.mp3
    """
    base = Path(filename).stem
    ext = Path(filename).suffix
    candidate = dest_folder / filename
    counter = 1

    while candidate.exists():
        candidate = dest_folder / f"{base}_{counter}{ext}"
        counter += 1

    return candidate


def format_time(seconds):
    """
    Convert seconds to HH:MM:SS format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


class FileCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder File Copier")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # Variables for paths
        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")

        self.create_widgets()

    def create_widgets(self):
        # Source selection
        tk.Label(self.root, text="Source Folder:").pack(anchor="w", padx=10, pady=(10, 0))
        source_frame = tk.Frame(self.root)
        source_frame.pack(fill="x", padx=10)

        tk.Entry(source_frame, textvariable=self.source_var).pack(side="left", fill="x", expand=True)
        tk.Button(source_frame, text="Browse", command=self.select_source).pack(side="left", padx=5)

        # Destination selection
        tk.Label(self.root, text="Destination Folder:").pack(anchor="w", padx=10, pady=(10, 0))
        dest_frame = tk.Frame(self.root)
        dest_frame.pack(fill="x", padx=10)

        tk.Entry(dest_frame, textvariable=self.dest_var).pack(side="left", fill="x", expand=True)
        tk.Button(dest_frame, text="Browse", command=self.select_dest).pack(side="left", padx=5)

        # Start button
        tk.Button(self.root, text="Start Copy", command=self.start_copy, height=2).pack(pady=15)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=650, mode="determinate")
        self.progress.pack(padx=10, fill="x")

        # Status label
        tk.Label(self.root, textvariable=self.status_var).pack(pady=5)

        # Log output
        self.log_box = tk.Text(self.root, height=18, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.root.update_idletasks()

    def select_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_var.set(folder)

    def select_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_var.set(folder)

    def start_copy(self):
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()

        if not source or not dest:
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return

        threading.Thread(target=self.copy_files, args=(source, dest), daemon=True).start()

    def copy_files(self, source, dest):
        source_dir = Path(source)
        dest_dir = Path(dest)

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create destination folder:\n{e}")
            return

        # Build file list
        all_files = []
        self.log("Scanning files...")

        try:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    all_files.append(Path(root) / file)
        except Exception as e:
            self.log(f"Error scanning files: {e}")
            return

        total_files = len(all_files)

        if total_files == 0:
            self.log("No files found.")
            return

        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        self.log(f"Found {total_files} files.")
        self.log("Starting copy...\n")

        start_time = time.time()
        copied = 0
        errors = 0

        for file_path in all_files:
            try:
                dest_file = get_unique_path(dest_dir, file_path.name)
                shutil.copy2(file_path, dest_file)
                copied += 1

                elapsed = time.time() - start_time
                avg = elapsed / copied
                remaining = avg * (total_files - copied)

                self.progress["value"] = copied
                self.status_var.set(
                    f"Copied {copied}/{total_files} | ETA: {format_time(remaining)}"
                )

                self.log(f"Copied: {file_path.name}")

            except Exception as e:
                errors += 1
                self.log(f"ERROR: {file_path} -> {e}")

        total_time = time.time() - start_time

        self.status_var.set("Complete")
        self.log("\nFinished")
        self.log(f"Copied files: {copied}")
        self.log(f"Errors: {errors}")
        self.log(f"Total time: {format_time(total_time)}")

        messagebox.showinfo(
            "Complete",
            f"Finished copying files.\n\nCopied: {copied}\nErrors: {errors}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()