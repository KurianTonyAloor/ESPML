import os
import json
import pymupdf as fitz

def inspect_page5_graphics(pdf_path: str):
    doc = fitz.open(pdf_path)
    page_num = 4  # Page 5 is index 4
    page = doc[page_num]

    print(f"=== INSPECTING PAGE 5 ({page.rect}) ===")
    
    # 1. Inspect raster images
    img_info_list = page.get_image_info()
    print(f"\n[Raster Images] Found {len(img_info_list)} images on Page 5:")
    for idx, info in enumerate(img_info_list):
        bbox = info["bbox"]
        print(f"  Img {idx+1}: bbox={bbox}, width={bbox[2]-bbox[0]:.1f}, height={bbox[3]-bbox[1]:.1f}")

    # 2. Inspect drawings / vector graphics
    drawings = page.get_drawings()
    print(f"\n[Vector Drawings] Found {len(drawings)} drawing paths on Page 5.")

    # 3. Search for Fig. 1.2 text / caption on Page 5
    text_dict = page.get_text("dict")
    print(f"\n[Text Blocks] Text blocks on Page 5 containing 'Fig' or 'Classification':")
    for b in text_dict["blocks"]:
        if b.get("type") == 0:
            b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
            if "Fig" in b_text or "Classification" in b_text or "1.2" in b_text:
                print(f"  Text block: bbox={b['bbox']} -> '{b_text}'")

    doc.close()

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    inspect_page5_graphics(pdf_path)
