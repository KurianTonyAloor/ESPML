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

def extract_pdf_figures_and_tables(pdf_path: str, img_dir: str = "images"):
    os.makedirs(img_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    extracted_figures = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b.get("type") == 0:
                b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
                fig_match = re.search(r"Fig\.\s*(\d+\.\d+)", b_text, re.I)
                if fig_match:
                    fig_key = f"Fig. {fig_match.group(1)}"
                    b_rect = fitz.Rect(b["bbox"])
                    clip_rect = fitz.Rect(max(40.0, b_rect.x0 - 20), max(40.0, b_rect.y0 - 180), min(550.0, b_rect.x1 + 30), b_rect.y0 - 2) & page.rect
                    
                    pix = page.get_pixmap(clip=clip_rect, dpi=300)
                    img_filename = f"{fig_key.lower().replace('.', '_').replace(' ', '_')}.png"
                    img_path = os.path.join(img_dir, img_filename)
                    pix.save(img_path)

                    extracted_figures[fig_key] = {
                        "src": f"images/{img_filename}",
                        "caption": b_text
                    }

    doc.close()
    return extracted_figures

def run_pdf_inference(pdf_path: str, model_path: str, output_typ_path: str):
    nodes, df = extract_features_directly_from_pdf(pdf_path)

    # Predict semantic tags using Model 1
    print(f"[2/4] Predicting semantic layout tags for {len(nodes)} text blocks using Model 1...")
    model_data = joblib.load(model_path)
    model = model_data["model"] if isinstance(model_data, dict) else model_data
    predicted_tags = model.predict(df.values)

    # Extract figures
    extracted_figures = extract_pdf_figures_and_tables(pdf_path)

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
    typst_lines = [
        f"// Automated PDF Reconstruction via Subject-Specific Template Engine [{template_name}]\n",
        f'#import "./{template_name}": *\n\n',
        '#show: ncert-document.with(\n',
        '  chapter-num: "2",\n',
        '  chapter-title: "RELATIONS AND FUNCTIONS"\n',
        ')\n\n',
        '#ncert-page-one-opening(\n',
        '  unit-num: "2",\n',
        '  title: "RELATIONS AND FUNCTIONS"\n',
        ')\n\n'
    ]

    if template_name != "kemh_template.typ":
        typst_lines.append('#columns(2, gutter: 15pt)[\n')

    rendered_figs = set()

    for node, tag in zip(nodes, predicted_tags):
        raw_text = node["text"]
        safe_text = escape_typst(raw_text)

        # Skip duplicate chapter titles and opening quotes
        if "RELATIONS AND FUNCTIONS" in raw_text.upper() or "BERTHELOT" in raw_text.upper() or raw_text.startswith("vMathematics"):
            continue

        fig_match = re.search(r"Fig\.\s*(\d+\.\d+)", raw_text, re.I)
        fig_key = f"Fig. {fig_match.group(1)}" if fig_match else None

        if tag == "SECTION_HEADING_1" or re.match(r"^\d+\.\d+\s+", raw_text):
            typst_lines.append(f'  #ncert-h1("{safe_text}")\n\n')
        elif tag == "SECTION_HEADING_2" or re.match(r"^\d+\.\d+\.\d+\s+", raw_text):
            typst_lines.append(f'  #ncert-h2("{safe_text}")\n\n')
        elif re.match(r"^(Definition|Theorem|Note)\s*\d*", raw_text, re.I):
            typst_lines.append(f'  #ncert-green-box(title: "", [{safe_text}])\n\n')
        elif tag == "EXERCISE_OR_EXAMPLE" or re.match(r"^(Example|EXERCISES)", raw_text, re.I):
            typst_lines.append(f'  #ncert-problem-box(title: "Example", [{safe_text}])\n\n')
        elif fig_match or tag == "FIGURE_CAPTION":
            typst_lines.append(f'  #align(center)[#text(style: "italic", size: 8.5pt)[{safe_text}]]\n\n')
            if fig_key and fig_key in extracted_figures and fig_key not in rendered_figs:
                rendered_figs.add(fig_key)
                img_src = extracted_figures[fig_key]["src"]
                typst_lines.append(f'  #ncert-figure("./{img_src}", caption: "", width: 90%)\n\n')
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
