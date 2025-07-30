import os
import pandas as pd
from paddleocr import PaddleOCR
from tkinter import filedialog, Tk
from tqdm import tqdm
from langdetect import detect
import language_tool_python
import paddle

# === HELPER FUNCTIONS ===
def select_base_folder():
    Tk().withdraw()
    return filedialog.askdirectory(title="Select Base Folder with Chapters")

def select_output_csv():
    Tk().withdraw()
    return filedialog.asksaveasfilename(
        title="Save CSV Output As",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        initialfile="all_chapters_text.csv"
    )

# === INIT PADDLE DEVICE & OCR ===
device = 'gpu' if paddle.is_compiled_with_cuda() else 'cpu'
paddle.set_device(device)
ocr = PaddleOCR(use_textline_orientation=True, 
                lang='en',
                # text_det_limit_side_len=12000,    # raise detection resize limit
                # det_max_side_len=12000,     # same for recognition
                text_det_box_thresh=0.3,      # default 0.3  (raise to merge nearby boxes)
                text_det_unclip_ratio=2.2    # default 1.5 (raise to enlarge each detection)
                )  # no `use_gpu` arg needed
print(f"PaddleOCR initialized on device: {device}")

# === INIT LANGUAGE TOOL ===
tools_by_lang = {
    'en': language_tool_python.LanguageTool('en-US'),
    # add more languages as needed
}

# === SLANG MAPPING ===
slang_map = {
    "gonna": "going to", "wanna": "want to", "gotta": "got to",
    "ain't": "is not", "lemme": "let me", "kinda": "kind of",
    "ya": "you", "tho": "though", "dunno": "do not know",
    "cuz": "because", "OMG": "Oh my god!", "Whaaaaat": "What",
    "Whaaaaat?!": "What?!", "Duuuuude!": "Dude!", "Duuuuude": "Dude",
    "AAAAAH!": "AAH", "_": " "
}

# === USER INPUT ===
BASE_FOLDER = select_base_folder()
OUTPUT_FILE = select_output_csv()

data = []
chapters = sorted(
    d for d in os.listdir(BASE_FOLDER)
    if os.path.isdir(os.path.join(BASE_FOLDER, d))
)

# === TEXT EXTRACTION ===
for chapter in tqdm(chapters, desc="Chapters"):
    chapter_path = os.path.join(BASE_FOLDER, chapter)
    images = sorted(
        f for f in os.listdir(chapter_path)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    )

    for filename in tqdm(images, desc=chapter, leave=False):
        file_path = os.path.join(chapter_path, filename)
        try:
            result = ocr.ocr(file_path)           # returns [[detections], ...]
            detections = result[0] if result else []

            # Text always lives in detections[i][1]:
            raw_lines = []
            for det in detections:
                text_item = det[1]
                # If PaddleOCR packs (text,score) tuple, grab .[0]
                if isinstance(text_item, (list, tuple)):
                    raw_lines.append(text_item[0])
                else:
                    raw_lines.append(str(text_item))

            raw_text = "\n".join(raw_lines).strip()

            if raw_text:
                lang = detect(raw_text)
                tool = tools_by_lang.get(lang)
                corrected = tool.correct(raw_text) if tool else raw_text
                # Apply slang replacements
                for slang, formal in slang_map.items():
                    corrected = corrected.replace(slang, formal)
            else:
                corrected = ""

        except Exception as e:
            print(f"[Error] Skipped {file_path}: {e}")
            corrected = ""

        data.append({
            'Chapter': chapter,
            'Filename': filename,
            'ExtractedText': corrected
        })

# === SAVE OUTPUT ===
df = pd.DataFrame(data)
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
print(f"\n✅ Extraction complete. Saved to: {OUTPUT_FILE}")
