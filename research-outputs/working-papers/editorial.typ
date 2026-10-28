// Shared editorial design; scientific content stays in each manuscript.
#let editorial(title: "", short: "", issue: "01", accent: rgb("#24584d"), deck: [], abstract: [], takeaway: [], hero: "", body) = {
  set document(title: title, author: "T.S. McNamara")
  set page(paper: "a4", margin: (left: 27mm, right: 25mm, top: 23mm, bottom: 23mm),
    header: context if counter(page).get().first() > 1 [
      #set text(font: "Lato", size: 8pt, fill: accent)
      #grid(columns: (1fr, auto), [FIELDNOTES / DISCRETE DYNAMICS], [#short])
      #v(3pt)#line(length: 100%, stroke: 0.4pt + accent)
    ],
    footer: context [#set text(font: "Lato", size: 8pt, fill: rgb("#6b706d"))
      #grid(columns: (1fr, auto), [RESEARCH DRAFT · 20 OCTOBER 2026 / #issue], [#counter(page).display("01")])])
  set text(font: ("Georgia", "Libertinus Serif"), size: 10.6pt, fill: rgb("#202623"))
  set par(justify: true, leading: 0.8em, spacing: 1.05em)
  set heading(numbering: "1.1")
  show heading.where(level: 1): it => block(above: 22pt, below: 11pt)[
    #set text(font: "Lato", size: 19pt, weight: "bold", fill: accent)
    #it]
  show heading.where(level: 2): it => block(above: 16pt, below: 8pt)[
    #set text(font: "Lato", size: 12pt, weight: "bold")
    #it]
  show heading.where(level: 3): set text(font: "Lato", size: 10.5pt, weight: "bold", fill: accent)
  set math.equation(numbering: "(1)")
  set figure(gap: 9pt)
  show figure: it => block(width: 100%, breakable: false, above: 16pt, below: 16pt)[#it]
  show figure.caption: it => block(above: 3pt)[
    #line(length: 16mm, stroke: 1pt + accent)#v(4pt)
    #set text(font: "Lato", size: 8.7pt, fill: rgb("#4d5751"))
    #set par(justify: false, leading: 0.6em, spacing: 5pt)
    #it]
  set table(stroke: 0.35pt + rgb("#d4dbd5"), inset: 6pt)
  set table.cell(breakable: false)
  show table: set text(font: "Lato", size: 8.5pt)
  show raw: set text(font: "DejaVu Sans Mono", size: 0.83em)
  set list(spacing: 5pt)
  set enum(spacing: 5pt)
  [#set par(justify: false)
    #grid(columns: (1fr, auto), align: (left, right), [#text(font: "Lato", size: 9pt, weight: "bold", fill: accent, tracking: 1.5pt)[FIELDNOTES / DISCRETE DYNAMICS]], [#text(font: "Lato", size: 30pt, weight: "light", fill: accent)[#issue]])
    #v(14mm)
    #text(size: 43pt, weight: "regular")[#title]
    #v(6mm)
    #text(font: "Lato", size: 13pt, fill: rgb("#56625c"))[#deck]
    #v(7mm)
    #text(font: "Lato", size: 9pt)[T.S. McNamara / Accelerant Ltd, Wellington]
    #v(6mm)
    #line(length: 22mm, stroke: 2pt + accent)
    #v(5mm)
    #image(hero, width: 100%, height: 65mm, fit: "contain")
    #v(4mm)
    #text(font: "Lato", size: 8pt, fill: accent)[WORKING PAPER · EXISTING EVIDENCE, NEW EDITORIAL STRUCTURE]
  ]
  pagebreak()
  [#set par(justify: false)
    #text(font: "Lato", size: 9pt, weight: "bold", fill: accent, tracking: 1pt)[THE QUESTION & THE EVIDENCE]
    #v(5mm)
    #text(size: 13.5pt)[#abstract]
    #v(7mm)
    #block(width: 100%, inset: 13pt, fill: accent.lighten(93%), stroke: (left: 2pt + accent))[
      #set text(font: "Lato", size: 10pt)
      *What this paper establishes*

#takeaway
    ]
    #v(5mm)
    #text(font: "Lato", size: 8.5pt, fill: rgb("#657068"))[This draft reorganizes existing measurements. It reports no new simulations or fitted results. Companion papers share methods and some datasets; their evidence is not independent replication.]
  ]
  v(5mm)
  body
}


