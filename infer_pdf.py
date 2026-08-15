import os
import re
import json
import numpy as np
import pandas as pd
import pymupdf as fitz
import joblib
import subprocess

def escape_typst(text: str) -> str:
    if not text:
        return ""
    replacements = [
        ('\\', '\\\\'), ('#', '\\#'), ('$', '\\$'), ('[', '\\['), (']', '\\]'),
        ('*', '\\*'), ('_', '\\_'), ('<', '\\<'), ('>', '\\>'), ('@', '\\@')
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def extract_all_spatial_images(pdf_path: str, img_dir: str = "images"):
    """
    Extracts ALL images (diagrams, scientist portraits, QR codes, flowcharts)
    and captures their exact (x0, y0, x1, y1, page) spatial coordinates.
    """
    os.makedirs(img_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    spatial_images = []

    print(f"[1.5/4] Harvesting spatial image bounding boxes from {os.path.basename(pdf_path)}...")

    for page_num in range(len(doc)):
        page = doc[page_num]
        p_width = page.rect.width
        img_info = page.get_image_info()

        for idx, info in enumerate(img_info):
            bbox = [round(v, 1) for v in info["bbox"]]
            x0, y0, x1, y1 = bbox
            w = x1 - x0
            h = y1 - y0

            # Filter out tiny icon artifacts (< 25pt) or full-page background graphics (> 500pt)
            if w > 25 and h > 25 and w < 500 and h < 600:
                clip_rect = fitz.Rect(max(0, x0 - 2), max(0, y0 - 2), min(p_width, x1 + 2), y1 + 2)
                pix = page.get_pixmap(clip=clip_rect, dpi=300)
                
                img_filename = f"spatial_img_p{page_num+1}_{idx}.png"
                img_path = os.path.join(img_dir, img_filename)
                pix.save(img_path)

                spatial_images.append({
                    "id": f"img_p{page_num+1}_{idx}",
                    "page": page_num + 1,
                    "bbox": bbox,
                    "y0": y0,
                    "width_pt": round(w, 1),
                    "height_pt": round(h, 1),
                    "width_ratio": round(w / p_width, 2),
                    "is_right_side": x0 > (p_width / 2),
                    "src": f"images/{img_filename}"
                })

    doc.close()
    print(f"Extracted {len(spatial_images)} spatial images across document.")
    return spatial_images

def extract_features_directly_from_pdf(pdf_path: str):
    """
    Extracts text nodes and 9D feature vectors directly from any input PDF.
    """
    doc = fitz.open(pdf_path)
    nodes = []
    features_list = []

    print(f"[1/4] Extracting layout features directly from: {os.path.basename(pdf_path)}")

    for page_num in range(len(doc)):
        page = doc[page_num]
        drawings = page.get_drawings()
        drawing_rects = [d["rect"] for d in drawings if d.get("fill")]

        blocks = page.get_text("dict")["blocks"]
        for b_idx, b in enumerate(blocks):
            if b.get("type") == 0:  # Text block
                b_rect = fitz.Rect(b["bbox"])
                b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
                if not b_text:
                    continue

                spans = [span for line in b["lines"] for span in line["spans"]]
                font_sizes = [s["size"] for s in spans]
                avg_font_size = float(np.mean(font_sizes)) if font_sizes else 10.0
                is_bold = int(any("bold" in s.get("font", "").lower() or s.get("flags", 0) & 2 for s in spans))
                is_italic = int(any("italic" in s.get("font", "").lower() or s.get("flags", 0) & 1 for s in spans))

                is_colored = 0
                for s in spans:
                    if "color" in s and s["color"] not in (0, 1118481, 2236962):
                        is_colored = 1
                        break

                inside_box = int(any(b_rect.intersects(r) for r in drawing_rects))
                word_count = len(b_text.split())
                is_upper = int(b_text.isupper())
                digit_start = int(bool(re.match(r"^\d+\.\d+", b_text)))

                node_info = {
                    "page": page_num + 1,
                    "text": b_text,
                    "bbox": [round(v, 1) for v in b["bbox"]],
                    "y0": round(b_rect.y0, 1),
                    "font_size": round(avg_font_size, 1),
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "is_colored": is_colored,
                    "x0": round(b_rect.x0, 1),
                    "inside_drawing_box": inside_box
                }

                feat_vector = [
                    avg_font_size,
                    is_bold,
                    is_italic,
                    is_colored,
                    b_rect.x0 / 595.0,
                    word_count,
                    inside_box,
                    is_upper,
                    digit_start
                ]

                nodes.append(node_info)
                features_list.append(feat_vector)

    doc.close()
    df = pd.DataFrame(features_list, columns=['font_size', 'is_bold', 'is_italic', 'is_colored', 'x0', 'word_count', 'inside_drawing_box', 'is_upper', 'digit_start'])
    return nodes, df

def run_pdf_inference(pdf_path: str, model_path: str, output_typ_path: str):
    nodes, df = extract_features_directly_from_pdf(pdf_path)

    # 100% Dynamic Metadata Extraction
    chapter_num = "1"
    chapter_title = "TEXTBOOK CHAPTER"
    quote_text = ""
    quote_author = ""

    for node in nodes[:25]:
        t = node["text"].strip()
        ch_m = re.search(r"(?:Chapter|UNIT)\s*(\d+)", t, re.I)
        if ch_m:
            chapter_num = ch_m.group(1)

        if len(t) > 3 and chapter_title == "TEXTBOOK CHAPTER":
            if not re.match(r"^(?:Chapter|UNIT)\s*\d+$", t, re.I) and "REPRINT" not in t.upper():
                if node["font_size"] >= 14.0 or (t.isupper() and len(t) > 4):
                    chapter_title = t

        if not quote_text and ("—" in t or "–" in t or "❖" in t or node["is_italic"]):
            q_m = re.search(r"^(?:[\"“❖]|\s)*(.+?)(?:[\"”❖]|\s)*(?:[–—\-]\s*([A-Z\s\.]{2,30}))?$", t)
            if q_m and len(q_m.group(1)) > 15:
                quote_text = q_m.group(1).strip()
                if q_m.group(2):
                    quote_author = q_m.group(2).strip()

    # Predict semantic tags using Model 1
    print(f"[2/4] Predicting semantic layout tags for {len(nodes)} text blocks using Model 1...")
    model_data = joblib.load(model_path)
    model = model_data["model"] if isinstance(model_data, dict) else model_data
    predicted_tags = model.predict(df.values)

    # Extract ALL spatial images with bounding boxes
    spatial_images = extract_all_spatial_images(pdf_path)

    # Dynamically select subject-specific master template
    base_file = os.path.basename(pdf_path).lower()
    if base_file.startswith("kemh"):
        template_name = "kemh_template.typ"
    elif base_file.startswith("keph"):
        template_name = "keph_template.typ"
    elif base_file.startswith("kebo"):
        template_name = "kebo_template.typ"
    else:
        template_name = "kech_template.typ"

    print(f"[3/4] Synthesizing Typst document using [{template_name}]: {output_typ_path}")
    
    safe_ch_title = escape_typst(chapter_title)
    safe_quote = escape_typst(f"{quote_text} – {quote_author}" if quote_author else quote_text)

    typst_lines = [
        f"// 100% Dynamic PDF Reconstruction Engine [{template_name}]\n",
        f'#import "./{template_name}": *\n\n',
        '#show: ncert-document.with(\n',
        f'  chapter-num: "{chapter_num}",\n',
        f'  chapter-title: "{safe_ch_title}"\n',
        ')\n\n',
        '#ncert-page-one-opening(\n',
        f'  unit-num: "{chapter_num}",\n',
        f'  title: "{safe_ch_title}",\n',
        f'  quote-text: "{safe_quote}"\n',
        ')\n\n'
    ]

    if template_name != "kemh_template.typ":
        typst_lines.append('#columns(2, gutter: 15pt)[\n')

    # Construct unified spatial sequence (interleaving text and spatial images by page & y0)
    all_elements = []
    for node, tag in zip(nodes, predicted_tags):
        all_elements.append({
            "elem_type": "TEXT",
            "page": node["page"],
            "y0": node["y0"],
            "data": node,
            "tag": tag
        })

    for img in spatial_images:
        all_elements.append({
            "elem_type": "IMAGE",
            "page": img["page"],
            "y0": img["y0"],
            "data": img
        })

    # Sort strictly by (page, y0)
    all_elements.sort(key=lambda el: (el["page"], el["y0"]))

    for item in all_elements:
        if item["elem_type"] == "IMAGE":
            img = item["data"]
            img_src = img["src"]
            w_pct = int(img["width_ratio"] * 100)
            
            if img["is_right_side"]:
                # Wrap portrait or right-aligned figure
                typst_lines.append(f'  #align(right)[#ncert-figure("./{img_src}", caption: "", width: {w_pct}%)]\n\n')
            else:
                typst_lines.append(f'  #align(center)[#ncert-figure("./{img_src}", caption: "", width: {min(95, max(40, w_pct))}%)]\n\n')

        else:  # TEXT node
            node = item["data"]
            tag = item["tag"]
            raw_text = node["text"]
            safe_text = escape_typst(raw_text)

            if chapter_title.lower() in raw_text.lower() or (quote_author and quote_author.lower() in raw_text.lower()) or raw_text.startswith("vMathematics"):
                continue

            if tag == "SECTION_HEADING_1" or re.match(r"^\d+\.\d+\s+", raw_text):
                typst_lines.append(f'  #ncert-h1("{safe_text}")\n\n')
            elif tag == "SECTION_HEADING_2" or re.match(r"^\d+\.\d+\.\d+\s+", raw_text):
                typst_lines.append(f'  #ncert-h2("{safe_text}")\n\n')
            elif re.match(r"^(Definition|Theorem|Note)\s*\d*", raw_text, re.I):
                typst_lines.append(f'  #ncert-green-box(title: "", [{safe_text}])\n\n')
            elif tag == "EXERCISE_OR_EXAMPLE" or re.match(r"^(Example|EXERCISES)", raw_text, re.I):
                typst_lines.append(f'  #ncert-problem-box(title: "Example", [{safe_text}])\n\n')
            elif tag == "FIGURE_CAPTION":
                typst_lines.append(f'  #align(center)[#text(style: "italic", size: 8.5pt)[{safe_text}]]\n\n')
            else:
                typst_lines.append(f'  {safe_text}\n\n')

    if template_name != "kemh_template.typ":
        typst_lines.append(']\n')

    with open(output_typ_path, "w", encoding="utf-8") as f:
        f.writelines(typst_lines)

    # Compile PDF using Typst CLI
    pdf_out = output_typ_path.replace(".typ", ".pdf")
    print(f"[4/4] Compiling output PDF: {pdf_out}")
    res = subprocess.run(["typst", "compile", output_typ_path, pdf_out], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"PDF successfully compiled: {pdf_out}")
    else:
        print(f"Typst compilation notice: {res.stderr}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(BASE_DIR, "testing_doc", "kemh102.pdf")
    model_path = os.path.join(BASE_DIR, "ncert_classifier.joblib")
    output_typ = os.path.join(BASE_DIR, "reconstructed_kemh102.typ")
    
    run_pdf_inference(input_pdf, model_path, output_typ)
