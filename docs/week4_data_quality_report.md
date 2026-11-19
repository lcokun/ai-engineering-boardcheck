# Week 4 Data Quality and Bias Report

## 1. Project and Data Overview

| Field | Response |
|---|---|
| Project | BoardCheck answers slot and lane questions about three AM5 B650 motherboards for DIY PC builders, citing the manual page for every claim. AI task: retrieval-grounded question answering. |
| Two Topic 2 requirements | FR5 (cite the document and page, or AMD spec field, for every claim): every record needs a title, a revision and a correct page or field. NFR2 (the evidence must include the deciding footnote or table row): the row and its footnote must sit in the same record. |
| Pathway and data type | Pathway A (PDF/TXT): 3 PDF board manuals (S01–S03) and 6 AMD HTML spec pages (S04–S09). |
| Audited output and manifest | Topic 3 Part B: `data/processed/prepared_text_S01.jsonl` … `S09.jsonl`, traced through `data/week3_manifest.json`. The Part C outputs in `data/pipeline_v1/documents/` are byte-identical (Cell 9), so the findings cover both. |
| Source and access status | Sources, versions and rights as in `docs/week3_data_inventory.md`. All nine are copyrighted, so raw and prepared files stay on my machine. The repository holds `data/sources.md` and the manifests. |
| Population and sample | 551 records: 170 manual chunks (unit: up to 1,500 characters from one PDF page) and 381 AMD spec fields (unit: one field). V1, V2, duplicate and coverage checks run on every record. The five-dimension review uses 20 records: 12 picked on purpose and 8 manual chunks drawn at random (seed 4). The purposive 12 are Week 2's slot-table pages, the Gigabyte p. 26 known gap, the most □-heavy unsampled page (Gigabyte p. 23), the ASUS layout diagram (p. 10), and the codename and lane fields for the 8700G and 8500G. |
| Limitations | The purposive half over-represents known problem pages. Only 4 of 381 AMD fields were sampled, all chosen on purpose. Accuracy was checked on 5 of the 20 records against rendered page images. |
| Evidence | `evaluation/week4_quality_checks.py`, output in `docs/evidence/week4_checks.txt` |

Checkpoint A1: if a deciding footnote went missing, FR1 would fail silently. For example, MSI p. 19 notes that M2_2 is unavailable with Ryzen 8500/8300 processors. Without that note, BoardCheck would tell an 8500G owner that M2_2 works, and they could buy an SSD that won't run in that slot.

## 2. Five-Dimension Quality Scorecard

| Dimension | Finding | Evidence | Impact on the task | Decision |
|---|---|---|---|---|
| Completeness | Observed: all 551 records carry source metadata and a locator. Every slot-table page cited in Week 2 is present. Six low-text pages (<40 letters) were skipped: MSI 16–17 (layout diagrams) and ASUS 12, 36, 38, 66. | Reused Topic 3 check, 551/551; skipped pages logged in `week3_manifest.json` | Physical slot positions shown only in the skipped diagrams can't be answered from text. FR1–3 answers come from spec tables, which are complete. | Pass |
| Consistency | Observed: records and the Week 2 gold set cite PDF pages, but the printed page numbers differ. MSI PDF = printed + 2. ASUS uses four numbering segments (roman, then chapter-page; e.g. PDF p. 26 = printed "1-14"). Gigabyte matches. | V1 on 143 pages (section 3) | A user who looks up an MSI or ASUS citation using the printed numbers lands on the wrong page (FR5, RAI1). | Warning |
| Accuracy | Observed: in 5 sampled chunks checked against rendered page images, every fact matched. The two slot-table pages (S01-p018, S02-p009) are clean. Three connector or layout pages have diagram-label noise, and S02-p023 has the wrong reading order (warnings placed before their section). | Manual check of S01-p018-c01, S02-p009-c01, S03-p010-c01, S02-p023-c01 and S01-p047-c01; p. 23 order confirmed by eye | Noise dilutes retrieval on layout pages. Wrong reading order can separate a caution from the header it belongs to. The 15 unchecked sample records are N.V. for accuracy. | Warning |
| Timeliness | Observed: the ASUS manual (E20268, Sept 2022) covers Ryzen 7000 only; 0 of 68 ASUS chunks mention Ryzen 8000 or 9000. The MSI and Gigabyte manuals (Dec 2024) cover all three generations. Manual byte sizes matched `sources.md` at ingest on 17 Nov 2026. AMD pages were saved 16 Nov 2026 and have no revision number. | Coverage check (section 4); Cell 3 size check; inventory | ASUS questions about Ryzen 8000/9000 can't be answered. That's expected and handled by FR7/RAI3, with 8 coverage-gap gold questions. Whether a vendor has replaced a file since 17 Nov is N.V. | Warning |
| Uniqueness | Observed: 0 exact duplicate texts across 551 records. The intentional 150-character overlap repeats 1.3% (MSI), 3.5% (Gigabyte) and 2.0% (ASUS) of manual text. 20 AMD field values are identical on all six CPU pages, and 62 on two to five pages. Inferred risk: for a shared value, retrieval may return another CPU's record, so the answer would be right but the citation would name the wrong CPU page. | Uniqueness check (section 4) | Possible FR5 citation mismatch on AMD fields. Each record's text starts with the CPU name, which should keep this low, but that's untested until retrieval exists (Topic 7). | Pass |

