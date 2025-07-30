# FROM-OCR-to-Videos

This repository extracts text from chapter image folders using EasyOCR.

## Usage

Run the script and choose the chapter folder and output CSV when prompted:

```bash
python image_to_text.py
```

Each selected subfolder is treated as a chapter containing images. The script
saves the recognized and corrected text from every image to the chosen CSV
file.
