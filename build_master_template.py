import os
import json
import pymupdf as fitz

def rgb_to_hex(color_tuple):
    if not color_tuple:
        return "#000000"
    r = int(color_tuple[0] * 255)
    g = int(color_tuple[1] * 255)
    b = int(color_tuple[2] * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_automated_master_template(pdf_path: str, output_typst_file: str = "generated_ncert_template.typ"):
    doc = fitz.open(pdf_path)
    
    font_sizes = []
    text_colors = []
    fill_colors = []

    # 1. Scan pages to harvest design tokens
    for page in doc[:5]:  # Analyze first 5 pages for brand tokens
        text_dict = page.get_text("dict")
        for b in text_dict["blocks"]:
            if b.get("type") == 0:
                for line in b["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(round(span["size"], 1))
                        if "color" in span:
                            # Convert sRGB int color to (r,g,b)
                            c_int = span["color"]
                            r = ((c_int >> 16) & 255) / 255.0
                            g = ((c_int >> 8) & 255) / 255.0
                            b_val = (c_int & 255) / 255.0
                            text_colors.append(rgb_to_hex((r, g, b_val)))

        # Extract vector drawing fills
        for d in page.get_drawings():
            if d.get("fill"):
                fill_colors.append(rgb_to_hex(d["fill"]))

    doc.close()

    # 2. Extract Brand Tokens
    primary_color = "#1b4f9c"  # NCERT Header Blue
    for c in text_colors:
        if c.startswith("#1b") or c.startswith("#1a") or c.startswith("#0c"):
            primary_color = c
            break

    green_bg = "#ebf5ed"
    green_border = "#5ca374"
    for c in fill_colors:
        if c.startswith("#eb") or c.startswith("#cb") or c.startswith("#d") or c.startswith("#e"):
            green_bg = c
            break

    # 3. Synthesize Master Typst Template
    template_code = f"""// ==============================================================================
// AUTOMATED MASTER TYPST TEMPLATE (Generated dynamically from {os.path.basename(pdf_path)})
// ==============================================================================

// Brand Color Palette
#let brand-primary = rgb("{primary_color}")
#let brand-callout-bg = rgb("{green_bg}")
#let brand-callout-border = rgb("{green_border}")
#let brand-problem-bg = rgb("#f9ebf0")
#let brand-problem-border = rgb("#d8829d")
#let brand-table-header = rgb("#e0deef")
#let brand-table-row-even = rgb("#ffe4b8")

// Document Layout Setup
#let ncert-document(
  chapter-num: "1",
  chapter-title: "",
  body
) = {{
  set page(
    paper: "a4",
    margin: (top: 2.2cm, bottom: 2.2cm, left: 1.8cm, right: 1.8cm),
    header: context {{
      let page-num = counter(page).get().first()
      if page-num > 1 {{
        if calc.even(page-num) {{
          text(size: 9pt, fill: rgb("#4a4a4a"))[#page-num #h(1fr) *CHEMISTRY*]
        }} else {{
          text(size: 9pt, fill: rgb("#4a4a4a"))[*SOME BASIC CONCEPTS OF CHEMISTRY* #h(1fr) #page-num]
        }}
      }}
    }},
    footer: align(center, text(size: 8pt, fill: rgb("#777777"))[Reprint 2026-27])
  )

  set text(
    font: ("Times New Roman", "Liberation Serif", "DejaVu Serif"),
    size: 10pt,
    fill: rgb("#111111")
  )

  set par(
    justify: true,
    leading: 0.65em,
    first-line-indent: 0pt
  )

  columns(2, gutter: 15pt)[
    #body
  ]
}}

// Dynamic Section Headings
#let ncert-h1(title) = {{
  v(14pt)
  text(size: 11pt, weight: "bold", fill: brand-primary)[#upper(title)]
  v(6pt)
}}

#let ncert-h2(title) = {{
  v(10pt)
  text(size: 10pt, weight: "bold", fill: brand-primary)[#upper(title)]
  v(4pt)
}}

// Dynamic Callout Box Component
#let ncert-green-box(title: "", body) = {{
  v(10pt)
  rect(
    width: 100%,
    fill: brand-callout-bg,
    stroke: 1pt + brand-callout-border,
    inset: 10pt,
    radius: 3pt,
    [
      #if title != "" [
        #text(size: 10pt, weight: "bold", fill: brand-primary)[#title]
        #v(4pt)
      ]
      #text(size: 9.5pt)[#body]
    ]
  )
  v(10pt)
}}

#let ncert-full-width-box(title: "", body) = {{
  ncert-green-box(title: title, body)
}}

// Dynamic Problem Box Component
#let ncert-problem-box(title: "", body) = {{
  v(10pt)
  rect(
    width: 100%,
    fill: brand-problem-bg,
    stroke: 1pt + brand-problem-border,
    inset: 10pt,
    radius: 3pt,
    [
      #if title != "" [
        #text(size: 10pt, weight: "bold", fill: rgb("#990033"))[#title]
        #v(4pt)
      ]
      #text(size: 9.5pt)[#body]
    ]
  )
  v(10pt)
}}

// Dynamic Table Component
#let ncert-table(caption: "", headers: (), rows: (), width: 100%) = {{
  v(8pt)
  align(center, block(width: width)[
    #if caption != "" [
      #align(center, text(weight: "bold", fill: brand-primary, size: 9pt)[#caption])
      #v(4pt)
    ]
    #table(
      columns: headers.len(),
      fill: (x, y) => if y == 0 {{ brand-table-header }} else if calc.even(y) {{ brand-table-row-even }} else {{ rgb("#ffffff") }},
      stroke: (x, y) => if y == 0 {{ 1.2pt + brand-primary }} else {{ 0.5pt + rgb("#cccccc") }},
      align: center + horizon,
      table.header(..headers.map(h => text(weight: "bold", size: 8.5pt, fill: brand-primary)[#h])),
      ..rows.map(r => if type(r) == array {{
        r.map(cell => text(size: 8pt)[#cell])
      }} else {{
        (text(size: 8pt)[#r],)
      }}).flatten()
    )
  ])
  v(8pt)
}}

// Dynamic Figure Component
#let ncert-figure(img-path, caption: "", width: 95%) = {{
  align(center, block(width: width, inset: (y: 6pt))[
    #image(img-path, width: 100%)
    #if caption != "" [
      #v(4pt)
      #text(size: 8.5pt, style: "italic", fill: rgb("#333333"))[#caption]
    ]
  ])
}}
"""

    with open(output_typst_file, "w", encoding="utf-8") as f:
        f.write(template_code)

    print(f"Automated Master Template generated: {output_typst_file}")
    return output_typst_file

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    generate_automated_master_template(pdf_path)
