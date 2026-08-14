import json

with open("callout_box_manifest.json", "r", encoding="utf-8") as f:
    boxes = json.load(f)

print(f"Total boxes: {len(boxes)}")
for b in boxes:
    bbox = b["bbox"]
    width = bbox[2] - bbox[0]
    title = b["title"][:40].replace("\n", " ")
    color = b.get("color_hex", "#000000")
    if color in ["#cbe7d3", "#f8c1d9"]:
        is_full_width = width > 350
        print(f"Page {b['page']} ({color}): Width={width:.1f}pt (Full-Width={is_full_width}) -> Title='{title}'")
