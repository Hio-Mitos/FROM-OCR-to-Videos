import os
import re
import tkinter as tk
from tkinter import filedialog

# === FOLDER SELECTION ===
tk.Tk().withdraw()
base_folder = filedialog.askdirectory(title="Select the base folder with subfolders to rename")
if not base_folder:
    print("❌ No folder selected. Exiting.")
    exit()

# === PROCESS FOLDERS ===
for name in os.listdir(base_folder):
    old_path = os.path.join(base_folder, name)
    if os.path.isdir(old_path):
        match = re.search(r"^(.*?)(\d+)$", name.strip())
        if match:
            prefix = match.group(1).rstrip(" _-")  # Trim space or dashes before number
            number = int(match.group(2))
            new_name = f"{prefix} {number:04d}"  # Always 4-digit padded number
            new_path = os.path.join(base_folder, new_name)
            if new_path != old_path:
                os.rename(old_path, new_path)
                print(f"✅ Renamed: {name} → {new_name}")
        else:
            print(f"⚠️ Skipped: {name} (no number found)")