## 3. Validation Findings

| Rule | Risk / requirement | Condition and scope | Result | Failure example | Action and justification |
|---|---|---|---|---|---|
| V1 | Wrong-page citations (FR5, RAI1) | For each kept manual page, the printed label in the first two lines parses, and PDF page minus label equals the most common offset for that label's numbering segment in that manual. All 143 kept pages. | 143 pass, 0 fail, 0 N.V. | None | A fail would be a hard fail: a page off its segment's offset means the page index is wrong, so every citation from that page is wrong. No action needed on the data. The mapping becomes a requirement (section 7). |
| V2 | Row separated from its footnote (NFR2) | In each manual chunk, every footnote level used as a reference (`*`, `**`, `(Note)`) also appears as a footnote body, and the reverse. All 170 manual chunks; 29 links found. | 16 pass, 2 fail, 11 reviewed (all exceptions) | Fail: S02-p026-c01 holds the `(Note)` reference in the M2B_CPU cell, and S02-p026-c02 holds the note body | Fail: keep with warning. Removing the chunk would lose the row too; the fix is row-plus-note units (ADR 2) before NFR2 is scored. Exceptions: keep. |

Mappings found by V1:

| Manual | Pages | PDF page = printed page + |
|---|---|---|
| MSI (S01) | 51 | 2 |
| Gigabyte (S02) | 33 | 0 |
| ASUS (S03) | 59 | roman 0 · chapter 1: 12 · chapter 2: 36 · chapter 3: 60 |

The 11 V2 review cases were classified from rendered page images, and three were confirmed by eye in the PDF (Gigabyte pp. 10, 14 and 23):

- Gigabyte, 9 cases on 8 pages (pp. 6, 8, 9, 10, 11, 13, 14, 26): positional notes placed directly under the line they qualify, with no marker in that line, or page-wide disclaimers. Gigabyte does not use reference markers for these.
- ASUS p. 57, 2 cases: the tables that p. 56's `*` and `**` point to ("Refer to the tables on the next page"). Chunks never cross pages.

Rule limits: V1 compares each page with its segment's most common offset, so it catches isolated wrong pages but not a whole segment shifted together. The accuracy check covers part of that gap (S01-p018 shows "16" on PDF p. 18 in the rendered image). V2 only sees marker-based footnotes, so Gigabyte's positional notes are invisible to it (section 5).

## 4. Duplicate, Anomaly and Coverage Findings

Duplicates: 0 exact duplicate texts across 551 records. The repeats that exist are intentional: the 150-character overlap (1.3–3.5% of manual text) and AMD fields shared across CPUs (20 identical on all six pages). The overlap is kept so a line cut at a chunk boundary still appears whole in one chunk.

Anomalies:

- Shortest chunks (72–84 characters: S01-p014-c01, S01-p015-c01, S03-p042-c01, S03-p049-c01, S03-p059-c01) are installation-step pages holding a heading, a video link or illustration step numbers. Valid, kept.
- The lowest letter ratios (0.46–0.56, e.g. S02-p021-c02) are pin-definition tables and layout pages: valid content that is mostly numbers and labels. Kept.
- Diagram-label noise on layout pages (S03-p010, S03-p014) and wrong reading order on Gigabyte connector pages (S02-p023) are warnings, carried into section 7.

Coverage:

