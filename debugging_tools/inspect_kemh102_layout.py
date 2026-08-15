import pymupdf as fitz
import numpy as np

doc = fitz.open("testing_doc/kemh102.pdf")
print(f"=== DIAGNOSTIC INSPECTION OF testing_doc/kemh102.pdf (Pages: {len(doc)}) ===")

for p_num in range(min(4, len(doc))):
    page = doc[p_num]
    print(f"\n--- Page {p_num + 1} (Size: {page.rect.width:.1f} x {page.rect.height:.1f}) ---")
    
    # Text Blocks
    blocks = page.get_text("dict")["blocks"]
    for b in blocks[:8]:
        if b.get("type") == 0:
            b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
            spans = [span for line in b["lines"] for span in line["spans"]]
            sizes = [round(s["size"], 1) for s in spans]
            fonts = list(set(s["font"] for s in spans))
            colors = list(set(s.get("color", 0) for s in spans))
            print(f"  [Text] BBox={[round(v,1) for v in b['bbox']]} Sizes={sizes} Colors={colors} -> '{b_text[:60]}...'")

    # Vector Fill Drawings
    drawings = page.get_drawings()
    fills = [d["fill"] for d in drawings if d.get("fill")]
    print(f"  [Drawings] Found {len(drawings)} vector paths, {len(fills)} colored fills.")
    if fills:
        unique_fills = list(set(fills[:10]))
        print(f"  [Sample Fills] {unique_fills}")

doc.close()
