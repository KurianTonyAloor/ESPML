import fitz

doc = fitz.open("test_automated_master_template.pdf")
print(f"Total Pages in test_automated_master_template.pdf: {len(doc)}")

for p in range(len(doc)):
    pix = doc[p].get_pixmap(dpi=150)
    out_png = f"test_template_page_{p+1}.png"
    pix.save(out_png)
    print(f"Saved {out_png} (Width={pix.width}, Height={pix.height})")

doc.close()
