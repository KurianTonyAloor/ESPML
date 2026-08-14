import os
import json
import pymupdf as fitz

def analyze_pdf_spatial_images(pdf_path: str, output_dir: str = "images_spatial"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    
    spatial_nodes = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Collect all text blocks with Y-coordinates
        text_blocks = []
        for b in page.get_text("dict")["blocks"]:
            if b.get("type") == 0:  # Text block
                block_text = "".join(
                    span["text"] for line in b["lines"] for span in line["spans"]
                ).strip()
                if block_text:
                    text_blocks.append({
                        "type": "text",
                        "bbox": b["bbox"],
                        "y0": b["bbox"][1],
                        "y1": b["bbox"][3],
                        "text": block_text[:60]
                    })
                    
        # 2. Collect all images with Y-coordinates
        image_info_list = page.get_image_info(xrefs=True)
        for img in image_info_list:
            bbox = img["bbox"]
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            
            # Ignore tiny elements or full page background graphics
            if w < 30 or h < 30 or w > 500 or h > 700:
                continue
                
            y0 = bbox[1]
            
            # Save cropped image pixmap matching exact visual rect in PDF
            pix = page.get_pixmap(clip=fitz.Rect(bbox), dpi=200)
            img_filename = f"img_p{page_num + 1}_y{int(y0)}.png"
            img_path = os.path.join(output_dir, img_filename)
            pix.save(img_path)
            
            text_blocks.append({
                "type": "image",
                "bbox": bbox,
                "y0": y0,
                "y1": bbox[3],
                "src": f"images_spatial/{img_filename}",
                "width": w,
                "height": h
            })
            
        # Sort all elements on page vertically by Y0 coordinate
        text_blocks.sort(key=lambda x: x["y0"])
        
        for item in text_blocks:
            item["page"] = page_num + 1
            spatial_nodes.append(item)
            if item["type"] == "image":
                print(f"Page {page_num + 1} Image at Y={int(item['y0'])}: {item['src']} ({int(item['width'])}x{int(item['height'])})")
                
    doc.close()
    
    with open("spatial_nodes.json", "w", encoding="utf-8") as f:
        json.dump(spatial_nodes, f, indent=2)
        
    print(f"\nSpatial layout saved. Total nodes: {len(spatial_nodes)}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    analyze_pdf_spatial_images(pdf_path)
