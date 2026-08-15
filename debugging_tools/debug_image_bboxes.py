import pymupdf as fitz

doc = fitz.open("testing_doc/kemh102.pdf")
print("=== DEBUGGING IMAGE BOUNDING BOXES IN kemh102.pdf ===")

for p_num in range(min(3, len(doc))):
    page = doc[p_num]
    p_w = page.rect.width
    p_h = page.rect.height
    p_area = p_w * p_h
    
    img_info = page.get_image_info()
    print(f"\nPage {p_num+1} (Size: {p_w:.1f} x {p_h:.1f}, Area: {p_area:.1f}): Found {len(img_info)} images")
    
    for idx, info in enumerate(img_info):
        bbox = [round(v, 1) for v in info["bbox"]]
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        area = w * h
        coverage = area / p_area
        print(f"  Img {idx+1}: BBox={bbox}, Size=({w:.1f} x {h:.1f}), AreaRatio={coverage*100:.1f}%")

doc.close()
