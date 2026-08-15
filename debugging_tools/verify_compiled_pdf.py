import fitz

doc = fitz.open("reconstructed_chapter_1.pdf")
print(f"Total Pages in reconstructed_chapter_1.pdf: {len(doc)}")

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    images = page.get_images()
    tables = page.find_tables()

    print(f"\n--- Page {page_num + 1} ---")
    print(f"Images count: {len(images)}")
    if "Isotope" in text or "Relative Abundance" in text:
        print(" [MATCH] Found Isotope text/table on this page!")
    if "Table 1.4" in text:
        print(" [MATCH] Found Table 1.4 on this page!")
    if "Fig. 1.10" in text or "Packing of Na+" in text:
        print(" [MATCH] Found Fig 1.10 on this page!")
    if "Balancing a chemical equation" in text:
        print(" [MATCH] Found Balancing a chemical equation box on this page!")

doc.close()
