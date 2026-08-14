import os
import re
import zipfile
from typing import List, Dict, Any, Tuple
import pymupdf as fitz  # Updated import to eliminate fitz deprecation warning
import docx
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import joblib


# ==========================================
# 1. PDF FEATURE & SPATIAL EXTRACTOR (PyMuPDF)
# ==========================================

def is_inside_rect(bbox: Tuple[float, float, float, float], rects: List[fitz.Rect]) -> int:
    """Checks if a text bounding box overlaps with any background drawing box."""
    t_rect = fitz.Rect(bbox)
    for r in rects:
        if r.contains(t_rect) or r.intersects(t_rect):
            return 1
    return 0


def extract_pdf_lines(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Groups PyMuPDF spans into full lines to match DOCX paragraph granularity.
    """
    doc = fitz.open(pdf_path)
    lines_data = []
    all_font_sizes = []

    # Collect font sizes across document to compute baseline median
    for page in doc:
        for block in page.get_text("dict").get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            all_font_sizes.append(span["size"])

    doc_median_font = np.median(all_font_sizes) if all_font_sizes else 10.0

    # Extract lines with spatial properties
    for page_num, page in enumerate(doc):
        bg_rects = [fitz.Rect(d["rect"]) for d in page.get_drawings() if d.get("fill") is not None]

        for block in page.get_text("dict").get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    line_text = "".join([s["text"] for s in line["spans"]]).strip()
                    if not line_text:
                        continue

                    first_span = line["spans"][0]
                    bbox = line["bbox"]
                    font_size = max([s["size"] for s in line["spans"]])
                    flags = first_span["flags"]
                    color = first_span["color"]

                    lines_data.append({
                        "text": line_text,
                        "page": page_num,
                        "font_size": font_size,
                        "font_ratio": font_size / doc_median_font,
                        "is_bold": 1 if (flags & 16 or "bold" in first_span["font"].lower()) else 0,
                        "is_italic": 1 if (flags & 2 or "italic" in first_span["font"].lower()) else 0,
                        "is_colored": 1 if color != 0 else 0,
                        "x0": bbox[0],
                        "inside_drawing_box": is_inside_rect(bbox, bg_rects),
                        "length": len(line_text)
                    })

    doc.close()
    return lines_data


def generate_pseudo_labels(pdf_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Applies rule-assisted heuristics on PDF line metadata to create ground-truth semantic tags.
    """
    for item in pdf_lines:
        text = item["text"]
        ratio = item["font_ratio"]
        inside_box = item["inside_drawing_box"]

        if ratio > 1.6:
            label = "CHAPTER_TITLE"
        elif ratio > 1.25:
            label = "SECTION_HEADING_1"
        elif ratio > 1.1 and item["is_bold"]:
            label = "SECTION_HEADING_2"
        elif re.match(r"^(Activity|Did You Know|Think, Discuss|Note)\b", text, re.I) or inside_box:
            label = "CALLOUT_BOX"
        elif re.match(r"^(Example|\d+\.\d+|Q\d+|Question)\b", text, re.I):
            label = "EXERCISE_OR_EXAMPLE"
        elif re.match(r"^(Fig|Figure)\s*\d+", text, re.I):
            label = "FIGURE_CAPTION"
        else:
            label = "MAIN_BODY_TEXT"

        item["label"] = label

    return pdf_lines


# ==========================================
# 2. DOCX PARSER & ALIGNMENT MODULE
# ==========================================

def parse_docx(docx_path: str) -> List[Dict[str, Any]]:
    """Extracts raw text nodes and basic markup properties from extracted DOCX."""
    if os.path.getsize(docx_path) == 0:
        raise ValueError(f"File is 0 bytes (empty): {docx_path}")

    if not zipfile.is_zipfile(docx_path):
        raise ValueError(f"File is not a valid DOCX package (missing ZIP structure): {docx_path}")

    doc = docx.Document(docx_path)
    docx_nodes = []

    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if not text:
            continue

        docx_nodes.append({
            "doc_index": i,
            "text": text,
            "docx_style": p.style.name,
            "length": len(text)
        })

    return docx_nodes


def align_docx_with_pdf(docx_nodes: List[Dict[str, Any]], pdf_lines: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Aligns DOCX paragraphs to PDF lines using windowed fuzzy string matching to transfer
    PDF spatial context and ground-truth labels onto DOCX feature vectors efficiently.
    """
    aligned_dataset = []
    num_pdf_lines = len(pdf_lines)
    last_matched_idx = 0
    window_size = 30  # Search radius around last match index

    for docx_node in docx_nodes:
        d_text = docx_node["text"].lower()
        best_match = None
        best_ratio = 0.0
        best_idx = -1

        # Localized window search first (monotonically moving forward)
        win_start = max(0, last_matched_idx - 10)
        win_end = min(num_pdf_lines, last_matched_idx + window_size)
        candidate_indices = list(range(win_start, win_end))

        for idx in candidate_indices:
            p_line = pdf_lines[idx]
            p_text = p_line["text"].lower()
            ratio = SequenceMatcher(None, d_text[:30], p_text[:30]).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = p_line
                best_idx = idx

        # Fallback to full document search if no good match found in window
        if best_ratio <= 0.35:
            for idx, p_line in enumerate(pdf_lines):
                if idx in candidate_indices:
                    continue
                p_text = p_line["text"].lower()
                ratio = SequenceMatcher(None, d_text[:30], p_text[:30]).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = p_line
                    best_idx = idx

        if best_match and best_ratio > 0.35:
            last_matched_idx = best_idx
            d_orig = docx_node["text"]
            row = {
                "font_ratio": best_match["font_ratio"],
                "is_bold": best_match["is_bold"],
                "is_italic": best_match["is_italic"],
                "is_colored": best_match["is_colored"],
                "x0": best_match["x0"],
                "inside_drawing_box": best_match["inside_drawing_box"],
                "length": docx_node["length"],
                "starts_with_digit": 1 if re.match(r"^\d+", d_orig) else 0,
                "has_keyword": 1 if re.match(r"^(Activity|Fig|Example|Q\d+|Table)", d_orig, re.I) else 0,
                "label": best_match["label"]
            }
            aligned_dataset.append(row)

    return pd.DataFrame(aligned_dataset)


# ==========================================
# 3. FEATURE ENGINEERING & TRAINING PIPELINE
# ==========================================

def train_lightweight_model(df: pd.DataFrame, model_output_path: str = "ncert_classifier.joblib"):
    """
    Builds context features (previous/next node characteristics) and trains
    a fast Random Forest Classifier.
    """
    # Contextual features (neighboring nodes)
    df["prev_font_ratio"] = df["font_ratio"].shift(1, fill_value=1.0)
    df["next_font_ratio"] = df["font_ratio"].shift(-1, fill_value=1.0)
    df["delta_font_prev"] = df["font_ratio"] - df["prev_font_ratio"]

    feature_cols = [
        "font_ratio", "is_bold", "is_italic", "is_colored",
        "x0", "inside_drawing_box", "length", "starts_with_digit",
        "has_keyword", "prev_font_ratio", "next_font_ratio", "delta_font_prev"
    ]

    X = df[feature_cols]
    y = df["label"]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    clf = RandomForestClassifier(
        n_estimators=80,
        max_depth=12,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("\n--- Model Evaluation Metrics ---")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    artifacts = {
        "model": clf,
        "encoder": label_encoder,
        "features": feature_cols
    }
    joblib.dump(artifacts, model_output_path)
    print(f"Successfully saved lightweight model package to: {model_output_path}")


# ==========================================
# 4. MAIN EXECUTION ENTRY POINT
# ==========================================

def run_pipeline(pdf_path: str, docx_path: str, model_save_path: str = "ncert_classifier.joblib"):
    print(f"[1/4] Extracting PDF spatial lines from: {pdf_path}")
    raw_pdf_lines = extract_pdf_lines(pdf_path)

    print("[2/4] Generating pseudo-labels from spatial/drawing heuristics...")
    labeled_pdf_lines = generate_pseudo_labels(raw_pdf_lines)

    print(f"[3/4] Parsing DOCX and aligning nodes: {docx_path}")
    docx_nodes = parse_docx(docx_path)
    dataset_df = align_docx_with_pdf(docx_nodes, labeled_pdf_lines)

    print(f"Dataset generated: {len(dataset_df)} aligned feature vectors.")

    print("[4/4] Training lightweight Random Forest Classifier...")
    train_lightweight_model(dataset_df, model_save_path)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    INPUT_PDF = os.path.join(BASE_DIR, "kech101.pdf")
    INPUT_DOCX = os.path.join(BASE_DIR, "extracted_chapter_1.docx")
    MODEL_OUTPUT = os.path.join(BASE_DIR, "ncert_classifier.joblib")

    if not os.path.exists(INPUT_PDF):
        raise FileNotFoundError(f"PDF file not found at: {INPUT_PDF}")
    if not os.path.exists(INPUT_DOCX):
        raise FileNotFoundError(f"DOCX file not found at: {INPUT_DOCX}")

    run_pipeline(INPUT_PDF, INPUT_DOCX, MODEL_OUTPUT)