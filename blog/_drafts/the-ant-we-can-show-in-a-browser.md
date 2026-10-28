---
title: The ant we can show in a browser
description: A live trail makes the rules tangible, but the column sweeper lives far beyond its stopping point.
author: Turmite researchers
status: Project note
tags: [visualisation, finite-time, communication]
---

The homepage now runs three ants. It is a useful way to explain the rule:
the ant turns, changes the cell, and moves. Watching the trail develop makes
the dependence on earlier visits much easier to see than a paragraph does.

But the most interesting RLRLLL behaviour we want to show happens after
billions of steps. The homepage stops at 100,000. Its live RLRLLL portrait
therefore cannot show the column sweeper described immediately below it.
That gap deserves a visible label. Without one, putting the animation beside
the finding could imply that the reader is watching the evidence for it.

The [sweeper record](../../experiments/archive/2026-10-g1-ribbon-breakout/README.md)
contains the long trajectory's archived extracts and provenance. The live
portrait is a short run from a blank grid, checked against an independent
stepping loop and the existing web simulator. Those checks establish its
dynamics on the tested cases; they cannot make its short time horizon stand
in for the archived experiment.

A possible next addition is an explicitly labelled replay of the saved
late-time trajectory alongside the blank-start simulation. That would let
readers compare the two modes without silently skipping billions of steps.
For now, the distinction is stated in the caption. No new research
measurement was made for the homepage.
