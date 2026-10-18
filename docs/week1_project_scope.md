# Week 1 Project Scope

| Field | Value |
|---|---|
| **Project name** | BoardCheck (working name): a manual-grounded motherboard configuration assistant |
| **Domain** | Consumer PC hardware / DIY PC building |
| **Author** | Amil Hakim Bin Anuar (A24AI0014) |

## Problem statement

Motherboard manuals hide the rules that decide how a build performs. Which slots slow down or switch off depends on the CPU installed and on which other slots are filled, and those rules sit in footnotes under spec tables. Builders usually find out after buying. Existing compatibility checkers handle part pairs ("does this CPU fit this board?") but miss many of these lane effects and never point to the manual. A retrieval-grounded assistant can answer configuration questions in plain language and cite the manual page. Keyword search can't do this when three vendors describe the same CPU family in three different ways, and hand-written rules don't scale across boards.

## Evidence of the problem

### Evidence 1: CPU-dependent slot behaviour is documented only in manual footnotes

AMD lists the Ryzen 5 8500G as supporting the B650 chipset with no caveat. The board manuals say otherwise:
- MSI MAG B650 Tomahawk WiFi (PDF pp. 18-19): PCI_E1 "Supports x4/x2 (For Ryzen™ 8500/ 8300 Series processor)" and "The M2_2 slot will be unavailable when using Ryzen™ 8500/ 8300 processor."
- Gigabyte B650 Aorus Elite AX rev 1204 (PDF p. 9): "AMD Ryzen™ 8000 Series-Phoenix 2 Processors support PCIe 4.0 x4 mode" for the main x16 slot, and only "PCIe 4.0 x2 SSDs" in M2B_CPU.

Source: official vendor manuals (URLs under Data sources); AMD Ryzen 5 8500G product page.

### Evidence 2: The most widely used compatibility checker misses these effects

I built a test list on PCPartPicker with a Ryzen 5 8500G, an MSI B650 Tomahawk WiFi, an RX 9070 XT, three NVMe SSDs and a PCIe x4 10GbE card. It flagged the BIOS version and the disabled M2_2 slot. It did not flag that the GPU slot drops to x4 with this CPU, or that the SSD in M2_3 and the card in PCI_E2 both drop to x2 when used together. It also labels PCI_E2 as "x16 @x4", while the MSI manual says "Supports up to PCIe 4.0 x2".

Source: https://pcpartpicker.com/list/kmcn9K (18 Oct 2026); screenshots in `docs/evidence/`.

## Initial related work

**1. PCPartPicker compatibility checker**
Source: pcpartpicker.com list builder; test list above.
Key limitation: its notes are curated rules for part pairs. It missed both lane-width effects in the test, gives no manual page for its notes, and its own disclaimer says "some physical constraints are not checked".

**2. General-purpose LLM chatbots (ChatGPT, Claude, "AI PC builder" tools)**
Source: TechEnclave forum, "Are AI builds legit?", 24 Sep 2026, https://techenclave.com/t/are-ai-builds-legit/442553
Key limitation: answers are not grounded in the manual. Users report socket mix-ups (an AM4 CPU on an AM5 board) and invented prices. This evidence is anecdotal; I found no measurement of chatbot accuracy on this task.

**3. MMLongBench-Doc benchmark**
Source: Ma et al., "MMLongBench-Doc: Benchmarking Long-context Document Understanding with Visualizations", NeurIPS 2024 Datasets & Benchmarks, arXiv:2407.01523.
Key limitation: it shows that question answering over long PDFs is far from solved (the best model, GPT-4o, reached 42.7% F1 on 130 PDFs averaging 49.4 pages, and 22.8% of the questions are deliberately unanswerable). It is a general benchmark and covers neither hardware manuals nor footnoted spec tables.

## Engineering gap

No existing tool answers slot-configuration questions ("what happens if I fill these two slots with this CPU?") from the official manual with a page citation. Two technical problems stand in the way. The deciding facts live in footnotes attached to table cells, and vendors name the same CPU group differently: MSI says "Ryzen 8500/8300", Gigabyte says "Phoenix 2", and AMD's own product page uses neither.

## Initial project objectives

- O1: To design a retrieval-grounded assistant that answers configuration questions about three AM5 B650 motherboards from their official manuals and AMD CPU specifications, citing the manual page for every answer.
- O2: To develop a document pipeline that extracts spec tables with their footnotes intact, plus retrieval and guardrails that refuse questions outside the document set.
- O3: To evaluate the system on a hand-written gold set of 60 to 75 questions for answer accuracy, citation accuracy, correct refusals and latency, reported per manual and compared against a no-retrieval LLM, keyword search and PCPartPicker.

## Scope

The corpus is 7 documents on one chipset: 3 B650 manuals (one per vendor) and 4 AMD CPU spec pages, one for each CPU family that changes how these boards behave (Ryzen 9000, Ryzen 7000, Ryzen 8000 Phoenix 1, Ryzen 8000 Phoenix 2). A stretch goal for Weeks 4 and 5, only if the pipeline holds up, is one B850 or X870 board per vendor.

