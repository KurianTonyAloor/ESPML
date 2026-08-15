import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder Mapping Rules
FOLDER_MAPPING = {
    "core_pipeline": [
        "train_dual_models.py",
        "template_style_classifier.py",
        "infer.py",
        "infer_pdf.py",
        "TSPdf.py"
    ],
    "extraction_tuning": [
        "subject_template_engine.py",
        "build_master_template.py",
        "extract_all_figure_captions.py",
        "extract_pdf_figures.py",
        "extract_pdf_figures_v2.py",
        "extract_pdf_tables.py",
        "clean_table_manifest.py",
        "detect_pdf_drawing_boxes.py",
        "spatial_anchor_predictor.py",
        "spatial_image_manager.py",
        "image_spatial_analyzer.py"
    ],
    "debugging_tools": [
        "debug_image_bboxes.py",
        "debug_page5_graphics.py",
        "inspect_kemh102_layout.py",
        "inspect_vector_graphs.py",
        "check_box_widths.py",
        "check_page11_content.py",
        "find_exact_pages.py",
        "test_dynamic_person_regex.py",
        "test_spatial_image_extraction.py",
        "render_pdf_page_images.py",
        "render_test_pdf_previews.py",
        "verify_compiled_pdf.py"
    ],
    "templates": [
        "kemh_template.typ",
        "kech_template.typ",
        "keph_template.typ",
        "kebo_template.typ",
        "ncert_template.typ",
        "generated_ncert_template.typ",
        "test_automated_master_template.typ"
    ],
    "models": [
        "ncert_classifier.joblib",
        "ncert_template_model.joblib"
    ]
}

print("=== REORGANIZING PROJECT DIRECTORY STRUCTURE ===")

for folder_name, file_list in FOLDER_MAPPING.items():
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    print(f"\n[Folder] {folder_name}/")
    
    for filename in file_list:
        src_path = os.path.join(BASE_DIR, filename)
        dst_path = os.path.join(folder_path, filename)
        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)
            print(f"  -> Moved: {filename} -> {folder_name}/{filename}")

print("\n=== REORGANIZATION COMPLETE ===")
