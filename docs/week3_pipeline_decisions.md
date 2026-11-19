# Week 3 Pipeline Decisions

## 1. Requirements served
FR1 and FR2 (slot rules and sharing footnotes in the manuals' spec tables), FR4 (usable lanes from the AMD pages), FR5 and RAI1 (every record keeps its document and page, or spec field), FR7 and RAI3 (each source records its revision and CPU coverage), RAI4 (comparison metrics reported per manual), RAI5 (no extracted text published) and NFR5 (re-runnable, fingerprinted pipeline).

## 2. Selected sources
Pathway A (PDF/TXT) only, on all nine real sources: three board manuals (S01–S03) and six AMD spec pages (S04–S09). No synthetic data. Details are in `week3_data_inventory.md`.

## 3. Part B comparison
All four methods ran on the same cleaned text of the three manuals. A probe is a known slot row plus its footnote, both already cited in Week 2. It passes when one chunk contains both terms and carries the right page.

| Method | Chunks | Records with a page | Chunks ending mid-line | Slot pages kept whole | Probes (terms + page) |
|---|---|---|---|---|---|
| Handout fixed-500 | 270 | 0% | 240 | 0/16 | 0/8 |
| Handout paragraph-500 | 278 | 0% | 236 | 0/16 | 0/8 |
| Page-aware 500/75 | 360 | 100% | 0 | 3/16 | 8/8 |
| Page-aware 1,500/150 | 170 | 100% | 0 | 13/16 | 8/8 |

The handout chunkers merge all pages into one string, so no record can carry a page, and FR5 fails before retrieval even starts. Their probe terms still land in the same chunk 7/8 times, but only by chance. The paragraph chunker gives almost the same output as the fixed one because pypdf produces very few blank-line paragraphs (S01: 1, S03: 4; S02 has 56, but only after cleaning).

Both page-aware settings pass all eight probes. 1,500 was chosen because it keeps 13 of 16 slot-table pages whole against 3 of 16, which is what NFR2 needs (the deciding row and its footnote in one chunk). The size limit comes from the embedding model, not from the probes: at 1,500 cleaned characters the longest chunk is 509 bge-small tokens, under the 512-token limit, while 2,000 produces chunks over 512. This assumes a 512-token embedding model; the actual model is a Topic 5 decision.

Per-manual figures are in the notebook, Cell 5A1 (part 3).

## 4. Chosen configuration
- Extraction: pypdf 7.1.0. The ASUS PDF is RC4-encrypted and opens with an empty password.
- Page ranges: MSI 5–57, Gigabyte 4–36, ASUS 4–66. Contents pages (dot leaders) and the legal, warranty and contact pages are excluded.
- Cleaning: collapse spaces and tabs, drop tokens containing □ (6,138 on Gigabyte), drop control characters (90 on Gigabyte), collapse runs of four or more dots.
- Chunking: whole lines packed into chunks of at most 1,500 characters with 150 characters of overlap. A chunk never crosses a page. Pages with fewer than 40 letters are skipped and logged (MSI 16, 17; ASUS 12, 36, 38, 66).
- AMD pages: one record per spec field (`dt`/`dd` pair), tagged with its spec section.
- Record IDs carry the locator: `S01-p018-c01` (source, page, chunk), `S08-f039` (source, field).

## 5. Accepted limitations
- A table row and its footnote can still land in different chunks. The Gigabyte p. 26 probe fails at every chunk size and is reported as a known gap, not asserted. Row-plus-footnote units (ADR 2) remain the target design.
- Chunk size is counted in characters, not tokens.
- Diagram-only pages are skipped. Diagram labels on kept pages remain as noise.
- AMD pages have no revision number, and re-saving a page changes its hash even if the specs are the same.
- The ASUS manual covers Ryzen 7000 only. This is a source limit, not a pipeline one, and RAI3 handles it at answer time.

## 6. ETL or ELT
ETL. The corpus is nine static documents, and what the next stage needs is clean, page-tagged chunks, not raw PDFs. Raw files stay local, so re-transforming with new settings is still possible.

## 7. Batch or streaming
Batch. Vendors replace a manual every few months at most. The trigger for a re-run is a change in a manual's file size or date in `data/sources.md`. One output file per source means a new manual adds a file without changing the others' outputs or hashes (NFR5).

## 8. Stage contracts

| Stage | Contract / evidence | Failure response |
|---|---|---|
| Ingest | All nine registry sources exist; manual byte sizes match `sources.md` (Cell 3) | Stop. A size change means the vendor replaced the file: re-check the gold-set pages first |
| Inspect | Each PDF opens and reports page count, characters per page, □ and control-character counts; each AMD page has spec fields with 0 empty values (Cell A3) | Stop if unreadable; flag near-empty pages |
| Prepare | Every record has a page or spec field; no chunk over 1,500 characters or across a page; eight probes pass (5A1, B3) | Stop the export and log the failing page |
| Validate | Nine non-empty output files with SHA-256 fingerprints; record checks PASS (B3) | Stop for missing or empty output |
| Record lineage | Each source maps to exactly one output in both manifests; 6B and Cell 9 PASS; Part C byte-identical to Part B | Stop and report the missing mapping |

## 9. Output location and access caveat

| Artefact | Location | In the repository? |
|---|---|---|
| Raw sources | `data/raw/manuals/`, `data/raw/amd/` | No |
| Part B outputs | `data/processed/prepared_text_S01–S09.jsonl` | No |
| Part C outputs | `data/pipeline_v1/documents/prepared_text_S01–S09.jsonl` | No |
| Lineage | `data/week3_manifest.json`, `data/pipeline_v1/documents/pipeline_manifest.json` | Yes |
| Source list | `data/sources.md` | Yes |

The raw files and every `.jsonl` stay on my own machine. All nine sources restrict reproduction: Gigabyte forbids reproducing the manual "in any form" without written permission, MSI reserves all rights, the ASUS PDF disallows copying (`copy:no`), and AMD's site terms allow personal, non-public use only. A public GitHub repository counts as publication, and the prepared files are extracted text, so committing them would republish the documents (RAI5).

What the repository holds instead is enough to rebuild the outputs. `sources.md` gives every URL, file size and date, and the manifests record the SHA-256 of every raw and prepared file. Anyone can download the manuals, run the notebook and compare hashes to confirm they got the same outputs. The AMD pages are the exception: they have no revision number and re-saving one changes its hash, so for those six only the spec values can be checked, not the files.

This follows the handout's rule for restricted data (Topic 3, C4b): commit the non-sensitive evidence and document where the data is stored.

*AI use: drafted with help from Claude (Anthropic). Figures were checked against the executed notebook and both manifests by Claude and then independently by me, on 19 Nov 2026.*
