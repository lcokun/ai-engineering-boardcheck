# BoardCheck

> Answers configuration questions about AM5 B650 motherboards for DIY PC builders, from the official manuals, with a page citation for every answer.

## Problem Statement
Which slots slow down or switch off on a motherboard depends on the CPU and on which other slots are filled. Those rules sit in manual footnotes, so builders usually find out after buying. A retrieval-grounded assistant can answer in plain language and cite the page. Keyword search can't, because vendors name the same CPU group differently, and hand-written rules don't scale across boards.

## Evidence of the Problem
- AMD lists the Ryzen 5 8500G as supporting B650 with no caveat, but the MSI B650 Tomahawk WiFi manual (pp. 18-19) disables M2_2 and drops PCI_E1 to x4 with this CPU, and the Gigabyte B650 Aorus Elite AX manual (rev 1204, p. 9) limits it to x4 and an x2 SSD slot. Source: official vendor manuals and the AMD 8500G product page (see Data Sources).
- A PCPartPicker test list (8500G, B650 Tomahawk, RX 9070 XT, three NVMe SSDs, a PCIe x4 NIC) did not flag that the GPU runs at x4 or that the M2_3 SSD and the PCI_E2 card both drop to x2. Source: https://pcpartpicker.com/list/kmcn9K (18 Oct 2026), screenshots in `docs/evidence/`.

## Initial Related Work / Existing Approaches
- PCPartPicker compatibility checker (pcpartpicker.com). It uses curated rules for part pairs. It missed both lane-width effects in the test list and gives no manual page for its notes.
- General-purpose LLM chatbots. TechEnclave forum, "Are AI builds legit?", 24 Sep 2026, https://techenclave.com/t/are-ai-builds-legit/442553. Their answers aren't grounded in the manual, and users report socket mix-ups and invented prices (anecdotal).
- MMLongBench-Doc. Ma et al., NeurIPS 2024 Datasets & Benchmarks, arXiv:2407.01523. The best model reached only 42.7% F1 on long-PDF question answering. It is a general benchmark and doesn't cover hardware manuals or footnoted spec tables.

## Engineering Gap / Limitation
No existing tool answers slot-configuration questions from the official manual with a page citation. The deciding facts live in footnotes attached to table cells, and vendors name the same CPU group differently (MSI: "Ryzen 8500/8300"; Gigabyte: "Phoenix 2"; AMD: "Phoenix" for all four 8000G parts).

## Project Objectives
- O1: To design a retrieval-grounded assistant that answers configuration questions about three AM5 B650 motherboards from their official manuals and AMD CPU specifications, citing the manual page for every answer.
- O2: To develop a document pipeline that keeps spec-table footnotes attached to their rows, a CPU-group mapping across vendor naming, and guardrails that refuse unanswerable questions and flag CPUs a manual does not cover.
- O3: To evaluate the system on a hand-written gold set of 74 questions (54 answerable, 20 unanswerable) for answer accuracy, citation accuracy, correct refusals and latency, reported per manual and compared against a no-retrieval LLM, keyword search and PCPartPicker.

## Target Users
DIY PC builders planning an AM5 B650 build or upgrade, especially first-time builders and people adding SSDs or expansion cards to a board they already own.

## Data Sources
- MSI MAG B650 TOMAHAWK WIFI user guide: https://download.msi.com/archive/mnu_exe/mb/MAGB650TOMAHAWKWIFI.pdf
- Gigabyte B650 AORUS ELITE AX user's manual, rev 1204: https://download.gigabyte.com/FileList/Manual/mb_manual_b650-aorus-elite-ax_1204_e.pdf
- ASUS ROG STRIX B650-A GAMING WIFI user manual, E20268: https://dlcdnets.asus.com/pub/ASUS/mb/Socket%20AM5/ROG%20STRIX%20B650-A%20GAMING%20WIFI/E20268_ROG_STRIX_B650-A_GAMING_WIFI_UM_WEB.pdf
- AMD Ryzen 7 9700X, Ryzen 5 7600, Ryzen 7 8700G, Ryzen 5 8600G, Ryzen 5 8500G and Ryzen 3 8300G specification pages (amd.com; full URLs and revisions in `data/sources.md`)

The documents are copyrighted, so this repository stores their URLs and not the PDFs.

## Weekly Progress
| Week | Focus | Deliverable | Status |
|------|-------|-------------|--------|
| W1 | System map + project scope | README + docs | ✅ |
| W2 | Requirements, evaluation criteria, V1 architecture | docs/week2_*.md + week2_architecture_v1.png | ✅ |
