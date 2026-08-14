import fitz

doc = fitz.open("reconstructed_chapter_1.pdf")

pages_to_render = [8, 11, 14]
for page_num in pages_to_render:
    if page_num <= len(doc):
        page = doc[page_num - 1]
        pix = page.get_pixmap(dpi=150)
        output_png = f"page_{page_num}_preview.png"
        pix.save(output_png)
        print(f"Saved {output_png} (Width={pix.width}, Height={pix.height})")

doc.close()
