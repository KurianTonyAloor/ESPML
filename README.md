# ESPML: Machine Learning & Typst 1:1 NCERT Textbook Reproduction Engine

An end-to-end Machine Learning and Typst layout reconstruction system that converts unformatted textbook documents (DOCX/PDF) into publication-ready 1:1 high-fidelity Typst PDFs.

---

## 📁 Repository Structure

```
ML Based/
├── core_pipeline/           # Core Machine Learning Training & Inference Engines
│   ├── train_dual_models.py           # Multi-Document Model 1 & Model 2 Training
│   ├── template_style_classifier.py    # 20D Publisher Style Predictor (Model 2)
│   ├── infer_pdf.py                   # 100% Dynamic PDF Inference Engine
│   ├── infer.py                       # DOCX Paragraph Inference Engine
│   └── TSPdf.py                       # 9D Paragraph Feature Extractor
│
├── extraction_tuning/       # Subject Asset Harvesters & Master Template Generators
│   ├── subject_template_engine.py     # Subject-Specific Master Template Synthesizer
│   ├── build_master_template.py       # Design Token Extraction & Master Template Generator
│   ├── extract_all_figure_captions.py # 300 DPI Figure & Scientist Portrait NER Engine
│   ├── detect_pdf_drawing_boxes.py    # Vector Shading Callout Box Harvester
│   └── clean_table_manifest.py        # 1:1 Table Schema Harvester
│
├── manifests/               # JSON Manifests & Spatial Anchor Schemas
│   ├── callout_box_manifest.json      # Vector Callout Box Shading Rectangles
│   ├── spatial_anchor_manifest.json   # 5D Spatial Bounding-Box Sequence Graph
│   ├── spatial_nodes.json             # Extracted Node Coordinates
│   └── table_manifest.json            # 1:1 Clean Table Schemas
│
├── debugging_tools/         # Inspection, Diagnostics & Preview Generation
│   ├── debug_image_bboxes.py          # Bounding Box Area Ratio Inspector
│   ├── inspect_vector_graphs.py       # Math Vector Graph Cluster Analyzer
│   ├── inspect_kemh102_layout.py      # NCERT Math Page Geometry Inspector
│   └── render_pdf_page_images.py      # PyMuPDF Page Renderer
│
├── templates/               # Subject Master Typst Design Systems (.typ)
│   ├── kemh_template.typ              # Mathematics (Royal Teal #00adef, Pill Banner, Single Column)
│   ├── kech_template.typ              # Chemistry (Header Blue #1b4f9c, Green Notes, Pink Problem Boxes)
│   ├── keph_template.typ              # Physics (Burgundy Red #800000, Cyan Note Boxes)
│   └── kebo_template.typ              # Biology (Forest Green #1e6b37, Lime Callouts)
│
├── models/                  # Serialized Machine Learning Model Weights (.joblib)
│   ├── ncert_classifier.joblib        # Model 1 Paragraph Semantic Classifier
│   └── ncert_template_model.joblib   # Model 2 Publisher Style Classifier
│
├── Training_DOc/            # Multi-Subject Training Datasets (DOCX & PDF pairs)
├── testing_doc/             # Testing Dataset PDFs (kemh102.pdf)
└── images/                  # Extracted 300 DPI Figures & Spatial Vector Graphs
```

---

## 🛠️ Usage Instructions

### 1. Run 100% Dynamic PDF Inference
```powershell
python core_pipeline/infer_pdf.py
```

### 2. Train Dual Models Across All 12 Chapters
```powershell
python core_pipeline/train_dual_models.py
```

### 3. Generate Subject Master Templates
```powershell
python extraction_tuning/subject_template_engine.py
```
