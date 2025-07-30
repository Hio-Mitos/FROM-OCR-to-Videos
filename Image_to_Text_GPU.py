import os
import pandas as pd
from easyocr import Reader
from tkinter import filedialog, Tk
from tqdm import tqdm
from langdetect import detect
import language_tool_python

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

# === SUPPRESS PIN_MEMORY WARNINGS ===
import warnings
warnings.filterwarnings(
    "ignore",
    message="'pin_memory' argument is set as true but no accelerator is found",
    category=UserWarning
)

# === INIT EASYOCR READER ON GPU/CPU ===
# If CUDA is available, EasyOCR will use GPU; otherwise falls back to CPU.
reader = Reader(['en'], gpu=True)
print(f"EasyOCR initialized on device: {reader.device}")


# === INIT LANGUAGE TOOL ===
tools_by_lang = {'en': language_tool_python.LanguageTool('en-US')}

# === SLANG MAP ===
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
            # detail=1 returns (bbox, text, confidence), paragraph=True merges lines
            results = reader.readtext(file_path, detail=1, paragraph=True)
            raw_text = "\n".join([res[1] for res in results]).strip()

            if raw_text:
                lang = detect(raw_text)
                tool = tools_by_lang.get(lang)
                corrected = tool.correct(raw_text) if tool else raw_text
                for slang, formal in slang_map.items():
                    corrected = corrected.replace(slang, formal)
            else:
                corrected = ""
        except Exception as e:
            print(f"[Error] Skipped {file_path}: {e}")
            corrected = ""

        data.append({'Chapter': chapter, 'Filename': filename, 'ExtractedText': corrected})

# === SAVE OUTPUT ===
df = pd.DataFrame(data)
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
print(f"\n✅ Extraction complete. Saved to: {OUTPUT_FILE}")
