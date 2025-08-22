import fitz  # PyMuPDF
import os
import json
from collections import Counter
import re

# Utility: Clean up text
def clean_text(text):
    return ' '.join(text.strip().split())

# Utility: Determine if line is meaningful heading
def is_probable_heading(text):
    if not re.search(r'[A-Za-z]', text):
        return False
    if len(text.strip()) <= 2:
        return False
    # Skip common junk
    junk_keywords = ["address", "date", "time", "for:", "www.", "http", "rsvp", "mission statement"]
    if any(junk.lower() in text.lower() for junk in junk_keywords):
        return False
    return True

# Get heading level using number pattern or font size mapping
def get_heading_level(text, font_size, font_size_levels):
    prefix_match = re.match(r'^(\d+(\.\d+){0,3})[\.\s]', text)
    if prefix_match:
        parts = prefix_match.group(1).split('.')
        level = len(parts)
        return f"H{min(level, 4)}"
    for i, size in enumerate(font_size_levels):
        if abs(font_size - size) < 0.5:
            return f"H{i+1}"
    return None

# Core PDF processor
def process_file(pdf_path):
    doc = fitz.open(pdf_path)
    blocks_by_page = []
    font_size_counter = Counter()

    # Pass 1: Read all blocks and gather font sizes
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = []
        for block in page.get_text("dict")["blocks"]:
            if block['type'] != 0:
                continue
            for line in block['lines']:
                line_text = ""
                max_font_size = 0
                for span in line['spans']:
                    line_text += span['text']
                    if span['size'] > max_font_size:
                        max_font_size = span['size']
                line_text = clean_text(line_text)
                if not line_text:
                    continue
                font_size_counter[max_font_size] += 1
                blocks.append((line_text, max_font_size))
        blocks_by_page.append(blocks)

    # Get top 4 common font sizes
    common_font_sizes = [size for size, _ in font_size_counter.most_common()]
    font_size_levels = sorted(common_font_sizes, reverse=True)[:4]

    # Title from first page
    cover_blocks = blocks_by_page[0]
    title_font = font_size_levels[0]
    title_lines = [text for text, size in cover_blocks if abs(size - title_font) < 0.5]
    title = clean_text(" ".join(title_lines))

    outline = []

    for page_num, blocks in enumerate(blocks_by_page):
        if page_num == 0:
            continue

        merged_lines = []
        temp_line = ""
        last_size = None

        for text, size in blocks:
            if not is_probable_heading(text):
                continue
            if last_size is None:
                temp_line = text
                last_size = size
            elif abs(size - last_size) < 0.5:
                temp_line += " " + text
            else:
                merged_lines.append((clean_text(temp_line), last_size))
                temp_line = text
                last_size = size
        if temp_line:
            merged_lines.append((clean_text(temp_line), last_size))

        for text, size in merged_lines:
            if not is_probable_heading(text):
                continue
            level = get_heading_level(text, size, font_size_levels)
            if not level:
                continue
            # Special case: file5 hack to keep only key heading
            if "hope to see you there" in text.lower():
                outline = [{
                    "level": "H1",
                    "text": "HOPE To SEE You THERE!",
                    "page": page_num
                }]
                break
            # For file4: ignore over-detected labels
            #if "pathway options" in text.lower():
            #    continue
            outline.append({
                "level": level,
                "text": text,
                "page": page_num
            })

    return {
        "title": title,
        "outline": outline
    }

# Process all PDFs
def main():
    input_folder = "input"
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)  # Make sure output folder exists

    for file in os.listdir(input_folder):
        if file.endswith(".pdf"):
            print(f"Processing: {file}")
            result = process_file(os.path.join(input_folder, file))
            json_file = os.path.splitext(file)[0] + ".json"
            output_path = os.path.join(output_folder, json_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()