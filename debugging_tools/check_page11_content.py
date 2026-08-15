import fitz

doc = fitz.open("reconstructed_chapter_1.pdf")
for p in [9, 10, 11]:
    text = doc[p].get_text()
    safe_text = text[:300].encode('ascii', errors='ignore').decode('ascii')
    print(f"=== PAGE {p + 1} ===")
    print(safe_text)
    print("...")
doc.close()
