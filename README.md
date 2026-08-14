# ESPML: Machine Learning & Typst 1:1 NCERT Textbook Reproduction Engine

An end-to-end Machine Learning and Typst layout reconstruction system that converts unformatted textbook documents (DOCX/PDF) into publication-ready 1:1 high-fidelity Typst PDFs.

---

## 🏛️ Architecture & Workflow

```
[Source Unformatted DOCX]  ──>  [Random Forest ML Classifier]  ──>  Predicts Semantic Tags
                                             │
                                             ▼ Merged With
[Original Reference PDF]   ──>  [Spatial Asset Harvesters]    ──>  Injects Figures, Tables & Callouts
                                             │
                                             ▼
                                  [Typst Code (.typ)]
                                             │
                                             ▼
                                  [Compiled 1:1 PDF]
```

---

## 🚀 Key Features

* **Machine Learning Tag Classifier (`TSPdf.py` & `infer.py`)**: Trained Random Forest model (98%+ accuracy) predicting semantic roles for headings, body text, problem boxes, callouts, and captions.
* **100% Dynamic Asset Harvesting (`extract_all_figure_captions.py`)**: Named Entity Recognition (NER) regex engines dynamically extract figure clips (`Fig. X.X`) and scientist portraits (*John Dalton, Antoine Lavoisier, etc.*) at 300 DPI without hardcoded lists.
* **Structured 1:1 Table Engine (`clean_table_manifest.py`)**: Extracted clean table schemas for multi-column and full-width tables (`Table 1.1`, `Table 1.2`, `Table 1.3`, `Table 1.4`, Isotope Table).
* **Vector Callout Detector (`detect_pdf_drawing_boxes.py`)**: Vector shading analyzer detecting green notes and pink problem boxes.
* **1:1 Page 1 Opening Engine**: Renders `UNIT 1` header, QR code, 12 Objectives list in full left column, and Roald Hoffmann quote in right column.
* **Automated Master Template Generator (`build_master_template.py`)**: Dynamically extracts brand color palettes (`#1b4f9c` Header Blue, `#ebf5ed` Green), page margins, and 2-column layout tokens from any reference PDF.

---

## 🛠️ Usage Instructions

### Run Inference & Local PDF Compilation
```powershell
python infer.py
```

### Harvest Figures & Portraits (300 DPI)
```powershell
python extract_all_figure_captions.py
```

### Generate Master Typst Template
```powershell
python build_master_template.py
```

---

## 📄 Core Outputs
* **Typst Source**: `reconstructed_chapter_1.typ`
* **Compiled PDF**: `reconstructed_chapter_1.pdf`
* **Master Design System**: `ncert_template.typ`
