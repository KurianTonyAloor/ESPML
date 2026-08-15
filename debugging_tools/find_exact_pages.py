import fitz

doc = fitz.open("reconstructed_chapter_1.pdf")
print("=== SEARCHING EXACT PAGES IN reconstructed_chapter_1.pdf ===")

for p_num in range(len(doc)):
    text = doc[p_num].get_text()
    if "Table 1.4" in text:
        print(f"Table 1.4 -> Page {p_num + 1}")
    if "Isotope" in text or "Relative Abundance" in text:
        print(f"Isotope Table -> Page {p_num + 1}")
    if "Fig. 1.10" in text or "Packing of Na+" in text:
        print(f"Fig 1.10 -> Page {p_num + 1}")
    if "Balancing a chemical equation" in text:
        print(f"Balancing Callout Box -> Page {p_num + 1}")

doc.close()
