import os
import glob
import json
import re
import numpy as np
import docx
import pymupdf as fitz
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import joblib

def extract_features_from_docx_pdf_pair(docx_path: str, pdf_path: str):
    """
    Extracts 9-dimensional paragraph feature matrix X and target labels y
    by aligning unformatted DOCX paragraphs with reference PDF layout metadata.
    """
    doc = fitz.open(pdf_path)
    docx_doc = docx.Document(docx_path)
    docx_paras = [p.text.strip() for p in docx_doc.paragraphs if p.text.strip()]

    # Extract PDF paragraph metadata
    pdf_nodes = []
    for p_num in range(len(doc)):
        page = doc[p_num]
        drawings = page.get_drawings()
        drawing_rects = [d["rect"] for d in drawings if d.get("fill")]

        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
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
                    if "color" in s and s["color"] not in (0, 1118481, 2236962):  # Non-black accent
                        is_colored = 1
                        break

                inside_box = int(any(b_rect.intersects(r) for r in drawing_rects))

                pdf_nodes.append({
                    "text": b_text,
                    "font_size": round(avg_font_size, 1),
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "is_colored": is_colored,
                    "x0": round(b_rect.x0, 1),
                    "inside_drawing_box": inside_box
                })
    doc.close()

    X = []
    y = []

    # Align DOCX paragraphs with PDF nodes
    for p_text in docx_paras:
        prefix = p_text[:35].lower().strip()
        matched_node = None
        for node in pdf_nodes:
            node_prefix = node["text"][:35].lower().strip()
            if prefix in node_prefix or node_prefix in prefix:
                matched_node = node
                break

        font_size = matched_node["font_size"] if matched_node else 10.0
        is_bold = matched_node["is_bold"] if matched_node else 0
        is_italic = matched_node["is_italic"] if matched_node else 0
        is_colored = matched_node["is_colored"] if matched_node else 0
        x0 = matched_node["x0"] if matched_node else 50.0
        inside_box = matched_node["inside_drawing_box"] if matched_node else 0

        word_count = len(p_text.split())
        is_upper = int(p_text.isupper())
        digit_start = int(bool(re.match(r"^\d+\.\d+", p_text)))

        # Rule-Assisted Target Labeling for Supervised Training
        if re.match(r"^Problem\s+\d+\.\d+", p_text, re.I) or "EXERCISES" in p_text.upper():
            label = "EXERCISE_OR_EXAMPLE"
        elif font_size >= 13.5 or (is_bold and digit_start and font_size >= 10.8):
            label = "SECTION_HEADING_1"
        elif digit_start or (is_bold and len(p_text) < 80):
            label = "SECTION_HEADING_2"
        elif inside_box:
            label = "CALLOUT_BOX"
        elif p_text.startswith("Fig.") or "Fig. " in p_text[:15]:
            label = "FIGURE_CAPTION"
        else:
            label = "MAIN_BODY_TEXT"

        feat_vector = [
            font_size,
            is_bold,
            is_italic,
            is_colored,
            x0 / 595.0,
            word_count,
            inside_box,
            is_upper,
            digit_start
        ]

        X.append(feat_vector)
        y.append(label)

    return X, y

def train_multi_document_models(training_dir: str = "Training_DOc"):
    docx_dir = os.path.join(training_dir, "docx")
    pdf_dir = os.path.join(training_dir, "pdf")

    docx_files = sorted(glob.glob(os.path.join(docx_dir, "*.docx")))
    print(f"=== MULTI-DOCUMENT TRAINING PIPELINE: Found {len(docx_files)} DOCX/PDF pairs ===")

    all_X = []
    all_y = []

    for docx_path in docx_files:
        base_name = os.path.splitext(os.path.basename(docx_path))[0]
        pdf_path = os.path.join(pdf_dir, f"{base_name}.pdf")
        if os.path.exists(pdf_path):
            print(f"[Processing Pair] {base_name}.docx <-> {base_name}.pdf")
            X_pair, y_pair = extract_features_from_docx_pdf_pair(docx_path, pdf_path)
            all_X.extend(X_pair)
            all_y.extend(y_pair)
            print(f"  -> Extracted {len(X_pair)} training paragraphs")

    X_mat = np.array(all_X, dtype=np.float32)
    y_mat = np.array(all_y)

    print(f"\nTotal Dataset Size: {X_mat.shape[0]} paragraphs across {len(docx_files)} chapters.")
    print("Class Distribution:", dict(zip(*np.unique(y_mat, return_counts=True))))

    # 1. Train Model 1 (Paragraph Classifier)
    print("\n--- Training Model 1: Paragraph Classifier ---")
    clf_m1 = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    scores_m1 = cross_val_score(clf_m1, X_mat, y_mat, cv=5)
    print(f"Model 1 5-Fold Cross-Validation Accuracy: {np.mean(scores_m1)*100:.2f}% (+/- {np.std(scores_m1)*100:.2f}%)")

    clf_m1.fit(X_mat, y_mat)
    joblib.dump(clf_m1, "ncert_classifier.joblib")
    print("Model 1 saved to: ncert_classifier.joblib")

    # 2. Train Model 2 (Publisher Style Classifier)
    print("\n--- Training Model 2: Publisher Style & Template Predictor ---")
    from template_style_classifier import train_and_save_template_style_classifier
    train_and_save_template_style_classifier("ncert_template_model.joblib")

    print("\n=== MULTI-DOCUMENT TRAINING COMPLETE! ALL MODELS UPDATED ===")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    training_dir = os.path.join(BASE_DIR, "Training_DOc")
    train_multi_document_models(training_dir)
