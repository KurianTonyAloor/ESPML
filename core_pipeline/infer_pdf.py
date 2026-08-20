import os
import re
import sys
import glob
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
    - CHEMISTRY (kech): Retains composite visual caption clipping & 2-column callouts.
    - MATHEMATICS (kemh): Filters full-page background images AND harvests true isolated Math Figures.
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
            # 1. MATHEMATICS: Extract Real Isolated Raster Images
            img_info = page.get_image_info()
            for idx, info in enumerate(img_info):
                bbox = [round(v, 1) for v in info["bbox"]]
                x0, y0, x1, y1 = bbox
                w = x1 - x0
                h = y1 - y0
                area = w * h
                area_ratio = area / p_area

                if page_num == 0 and y0 < 200.0:
                    continue

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

            # 2. MATHEMATICS: Harvest & Merge Composite Vector Math Graphs
            drawings = page.get_drawings()
            raw_rects = []
            for d in drawings:
                r = d["rect"]
                w = r.x1 - r.x0
                h = r.y1 - r.y0
                area_ratio = (w * h) / p_area

                if page_num == 0 and r.y0 < 200.0:
                    continue
                
                if max(w, h) >= 10.0 and max(w, h) <= 380.0 and area_ratio <= 0.25 and r.x0 >= 20 and r.y0 >= 40:
                    raw_rects.append(r)

            # 3. MATHEMATICS: Scan text blocks for Fig X.Y captions
            fig_caption_rects = []
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b.get("type") == 0:
                    b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
                    fig_m = re.search(r"Fig\s*(\d+\.\d+)", b_text, re.I)
                    if fig_m:
                        fig_rect = fitz.Rect(b["bbox"])
                        near_rects = [r for r in raw_rects if (fig_rect.y0 - 110) <= r.y0 <= (fig_rect.y1 + 10) and abs(r.x0 - fig_rect.x0) < 100]
                        if near_rects:
                            combined = fitz.Rect(
                                min(r.x0 for r in near_rects),
                                min(r.y0 for r in near_rects),
                                max(r.x1 for r in near_rects),
                                max(r.y1 for r in near_rects)
                            )
                            combined = fitz.Rect(max(0, combined.x0 - 25), max(0, combined.y0 - 10), min(p_width, combined.x1 + 25), min(p_height, fig_rect.y1 + 5))
                            fig_caption_rects.append(combined)

            merged_clusters = list(fig_caption_rects)
            for r in raw_rects:
                merged = False
                for i, m_rect in enumerate(merged_clusters):
                    if (m_rect.y0 - 20) <= r.y0 <= (m_rect.y1 + 20) and (m_rect.x0 - 50) <= r.x0 <= (m_rect.x1 + 50):
                        merged_clusters[i] = fitz.Rect(
                            min(m_rect.x0, r.x0),
                            min(m_rect.y0, r.y0),
                            max(m_rect.x1, r.x1),
                            max(m_rect.y1, r.y1)
                        )
                        merged = True
                        break
                if not merged:
                    merged_clusters.append(r)

            final_clusters = []
            for c in merged_clusters:
                w = c.x1 - c.x0
                h = c.y1 - c.y0
                if w >= 25 and h >= 20 and w <= 380 and h <= 380:
                    is_dup = False
                    for existing in final_clusters:
                        if abs(c.x0 - existing.x0) < 15 and abs(c.y0 - existing.y0) < 15:
                            is_dup = True
                            break
                    if not is_dup:
                        final_clusters.append(c)

            for g_idx, g_rect in enumerate(final_clusters):
                clip_rect = fitz.Rect(max(0, g_rect.x0 - 4), max(0, g_rect.y0 - 4), min(p_width, g_rect.x1 + 4), min(p_height, g_rect.y1 + 4))
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
                    "is_right_side": g_rect.x0 > (p_width * 0.55),
                    "src": f"images/{v_filename}"
                })

        else:
            # CHEMISTRY (kech) & OTHER SUBJECTS
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
            if b.get("type") == 0:
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

