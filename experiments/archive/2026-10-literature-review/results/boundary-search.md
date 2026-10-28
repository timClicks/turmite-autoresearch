# Boundary search log

Date: 2026-10-15 NZDT. Scope: literature-review plan section3. No date/domain filters. Queries below are exact; results screened by observables and model, not exponent alone. Search snippets used only for discovery. All substantive external claims in boundary.md use original-paper full text except the explicitly inaccessible Family–Vicsek item.

## Requested service and fallback

1. Requested connector `mcp__codex_apps__search_service_web_run`, batch queries: `Kapri Dhar 0906.5506 interface width`; `Family Vicsek 1985 scaling active zone Eden 18 L75`; `Ramasco Lopez Rodriguez generic dynamic scaling kinetic roughening 2000`. Returned empty content, `isError:true`.
2. Same connector, single query `Kapri Dhar 0906.5506 interface width`. Same error. Switched to built-in `web__run`; did not continue retrying unavailable service.

## Fallback sequence

3. Open arxiv HTML and PDF 0906.5506; search `Ramasco Lopez Rodriguez generic dynamic scaling kinetic roughening 2000` and `Family Vicsek scaling active zone Eden 1985 L75`. Included KD (immediate comparator), Ramasco (distinguishes measured exponents), FV (original scaling provenance). Excluded search-result reviews/theses as technical evidence.
4. Open KD HTML SecIII, abstract/version record, Ramasco arxiv PDF, discovered electronicsandbooks FV scan and APS KPZ abstract. FV scan failed; remaining accesses succeeded. KD current v2, 17 Sep2009; Ramasco v1,10 Jan2000.
5. Open Ramasco PDF at line30, KD abstract/history and PDF at line420; try APS KPZ PDF and FV DOI. Both latter failed. KD Eq10/Fig8 verified including body/caption uncertainty disagreement. Reference18 of KD is Halpin-Healy/Zhang1995 review; used it only as a trail toward original KPZ.
6. Backward/original-source queries: `"Dynamic Scaling of Growing Interfaces" pdf Kardar 1986`; `"Family" "Vicsek" "L75" pdf emory`. Forward-comparator query: `"Kapri" "Dhar" boundary roughness Eulerian KPZ`. Open Ramasco PDF line120. Discovered UCSD scan of original KPZ; publisher full text not needed after scan. Found published KD mirror but did not resolve discrepancy through publisher.
7. Open original KPZ UCSD scan, author-hosted Ramasco published PDF. Query `rotor router cluster boundary roughness KPZ Papoyan Povolotsky` and `"Scaling of the active zone" "pdf" Family Vicsek`. Included Papoyan/Poghosyan/Priezzhev2016 cylinder because it independently varies lateral size and measures saturation. Excluded Priezzhev arxiv1612.03701 aggregation as different process; loop-reversibility1501.02580 and spiral1512.00280 are mechanism trails assigned elsewhere, not closer boundary measurements. FV search yielded no accessible authoritative full text.
8. Open arxiv1606.01756 abstract and PDF plus KPZ scan line40. Cylinder v2,15 Jul2016, DOI10.1088/1742-5468/2016/07/073209,17pp. KPZ original PRL scan4pp (889–892), DOI10.1103/PhysRevLett.56.889.
9. Find cylinder PDF `width`, `0.5`, `10000`: first exposes relevant SecI/IV, latter literal strings not found due PDF extraction. Read SecIV pp10–11 Eq4.1–4.6 directly in extracted text. Explicit sample/circumference/time definitions recorded. Stop after this forward round: closer boundary paper found and included; no exhaustive citation-network claim.

## Local evidence inspected

`notes/literature-review-plan-2026-10-15.md`; current main.typ boundary passages and refs.bib; hull-width README including band-power correction; width-radius-refit README/JSON; notes/hull-checks.md and hull-checks README/status; shape.rs and hull_width.rs centring definitions. No shared notes/manuscript edits. No new measurements or dependency changes.

Access/verification limits: FV original not full-text verified; APS KPZ PDF failed but original-paper university-hosted scan succeeded; arxiv KD metadata has a journal-article-number typo, so DOI and repository bibliography identify051118. Extracted technical claims refer to PDF pages/sections/equations, not search snippets. Numeric uncertainty semantics (fit error vs between-seed sd) must not be treated as identical across papers and local work.
