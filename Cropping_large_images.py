from PIL import Image
import os
from tkinter import filedialog, Tk
from tqdm import tqdm
from pathlib import Path
import shutil

def get_all_image_files(base_folder, supported_formats):
    return [Path(root) / file
            for root, _, files in os.walk(base_folder)
            for file in files
            if file.lower().endswith(supported_formats)]

def process_images(base_folder, output_folder, segment_height=1250):
    supported_formats = ('.webp', '.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    all_images = get_all_image_files(base_folder, supported_formats)

    if not all_images:
        print("No images found in base folder.")
        return

    for img_path in tqdm(all_images, desc="Overall Progress", unit="image"):
        try:
            rel_path = img_path.relative_to(base_folder)
            output_img_folder = (Path(output_folder) / rel_path.parent)
            output_img_folder.mkdir(parents=True, exist_ok=True)

            with Image.open(img_path) as img:
                width, height = img.size
                base_name = img_path.stem

                if height > segment_height:
                    for idx, y in enumerate(range(0, height, segment_height)):
                        box = (0, y, width, min(y + segment_height, height))
                        segment = img.crop(box)
                        output_file = output_img_folder / f"{base_name}_part{idx+1:02}.jpg"
                        segment.save(output_file)
                else:
                    # Just copy original image to output folder
                    output_file = output_img_folder / f"{base_name}.jpg"
                    img.save(output_file)

        except Exception as e:
            print(f"[Error] Failed to process {img_path}: {e}")

# GUI for folder selection
Tk().withdraw()
base_folder = filedialog.askdirectory(title="Select Base Folder Containing Images")
if not base_folder:
    print("No base folder selected. Exiting.")
    exit()

output_folder = filedialog.askdirectory(title="Select Output Folder for Processed Images")
if not output_folder:
    print("No output folder selected. Exiting.")
    exit()

# Start processing
process_images(Path(base_folder), Path(output_folder))
