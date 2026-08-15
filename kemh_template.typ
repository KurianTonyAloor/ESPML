// ==============================================================================
// 1:1 EXACT NCERT MATHEMATICS MASTER TYPST TEMPLATE (kemh_template.typ)
// ==============================================================================

#let kemh-teal = rgb("#00adef")          // Primary Math Accent Teal (#00adef)
#let kemh-def-bg = rgb("#c6eafb")        // Light Cyan Shaded Definition Box (#c6eafb)
#let kemh-def-border = rgb("#0097a7")    // Dark Teal Border
#let kemh-text-color = rgb("#131212")

#let ncert-document(
  chapter-num: "2",
  chapter-title: "RELATIONS AND FUNCTIONS",
  body
) = {
  set page(
    paper: "a4",
    margin: (top: 2.2cm, bottom: 2.2cm, left: 2.2cm, right: 2.2cm),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        if calc.even(page-num) {
          text(size: 8.5pt, fill: rgb("#4a4a4a"))[#page-num #h(1fr) *MATHEMATICS*]
        } else {
          text(size: 8.5pt, fill: rgb("#4a4a4a"))[*RELATIONS AND FUNCTIONS* #h(1fr) #page-num]
        }
      }
    },
    footer: align(center, text(size: 8pt, fill: rgb("#777777"))[Reprint 2026-27])
  )

  set text(
    font: ("Times New Roman", "Liberation Serif", "DejaVu Serif"),
    size: 10.5pt,
    fill: kemh-text-color
  )

  set par(
    justify: true,
    leading: 0.68em,
    first-line-indent: 0pt
  )

  // Single Wide Column Layout (NCERT Math Original)
  body
}

// Chapter Page 1 Opening Layout (NCERT Math)
#let ncert-page-one-opening(
  unit-num: "2",
  title: "RELATIONS AND FUNCTIONS",
  quote-text: "Mathematics is the indispensable instrument of all physical research.",
  quote-author: "BERTHELOT"
) = {
  grid(
    columns: (1fr, auto),
    align: (left + horizon, right + horizon),
    [
      #v(4pt)
      #text(size: 13pt, weight: "bold", fill: rgb("#c02626"))[Chapter #unit-num]
    ],
    [
      #rect(
        stroke: 0.5pt + rgb("#a0a0a0"),
        radius: 2pt,
        fill: rgb("#fafafa"),
        inset: (x: 8pt, y: 4pt),
        align(center)[#text(size: 7.5pt, weight: "bold")[QR CODE\ 11082CH02]]
      )
    ]
  )
  v(6pt)
  text(size: 22pt, weight: "bold", fill: kemh-teal, hyphenate: false)[#title]
  v(4pt)
  line(length: 100%, stroke: 1.8pt + kemh-teal)
  v(12pt)

  // Opening Quote Box
  align(center)[
    #block(width: 85%, inset: 8pt)[
      #text(size: 10pt, style: "italic", weight: "medium", fill: rgb("#222222"))["#quote-text"]
      #v(2pt)
      #align(right)[#text(size: 9pt, weight: "bold", fill: kemh-teal)[— #quote-author]]
    ]
  ]
  v(10pt)
}

// Math Section Headings
#let ncert-h1(title) = {
  v(14pt)
  text(size: 11.5pt, weight: "bold", fill: kemh-teal)[#title]
  v(6pt)
}

#let ncert-h2(title) = {
  v(10pt)
  text(size: 10.5pt, weight: "bold", fill: kemh-teal)[#title]
  v(4pt)
}

// Math Definition / Theorem Box
#let ncert-green-box(title: "", body) = {
  v(10pt)
  rect(
    width: 100%,
    fill: kemh-def-bg,
    stroke: 1pt + kemh-def-border,
    inset: 10pt,
    radius: 3pt,
    [
      #if title != "" [
        #text(size: 10pt, weight: "bold", fill: kemh-teal)[#title]
        #v(4pt)
      ]
      #text(size: 10pt)[#body]
    ]
  )
  v(10pt)
}

#let ncert-full-width-box(title: "", body) = {
  ncert-green-box(title: title, body)
}

#let ncert-problem-box(title: "", body) = {
  v(10pt)
  rect(
    width: 100%,
    fill: rgb("#f5f5f5"),
    stroke: (left: 2.5pt + kemh-teal, rest: 0.5pt + rgb("#dddddd")),
    inset: 10pt,
    radius: (right: 3pt),
    [
      #if title != "" [
        #text(size: 10pt, weight: "bold", fill: kemh-teal)[#title]
        #v(4pt)
      ]
      #text(size: 10pt)[#body]
    ]
  )
  v(10pt)
}

#let ncert-table(caption: "", headers: (), rows: (), width: 100%) = {
  v(8pt)
  align(center, block(width: width)[
    #if caption != "" [
      #align(center, text(weight: "bold", fill: kemh-teal, size: 9pt)[#caption])
      #v(4pt)
    ]
    #table(
      columns: headers.len(),
      fill: (x, y) => if y == 0 { rgb("#d1c4e9") } else if calc.even(y) { rgb("#f3e5f5") } else { rgb("#ffffff") },
      stroke: (x, y) => if y == 0 { 1.2pt + kemh-teal } else { 0.5pt + rgb("#cccccc") },
      align: center + horizon,
      table.header(..headers.map(h => text(weight: "bold", size: 8.5pt, fill: kemh-teal)[#h])),
      ..rows.map(r => if type(r) == array {
        r.map(cell => text(size: 8pt)[#cell])
      } else {
        (text(size: 8pt)[#r],)
      }).flatten()
    )
  ])
  v(8pt)
}

#let ncert-figure(img-path, caption: "", width: 95%) = {
  align(center, block(width: width, inset: (y: 6pt))[
    #image(img-path, width: 100%)
    #if caption != "" [
      #v(4pt)
      #text(size: 8.5pt, style: "italic", fill: rgb("#333333"))[#caption]
    ]
  ])
}
