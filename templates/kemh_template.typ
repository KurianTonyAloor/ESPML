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

  body
}

// 1:1 Chapter Page 1 Opening Header
#let ncert-page-one-opening(
  unit-num: "2",
  title: "RELATIONS AND FUNCTIONS",
  quote-text: "Mathematics is the indispensable instrument of all physical research. – BERTHELOT"
) = {
  v(10pt)
  grid(
    columns: (1fr, auto),
    align: (left + horizon, right + horizon),
    [
      #rect(
        stroke: 0.5pt + rgb("#a0a0a0"),
        radius: 2pt,
        fill: rgb("#ffffff"),
        inset: (x: 8pt, y: 6pt),
        align(center)[
          #text(size: 7.5pt, weight: "bold")[QR CODE]\
          #text(size: 7pt, fill: rgb("#555555"))[11076CH02]
        ]
      )
    ],
    [
      #grid(
        columns: (auto, auto),
        gutter: 6pt,
        align: horizon,
        text(size: 16pt, weight: "medium", fill: rgb("#777777"))[Chapter],
        rect(
          fill: kemh-teal,
          radius: 2pt,
          inset: (x: 10pt, y: 8pt),
          text(size: 18pt, weight: "bold", fill: rgb("#ffffff"))[#unit-num]
        )
      )
    ]
  )

  v(16pt)

  align(center)[
    #rect(
      width: 100%,
      radius: 18pt,
      fill: rgb("#ffffff"),
      stroke: 2.5pt + rgb("#90a4ae"),
      inset: (x: 20pt, y: 10pt),
      align(center)[
        #text(size: 18pt, weight: "bold", fill: kemh-teal)[#upper(title)]
      ]
    )
  ]

  v(14pt)

  align(center)[
    #text(size: 10pt, style: "italic", weight: "bold", fill: kemh-teal)[
      ❖ #quote-text ❖
    ]
  ]

  v(16pt)
}

// Section Headings
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

// 1:1 EXERCISE SECTION MACROS
#let ncert-exercise-banner(title) = {
  v(16pt)
  align(center)[
    #rect(
      radius: 4pt,
      fill: rgb("#e1f5fe"),
      stroke: 1.5pt + kemh-teal,
      inset: (x: 22pt, y: 8pt),
      text(size: 13pt, weight: "bold", fill: kemh-teal)[#upper(title)]
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
    text(size: 10.5pt, weight: "bold", fill: kemh-teal)[#num],
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
      text(size: 10pt, weight: "bold", fill: kemh-teal)[#num],
      text(size: 10pt)[#body]
    )
  ]
}

#let ncert-solution(body) = {
  v(6pt)
  text(size: 10.5pt, weight: "bold", fill: kemh-teal)[Solution ]
  text(size: 10.5pt)[#body]
  v(6pt)
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

#let ncert-figure(img-path, caption: "", width: 95%) = {
  align(center, block(width: width, inset: (y: 6pt))[
    #image(img-path, width: 100%)
    #if caption != "" [
      #v(4pt)
      #text(size: 8.5pt, style: "italic", fill: rgb("#333333"))[#caption]
    ]
  ])
}
