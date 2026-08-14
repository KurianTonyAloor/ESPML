import os
import re
import json
import pymupdf as fitz

def extract_and_map_figures(pdf_path: str, output_dir: str = "images"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    
    extracted_figures = []
    figure_manifest = {}
    
    # Portrait keywords to match portraits to scientist names
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
        text_blocks = page.get_text("blocks")
        
        # 1. Collect figure captions & scientist names on this page
        page_captions = []
        page_portraits = []
        
        for b in text_blocks:
            text = b[4].strip()
            # Check figure caption
            match = re.search(r"(Fig\.\s*\d+\.\d+[^\n]*)", text, re.I)
            if match:
                caption_text = match.group(1).replace("\n", " ").strip()
                page_captions.append((b[1], caption_text))
            # Check scientist name
            for key, name in portrait_keywords.items():
                if key in text.lower():
                    page_portraits.append((b[1], name))
                
        # Sort captions by Y-coordinate
        page_captions.sort(key=lambda x: x[0])
        page_portraits.sort(key=lambda x: x[0])

        # 2. Extract image xrefs
        image_info_list = page.get_image_info(xrefs=True)
        img_idx = 0
        
        for img_info in image_info_list:
            xref = img_info.get("xref", 0)
            if not xref:
                continue
            bbox = img_info["bbox"]
            w_pt = bbox[2] - bbox[0]
            h_pt = bbox[3] - bbox[1]
            img_area = w_pt * h_pt

            # Skip full-page background graphics (covering > 80% of page area) or tiny icons (< 30pt)
            if img_area > 0.8 * page_area or w_pt < 30 or h_pt < 30:
                continue

            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            w_px, h_px = base_image["width"], base_image["height"]
            
            # Skip full-page background graphics (w_px > 1500 or h_px > 1500)
            if w_px > 1500 or h_px > 1500:
                continue
            
            img_idx += 1
            y0 = bbox[1]

            # Determine best caption or portrait label
            caption_name = f"page_{page_num + 1}_img_{img_idx}"
            matched_caption = ""
            fig_key = ""

            # Check if image is near a figure caption on this page
            if page_captions:
                # Find caption closest in Y-coordinate to image
                closest_cap = min(page_captions, key=lambda c: abs(c[0] - y0))
                matched_caption = closest_cap[1]
                fig_match = re.search(r"Fig\.\s*(\d+\.\d+)", matched_caption, re.I)
                if fig_match:
                    fig_num = fig_match.group(1).replace(".", "_")
                    fig_key = f"Fig. {fig_match.group(1)}"
                    caption_name = f"fig_{fig_num}"

            # Check if image is a scientist portrait
            if not fig_key and page_portraits:
                closest_portrait = min(page_portraits, key=lambda p: abs(p[0] - y0))
                portrait_name = closest_portrait[1].replace(" ", "_").lower()
                caption_name = f"portrait_{portrait_name}"
                fig_key = closest_portrait[1]

            filename = f"{caption_name}.{image_ext}"
            filepath = os.path.join(output_dir, filename)

            # Avoid overwriting distinct images with same key
            counter = 1
            while os.path.exists(filepath):
                filename = f"{caption_name}_{counter}.{image_ext}"
                filepath = os.path.join(output_dir, filename)
                counter += 1

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            extracted_figures.append({
                "page": page_num + 1,
                "filename": filename,
                "relative_path": f"{output_dir}/{filename}",
                "caption": matched_caption,
                "fig_key": fig_key,
                "width": w_px,
                "height": h_px
            })

            if fig_key and fig_key not in figure_manifest:
                figure_manifest[fig_key] = f"{output_dir}/{filename}"

            print(f"Extracted Figure: {filename} (Page {page_num + 1}, {w_px}x{h_px}) -> {fig_key or 'Unmapped'}")

    doc.close()

    manifest_path = os.path.join(output_dir, "figure_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(figure_manifest, f, indent=2)

    print(f"\nFigure manifest saved to: {manifest_path}")
    print(f"Total figures extracted: {len(extracted_figures)}")
    return extracted_figures

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    extract_and_map_figures(pdf_path)