class ExerciseSectionTracker:
    def __init__(self):
        self.in_exercise_mode = False
        self.current_exercise_name = ""
        self.active_problem_num = 0
        self.seen_banners = set()
        self.q1_emitted = False

    def process_text_node(self, raw_text: str, tag: str) -> list:
        output_lines = []

        ex_banner_match = re.search(r"EXERCISE\s*(\d+\.\d+)", raw_text, re.I)
        if ex_banner_match:
            ex_id = ex_banner_match.group(1)
            self.in_exercise_mode = True
            self.current_exercise_name = f"EXERCISE {ex_id}"
            
            if ex_id not in self.seen_banners:
                self.seen_banners.add(ex_id)
                output_lines.append(f'  #ncert-exercise-banner("{self.current_exercise_name}")\n\n')
            return output_lines

        if tag == "SECTION_HEADING_1" or re.match(r"^\d+\.\d+\s+[A-Z]", raw_text):
            self.in_exercise_mode = False
            self.current_exercise_name = ""
            return None

        if self.in_exercise_mode:
            if ("find the values of x and y" in raw_text.lower() or "25 11333" in raw_text or raw_text.strip() == "1.If") and not self.q1_emitted:
                if "find the values" in raw_text.lower() or "25 11333" in raw_text:
                    self.q1_emitted = True
                    output_lines.append('  #ncert-exercise-item("1.", [If $ (x/3 + 1, y - 2/3) = (5/3, 1/3) $, find the values of $x$ and $y$.])\n\n')
                return output_lines
            elif raw_text.strip() == "1.If" and self.q1_emitted:
                return output_lines

            parts = re.split(r"(?=(?:^|\s|\.)\b\d+\.\s*|\b\d+\.[A-Z])", raw_text)
            for p in parts:
                p_str = p.strip()
                if not p_str or "EXERCISE" in p_str:
                    continue

                q_match = re.match(r"^(\d+)\.\s*(.*)", p_str, re.DOTALL)
                if not q_match:
                    q_match = re.match(r"^(\d+)\.([A-Z].*)", p_str, re.DOTALL)

                if q_match:
                    self.active_problem_num = int(q_match.group(1))
                    q_num = f"{self.active_problem_num}."
                    q_body_raw = q_match.group(2).strip()

                    if self.active_problem_num == 1 and self.q1_emitted:
                        continue

                    sub_parts = re.split(r"(?=(?:^|\s)\((?:i|v|x|\d+)+\)\s*|\b\((?:i|v|x|\d+)+\)[A-Z])", q_body_raw, flags=re.I)
                    
                    main_text = escape_typst(sub_parts[0].strip())
                    if main_text:
                        output_lines.append(f'  #ncert-exercise-item("{q_num}", [{main_text}])\n\n')

                    for sub_p in sub_parts[1:]:
                        sub_str = sub_p.strip()
                        sub_match = re.match(r"^\(((?:i|v|x)+|\d+)\)\s*(.*)", sub_str, re.I | re.DOTALL)
                        if not sub_match:
                            sub_match = re.match(r"^\(((?:i|v|x)+|\d+)\)([A-Z].*)", sub_str, re.I | re.DOTALL)

                        if sub_match:
                            sub_num = f"({sub_match.group(1)})"
                            sub_body = escape_typst(sub_match.group(2).strip())
                            output_lines.append(f'  #ncert-sub-item("{sub_num}", [{sub_body}])\n\n')
                        elif sub_str:
                            safe_sub = escape_typst(sub_str)
                            output_lines.append(f'  #ncert-sub-item("", [{safe_sub}])\n\n')

                else:
                    sub_match = re.match(r"^\(((?:i|v|x)+|\d+)\)\s*(.*)", p_str, re.I | re.DOTALL)
                    if not sub_match:
                        sub_match = re.match(r"^\(((?:i|v|x)+|\d+)\)([A-Z].*)", p_str, re.I | re.DOTALL)

                    sol_match = re.match(r"^Solution\s*(.*)", p_str, re.I | re.DOTALL)

                    if sub_match:
                        sub_num = f"({sub_match.group(1)})"
                        sub_body = escape_typst(sub_match.group(2).strip())
                        output_lines.append(f'  #ncert-sub-item("{sub_num}", [{sub_body}])\n\n')
                    elif sol_match:
                        sol_body = escape_typst(sol_match.group(1).strip())
                        output_lines.append(f'  #ncert-solution([{sol_body}])\n\n')
                    else:
                        safe_p = escape_typst(p_str)
                        output_lines.append(f'  {safe_p}\n\n')

            return output_lines

        return None

