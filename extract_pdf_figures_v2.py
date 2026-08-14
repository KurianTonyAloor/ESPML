import os
import json
import pymupdf as fitz

def extract_clean_page_clip_figures(pdf_path: str, output_dir: str = "images"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    spatial_manifest = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_area = page.rect.width * page.rect.height
        image_info_list = page.get_image_info()

        for idx, img_info in enumerate(image_info_list):
            bbox = img_info["bbox"]
            r = fitz.Rect(bbox)
            w_pt, h_pt = r.width, r.height
            area = w_pt * h_pt

            # Skip tiny icons (< 15pt) or full page background graphics (> 75% page area)
            if area < 400 or area > 0.75 * page_area:
                continue

            # Determine key / caption by scanning surrounding text
            text_blocks = page.get_text("dict")["blocks"]
            matched_key = f"page_{page_num + 1}_img_{idx + 1}"
            caption_text = ""
            anchor_prefix = ""

            for b in text_blocks:
                if b.get("type") == 0:
                    b_rect = fitz.Rect(b["bbox"])
                    b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()

                    # Look for caption right below image (y0 within 35pt of image bottom)
                    if b_rect.y0 >= r.y1 and b_rect.y0 - r.y1 < 35:
                        if "Fig" in b_text or "Figure" in b_text or "Antoine" in b_text or "Lavoisier" in b_text or "Dalton" in b_text:
                            caption_text = b_text
                            if "Fig. 1.10" in b_text:
                                matched_key = "Fig. 1.10"
                            elif "Fig. 1.1" in b_text:
                                matched_key = "Fig. 1.1"
                            elif "Fig. 1.5" in b_text:
                                matched_key = "Fig. 1.5"
                            elif "Fig. 1.6" in b_text:
                                matched_key = "Fig. 1.6"
                            elif "Fig. 1.7" in b_text:
                                matched_key = "Fig. 1.7"
                            elif "Fig. 1.8" in b_text:
                                matched_key = "Fig. 1.8"
                            elif "Fig. 1.9" in b_text:
                                matched_key = "Fig. 1.9"
                            elif "Fig. 1.11" in b_text:
                                matched_key = "Fig. 1.11"
                            elif "Lavoisier" in b_text:
                                matched_key = "Antoine Lavoisier"

            # Render exact page clip as high-res PNG (300 DPI)
            # Expand bbox slightly (1pt) to capture border cleanly
            clip_rect = fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1) & page.rect
            pix = page.get_pixmap(clip=clip_rect, dpi=300)
            
            img_filename = f"{matched_key.lower().replace('.', '_').replace(' ', '_')}.png"
            img_path = os.path.join(output_dir, img_filename)
            pix.save(img_path)

            col_width = (page.rect.width - 70) / 2
            width_ratio = min(95, max(30, int((w_pt / col_width) * 100)))

            spatial_manifest[matched_key] = {
                "fig_key": matched_key,
                "src": f"images/{img_filename}",
                "caption": caption_text,
                "width_pt": round(w_pt, 1),
                "height_pt": round(h_pt, 1),
                "width_ratio_pct": width_ratio,
                "page": page_num + 1
            }
            print(f"[High-Res Clip] Page {page_num + 1}: Key='{matched_key}' -> {img_filename} (Ratio={width_ratio}%)")

    doc.close()

    manifest_path = os.path.join(output_dir, "spatial_figure_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(spatial_manifest, f, indent=2)

    print(f"\nSaved {len(spatial_manifest)} high-res clipped figures to {manifest_path}")
    return spatial_manifest

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    extract_clean_page_clip_figures(pdf_path)
