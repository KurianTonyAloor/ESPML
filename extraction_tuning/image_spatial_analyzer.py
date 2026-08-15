import os
import re
import json
import pymupdf as fitz

def analyze_and_extract_spatial_images(pdf_path: str, output_dir: str = "images"):
    """
    Extracts PDF images, measures spatial bounding boxes/widths, detects text overlapping
    the image area, and builds an anchor manifest for 1:1 Typst injection.
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    extracted_figures = []
    figure_manifest = {}

    portrait_keywords = {
        "lavoisier": "Antoine Lavoisier",
        "proust": "Joseph Proust",
        "gay-lussac": "Joseph Louis Gay Lussac",
        "gay lussac": "Joseph Louis Gay Lussac",
        "avogadro": "Amedeo Avogadro",
        "dalton": "John Dalton",
        "nagarjuna": "Nagarjuna",
        "chakrapani": "Chakrapani"
    }

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_rect = page.rect
        page_area = page_rect.width * page_rect.height
        col_width_pt = (page_rect.width - 72) / 2.0  # Approx column width in 2-col layout (~260pt)

        # 1. Collect all text blocks with bounding boxes on this page
        page_text_blocks = []
        page_captions = []
        page_portraits = []

        for b in page.get_text("dict")["blocks"]:
            if b.get("type") == 0:  # Text block
                block_text = "".join(
                    span["text"] for line in b["lines"] for span in line["spans"]
                ).strip()
                if block_text:
                    bbox = fitz.Rect(b["bbox"])
                    node_data = {
                        "bbox": bbox,
                        "y0": bbox.y0,
                        "text": block_text
                    }
                    page_text_blocks.append(node_data)

                    # Check for figure caption
                    match = re.search(r"(Fig\.\s*\d+\.\d+[^\n]*)", block_text, re.I)
                    if match:
                        caption_text = match.group(1).replace("\n", " ").strip()
                        page_captions.append((bbox.y0, caption_text))

                    # Check for scientist portrait
                    for key, name in portrait_keywords.items():
                        if key in block_text.lower():
                            page_portraits.append((bbox.y0, name))

        page_text_blocks.sort(key=lambda x: x["y0"])
        page_captions.sort(key=lambda x: x[0])
        page_portraits.sort(key=lambda x: x[0])

        # 2. Inspect image xrefs and spatial bounding boxes
        image_info_list = page.get_image_info(xrefs=True)
        img_idx = 0

        for img_info in image_info_list:
            xref = img_info.get("xref", 0)
            if not xref:
                continue

            bbox_rect = fitz.Rect(img_info["bbox"])
            w_pt, h_pt = bbox_rect.width, bbox_rect.height
            img_area = w_pt * h_pt

            # Skip full-page background graphics (> 80% page area) or tiny icons (< 30pt)
            if img_area > 0.8 * page_area or w_pt < 30 or h_pt < 30:
                continue

            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            w_px, h_px = base_image["width"], base_image["height"]

            # Skip high-res full page canvas images
            if w_px > 1500 or h_px > 1500:
                continue

            img_idx += 1
            y0 = bbox_rect.y0

            # 3. Detect Text Overlay (text spans intersecting image bounding box)
            overlapping_texts = []
            for tb in page_text_blocks:
                # If text block intersects image bbox
                if bbox_rect.intersects(tb["bbox"]) or bbox_rect.contains(tb["bbox"]):
                    # Avoid capturing figure caption itself as overlay
                    if not tb["text"].startswith("Fig."):
                        overlapping_texts.append(tb["text"])

            has_text_overlay = len(overlapping_texts) > 0
            overlay_text = " | ".join(overlapping_texts) if has_text_overlay else ""

            # 4. Determine Image Width Ratio Relative to Column/Page Width
            width_ratio_pct = min(100, max(30, int((w_pt / col_width_pt) * 90)))
            if w_pt > 1.4 * col_width_pt:
                width_ratio_pct = min(100, int((w_pt / page_rect.width) * 100))

            # 5. Determine best caption or portrait label & anchor text
            caption_name = f"page_{page_num + 1}_img_{img_idx}"
            matched_caption = ""
            fig_key = ""

            if page_captions:
                closest_cap = min(page_captions, key=lambda c: abs(c[0] - y0))
                matched_caption = closest_cap[1]
                fig_match = re.search(r"Fig\.\s*(\d+\.\d+)", matched_caption, re.I)
                if fig_match:
                    fig_num = fig_match.group(1).replace(".", "_")
                    fig_key = f"Fig. {fig_match.group(1)}"
                    caption_name = f"fig_{fig_num}"

            if not fig_key and page_portraits:
                closest_portrait = min(page_portraits, key=lambda p: abs(p[0] - y0))
                portrait_name = closest_portrait[1].replace(" ", "_").lower()
                caption_name = f"portrait_{portrait_name}"
                fig_key = closest_portrait[1]

            # 6. Find preceding text anchor prefix
            preceding_text = ""
            for tb in page_text_blocks:
                if tb["y0"] <= y0:
                    preceding_text = tb["text"]
                else:
                    break

            anchor_prefix = preceding_text[:35].lower().strip() if preceding_text else ""

            filename = f"{caption_name}.{image_ext}"
            filepath = os.path.join(output_dir, filename)

            counter = 1
            while os.path.exists(filepath):
                filename = f"{caption_name}_{counter}.{image_ext}"
                filepath = os.path.join(output_dir, filename)
                counter += 1

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            fig_entry = {
                "fig_key": fig_key or caption_name,
                "src": f"{output_dir}/{filename}",
                "caption": matched_caption,
                "anchor_prefix": anchor_prefix,
                "width_pt": round(w_pt, 1),
                "height_pt": round(h_pt, 1),
                "width_ratio_pct": width_ratio_pct,
                "has_text_overlay": has_text_overlay,
                "overlay_text": overlay_text,
                "page": page_num + 1
            }

            extracted_figures.append(fig_entry)

            manifest_key = fig_key or caption_name
            if manifest_key not in figure_manifest:
                figure_manifest[manifest_key] = fig_entry

            print(f"[Image Analyzer] Extracted '{filename}' (W={w_pt:.1f}pt, Ratio={width_ratio_pct}%, Overlay={has_text_overlay}) -> Key: {manifest_key}")

    doc.close()

    manifest_path = os.path.join(output_dir, "spatial_figure_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(figure_manifest, f, indent=2)

    print(f"\n[Image Analyzer] Saved rich spatial manifest to: {manifest_path}")
    print(f"[Image Analyzer] Total valid figures/portraits analyzed: {len(extracted_figures)}")
    return figure_manifest

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    analyze_and_extract_spatial_images(pdf_path)
