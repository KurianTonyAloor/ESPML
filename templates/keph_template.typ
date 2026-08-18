// ==============================================================================
// MASTER TYPST TEMPLATE FOR PHYSICS (Automated Subject Generator)
// ==============================================================================

#let brand-primary = rgb("#800000")
#let brand-callout-bg = rgb("#e0f7fa")
#let brand-callout-border = rgb("#0097a7")
#let brand-problem-bg = rgb("#fff3e0")
#let brand-problem-border = rgb("#ff9800")
#let brand-table-header = rgb("#ffe0b2")
#let brand-table-row-even = rgb("#fff8e1")

#let ncert-document(
  chapter-num: "1",
  chapter-title: "",
  body
) = {
  set page(
    paper: "a4",
    margin: (top: 2.2cm, bottom: 2.2cm, left: 2.2cm, right: 2.2cm),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        if calc.even(page-num) {
          text(size: 8.5pt, fill: rgb("#4a4a4a"))[#page-num #h(1fr) *PHYSICS*]
        } else {
          text(size: 8.5pt, fill: rgb("#4a4a4a"))[*#upper(chapter-title)* #h(1fr) #page-num]
        }
      }
    },
    footer: align(center, text(size: 8pt, fill: rgb("#777777"))[Reprint 2026-27])
  )

  set text(
    font: ("Times New Roman", "Liberation Serif", "DejaVu Serif"),
    size: 10.5pt,
    fill: rgb("#131212")
  )

  set par(
    justify: true,
    leading: 0.68em,
    first-line-indent: 0pt
  )

  body
}


#let ncert-page-one-opening(
  unit-num: "1",
  title: "",
  quote-text: ""
) = {
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
}


// Section Headings
#let ncert-h1(title) = {
  v(14pt)
  text(size: 11.5pt, weight: "bold", fill: brand-primary)[#title]
  v(6pt)
}

#let ncert-h2(title) = {
  v(10pt)
  text(size: 10.5pt, weight: "bold", fill: brand-primary)[#title]
  v(4pt)
}

// 1:1 PLUGABLE EXERCISE SECTION MACROS
#let ncert-exercise-banner(title) = {
  v(16pt)
  align(center)[
    #rect(
      radius: 4pt,
      fill: rgb("#e1f5fe"),
      stroke: 1.5pt + brand-primary,
      inset: (x: 22pt, y: 8pt),
      text(size: 13pt, weight: "bold", fill: brand-primary)[#upper(title)]
    )
  ]
  v(12pt)
}

#let ncert-exercise-item(num, body) = {
  v(8pt)
  grid(
    columns: (24pt, 1fr),
    gutter: 4pt,
    align: (left + top, left + top),
    text(size: 10.5pt, weight: "bold", fill: brand-primary)[#num],
    text(size: 10.5pt)[#body]
  )
}

#let ncert-sub-item(num, body) = {
  v(4pt)
  pad(left: 24pt)[
    grid(
      columns: (26pt, 1fr),
      gutter: 4pt,
      align: (left + top, left + top),
      text(size: 10pt, weight: "bold", fill: brand-primary)[#num],
      text(size: 10pt)[#body]
    )
  ]
}

#let ncert-solution(body) = {
  v(6pt)
  text(size: 10.5pt, weight: "bold", fill: brand-primary)[Solution ]
  text(size: 10.5pt)[#body]
  v(6pt)
}

// Callout & Problem Boxes
#let ncert-green-box(title: "", body) = {
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
      #text(size: 10pt)[#body]
    ]
  )
  v(10pt)
}

#let ncert-problem-box(title: "", body) = {
  v(10pt)
  rect(
    width: 100%,
    fill: brand-problem-bg,
    stroke: (left: 2.5pt + brand-primary, rest: 0.5pt + rgb("#dddddd")),
    inset: 10pt,
    radius: (right: 3pt),
    [
      #if title != "" [
        #text(size: 10pt, weight: "bold", fill: brand-primary)[#title]
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
      #align(center, text(weight: "bold", fill: brand-primary, size: 9pt)[#caption])
      #v(4pt)
    ]
    #table(
      columns: headers.len(),
      fill: (x, y) => if y == 0 { brand-table-header } else if calc.even(y) { brand-table-row-even } else { rgb("#ffffff") },
      stroke: (x, y) => if y == 0 { 1.2pt + brand-primary } else { 0.5pt + rgb("#cccccc") },
      align: center + horizon,
      table.header(..headers.map(h => text(weight: "bold", size: 8.5pt, fill: brand-primary)[#h])),
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
