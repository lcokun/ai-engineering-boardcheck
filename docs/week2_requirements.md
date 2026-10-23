# Requirements Specification — BoardCheck
Version: 1.0 · Week 2 · Amil Hakim Bin Anuar (A24AI0014)

## Section 0 — Project Framing & Application Scope Checkpoint

| Framing element | Content |
|---|---|
| **Problem Evidence** | **E1.** AMD lists the Ryzen 5 8500G as supporting B650 with no caveat, but the board manuals disagree. The MSI MAG B650 Tomahawk WiFi manual (PDF pp. 18–19) drops PCI_E1 to x4 and disables M2_2 with "Ryzen 8500/8300", and the Gigabyte B650 Aorus Elite AX manual (rev 1204, p. 9) limits PCIEX16 to x4 and M2B_CPU to x2 for "Phoenix 2". **E2.** A PCPartPicker test list (https://pcpartpicker.com/list/kmcn9K, 18 Oct 2026) with an 8500G, the Tomahawk, an RX 9070 XT, three NVMe SSDs and an x4 NIC did not flag that the GPU runs at x4, or that M2_3 and PCI_E2 both drop to x2. Screenshots are in `docs/evidence/`. |
| **Existing Approaches** | 1. **PCPartPicker**: curated part-pair rules. It caught the BIOS version and the disabled M2_2 but missed both lane-width effects, and it gives no manual page. 2. **General LLM chatbots**: answer free-form build questions without grounding in the manual. A TechEnclave thread (24 Sep 2026) reports socket mix-ups and invented prices (anecdotal). 3. **MMLongBench-Doc** (Ma et al., NeurIPS 2024): long-PDF question answering over 130 documents. The best model (GPT-4o) reached 42.7% F1, and 22.8% of the questions are unanswerable by design, to catch hallucination. 4. **TAT-QA** (Zhu et al., ACL 2021): question answering over tables plus text in financial reports. The authors' own model (TAGOP) reached 58.0% F1, against 90.8% for human experts. Its tables are clean and have no footnotes. 5. **TechQA** (Castelli et al., ACL 2020): real tech-support questions answered from IBM Technotes, with 600/310/490 train/dev/test pairs. The closest domain, but text only. |
| **Project / Engineering Gap** | No existing tool answers slot-configuration questions from the official manual with a page citation. Three practical problems stand in the way. (a) The deciding facts live in footnotes attached to table cells. (b) Vendors name the same CPU group differently: MSI says "8500/8300", Gigabyte says "Phoenix 2", and AMD calls all four 8000G parts "Phoenix"; its spec fields separate them by core mix and usable PCIe lanes (10 vs 16).¹ (c) Manuals go out of date: the ASUS manual covers only Ryzen 7000. |
| **Objective O1** | To design a retrieval-grounded assistant that answers configuration questions about three AM5 B650 motherboards from their official manuals and AMD CPU specifications, citing the manual page for every answer. |
| **Objective O2** | To develop a document pipeline that keeps spec-table footnotes attached to their rows, a CPU-group mapping across vendor naming, and guardrails that refuse unanswerable questions and flag CPUs a manual does not cover. |
| **Objective O3** | To evaluate the system on a hand-written gold set of 74 questions (54 answerable, 20 unanswerable) for answer accuracy, citation accuracy, correct refusals and latency, reported per manual and compared against a no-retrieval LLM, keyword search and PCPartPicker. |
| **Intended Users** | DIY PC builders planning an AM5 B650 build or upgrade, especially first-time builders and owners adding SSDs or expansion cards to a board they already have. |
| **Supported Tasks** | 1. What a slot does with a given CPU. 2. What happens when two slots that share lanes are both filled. 3. Spec lookups: storage, maximum memory and rated speed, and whether a slot is wired to the CPU or the chipset. 4. Recognising questions the documents can't answer, and refusing them. |
| **Information / Knowledge Domain** | Nine documents: the MSI MAG B650 Tomahawk WiFi, Gigabyte B650 Aorus Elite AX (rev 1204) and ASUS ROG Strix B650-A Gaming WiFi (E20268) manuals, and the AMD specification pages for the Ryzen 7 9700X, Ryzen 5 7600, Ryzen 7 8700G, Ryzen 5 8600G, Ryzen 5 8500G and Ryzen 3 8300G, covering all four Ryzen 8000G desktop APUs. Each is pinned to the revision recorded in `data/sources.md`. |
| **Operating Context** | A text question-and-answer interface in English, one question at a time, used while planning a purchase or before installing a device. The user knows their board and CPU model. The user makes the final decision. |
| **Important Constraints** | The documents are copyrighted, so the public repository holds no PDFs and answers quote only short excerpts. The ASUS manual (newest English edition E20268, Sept 2022) covers only Ryzen 7000. I found no AMD document that names "Phoenix 2". The MSI manual is 453 multilingual pages, of which only the English section is used. One author, one semester, the Colab free tier, and a near-zero API budget. |
| **Explicit Out-of-Scope Tasks** | BIOS CPU-support lists, memory QVL lists, physical clearance, PSU sizing, prices, part recommendations and buy/don't-buy decisions, troubleshooting, overclocking, Intel platforms, boards outside the corpus, and diagrams or images. |
| **Evaluation Focus** | Does BoardCheck answer slot and lane questions about the three boards correctly, with a cited page that supports the answer, and more accurately than a no-retrieval LLM? Does it refuse what the documents can't answer, and perform about equally well on each manual? |

¹ Corrects Week 1, which said AMD's product page uses neither vendor name. Re-checked 23 Oct 2026: all four Ryzen 8000G pages list "Former Codename: Phoenix", with no Phoenix 1/2 split. The lane-based mapping is justified in `week2_architecture_decisions.md` (ADR 3).

## Section 1 — Functional Requirements

| # | Requirement — The system SHALL | Scope Boundary — SHALL NOT |
|---|---|---|
| FR1 | State what a named slot supports (available or disabled, PCIe generation, lane width) on one of the three boards with a named CPU. When no CPU is named and the answer depends on it, give the answer for each CPU group the manual lists. | Assume a CPU the user did not name. |
| FR2 | Explain what happens to each device when two slots that share bandwidth are both filled. | Infer a sharing rule that the manual does not state. |
| FR3 | Answer spec lookups: number and type of storage connectors, maximum memory and rated memory speed, and whether a slot connects to the CPU or the chipset. | Answer from memory QVL lists or BIOS CPU-support lists. |
| FR4 | Identify which vendor CPU group a named AMD CPU belongs to (for example, the 8500G is MSI "8500/8300" and Gigabyte "Phoenix 2"), state that mapping in the answer, and label it as derived. | Present the mapping as if a document stated it. |
| FR5 | Give the document and page (or spec field, for AMD web pages) for every factual claim in an answer. A derived claim, such as a CPU-group mapping, cites every source it is derived from. | Present unsupported information as if it came from a manual. |
| FR6 | Decline questions outside the supported tasks or the document set, and say what it can answer instead. | Recommend parts or advise whether to buy. |
| FR7 | Say when a board's manual does not cover the user's CPU, and name the manual revision it checked. | Fill the gap with another board's behaviour or with general knowledge. |

## Section 2 — Non-Functional Requirements

| # | Quality Attribute | Requirement | Measurement Method | Metric | Threshold |
|---|---|---|---|---|---|
| NFR1 | Correctness | Answers to answerable questions shall match what the cited manual states. | Score the 54 answerable gold questions with a rubric: an answer is correct only if every field that applies (slot state, PCIe generation, lane width, capacity or speed, conditions) matches the manual. Run the same 54 through a no-retrieval LLM baseline. | Correct answer rate (%); margin over the baseline (percentage points) | ≥ 80%, and ≥ 20 pp above the no-retrieval baseline |
| NFR2 | Correctness (evidence) | The evidence each answer is based on shall include the footnote or table row that decides it. | Record the deciding page and footnote for each answerable gold question, then check whether that evidence is among what the system used to answer. | Evidence recall (% of answerable questions) | ≥ 90% |
| NFR3 | Performance | Responses shall arrive within an interactive wait time. | Measure end-to-end time from question submitted to answer returned across all 74 gold questions. | p90 latency | < 5,000 ms |
| NFR4 | Cost | Running the system shall stay within a student budget. | Record model and API usage over the full gold-set run and convert it to cost. | Cost per 100 queries | < US$0.50 |
| NFR5 | Maintainability | Adding a new manual or revision shall not require reprocessing the existing documents. | Controlled update test: add one new manual to the document set, time it from download until it can be queried, then re-run the existing gold set. | Update time; regressions (questions correct before and wrong after) | < 30 min; 0 regressions |
| NFR6 | Reliability | Repeating the same question shall give the same verdict. | Run a 20-question subset of the gold set (shared-lane, CPU-group and coverage-gap questions) three times each and compare each verdict (slot state, lane width, or refusal) with the first run. | Verdict consistency rate (%) | ≥ 95% |

## Section 3 — Responsible AI Requirements

| # | Responsible AI Risk | Requirement | Measurement Method | Metric | Threshold |
|---|---|---|---|---|---|
| RAI1 | Transparency / Grounding (a wrong answer leads to a wrong purchase) | Every answer shall cite the document and page (or AMD spec field) behind each claim, and the cited source shall support the claim. | Inspect every answered gold question: check that a citation is present, then that the cited source states what the answer claims. For a derived claim, check that each cited source supports its part of the derivation. | Citation presence rate; citation-support rate | 100% presence; ≥ 95% support |
| RAI2 | Safety / Scope (confident answers to questions the documents can't answer) | The system shall refuse unanswerable and out-of-scope questions without refusing answerable ones. | Run the 20 unanswerable gold questions (12 out of scope or not in any document, 8 coverage gaps), plus the 54 answerable ones to check for false refusals. | Correct refusal rate; false refusal rate | ≥ 90% correct refusals; ≤ 10% false refusals |
| RAI3 | Outdated documents (the ASUS manual predates Ryzen 8000/9000) | When a manual does not cover the user's CPU, the system shall say so, name the revision it checked, and not state slot behaviour for that CPU. | Run the 8 coverage-gap gold questions (ASUS with Ryzen 8000/9000) and check each answer for a coverage notice, the revision, and the absence of any lane claim. | Coverage-notice rate; uncovered-CPU claims | 100%; 0 |
| RAI4 | Fairness across manuals (extraction quality differs by layout) | Answer quality shall not differ beyond the agreed tolerance between the three manuals. | Score NFR1 separately per manual (18 answerable questions each), and report NFR2 evidence recall per manual to locate the cause of any gap. | Largest gap in correct answer rate between any two manuals | ≤ 15 pp |
| RAI5 | Copyright (the manuals and AMD pages forbid reproduction) | The public repository shall not contain source documents or their extracted text, and answers shall quote only short excerpts. | Check the repository file list before each push for PDFs and extracted text, and measure the longest verbatim overlap between each gold-run answer and its source text. | Source files in the repository; longest verbatim quote | 0 files; ≤ 25 words |

## Reflection

**Which Responsible AI requirement will be the most difficult to measure or enforce technically? Why?**

RAI1's citation-support check. It needs a human to judge each claim against the cited page, and many answers combine two documents. The CPU-group mapping is harder still: no page states it, so the claim has to cite two sources and be labelled as derived. A presence check would pass an answer whose cited page says something else, so support has to be judged claim by claim.

*AI use: drafted with help from Claude (Anthropic). Quotes, figures and URLs were checked against the source documents by Claude and then independently by me, between 18 and 23 Oct 2026.*
