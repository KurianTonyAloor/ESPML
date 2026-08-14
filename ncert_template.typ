// ==============================================================================
// NCERT MASTER TYPST TEMPLATE (1:1 High-Fidelity Reproduction)
// ==============================================================================

// Design System Color Palette
#let ncert-blue = rgb("#1a5fb4")
#let ncert-dark-blue = rgb("#0d3875")
#let ncert-header-blue = rgb("#1b4f9c")
#let ncert-pink-bg = rgb("#f9ebf0")
#let ncert-pink-border = rgb("#d8829d")
#let ncert-green-bg = rgb("#ebf5ed")
#let ncert-green-border = rgb("#5ca374")
#let ncert-green-header = rgb("#1e6b37")
#let ncert-gray-text = rgb("#4a4a4a")

// Document Page & Layout Setup
#let ncert-document(
  chapter-num: "1",
  chapter-title: "",
  body
) = {
  set page(
    paper: "a4",
    margin: (top: 2.2cm, bottom: 2.2cm, left: 1.8cm, right: 1.8cm),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        if calc.even(page-num) {
          text(size: 9pt, fill: ncert-gray-text, font: "Liberation Sans")[
            #page-num #h(1fr) *CHEMISTRY*
          ]
        } else {
          text(size: 9pt, fill: ncert-gray-text, font: "Liberation Sans")[
            *SOME BASIC CONCEPTS OF CHEMISTRY* #h(1fr) #page-num
          ]
        }
      }
    },
    footer: align(center, text(size: 8pt, fill: rgb("#777777"))[Reprint 2026-27])
  )

  set text(
    font: ("Times New Roman", "Nimbus Roman", "Liberation Serif", "DejaVu Serif"),
    size: 10pt,
    fill: rgb("#111111")
  )

  set par(
    justify: true,
    leading: 0.65em,
    first-line-indent: 0pt
  )

  body
}

