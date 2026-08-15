import pymupdf as fitz

doc = fitz.open("testing_doc/kemh102.pdf")
print("=== INSPECTING VECTOR DRAWINGS (VENN DIAGRAMS & MATH GRAPHS) ===")

for p_num in range(min(5, len(doc))):
    page = doc[p_num]
    drawings = page.get_drawings()
    print(f"\nPage {p_num+1}: Found {len(drawings)} vector drawing paths")
    
    # Cluster vector paths by bounding box proximity
    clusters = []
    for d in drawings:
        r = d["rect"]
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        # Filter vector lines/shapes that form diagrams (e.g. circles, curves, arrows)
        if w > 15 and h > 15 and w < 380 and h < 400:
            clusters.append(r)
            
    print(f"  -> Identified {len(clusters)} diagram-like vector shape bounding boxes")
    for idx, rect in enumerate(clusters[:5]):
        print(f"     Cluster {idx+1}: BBox=[{rect.x0:.1f}, {rect.y0:.1f}, {rect.x1:.1f}, {rect.y1:.1f}], Size=({rect.width:.1f} x {rect.height:.1f})")

doc.close()