The system handles four question types:
1. What a slot does with a given CPU ("8500G on the Tomahawk: what speed does PCI_E1 run at?")
2. What happens when two slots that share lanes are both used
3. Spec lookups: storage, max memory and rated speed, and which slots come from the CPU or the chipset
4. Questions the documents can't answer, which the system must refuse

Out of scope: BIOS CPU-support lists, memory compatibility (QVL) lists, physical clearance, PSU sizing, prices, part recommendations, troubleshooting, Intel platforms, diagrams and images.

The three baselines measure different things, so each is reported separately. The no-retrieval LLM is the only like-for-like accuracy comparison. Keyword search returns passages, so it is scored on whether the top passage contains the answer. PCPartPicker is not a Q&A tool, so it is scored on coverage: whether it surfaces the issue at all. With one board per vendor, results are reported per manual, because a gap could come from one manual's layout and not from the vendor. Vendor-level claims wait until the stretch boards are added.

## Target users

DIY PC builders planning an AM5 B650 build or upgrade, especially first-time builders and people adding SSDs or expansion cards to a board they already own.

## Data sources

| # | Document | URL |
|---|---|---|
| 1 | MSI MAG B650 TOMAHAWK WIFI user guide | https://download.msi.com/archive/mnu_exe/mb/MAGB650TOMAHAWKWIFI.pdf |
| 2 | Gigabyte B650 AORUS ELITE AX user's manual, rev 1204 | https://download.gigabyte.com/FileList/Manual/mb_manual_b650-aorus-elite-ax_1204_e.pdf |
| 3 | ASUS ROG STRIX B650-A GAMING WIFI user manual, E20268 (Sept 2022) | https://dlcdnets.asus.com/pub/ASUS/mb/Socket%20AM5/ROG%20STRIX%20B650-A%20GAMING%20WIFI/E20268_ROG_STRIX_B650-A_GAMING_WIFI_UM_WEB.pdf |
| 4 | AMD Ryzen 7 9700X specifications | https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-7-9700x.html |
| 5 | AMD Ryzen 5 7600 specifications | https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-5-7600.html |
| 6 | AMD Ryzen 7 8700G specifications | https://www.amd.com/en/products/processors/desktops/ryzen/8000-series/amd-ryzen-7-8700g.html |
| 7 | AMD Ryzen 5 8500G specifications | https://www.amd.com/en/products/processors/desktops/ryzen/8000-series/amd-ryzen-5-8500g.html |

All seven are publicly downloadable but copyrighted. Gigabyte's manual forbids reproduction without written permission, and AMD's site terms limit use to personal, non-public purposes. The repository therefore keeps only `data/sources.md` (URLs and revisions) and a download script, and the PDFs stay local and gitignored. The gold question set is my own work and cites page numbers instead of copying text.

## Similar to EduAdvisor

Like EduAdvisor, it is a document-grounded assistant over official PDFs that cites its sources, refuses out-of-scope questions, and follows the same lifecycle of data pipeline, retrieval, model and prompt, guardrails, evaluation and deployment.

## Different from EduAdvisor

- The answers sit in spec tables and footnotes instead of prose, so chunking must keep each footnote attached to the table row it modifies.
- Many answers need two documents combined (board manual plus CPU spec) and a name mapping that none of them states.
- Evaluation includes comparisons with existing tools (no-retrieval LLM, keyword search, PCPartPicker) as well as the gold set.
- The source documents are copyrighted, so the repository holds URLs and not the documents.

## Responsible AI risks

- Risk 1, wrong compatibility answer: a builder trusts an answer and buys the wrong part, or runs a GPU at x4 without knowing. The harm is wasted money. Control: every answer must cite a page, and the system refuses when no retrieved passage supports it.
- Risk 2, outdated documents: the ASUS manual in the corpus dates from September 2022, before Ryzen 8000 and 9000 existed, so it says nothing about them. ASUS has not updated it: the newest edition in any language (Japanese V3, November 2022) still covers only Ryzen 7000. Treating it as complete would mislead owners of newer CPUs. Control: record each document's revision, and have the system say when a manual doesn't cover the user's CPU.
- Risk 3, uneven quality across manuals: the manuals are laid out very differently (Gigabyte has 41 pages in English only; MSI has 453 pages in several languages). If extraction works worse on one, owners of that board get worse answers. Control: report accuracy per manual and close the gap before claiming overall accuracy.

## Assumptions to confirm in Week 2

- The mapping of the 8500G and 8300G to "Phoenix 2" comes from PCPartPicker's note and from MSI grouping "8500/8300" under the same x4 rule. I haven't found an AMD document that states it.
- The ASUS manual's lane rules for Ryzen 8000 and 9000 are unknown, since no edition covers them. Decide whether to keep ASUS questions to Ryzen 7000, or treat newer-CPU questions on this board as ones the system must refuse.

*AI use: drafted with help from Claude (Anthropic). Every quote, figure and URL above was checked against the source documents on 18 Oct 2026.*
