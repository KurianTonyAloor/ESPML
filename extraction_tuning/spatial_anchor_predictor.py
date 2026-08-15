import os
import json
import pymupdf as fitz

def extract_and_predict_spatial_anchors(pdf_path: str, output_manifest: str = "spatial_anchor_manifest.json"):
    """
    Extracts and predicts the exact spatial coordinates (x0, y0, x1, y1, page, column)
    for every paragraph, table, figure, and callout box in any reference document.
    """
    doc = fitz.open(pdf_path)
    spatial_elements = []

    print(f"=== SPATIAL COORDINATE & ANCHOR PREDICTOR: Analyzing {os.path.basename(pdf_path)} ===")

    for page_num in range(len(doc)):
        page = doc[page_num]
        p_width = page.rect.width
        p_height = page.rect.height

        # 1. Extract Text Blocks & Paragraph Spatial Coordinates
        text_blocks = page.get_text("dict")["blocks"]
        for b_idx, b in enumerate(text_blocks):
            if b.get("type") == 0:  # Text block
                bbox = [round(v, 1) for v in b["bbox"]]
                x0, y0, x1, y1 = bbox
                b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
                
                if not b_text:
                    continue

                # Determine Column & Width Category
                col_index = 1 if x0 < (p_width / 2) else 2
                is_full_width = (x1 - x0) > 350.0

                spatial_elements.append({
                    "id": f"text_p{page_num+1}_{b_idx}",
                    "type": "TEXT",
                    "page": page_num + 1,
                    "column": "FULL_WIDTH" if is_full_width else f"COL_{col_index}",
                    "bbox": bbox,
                    "width_pt": round(x1 - x0, 1),
                    "height_pt": round(y1 - y0, 1),
                    "text_prefix": b_text[:40]
                })

        # 2. Extract Vector Drawings & Callout Box Spatial Coordinates
        drawings = page.get_drawings()
        for d_idx, d in enumerate(drawings):
            if d.get("fill"):
                rect = d["rect"]
                bbox = [round(rect.x0, 1), round(rect.y0, 1), round(rect.x1, 1), round(rect.y1, 1)]
                w = rect.x1 - rect.x0
                h = rect.y1 - rect.y0
                if w > 100 and h > 20:  # Valid shaded callout box
                    col_index = 1 if rect.x0 < (p_width / 2) else 2
                    is_full_width = w > 350.0

                    spatial_elements.append({
                        "id": f"callout_p{page_num+1}_{d_idx}",
                        "type": "CALLOUT_BOX",
                        "page": page_num + 1,
                        "column": "FULL_WIDTH" if is_full_width else f"COL_{col_index}",
                        "bbox": bbox,
                        "width_pt": round(w, 1),
                        "height_pt": round(h, 1),
                        "fill_color": [round(c, 3) for c in d["fill"]]
                    })

        # 3. Extract Image & Figure Bounding Boxes
        img_info = page.get_image_info()
        for i_idx, info in enumerate(img_info):
            bbox = [round(v, 1) for v in info["bbox"]]
            x0, y0, x1, y1 = bbox
            w = x1 - x0
            h = y1 - y0
            if w > 30 and h > 30:  # Skip tiny icon artifacts
                col_index = 1 if x0 < (p_width / 2) else 2
                is_full_width = w > 350.0

                spatial_elements.append({
                    "id": f"fig_p{page_num+1}_{i_idx}",
                    "type": "FIGURE",
                    "page": page_num + 1,
                    "column": "FULL_WIDTH" if is_full_width else f"COL_{col_index}",
                    "bbox": bbox,
                    "width_pt": round(w, 1),
                    "height_pt": round(h, 1)
                })

    doc.close()

    # Sort all elements strictly by Spatial Reading Order: (Page, Column, y0)
    spatial_elements.sort(key=lambda el: (
        el["page"],
        0 if el["column"] == "FULL_WIDTH" else (1 if el["column"] == "COL_1" else 2),
        el["bbox"][1]  # y0 coordinate
    ))

    with open(output_manifest, "w", encoding="utf-8") as f:
        json.dump(spatial_elements, f, indent=2)

    print(f"Extracted {len(spatial_elements)} spatially anchored elements to {output_manifest}")
    return spatial_elements

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    extract_and_predict_spatial_anchors(pdf_path)
