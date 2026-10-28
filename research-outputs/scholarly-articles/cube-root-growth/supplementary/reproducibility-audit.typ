#set document(title: "Supplementary material: Reproducibility & Preregistration Audit", author: "T.S. McNamara")
#let ink = rgb("#20201e")
#let accent = ink
#let muted = rgb("#696963")
#let sans = "Lato"
#let panel = rgb("#f7f8f6")
#let hairline = rgb("#d9dedb")
#set page(
  paper: "a4",
  margin: (left: 24mm, right: 24mm, top: 23mm, bottom: 23mm),
  header: context if counter(page).get().first() > 1 [
    #set text(font: sans, size: 8pt, fill: muted)
    #grid(columns: (1fr, auto), [GENERALISED LANGTON’S ANTS], [T.S. McNamara])
  ],
  footer: context [
    #set text(font: sans, size: 8pt, fill: muted)
    #align(right, counter(page).display("1"))
  ],
)
#set text(font: "Libertinus Serif", size: 11.25pt, fill: ink)
// Paragraph spacing must exceed leading: Typst combines these gaps by maximum.
#set par(justify: true, leading: 0.68em, spacing: 1.3em, first-line-indent: 0pt)
// Use @label for numbered references and link(<label>)[text] for named paragraphs.
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => block(above: 24pt, below: 12pt)[
  #set text(font: sans, size: 17pt, weight: "bold", fill: ink)
  #it
]
#show heading.where(level: 2): it => block(above: 18pt, below: 9pt)[
  #set text(font: sans, size: 11.5pt, weight: "bold", fill: ink)
  #it
]
#show heading.where(level: 3): set text(font: sans, size: 10.5pt, fill: accent)
#set figure(gap: 10pt)
// One panel keeps the illustration and its explanation visually associated.
#show figure: it => block(
  width: 100%, breakable: false, above: 18pt, below: 18pt,
  fill: panel, stroke: 0.45pt + hairline, radius: 3pt, inset: 11pt,
)[#it]
#show figure.caption: it => block[
  #set text(font: sans, size: 9pt, fill: ink)
  #set par(justify: false, leading: 0.55em, spacing: 6pt)
  #align(left, it)
]
#set list(spacing: 5pt)
#set enum(spacing: 5pt)
#set table(stroke: 0.4pt + rgb("#d4dfe3"), inset: 7pt)
#set table.cell(breakable: false)
#show table: set text(font: sans, size: 9pt)
#show raw: set text(font: "DejaVu Sans Mono", size: 0.85em)
#set math.equation(numbering: "(1)")


#set heading(numbering: none)
Companion to *Cube-root growth of most non-highway generalised Langton's ants of length up to 12*.

Audit numbers match the references in the main paper.

#include "../audit.typ"
