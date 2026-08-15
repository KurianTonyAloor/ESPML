import os
import json
import pymupdf as fitz
import joblib

# Subject Brand Token Definitions
SUBJECT_TOKENS = {
    "MATHEMATICS": {
        "prefix": "kemh",
        "primary_color": "#2e3092",      # Deep Navy/Purple Blue
        "callout_bg": "#f0f2fb",         # Soft Blue Tint
        "callout_border": "#5c6bc0",     # Indigo Border
        "problem_bg": "#eef2f8",         # Soft Slate
        "problem_border": "#3f51b5",
        "table_header": "#d1c4e9",       # Soft Purple Header
        "table_row_even": "#f3e5f5"
    },
    "CHEMISTRY": {
        "prefix": "kech",
        "primary_color": "#1b4f9c",      # NCERT Header Blue
        "callout_bg": "#ebf5ed",         # Green Note BG
        "callout_border": "#5ca374",     # Green Border
        "problem_bg": "#f9ebf0",         # Pink Problem BG
        "problem_border": "#d8829d",     # Pink Border
        "table_header": "#e0deef",       # Lavender Header
        "table_row_even": "#ffe4b8"       # Warm Beige Row Fill
    },
    "PHYSICS": {
        "prefix": "keph",
        "primary_color": "#800000",      # Deep Burgundy Red
        "callout_bg": "#e0f7fa",         # Light Cyan Note BG
        "callout_border": "#0097a7",     # Cyan Border
        "problem_bg": "#fff3e0",         # Warm Orange Example BG
        "problem_border": "#ff9800",
        "table_header": "#ffe0b2",       # Light Orange Header
        "table_row_even": "#fff8e1"
    },
    "BIOLOGY": {
        "prefix": "kebo",
        "primary_color": "#1e6b37",      # Forest Green
        "callout_bg": "#f1f8e9",         # Light Lime BG
        "callout_border": "#7cb342",     # Lime Border
        "problem_bg": "#f3e5f5",         # Soft Violet BG
        "problem_border": "#ab47bc",
        "table_header": "#c8e6c9",       # Soft Mint Header
        "table_row_even": "#e8f5e9"
    }
}

def generate_subject_master_template(subject_name: str, tokens: dict, output_file: str):
    """
    Generates a dedicated, subject-tailored Master Typst Template.
    """
    template_code = f"""// ==============================================================================
// MASTER TYPST TEMPLATE FOR {subject_name.upper()} (Automated Subject Generator)
// ==============================================================================

#let brand-primary = rgb("{tokens['primary_color']}")
#let brand-callout-bg = rgb("{tokens['callout_bg']}")
#let brand-callout-border = rgb("{tokens['callout_border']}")
#let brand-problem-bg = rgb("{tokens['problem_bg']}")
#let brand-problem-border = rgb("{tokens['problem_border']}")
#let brand-table-header = rgb("{tokens['table_header']}")
#let brand-table-row-even = rgb("{tokens['table_row_even']}")

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
          text(size: 9pt, fill: rgb("#4a4a4a"))[#page-num #h(1fr) *{subject_name.upper()}*]
        }} else {{
          text(size: 9pt, fill: rgb("#4a4a4a"))[*#upper(chapter-title)* #h(1fr) #page-num]
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

  body
}}

#let ncert-page-one-opening(
  unit-num: "1",
  title: ""
) = {{
  grid(
    columns: (1fr, auto),
    align: (left + horizon, right + horizon),
    [
      #v(6pt)
      #text(size: 13pt, weight: "bold", fill: brand-primary)[UNIT #unit-num]
    ],
    [
      #rect(
        stroke: 0.5pt + rgb("#a0a0a0"),
        radius: 2pt,
        fill: rgb("#fafafa"),
        inset: (x: 8pt, y: 4pt),
        align(center)[#text(size: 7.5pt, weight: "bold")[QR CODE]]
      )
    ]
  )
  v(6pt)
  text(size: 20pt, weight: "bold", fill: brand-primary, hyphenate: false)[#title]
  v(4pt)
  line(length: 100%, stroke: 1.5pt + brand-primary)
  v(10pt)
}}

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
        #text(size: 10pt, weight: "bold", fill: brand-primary)[#title]
        #v(4pt)
      ]
      #text(size: 9.5pt)[#body]
    ]
  )
  v(10pt)
}}

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
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(template_code)
    print(f"[Generated Master Template] {subject_name.upper()} -> {output_file}")

def build_all_subject_templates(base_dir: str = "."):
    """
    Generates dedicated master templates for Mathematics, Chemistry, Physics, and Biology.
    """
    print("=== BUILDING SUBJECT-SPECIFIC MASTER TYPST TEMPLATES ===")
    
    generated_templates = {}
    for subj_name, tokens in SUBJECT_TOKENS.items():
        out_filename = f"{tokens['prefix']}_template.typ"
        out_path = os.path.join(base_dir, out_filename)
        generate_subject_master_template(subj_name, tokens, out_path)
        generated_templates[tokens['prefix']] = out_path

    return generated_templates

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    build_all_subject_templates(BASE_DIR)