// Chapter 1 Page 1 Opening Layout (1:1 NCERT Reproduction)
#let ncert-page-one-opening(
  unit-num: "1",
  title: "SOME BASIC CONCEPTS OF CHEMISTRY",
  objectives: (
    "appreciate the contribution of India in the development of chemistry;",
    "understand the role of chemistry in different spheres of life;",
    "explain the characteristics of three states of matter;",
    "classify different substances into elements, compounds and mixtures;",
    "use scientific notations and determine significant figures;",
    "differentiate between precision and accuracy;",
    "define SI base units and convert physical quantities from one system of units to another;",
    "explain various laws of chemical combination;",
    "appreciate significance of atomic mass, average atomic mass, molecular mass and formula mass;",
    "describe the terms – mole and molar mass;",
    "calculate the mass per cent of component elements constituting a compound;",
    "determine empirical formula and molecular formula for a compound from the given experimental data;"
  ),
  quote-text: "Chemistry is the science of molecules and their transformations. It is the science not so much of the one hundred elements but of the infinite variety of molecules that may be built from them.",
  quote-author: "Roald Hoffmann"
) = {
  // Top Banner: UNIT 1 & QR Code Box
  grid(
    columns: (1fr, auto),
    align: (left + horizon, right + horizon),
    [
      #v(6pt)
      #text(size: 13pt, weight: "bold", fill: rgb("#c02626"))[UNIT #unit-num]
    ],
    [
      #rect(
        stroke: 0.5pt + rgb("#a0a0a0"),
        radius: 2pt,
        fill: rgb("#fafafa"),
        inset: (x: 8pt, y: 4pt),
        align(center)[
          #text(size: 7.5pt, weight: "bold", fill: rgb("#444444"))[QR CODE\ 11082CH01]
        ]
      )
    ]
  )
  v(6pt)

  // Chapter Title across 100% width
  text(size: 20pt, weight: "bold", fill: ncert-header-blue, hyphenate: false)[#title]
  v(4pt)
  line(length: 100%, stroke: 1.5pt + ncert-header-blue)
  v(10pt)

  // 2-Column Opening: Full Left Column Objectives | Right Column Quote + Intro Text
  columns(2, gutter: 16pt)[
    // LEFT COLUMN: Full Height Objectives Box
    #rect(
      width: 100%,
      fill: rgb("#f3f8fd"),
      stroke: (left: 3pt + rgb("#3399cc"), rest: 0.4pt + rgb("#d0e2f2")),
      inset: (x: 8pt, y: 8pt),
      radius: (right: 2pt),
      [
        #text(size: 12pt, weight: "bold", fill: ncert-header-blue)[Objectives]
        #v(3pt)
        #text(size: 8pt, style: "italic", fill: rgb("#008080"))[After studying this unit, you will be able to]
        #v(4pt)
        #list(
          marker: text(fill: rgb("#008080"), size: 7pt)[•],
          body-indent: 4pt,
          spacing: 6.5pt,
          ..objectives.map(item => text(size: 7.8pt, fill: rgb("#004080"))[#item])
        )
      ]
    )

    #colbreak()

    // RIGHT COLUMN: Roald Hoffmann Quote + Opening Paragraphs
    #rect(
      width: 100%,
      fill: rgb("#ffffff"),
      stroke: none,
      inset: (x: 0pt, y: 0pt),
      [
        #text(size: 20pt, fill: rgb("#3399cc"), weight: "bold")[“]
        #h(-4pt)
        #text(size: 9.5pt, style: "italic", weight: "bold", fill: rgb("#222222"))[#quote-text]
        #v(3pt)
        #align(right)[
          #text(size: 9.5pt, style: "italic", weight: "bold", fill: ncert-header-blue)[#quote-author]
        ]
      ]
    )
    #v(8pt)

    Science can be viewed as a continuing human effort to systematise knowledge for describing and understanding nature. You have learnt in your previous classes that we come across diverse substances present in nature and changes in them in daily life. Curd formation from milk, formation of vinegar from sugarcane juice on keeping for prolonged time and rusting of iron are some of the examples of changes which we come across many times. For the sake of convenience, science is sub-divided into various disciplines: chemistry, physics, biology, geology, etc. The branch of science that studies the preparation, properties, structure and reactions of material substances is called chemistry.

    #v(6pt)
    #text(size: 10pt, weight: "bold", fill: ncert-header-blue)[DEVELOPMENT OF CHEMISTRY]
    #v(4pt)

    Chemistry, as we understand it today, is not a very old discipline. Chemistry was not studied for its own sake, rather it came up as a result of search for two interesting things:

    i. #text(style: "italic")[Philosopher’s stone (Paras)] which would convert all baser metals e.g., iron and copper into gold.

    ii. #text(style: "italic")[‘Elixir of life’] which would grant immortality.

    People in ancient India, already had the knowledge of many scientific phenomenon much before the advent of modern science. They applied that knowledge in various walks of life. Chemistry developed mainly in the form of Alchemy and Iatrochemistry during 1300-1600 CE. Modern chemistry took shape in the 18th century Europe, after a few centuries of alchemical traditions which were introduced in Europe by the Arabs.
  ]
  v(12pt)
}

// Section & Subsection Headings
#let ncert-h1(title) = {
  v(14pt)
  text(size: 11pt, weight: "bold", fill: ncert-header-blue)[#upper(title)]
  v(4pt)
}

#let ncert-h2(title) = {
  v(10pt)
  text(size: 10.5pt, weight: "bold", fill: ncert-header-blue)[#title]
  v(3pt)
}

#let ncert-h3(title) = {
  v(8pt)
  text(size: 10pt, weight: "bold", fill: rgb("#c00000"))[#title]
  v(2pt)
}

