import os
import re
import json
import datetime
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

def extract_subject_specific_assets(pdf_path: str, subject_prefix: str, img_dir: str = "images"):
    """
    Extracts assets with strict subject-specific rules:
    - CHEMISTRY (kech): Retains composite visual caption clipping (Fig 1.2, 1.10) & 2-column callouts.
    - MATHEMATICS (kemh): Filters full-page background images (AreaRatio > 20% or w > 260pt) 
      AND harvests true isolated Math Figures (Leibniz portrait, Venn diagrams, set circles, cartesian graphs).
    """
    os.makedirs(img_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    spatial_assets = []

    print(f"[1.5/4] Harvesting subject-specific assets for [{subject_prefix.upper()}] from {os.path.basename(pdf_path)}...")

    for page_num in range(len(doc)):
        page = doc[page_num]
        p_width = page.rect.width
        p_height = page.rect.height
        p_area = p_width * p_height

        if subject_prefix == "kemh":
            # 1. MATHEMATICS: Extract Real Isolated Raster Images (Strict AreaRatio <= 20.0%, w <= 260pt, h <= 280pt)
            # EXCLUDE PAGE 1 HEADER GRAPHICS (y0 < 200pt) like QR codes and Chapter squares which are managed by #ncert-page-one-opening
            img_info = page.get_image_info()
            for idx, info in enumerate(img_info):
                bbox = [round(v, 1) for v in info["bbox"]]
                x0, y0, x1, y1 = bbox
                w = x1 - x0
                h = y1 - y0
                area = w * h
                area_ratio = area / p_area

                # Filter out Page 1 header graphics (y0 < 200pt)
                if page_num == 0 and y0 < 200.0:
                    continue

                # STRICT ISOLATED FIGURE FILTER
                if w > 25 and h > 25 and w <= 260 and h <= 280 and area_ratio <= 0.20 and x0 >= 0 and y0 >= 0:
                    clip_rect = fitz.Rect(max(0, x0 - 2), max(0, y0 - 2), min(p_width, x1 + 2), min(p_height, y1 + 2))
                    pix = page.get_pixmap(clip=clip_rect, dpi=300)
                    
                    img_filename = f"math_real_img_p{page_num+1}_{idx}.png"
                    img_path = os.path.join(img_dir, img_filename)
                    pix.save(img_path)

                    spatial_assets.append({
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

            # 2. MATHEMATICS: Harvest Isolated Vector Math Graphs (Venn Diagrams, Set Circles, Coordinate Graphs)
            drawings = page.get_drawings()
            graph_clusters = []
            for d in drawings:
                r = d["rect"]
                w = r.x1 - r.x0
                h = r.y1 - r.y0
                area_ratio = (w * h) / p_area

                # Filter out Page 1 header graphics (y0 < 200pt)
                if page_num == 0 and r.y0 < 200.0:
                    continue
                
                if w > 20 and h > 20 and w <= 260 and h <= 260 and area_ratio <= 0.18 and r.x0 >= 20 and r.y0 >= 40:
                    is_dup = False
                    for existing in graph_clusters:
                        if abs(r.x0 - existing.x0) < 15 and abs(r.y0 - existing.y0) < 15:
                            is_dup = True
                            break
                    if not is_dup:
                        graph_clusters.append(r)

            for g_idx, g_rect in enumerate(graph_clusters):
                clip_rect = fitz.Rect(max(0, g_rect.x0 - 3), max(0, g_rect.y0 - 3), min(p_width, g_rect.x1 + 3), min(p_height, g_rect.y1 + 3))
                pix = page.get_pixmap(clip=clip_rect, dpi=300)
                
                v_filename = f"math_vector_graph_p{page_num+1}_{g_idx}.png"
                v_path = os.path.join(img_dir, v_filename)
                pix.save(v_path)

                w = g_rect.x1 - g_rect.x0
                spatial_assets.append({
                    "id": f"vgraph_p{page_num+1}_{g_idx}",
                    "page": page_num + 1,
                    "bbox": [g_rect.x0, g_rect.y0, g_rect.x1, g_rect.y1],
                    "y0": g_rect.y0,
                    "width_pt": round(w, 1),
                    "height_pt": round(g_rect.y1 - g_rect.y0, 1),
                    "width_ratio": round(w / p_width, 2),
                    "is_right_side": g_rect.x0 > (p_width / 2),
                    "src": f"images/{v_filename}"
                })

        else:
            # CHEMISTRY (kech) & OTHER SUBJECTS (100% UNCHANGED):
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

                        spatial_assets.append({
                            "id": fig_key,
                            "page": page_num + 1,
                            "bbox": [b_rect.x0, b_rect.y0 - 180, b_rect.x1, b_rect.y0],
                            "y0": b_rect.y0 - 180,
                            "width_ratio": 0.90,
                            "is_right_side": False,
                            "src": f"images/{img_filename}"
                        })

    doc.close()
    print(f"Extracted {len(spatial_assets)} real isolated assets for [{subject_prefix.upper()}].")
    return spatial_assets

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

def run_pdf_inference(pdf_path: str, model_path: str, output_dir: str):
    nodes, df = extract_features_directly_from_pdf(pdf_path)

    # Setup Versioned Output Directories
    typ_dir = os.path.join(output_dir, "typ_files")
    pdf_dir = os.path.join(output_dir, "pdf_files")
    os.makedirs(typ_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    log_file = os.path.join(output_dir, "iteration_log.json")
    iteration_log = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                iteration_log = json.load(f)
        except Exception:
            iteration_log = []

    iter_count = len(iteration_log) + 1
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_stem = os.path.splitext(os.path.basename(pdf_path))[0]

    versioned_typ_filename = f"reconstructed_{doc_stem}_v{iter_count}_{timestamp_str}.typ"
    versioned_pdf_filename = f"reconstructed_{doc_stem}_v{iter_count}_{timestamp_str}.pdf"

    output_typ_path = os.path.join(typ_dir, versioned_typ_filename)
    output_pdf_path = os.path.join(pdf_dir, versioned_pdf_filename)

    # Detect Subject Prefix
    base_file = os.path.basename(pdf_path).lower()
    if base_file.startswith("kemh"):
        subject_prefix = "kemh"
        template_name = "kemh_template.typ"
    elif base_file.startswith("keph"):
        subject_prefix = "keph"
        template_name = "keph_template.typ"
    elif base_file.startswith("kebo"):
        subject_prefix = "kebo"
        template_name = "kebo_template.typ"
    else:
        subject_prefix = "kech"
        template_name = "kech_template.typ"

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

    # Extract subject-specific assets
    spatial_assets = extract_subject_specific_assets(pdf_path, subject_prefix)

    print(f"[3/4] Synthesizing Typst document [Iteration v{iter_count}]: {output_typ_path}")
    
    safe_ch_title = escape_typst(chapter_title)
    safe_quote = escape_typst(f"{quote_text} – {quote_author}" if quote_author else quote_text)

    typst_lines = [
        f"// Versioned Output v{iter_count} - {timestamp_str} [{template_name}]\n",
        f'#import "/templates/{template_name}": *\n\n',
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

    all_elements = []
    for node, tag in zip(nodes, predicted_tags):
        all_elements.append({
            "elem_type": "TEXT",
            "page": node["page"],
            "y0": node["y0"],
            "data": node,
            "tag": tag
        })

    for asset in spatial_assets:
        all_elements.append({
            "elem_type": "IMAGE",
            "page": asset["page"],
            "y0": asset["y0"],
            "data": asset
        })

    all_elements.sort(key=lambda el: (el["page"], el["y0"]))

    for item in all_elements:
        if item["elem_type"] == "IMAGE":
            img = item["data"]
            img_src = f"/{img['src']}"
            w_pct = int(img["width_ratio"] * 100) if "width_ratio" in img else 40
            
            if img.get("is_right_side"):
                typst_lines.append(f'  #align(right)[#ncert-figure("{img_src}", caption: "", width: {max(20, min(40, w_pct))}%)]\n\n')
            else:
                typst_lines.append(f'  #align(center)[#ncert-figure("{img_src}", caption: "", width: {min(75, max(30, w_pct))}%)]\n\n')

        else:
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

    # Maintain latest copies
    latest_typ = os.path.join(typ_dir, f"reconstructed_{doc_stem}_latest.typ")
    latest_pdf = os.path.join(pdf_dir, f"reconstructed_{doc_stem}_latest.pdf")
    with open(latest_typ, "w", encoding="utf-8") as f:
        f.writelines(typst_lines)

    # Compile PDF using Typst CLI with --root PROJECT_ROOT
    print(f"[4/4] Compiling versioned PDF [v{iter_count}]: {output_pdf_path}")
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    res = subprocess.run(["typst", "compile", "--root", PROJECT_ROOT, output_typ_path, output_pdf_path], capture_output=True, text=True)
    subprocess.run(["typst", "compile", "--root", PROJECT_ROOT, latest_typ, latest_pdf], capture_output=True, text=True)

    status = "SUCCESS" if res.returncode == 0 else f"FAILED: {res.stderr}"
    print(f"PDF Compilation Status: {status}")

    # Record Iteration Audit Log
    log_entry = {
        "iteration": iter_count,
        "timestamp": timestamp_str,
        "document": os.path.basename(pdf_path),
        "subject": subject_prefix.upper(),
        "template_used": template_name,
        "nodes_count": len(nodes),
        "extracted_assets_count": len(spatial_assets),
        "typ_path": os.path.relpath(output_typ_path, PROJECT_ROOT),
        "pdf_path": os.path.relpath(output_pdf_path, PROJECT_ROOT),
        "compilation_status": status
    }
    iteration_log.append(log_entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(iteration_log, f, indent=2)

    print(f"Iteration Audit Log updated: {log_file}")

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_pdf = os.path.join(PROJECT_ROOT, "testing_doc", "kemh102.pdf")
    model_path = os.path.join(PROJECT_ROOT, "models", "ncert_classifier.joblib")
    output_dir = os.path.join(PROJECT_ROOT, "output")
    
    run_pdf_inference(input_pdf, model_path, output_dir)