| In-scope category | Expected evidence | Observed evidence / gap | Possible downstream effect |
|---|---|---|---|
| CPU generations per manual (Ryzen 7000, 8000 incl. Phoenix 1/2, 9000) | Each manual's slot rules for each generation | Chunks mentioning 9000 / 8000 / 7000, out of 55 / 47 / 68 chunks: MSI 1 / 2 / 1, Gigabyte 2 / 2 / 2, ASUS 0 / 0 / 3 | ASUS cannot answer 8000/9000 questions; the system must refuse and name revision E20268 (FR7, RAI3). Counts are small because spec tables sit on 1–2 pages per manual, so a mention count does not measure depth of coverage. |
| Lane-sharing rules per manual | Explicit sharing statements for FR2 | MSI 4 chunks (pp. 18, 19, 31, 36), ASUS 4 (pp. 6 ×2, 10, 22), Gigabyte 0. The raw Gigabyte text has no sharing rule on any of its 41 pages. | FR2 questions on Gigabyte can only be answered as "the manual states no sharing rule". A source gap, not pipeline loss. |

Limits: both coverage counts are keyword matches. A mention does not prove a complete rule, and phrasing the patterns miss would be under-counted.

## 5. Bias Assessment

Main risk: measurement and pipeline-induced skew against the Gigabyte manual.

| Step | Evidence |
|---|---|
| Source and preparation decision | Gigabyte attaches notes by position: a `*` line directly under the item it qualifies, with no marker in the item. MSI and ASUS pair a marker with a footnote. The pipeline packs whole lines into chunks of up to 1,500 characters and has no notion of "this note belongs to the line above". |
| Data skew | Gigabyte pages are the densest (median 1,579 characters per page against 556 for MSI and 718 for ASUS), so more Gigabyte pages are split across chunks, giving more boundaries where a note can be cut off from its item. Slot-table pages kept whole: Gigabyte 3/5, MSI 6/6, ASUS 4/5. The one known row/note split (p. 26) is Gigabyte, and the reading-order and diagram-noise problems also concentrate on Gigabyte connector pages. V2 cannot see positional notes, so the quality check itself measures Gigabyte less well than the other two manuals. |
| Potential effect | Lower NFR2 evidence recall for Gigabyte questions, and so a per-manual gap under RAI4: Gigabyte owners would get more answers missing the deciding note. Because the check is weaker for Gigabyte, the gap could go unnoticed until gold-set scoring. |
| Proposed control | (1) Row-plus-note units (ADR 2), with a Gigabyte rule that attaches each `*` line to the item above it. (2) A positional V2 variant for Gigabyte: every note line must share a chunk with the line above it. (3) Report NFR2 and NFR1 per manual, as RAI4 already requires, so the gap shows up. |

This is a potential risk, not proven unfairness. No retrieval or answers exist yet, so per-manual answer quality cannot be measured until the RAG prototype (Topic 7) is evaluated (Topic 8).

Secondary risk: historical bias in the ASUS source. The only ASUS edition is from 2022 and covers Ryzen 7000 only, so ASUS owners with newer CPUs will get coverage notices instead of answers. That is correct behaviour under RAI3, but the per-manual answer rate will be lower for ASUS for reasons outside the system, so RAI4 reporting should separate those refusals from wrong answers.

Checked and ruled out: □ stripping. On Gigabyte pp. 23–30 it removed 936 tokens. The letters inside them were fragments of the repeated board-location graphic labels (`F_□U□□□□□□`, `□B_□□□`), and prepared letters equal raw letters minus exactly those fragments. No prose was lost.

## 6. Privacy, Rights and Governance

| Question | Finding |
|---|---|
| Provenance and version | Source IDs S01–S09 with URLs, revisions, file dates and sizes in `data/sources.md`. SHA-256 for every raw and prepared file in `data/week3_manifest.json`; Part C run in `data/pipeline_v1/documents/pipeline_manifest.json`; pypdf 7.1.0 recorded. AMD pages have no revision, only the 16 Nov 2026 save date. |
| Rights and permissions | All nine are copyrighted. Gigabyte forbids reproduction without written permission, MSI reserves all rights, the ASUS PDF disallows copying (`copy:no`), and AMD allows personal, non-public use. No written permission was obtained for using the text in a coursework prototype: N.V. Sharing restriction: no redistribution. |
| Privacy and sensitive data | No personal data: the sources are product manuals and spec pages, and no user data exists at this stage. Later, user questions could contain personal details, so later logging should store questions without identities. |
| Consent or collection basis | Not applicable: no data about people. The basis is publicly downloadable vendor documents, used under their own terms. |
| Ongoing maintenance | Owner: me. Re-validation triggers: a manual's size or date changing in `sources.md` (vendor replaced the file), a new ASUS edition covering Ryzen 8000/9000, or an AMD spec change. Re-validation means re-running the notebook and `evaluation/week4_quality_checks.py`, then re-checking the gold-set pages. |

