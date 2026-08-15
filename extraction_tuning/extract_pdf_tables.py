import os
import json
import pymupdf as fitz

def extract_all_pdf_tables(pdf_path: str, output_manifest: str = "table_manifest.json"):
    doc = fitz.open(pdf_path)
    tables_list = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        tabs = page.find_tables()

        for t_idx, tab in enumerate(tabs):
            bbox = tab.bbox  # (x0, y0, x1, y1)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            # Extract header and rows content
            df_rows = tab.extract()
            if not df_rows or len(df_rows) == 0:
                continue

            # Look for preceding text line on page for table caption (e.g. Table 1.1, Table 1.4)
            caption = ""
            text_instances = page.get_text("dict")["blocks"]
            for b in text_instances:
                if b.get("type") == 0:
                    b_rect = fitz.Rect(b["bbox"])
                    # Check if text block sits right above the table (within 30 points)
                    if b_rect.y1 <= bbox[1] and bbox[1] - b_rect.y1 < 45:
                        b_text = "".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
                        if "Table" in b_text or "table" in b_text:
                            caption = b_text
                            break

            table_entry = {
                "page": page_num + 1,
                "table_id": f"table_p{page_num + 1}_{t_idx + 1}",
                "bbox": [bbox[0], bbox[1], bbox[2], bbox[3]],
                "width": round(width, 1),
                "height": round(height, 1),
                "is_full_width": width > 350,
                "caption": caption,
                "rows": df_rows,
                "first_cell_text": df_rows[0][0] if df_rows and len(df_rows[0]) > 0 else ""
            }
            tables_list.append(table_entry)
            first_cell = df_rows[0][0] if (df_rows and len(df_rows[0]) > 0 and df_rows[0][0] is not None) else ""
            safe_caption = caption[:60].encode('ascii', errors='ignore').decode('ascii')
            safe_first = str(first_cell)[:40].encode('ascii', errors='ignore').decode('ascii')
            print(f"[Table Extracted] Page {page_num + 1}: {len(df_rows)} rows x {len(df_rows[0])} cols | Caption='{safe_caption}' | First cell='{safe_first}'")

    doc.close()

    with open(output_manifest, "w", encoding="utf-8") as f:
        json.dump(tables_list, f, indent=2)

    print(f"\nSaved {len(tables_list)} extracted tables to {output_manifest}")
    return tables_list

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    extract_all_pdf_tables(pdf_path)
