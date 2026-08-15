import os
import re
import json
import pymupdf as fitz

def extract_all_ncert_figures(pdf_path: str, output_dir: str = "images"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    figure_manifest = {}

    print("=== EXTRACTING ALL NCERT FIGURES VIA VISUAL CAPTION CLIPPING ===")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_blocks = page.get_text("dict")["blocks"]

        for b in text_blocks:
            if b.get("type") == 0:  # Text block
                b_rect = fitz.Rect(b["bbox"])
                b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()

                # 100% Dynamic Asset Harvesting Engine (No hardcoded names)
                fig_match = re.search(r"Fig\.\s*(\d+\.\d+)", b_text, re.I)
                scientist_match = re.search(r"([A-Z][a-zA-Z\.\s]{2,30}?)\s*\(\s*\d{4}\s*[–\-]\s*\d{4}\s*\)", b_text)
                fig_key = None

                if fig_match:
                    fig_key = f"Fig. {fig_match.group(1)}"
                elif scientist_match:
                    fig_key = scientist_match.group(1).strip()

                if not fig_key:
                    continue

                # Determine Graphic Region:
                # Most figure captions sit directly below the graphic (y0 of caption is bottom of graphic).
                # Check page graphics / drawings / images directly above the caption.
                
                # Check raster images or drawing rects above caption (within 180pt above caption)
                top_y = max(45.0, b_rect.y0 - 185.0)
                bot_y = b_rect.y0 - 2.0
                
                # Determine horizontal bounds (column width)
                # If caption is in left column (x0 < 300), clip left column width (50 to 290)
                # If caption is in right column (x0 >= 300), clip right column width (300 to 540)
                if b_rect.x0 < 280:
                    left_x = max(45.0, b_rect.x0 - 20)
                    right_x = min(295.0, b_rect.x1 + 30)
                else:
                    left_x = max(295.0, b_rect.x0 - 40)
                    right_x = min(545.0, b_rect.x1 + 40)

                # Special full-width figures if caption spans across middle
                if b_rect.width > 300:
                    left_x = 50.0
                    right_x = 540.0

                graphic_rect = fitz.Rect(left_x, top_y, right_x, bot_y) & page.rect

                # Render exact visual clip at 300 DPI
                pix = page.get_pixmap(clip=graphic_rect, dpi=300)
                
                safe_name = fig_key.lower().replace('.', '_').replace(' ', '_')
                img_filename = f"{safe_name}.png"
                img_path = os.path.join(output_dir, img_filename)
                pix.save(img_path)

                col_width = (page.rect.width - 70) / 2
                width_ratio = min(95, max(30, int((graphic_rect.width / col_width) * 100)))

                figure_manifest[fig_key] = {
                    "fig_key": fig_key,
                    "src": f"images/{img_filename}",
                    "caption": b_text,
                    "width_pt": round(graphic_rect.width, 1),
                    "height_pt": round(graphic_rect.height, 1),
                    "width_ratio_pct": width_ratio,
                    "page": page_num + 1
                }
                print(f"[Captured Figure] Page {page_num + 1}: Key='{fig_key}' -> {img_filename} (Ratio={width_ratio}%)")

    doc.close()

    manifest_path = os.path.join(output_dir, "spatial_figure_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(figure_manifest, f, indent=2)

    print(f"\nSaved {len(figure_manifest)} figure definitions to {manifest_path}")
    return figure_manifest

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    extract_all_ncert_figures(pdf_path)