Safeguards in place: `.gitignore` excludes the raw files and every `.jsonl`; notebook previews are capped at 25 words; answers quote only short excerpts (RAI5).

Required action: the Topic 3 `.gitignore` rules have to re-include the two manifests without letting any `.jsonl` through. Before pushing, check that `git status` lists no `.jsonl`, `.pdf` or `.html` files.

## 7. Mitigation and Impact on Requirements

Two priority improvements:

| # | Improvement | Who | When | Requirements protected |
|---|---|---|---|---|
| 1 | Row-plus-note units (ADR 2): attach each footnote or positional `*` note to its row, then add the positional V2 check for Gigabyte. Re-run V2 and the p. 26 known-gap probe, which should then pass. | Me | Topic 7, before building the index; before any NFR2 scoring in Topic 8 | NFR2 (evidence recall ≥ 90%), RAI4 (per-manual gap ≤ 15 pp), NFR1 |
| 2 | Printed page numbers in citations: add a `printed_page` field to every manual record from the V1 mapping, and show citations as "PDF p. 18 (printed p. 16)". Label the Week 2 gold set's pages explicitly as PDF pages. | Me | Topic 7, before citations reach users; gold-set labels before Topic 8 scoring | FR5, RAI1 (a citation the user can actually find) |

Lower-priority follow-ups: filter runs of diagram-label lines on layout pages (retrieval noise), and re-check the AMD pages and manual sizes before the gold-set run.

Impact on Topic 2 requirements and evaluation:

| Requirement | Affected by | Effect if unresolved |
|---|---|---|
| FR5, RAI1 | PDF vs printed page mismatch (MSI, ASUS) | Citations are correct but hard for users to find |
| NFR2 | p. 26 split; Gigabyte positional notes | Evidence recall below the 90% threshold on Gigabyte questions |
| RAI4 | Gigabyte skew; ASUS coverage refusals | Per-manual gap could exceed 15 pp for reasons unrelated to the model |
| FR2 | No Gigabyte sharing rule in the source | Gigabyte FR2 answers can only say "the manual states no rule" (already reflected in the Week 2 gold set) |
| FR7, RAI3 | ASUS covers Ryzen 7000 only | Expected; handled by the coverage notice |

Residual risks after both improvements: accuracy is N.V. for the 15 unchecked sample records and every record outside the sample; the AMD shared-field citation mismatch stays untested until retrieval exists; reading-order errors on connector pages remain; rights for prototype use stay N.V.; the coverage counts are keyword-based.

## 8. Quality-Gate Decision

Decision: GO WITH CONDITIONS. Scope: the Topic 3 Part B prepared text (551 records, pipeline `week3-v1`), for building and testing the Topic 7 RAG prototype. Gold-set scoring of NFR2 and RAI4 is not covered until conditions C1 and C2 are met.

Evidence:

1. Every record can be traced. 551/551 records carry source metadata and a locator, and V1 confirms all 143 page assignments.
2. The content needed for FR1–3 survived preparation. All facts matched in the 5 accuracy checks, including both slot-table pages; the 8 regression probes pass; □ stripping lost no prose.
3. No blocking rights or privacy issue: there is no personal data, and copyrighted files stay local under the handout's restricted-data rule.

Conditions (owner: me; C1 to C3 in Topic 7, C4 before the Topic 8 gold-set run):

- C1. Row-plus-note units are in place, and V2 plus the p. 26 probe pass, before NFR2 is scored.
- C2. Records carry printed page numbers, and the gold set is labelled with PDF pages, before citations are shown to users.
- C3. ASUS answers stay limited to Ryzen 7000, with a coverage notice naming E20268 (RAI3).
- C4. The AMD pages and manual sizes are re-checked before the gold-set run.

Not GO, because NFR2 has a known failure and a blind spot (Gigabyte positional notes), and citations need the page mapping. Not HOLD, because none of these blocks building or testing retrieval; they block scoring, and the conditions cover that.

Residual risks are listed in section 7.

Re-review triggers: a vendor replaces a manual (size or date change in `sources.md`); a new ASUS edition appears; any change to pipeline settings (chunk size, cleaning, page ranges); V1 or the probes fail on a re-run; gold-set scoring shows a per-manual gap above 15 pp.

*AI use: drafted with help from Claude (Anthropic). Figures were checked against `docs/evidence/week4_checks.txt` and the rendered source pages by Claude and then independently by me, on 19 Nov 2026.*