// NCERT Problem / Example Box (Pink Theme)
#let ncert-problem-box(title: "Problem", problem-body, solution-body: "") = {
  v(8pt)
  rect(
    width: 100%,
    stroke: 1pt + ncert-pink-border,
    fill: ncert-pink-bg,
    inset: 10pt,
    radius: 3pt,
    [
      #text(weight: "bold", fill: rgb("#990033"), size: 10pt)[#title]
      #v(4pt)
      #text(size: 9.5pt)[#problem-body]
      #if solution-body != "" [
        #v(6pt)
        #text(weight: "bold", fill: rgb("#990033"), size: 9.5pt)[Solution:]
        #v(2pt)
        #text(size: 9.5pt)[#solution-body]
      ]
    ]
  )
  v(8pt)
}

// NCERT Reference / Standards Callout Box (Single Column Width)
#let ncert-green-box(title: "", body) = {
  v(8pt)
  rect(
    width: 100%,
    stroke: 1.2pt + ncert-green-border,
    fill: ncert-green-bg,
    inset: 10pt,
    radius: 3pt,
    [
      #align(center, text(weight: "bold", fill: ncert-green-header, size: 10pt)[#title])
      #v(4pt)
      #text(size: 9pt)[#body]
    ]
  )
  v(8pt)
}

// NCERT Full-Width Callout Box Component (Spans across both columns)
#let ncert-full-width-box(title: "", body) = {
  v(10pt)
  rect(
    width: 100%,
    stroke: 1.2pt + ncert-green-border,
    fill: ncert-green-bg,
    inset: 12pt,
    radius: 3pt,
    [
      #align(center, text(weight: "bold", fill: ncert-green-header, size: 11pt)[#title])
      #v(6pt)
      #text(size: 9.5pt)[#body]
    ]
  )
  v(10pt)
}
#let ncert_full_width_box = ncert-full-width-box

// NCERT Summary Banner & Box
#let ncert-summary-box(body) = {
  v(14pt)
  align(center, rect(
    fill: ncert-green-header,
    radius: 3pt,
    inset: (x: 20pt, y: 5pt),
    text(weight: "bold", fill: white, size: 11pt)[SUMMARY]
  ))
  v(4pt)
  rect(
    width: 100%,
    fill: ncert-green-bg,
    stroke: 1pt + ncert-green-border,
    inset: 12pt,
    radius: 3pt,
    text(size: 9.5pt)[#body]
  )
  v(14pt)
}

// NCERT Table Component (Matching NCERT Header Blue & Warm Background Fills)
#let ncert-table(caption: "", headers: (), rows: (), width: 100%) = {
  v(8pt)
  align(center, block(width: width)[
    #if caption != "" [
      #align(center, text(weight: "bold", fill: ncert-header-blue, size: 9pt)[#caption])
      #v(4pt)
    ]
    #table(
      columns: headers.len(),
      fill: (x, y) => if y == 0 { rgb("#e0deef") } else if calc.even(y) { rgb("#ffe4b8") } else { rgb("#ffffff") },
      stroke: (x, y) => if y == 0 { 1.2pt + ncert-header-blue } else { 0.5pt + rgb("#cccccc") },
      align: center + horizon,
      table.header(..headers.map(h => text(weight: "bold", size: 8.5pt, fill: ncert-header-blue)[#h])),
      ..rows.map(r => if type(r) == array {
        r.map(cell => text(size: 8pt)[#cell])
      } else {
        (text(size: 8pt)[#r],)
      }).flatten()
    )
  ])
  v(8pt)
}
#let ncert_table = ncert-table

// NCERT Figure Component
#let ncert-figure(img-path, caption: "", width: 95%) = {
  align(center, block(width: width, inset: (y: 6pt))[
    #image(img-path, width: 100%)
    #if caption != "" [
      #v(4pt)
      #text(size: 8.5pt, style: "italic", fill: rgb("#333333"))[#caption]
    ]
  ])
}
#let ncert_figure = ncert-figure
#let ncert_box = ncert-green-box

// NCERT Exercises Header & Item
#let ncert-exercises-header() = {
  v(14pt)
  align(center, rect(
    fill: ncert-header-blue,
    radius: 3pt,
    inset: (x: 25pt, y: 5pt),
    text(weight: "bold", fill: white, size: 11pt)[EXERCISES]
  ))
  v(8pt)
}
