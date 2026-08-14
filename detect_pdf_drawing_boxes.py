import os
import json
import pymupdf as fitz

def detect_pdf_shaded_boxes(pdf_path: str, output_manifest: str = "callout_box_manifest.json"):
    doc = fitz.open(pdf_path)
    shaded_boxes = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        drawings = page.get_drawings()
        
        # Get filled rects (background shaded boxes)
        fill_rects = []
        for d in drawings:
            fill_color = d.get("fill")
            if fill_color is not None:
                r = fitz.Rect(d["rect"])
                # Filter out line rules (h < 5) or full page fills (w > 500 and h > 700)
                if r.height > 20 and r.width > 100 and not (r.width > 500 and r.height > 700):
                    fill_rects.append((r, fill_color))

        if not fill_rects:
            continue

        # Get text blocks inside these filled rects
        blocks = page.get_text("dict")["blocks"]
        for rect, color in fill_rects:
            contained_texts = []
            title_text = ""

            for b in blocks:
                if b.get("type") == 0:  # Text block
                    b_rect = fitz.Rect(b["bbox"])
                    if rect.contains(b_rect) or rect.intersects(b_rect):
                        block_text = "".join(
                            span["text"] for line in b["lines"] for span in line["spans"]
                        ).strip()
                        if block_text:
                            contained_texts.append(block_text)

            if contained_texts:
                # First line is usually the box title (e.g. Maintaining the National Standards...)
                title_text = contained_texts[0]
                body_text = "\n\n".join(contained_texts[1:]) if len(contained_texts) > 1 else contained_texts[0]

                # Determine box style by fill color (Green vs Pink vs Blue)
                # color is tuple (r, g, b)
                color_hex = f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}" if isinstance(color, (tuple, list)) and len(color) >= 3 else "#ebf5ed"

                box_entry = {
                    "page": page_num + 1,
                    "bbox": [rect.x0, rect.y0, rect.x1, rect.y1],
                    "color_hex": color_hex,
                    "title": title_text,
                    "body": body_text,
                    "full_text_prefix": contained_texts[0][:35].lower().strip()
                }
                shaded_boxes.append(box_entry)
                safe_title = title_text[:40].encode('ascii', errors='ignore').decode('ascii')
                print(f"[Shaded Box] Page {page_num + 1} ({color_hex}): Title='{safe_title}...' ({len(contained_texts)} paragraphs)")

    doc.close()

    with open(output_manifest, "w", encoding="utf-8") as f:
        json.dump(shaded_boxes, f, indent=2)

    print(f"\nSaved {len(shaded_boxes)} shaded callout boxes to {output_manifest}")
    return shaded_boxes

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    detect_pdf_shaded_boxes(pdf_path)
