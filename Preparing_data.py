import pandas as pd
from tkinter import filedialog, Tk

def clean_extracted_text(text):
    lines = str(text).strip().splitlines()
    cleaned = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if buffer:
            if line and not line.endswith(('.', '?', '!', ':')) and not buffer.endswith(('.', '?', '!', ':')):
                buffer += ' ' + line
            else:
                cleaned.append(buffer)
                buffer = line
        else:
            buffer = line

    if buffer:
        cleaned.append(buffer)

    return ' '.join(cleaned)

def select_csv():
    Tk().withdraw()
    return filedialog.askopenfilename(title="Select Original CSV", filetypes=[("CSV files", "*.csv")])

def select_output_csv():
    Tk().withdraw()
    return filedialog.asksaveasfilename(
        title="Save Enriched CSV As",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile="all_enriched_chapters_text_in_original_language.csv"
    )

def enrich_and_clean_csv(csv_path, output_path):
    df = pd.read_csv(csv_path, encoding="utf-8")

    # Prompt user to select a text column
    text_columns = [col for col in df.columns if df[col].dtype == 'object']
    print("\nAvailable columns:")
    for i, col in enumerate(text_columns):
        print(f"{i + 1}: {col}")
    sel = int(input("Enter the number of the column to clean: ")) - 1
    selected_col = text_columns[sel]

    cleaned_texts = []
    durations = []
    starts = []
    ends = []

    frame_offset = 0

    for text in df[selected_col]:
        cleaned = clean_extracted_text(text)
        word_count = len(cleaned.split())
        duration = max(90, min(word_count * 15, 360))

        cleaned_texts.append(cleaned)
        durations.append(duration)
        starts.append(frame_offset)
        ends.append(frame_offset + duration)

        frame_offset += duration

    df['CleanedText'] = cleaned_texts
    df['DurationFrames'] = durations
    df['StartFrame'] = starts
    df['EndFrame'] = ends

    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned and enriched CSV saved to:\n{output_path}")

# === Execution ===
input_csv = select_csv()
output_csv = select_output_csv()
enrich_and_clean_csv(input_csv, output_csv)