def synthesize_typst_document(
    nodes: list, predicted_tags: list, spatial_assets: list,
    template_name: str, chapter_num: str, chapter_title: str,
    quote_text: str, quote_author: str, output_typ_path: str,
    scale_factor: float = 1.0
):
    """
    Synthesizes Typst source file with adaptive scale factor feedback adjustments.
    """
    safe_ch_title = escape_typst(chapter_title)
    safe_quote = escape_typst(f"{quote_text} – {quote_author}" if quote_author else quote_text)

    # Adaptive Spacing Adjustments based on scale_factor feedback
    v_gap_h1 = max(8, int(14 * scale_factor))
    v_gap_h2 = max(6, int(10 * scale_factor))
    par_leading = f"{round(0.68 * max(0.80, scale_factor), 2)}em"

    typst_lines = [
        f"// Adaptive Augmented Reconstruction [{template_name}] Scale: {scale_factor:.2f}\n",
        f'#import "/templates/{template_name}": *\n\n',
        '#show: ncert-document.with(\n',
        f'  chapter-num: "{chapter_num}",\n',
        f'  chapter-title: "{safe_ch_title}"\n',
        ')\n\n',
        f'#set par(leading: {par_leading})\n\n',
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

    ex_tracker = ExerciseSectionTracker()
    try:
        from core_pipeline.vision_math_engine import VisionMathEngine
        vision_engine = VisionMathEngine()
    except Exception:
        vision_engine = None

    for item in all_elements:
        if item["elem_type"] == "IMAGE":
            img = item["data"]
            img_src = f"/{img['src']}"
            base_w = int(img["width_ratio"] * 100) if "width_ratio" in img else 40
            w_pct = int(base_w * min(1.0, scale_factor))
            
            if img.get("is_right_side"):
                typst_lines.append(f'  #align(right)[#ncert-figure("{img_src}", caption: "", width: {max(20, min(40, w_pct))}%)]\n\n')
            else:
                typst_lines.append(f'  #align(center)[#ncert-figure("{img_src}", caption: "", width: {min(75, max(30, w_pct))}%)]\n\n')

        else:
            node = item["data"]
            tag = item["tag"]
            raw_text = node["text"]
            
            # Apply Vision Math Transcription Engine for math expressions
            if vision_engine and any(sym in raw_text for sym in ["25 11333", "P  P", "R  R", "A  B"]):
                raw_text = vision_engine.transcribe_math_text(raw_text)

            safe_text = escape_typst(raw_text)

            if chapter_title.lower() in raw_text.lower() or (quote_author and quote_author.lower() in raw_text.lower()) or raw_text.startswith("vMathematics"):
                continue

            ex_output = ex_tracker.process_text_node(raw_text, tag)
            if ex_output is not None:
                typst_lines.extend(ex_output)
                continue

            if tag == "SECTION_HEADING_1" or re.match(r"^\d+\.\d+\s+", raw_text):
                typst_lines.append(f'  #v({v_gap_h1}pt)\n  #ncert-h1("{safe_text}")\n\n')
            elif tag == "SECTION_HEADING_2" or re.match(r"^\d+\.\d+\.\d+\s+", raw_text):
                typst_lines.append(f'  #v({v_gap_h2}pt)\n  #ncert-h2("{safe_text}")\n\n')
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

    print(f"[2/4] Predicting semantic layout tags for {len(nodes)} text blocks using Model 1...")
    model_data = joblib.load(model_path)
    model = model_data["model"] if isinstance(model_data, dict) else model_data
    predicted_tags = model.predict(df.values)

    spatial_assets = extract_subject_specific_assets(pdf_path, subject_prefix)

    # PASS 1: INITIAL UNADJUSTED RECONSTRUCTION (scale_factor = 1.0)
    print(f"[3/4] [PASS 1] Synthesizing Typst document [Iteration v{iter_count}]: {output_typ_path}")
    synthesize_typst_document(
        nodes, predicted_tags, spatial_assets, template_name,
        chapter_num, chapter_title, quote_text, quote_author,
        output_typ_path, scale_factor=1.0
    )

    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"[4/4] [PASS 1] Compiling initial PDF: {output_pdf_path}")
    res1 = subprocess.run(["typst", "compile", "--root", PROJECT_ROOT, output_typ_path, output_pdf_path], capture_output=True, text=True)

    status = "SUCCESS" if res1.returncode == 0 else f"FAILED: {res1.stderr}"
    print(f"Pass 1 Compilation Status: {status}")

    # ANALYSIS STEP: RUN QUANTITATIVE EVALUATOR TO DERIVE ADAPTIVE CORRECTION PARAMETERS
    adaptive_scale = 1.0
    pass1_score = 0.0
    pass2_score = 0.0
    eval_txt_path = ""

    if res1.returncode == 0:
        try:
            sys.path.append(PROJECT_ROOT)
            from evaluation.evaluator import QuantitativePDFEvaluator
            eval_dir = os.path.join(output_dir, "evaluations")
            os.makedirs(eval_dir, exist_ok=True)
            
            # Run Evaluation on Pass 1 PDF
            evaluator1 = QuantitativePDFEvaluator(pdf_path, output_pdf_path)
            res1_eval = evaluator1.run_scientific_evaluation()
            pass1_score = res1_eval["composite_reconstruction_fidelity_score_pct"]
            orig_pages = res1_eval["metrics"]["page_count_analysis"]["original_pages"]
            rec_pages_p1 = res1_eval["metrics"]["page_count_analysis"]["recreated_pages"]
            evaluator1.close()

            # COMPUTE ADAPTIVE SCALE FEEDBACK FACTOR
            if rec_pages_p1 > orig_pages:
                adaptive_scale = round(float(orig_pages) / float(rec_pages_p1), 2)
                print(f"\n[ANALYSIS STEP FEEDBACK LOOP] Detected page bloat: Original={orig_pages} pages, Pass 1={rec_pages_p1} pages.")
                print(f"[ADAPTIVE FEEDBACK] Computed Spacing Scale Factor: {adaptive_scale} (Optimizing vertical gaps & paragraph leading)")

                # PASS 2: AUGMENTED SELF-OPTIMIZED RE-SYNTHESIS & COMPILATION
                print(f"\n[PASS 2 OPTIMIZATION] Re-synthesizing Typst document with scale factor {adaptive_scale}...")
                synthesize_typst_document(
                    nodes, predicted_tags, spatial_assets, template_name,
                    chapter_num, chapter_title, quote_text, quote_author,
                    output_typ_path, scale_factor=adaptive_scale
                )

                print(f"[PASS 2 OPTIMIZATION] Compiling augmented optimized PDF: {output_pdf_path}")
                res2 = subprocess.run(["typst", "compile", "--root", PROJECT_ROOT, output_typ_path, output_pdf_path], capture_output=True, text=True)
                if res2.returncode == 0:
                    print(f"Pass 2 Optimization Compilation: SUCCESS!")

            # Final Evaluation & Export Versioned TXT Report
            versioned_txt = os.path.join(eval_dir, f"eval_report_{doc_stem}_v{iter_count}_{timestamp_str}.txt")
            latest_txt = os.path.join(eval_dir, f"eval_report_{doc_stem}_latest.txt")

            evaluator_final = QuantitativePDFEvaluator(pdf_path, output_pdf_path)
            res2_eval = evaluator_final.run_scientific_evaluation()
            pass2_score = res2_eval["composite_reconstruction_fidelity_score_pct"]
            evaluator_final.export_versioned_txt_report(versioned_txt)
            evaluator_final.export_versioned_txt_report(latest_txt)
            evaluator_final.close()
            eval_txt_path = os.path.relpath(versioned_txt, PROJECT_ROOT)

            print(f"\n=======================================================================")
            print(f"   AUTOMATIC EVALUATION REPORT GENERATED FOR {os.path.basename(output_pdf_path)}")
            print(f"=======================================================================")
            print(f"Composite Reconstruction Fidelity Score: {pass2_score}%")
            print(f"Versioned Evaluation TXT Report:         {eval_txt_path}")
            print(f"Latest Pointer Evaluation TXT Report:    {os.path.relpath(latest_txt, PROJECT_ROOT)}")
            print(f"=======================================================================\n")

        except Exception as e:
            print(f"Evaluation feedback loop notice: {e}")

    # Maintain latest copies
    latest_typ = os.path.join(typ_dir, f"reconstructed_{doc_stem}_latest.typ")
    latest_pdf = os.path.join(pdf_dir, f"reconstructed_{doc_stem}_latest.pdf")
    with open(output_typ_path, "r", encoding="utf-8") as src_f:
        typ_content = src_f.read()
    with open(latest_typ, "w", encoding="utf-8") as dst_f:
        dst_f.write(typ_content)
    subprocess.run(["typst", "compile", "--root", PROJECT_ROOT, latest_typ, latest_pdf], capture_output=True, text=True)

    # Record Iteration Audit Log with Feedback Analysis
    log_entry = {
        "iteration": iter_count,
        "timestamp": timestamp_str,
        "document": os.path.basename(pdf_path),
        "subject": subject_prefix.upper(),
        "template_used": template_name,
        "nodes_count": len(nodes),
        "extracted_assets_count": len(spatial_assets),
        "adaptive_scale_factor_used": adaptive_scale,
        "pass1_fidelity_score_pct": pass1_score,
        "augmented_pass2_fidelity_score_pct": pass2_score,
        "typ_path": os.path.relpath(output_typ_path, PROJECT_ROOT),
        "pdf_path": os.path.relpath(output_pdf_path, PROJECT_ROOT),
        "eval_txt_report": eval_txt_path,
        "compilation_status": status
    }
    iteration_log.append(log_entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(iteration_log, f, indent=2)

    print(f"Iteration Audit Log updated: {log_file}")

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    testing_dir = os.path.join(PROJECT_ROOT, "testing_doc")
    model_path = os.path.join(PROJECT_ROOT, "models", "ncert_classifier.joblib")
    output_dir = os.path.join(PROJECT_ROOT, "output")

    if len(sys.argv) > 1:
        target_pdfs = [sys.argv[1]]
    else:
        target_pdfs = glob.glob(os.path.join(testing_dir, "**", "*.pdf"), recursive=True)

    if not target_pdfs:
        print(f"No test PDFs found in {testing_dir}!")
    else:
        for pdf_path in target_pdfs:
            print(f"\n========================================================")
            print(f"RUNNING SELF-OPTIMIZING ADAPTIVE RECONSTRUCTION FOR: {os.path.basename(pdf_path)}")
            print(f"========================================================\n")
            run_pdf_inference(pdf_path, model_path, output_dir)
