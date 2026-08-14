import os
import re
import json
from difflib import SequenceMatcher
import pymupdf as fitz

def build_spatial_image_anchors(pdf_path: str, output_dir: str = "images_spatial"):
    """
    Extracts all images from PDF with exact Y-coordinates and binds each image
    to the preceding PDF text line prefix for 1:1 placement reconstruction.
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    
    anchor_map = {}  # Maps text_prefix -> list of image_paths
    extracted_images_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Collect all text blocks with Y-coordinates
        text_nodes = []
        for b in page.get_text("dict")["blocks"]:
            if b.get("type") == 0:  # Text block
                block_text = "".join(
                    span["text"] for line in b["lines"] for span in line["spans"]
                ).strip()
                if block_text:
                    text_nodes.append({
                        "y0": b["bbox"][1],
                        "y1": b["bbox"][3],
                        "text": block_text
                    })
                    
        # Sort text nodes by Y-coordinate
        text_nodes.sort(key=lambda x: x["y0"])

        # 2. Extract images on page
        image_info_list = page.get_image_info(xrefs=True)
        for img_idx, img in enumerate(image_info_list):
            bbox = img["bbox"]
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]

            # Filter out background graphics or tiny icons
            if w < 40 or h < 40 or w > 1500 or h > 1500:
                continue

            y0 = bbox[1]
            img_filename = f"img_p{page_num + 1}_y{int(y0)}_{img_idx}.png"
            img_rel_path = f"{output_dir}/{img_filename}"
            img_full_path = os.path.join(output_dir, img_filename)

            # Crop image visually
            pix = page.get_pixmap(clip=fitz.Rect(bbox), dpi=200)
            pix.save(img_full_path)
            extracted_images_count += 1

            # 3. Find preceding text node on same page
            preceding_text = ""
            for node in text_nodes:
                if node["y0"] <= y0:
                    preceding_text = node["text"]
                else:
                    break

            if not preceding_text and text_nodes:
                preceding_text = text_nodes[0]["text"]

            if preceding_text:
                prefix_key = preceding_text[:35].lower().strip()
                if prefix_key not in anchor_map:
                    anchor_map[prefix_key] = []
                anchor_map[prefix_key].append({
                    "src": img_rel_path,
                    "y0": y0,
                    "page": page_num + 1
                })

    total_pages = len(doc)
    doc.close()

    manifest_file = os.path.join(output_dir, "spatial_anchor_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(anchor_map, f, indent=2)

    print(f"[Spatial Image Manager] Extracted {extracted_images_count} images across {total_pages} pages.")
    print(f"[Spatial Image Manager] Saved anchor manifest to: {manifest_file}")
    return anchor_map

def find_anchored_images_for_text(text: str, anchor_map: dict, min_ratio: float = 0.6):
    """
    Finds any images bound to a text paragraph using fuzzy prefix matching.
    """
    if not text.strip() or not anchor_map:
        return []

    target_prefix = text[:35].lower().strip()
    
    # Direct match
    if target_prefix in anchor_map:
        return anchor_map[target_prefix]

    # Fuzzy prefix match
    best_match_key = None
    best_ratio = 0.0
    
    for key in anchor_map:
        ratio = SequenceMatcher(None, target_prefix, key).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match_key = key

    if best_match_key and best_ratio >= min_ratio:
        return anchor_map[best_match_key]

    return []

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    build_spatial_image_anchors(pdf_path)
