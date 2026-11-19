# Week 3 Data Inventory

## 1. Which requirements need this data

| Requirement | Data it needs | Sources |
|---|---|---|
| FR1, FR2, FR3 | Slot rows, footnotes and lane-sharing rules from each board's spec tables | S01–S03 |
| FR4 | CPU codename and usable PCIe lanes, to map each CPU to a vendor CPU group | S04–S09 (plus the Gigabyte p. 9 "Phoenix 1/2" labels) |
| FR5, RAI1 | Document title, revision, and page or spec field on every record | All |
| FR7, RAI3 | Manual revision and the CPU generations it covers | S01–S03 |
| RAI5 | Rights status and where raw and prepared copies are stored | All |

If this data is wrong, two evaluation measures suffer. NFR2 (evidence recall) needs the deciding row and its footnote in the same chunk, and RAI4 (per-manual score gap) depends on extraction quality, which differs by manual layout.

## 2. Sources

| Source ID | Filename / URL | Type and purpose | Version / date / owner | Access / rights | Inspection evidence |
|---|---|---|---|---|---|
| S01 | `MAGB650TOMAHAWKWIFI.pdf` (download.msi.com) | PDF manual; slot rules for FR1–3 | MSI; no edition code; file date 2024-12-18 | Copyrighted; local copy only | 453 pp., English pp. 3–57; kept pp. 5–57; skipped diagram pp. 16–17 (<40 letters); 55 chunks; probes on pp. 18, 19, 31 pass |
| S02 | `mb_manual_b650-aorus-elite-ax_1204_e.pdf` (download.gigabyte.com) | PDF manual; slot rules for FR1–3 | Gigabyte; rev 1204; file date 2024-12-06 | Reproduction forbidden without written permission; local copy only | 41 pp.; kept pp. 4–36; 0 skipped; 6,138 □ glyphs and 90 control characters removed; 47 chunks; p. 9 probes pass; p. 26 row and footnote land in different chunks (known gap) |
| S03 | `E20268_ROG_STRIX_B650-A_GAMING_WIFI_UM_WEB.pdf` (dlcdnets.asus.com) | PDF manual; slot rules for FR1–3 (Ryzen 7000 only) | ASUS; E20268, September 2022 | Copyrighted; PDF permissions set `copy:no`; text extracted for private coursework only | 80 pp., RC4-encrypted (empty user password); kept pp. 4–66; skipped pp. 12, 36, 38, 66 (<40 letters); 68 chunks; probes on pp. 6, 10 pass |
| S04–S09 | AMD product pages for the 9700X, 7600, 8700G, 8600G, 8500G and 8300G (amd.com) | HTML spec pages; codename and lanes for FR4 | AMD; no revision number; saved 2026-11-16 | AMD site terms allow personal, non-public use; local copy only | 54 / 57 / 67 / 66 / 68 / 69 spec fields; 0 empty values; 0 fields without a section; codename and lane fields match Week 2 |

Per-source hashes, record counts and page ranges are in `data/week3_manifest.json` and `data/pipeline_v1/documents/pipeline_manifest.json`.

## 3. Raw vs prepared storage

Raw files (`data/raw/manuals/`, `data/raw/amd/`) stay on the local machine and are never committed. `data/sources.md` lists each URL, file size and date, so anyone can download the same files.

Prepared files (`data/processed/*.jsonl`, `data/pipeline_v1/documents/*.jsonl`) also stay local. They hold extracted text, and committing them would break RAI5.

The repository holds both manifests (SHA-256 hashes, record counts and paths, no text), the notebook (text previews capped at 25 words) and this document.

*AI use: drafted with help from Claude (Anthropic). Figures were checked against the executed notebook and both manifests by Claude and then independently by me, on 19 Nov 2026.*
