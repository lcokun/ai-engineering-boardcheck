# Prepared text (Topic 3 Part B)

The `.jsonl` files that belong here are not in the repository. They hold text extracted from copyrighted manuals and AMD pages (RAI5), so they stay on the author's machine. To rebuild them, download the sources listed in `data/sources.md` into `data/raw/` and run `notebooks/week3_pipeline.ipynb`. Compare the result with the SHA-256 values in `data/week3_manifest.json`.

## Files

One file per source, `prepared_text_S01.jsonl` to `prepared_text_S09.jsonl`, one JSON record per line.

| Source | Records | Unit |
|---|---|---|
| S01 MSI manual | 55 | chunk |
| S02 Gigabyte manual | 47 | chunk |
| S03 ASUS manual | 68 | chunk |
| S04–S09 AMD spec pages | 54 / 57 / 67 / 66 / 68 / 69 | spec field |

Total: 551 records. The Part C outputs in `data/pipeline_v1/documents/` are byte-identical.

## Record fields

| Field | Meaning |
|---|---|
| `record_id` | `S01-p018-c01` (source, PDF page, chunk) or `S08-f039` (source, field number) |
| `source_id`, `source`, `source_sha256` | Source ID, path under `data/raw/`, hash of the raw file |
| `doc_title`, `revision` | Document title and the revision or file date |
| `locator_type` | `pdf_page` for manuals, `spec_field` for AMD pages |
| `page` | PDF page number (manuals); not the printed page number, see `docs/week4_data_quality_report.md` |
| `spec_section`, `spec_field` | AMD section and field name (AMD pages) |
| `chunk_index`, `n_chars` | Chunk position on the page and its length |
| `processing` | `page-aware-lines-1500-ov150` or `amd-spec-fields-dt-dd` |
| `text` | The extracted text |
