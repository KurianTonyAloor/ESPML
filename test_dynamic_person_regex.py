import re
import pymupdf as fitz

doc = fitz.open("kech101.pdf")
print("=== DYNAMIC SCIENTIST & CAPTION RECOGNITION TEST ===")

# Regex 1: Figure Captions (e.g. Fig. 1.1, Fig 1.2)
FIG_REGEX = re.compile(r"Fig\.\s*(\d+\.\d+)", re.I)

# Regex 2: Scientist / Person Portraits with Lifespan Years (e.g. Antoine Lavoisier (1743–1794), Joseph Proust (1754-1826))
SCIENTIST_REGEX = re.compile(r"([A-Z][a-zA-Z\.\s]{2,30}?)\s*\(\s*\d{4}\s*[–\-]\s*\d{4}\s*\)")

# Regex 3: Capitalized Person Name near image clip
PERSON_NAME_REGEX = re.compile(r"^[A-Z][a-z]+\s+[A-Z][a-z]+$")

found_figures = {}

for p_num in range(len(doc)):
    page = doc[p_num]
    text_blocks = page.get_text("dict")["blocks"]

    for b in text_blocks:
        if b.get("type") == 0:
            b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
            
            fig_match = FIG_REGEX.search(b_text)
            scientist_match = SCIENTIST_REGEX.search(b_text)

            if fig_match:
                key = f"Fig. {fig_match.group(1)}"
                found_figures[key] = {"type": "FIGURE", "caption": b_text, "page": p_num + 1}
                safe_cap = b_text[:40].encode('ascii', errors='ignore').decode('ascii')
                print(f"[Dynamic Fig] Page {p_num + 1}: Key='{key}' -> '{safe_cap}...'")
            elif scientist_match:
                person_name = scientist_match.group(1).strip()
                found_figures[person_name] = {"type": "PORTRAIT", "name": person_name, "caption": b_text, "page": p_num + 1}
                safe_cap = b_text.encode('ascii', errors='ignore').decode('ascii')
                print(f"[Dynamic Scientist] Page {p_num + 1}: Name='{person_name}' -> '{safe_cap}'")

doc.close()
print(f"\nTotal Dynamically Discovered Assets: {len(found_figures)}")
