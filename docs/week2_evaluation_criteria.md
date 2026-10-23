# Evaluation Criteria — BoardCheck
Version: 1.0 · Week 2 · Amil Hakim Bin Anuar (A24AI0014)

Requirement IDs refer to `docs/week2_requirements.md`.

## Evaluation Criteria Table

| Objective / Requirement ID | Evaluation Criterion | Capability Bucket | Measurement Method | Metric | Threshold | User / Business Outcome |
|---|---|---|---|---|---|---|
| O3 / NFR1 | Answer correctness | Domain-specific capability | Score the 54 answerable gold questions with the correctness rubric (below), then run the same set through a no-retrieval LLM. | Correct answer rate; margin over the baseline | ≥ 80%; ≥ 20 pp | Builders get the right slot and lane facts before buying, and retrieval shows a clear advantage over a plain chatbot. |
| O2 / NFR2 | Footnote evidence recall | Domain-specific capability | For each answerable question, check whether the deciding footnote or table row is in the evidence the system used. | Evidence recall | ≥ 90% | Confirms the pipeline keeps footnotes with their rows, and separates pipeline failures from model failures. |
| O2 / FR4 | CPU-group mapping | Domain-specific capability | Check every gold question that names a Ryzen 8000 CPU, including at least 3 "Phoenix" trap questions, for the correct vendor group and a "derived" label. | Mapping accuracy | 100% | Owners of an 8000G CPU get the limits for their own group (x4 vs x8), not the other one. |
| O3 / RAI4 | Per-manual parity | Domain-specific capability | Compute NFR1 separately for each manual (18 answerable questions each), alongside evidence recall per manual. | Largest gap in correct answer rate between any two manuals | ≤ 15 pp | Owners of each board get similarly reliable answers. |
| O1 / FR5 | Faithfulness | Generation capability | Check each claim in every answer against the evidence the system used. | Answers with no unsupported claims | ≥ 90% | Answers add nothing that the manual does not say. |
| O3 / NFR6 | Verdict consistency | Generation capability | Ask the 20-question subset three times and compare each verdict with the first run automatically. | Verdict consistency rate | ≥ 95% | Asking twice does not give a builder two different answers. |
| O1 / FR5 / RAI1 | Citation presence and support | Instruction-following capability | Inspect every answered question for a citation, then check that the cited source supports each claim; for derived claims, check each source. | Citation presence rate; citation-support rate | 100%; ≥ 95% | Builders can verify any answer against the manual themselves. |
| O2 / FR6 / RAI2 | Refusal of unanswerable questions | Instruction-following capability | Run the 20 unanswerable gold questions, plus the 54 answerable ones to check for false refusals. | Correct refusal rate; false refusal rate | ≥ 90%; ≤ 10% | No confident guesses where the documents are silent, and no blocked answers where they are not. |
| O2 / FR7 / RAI3 | Coverage notice | Instruction-following capability | Run the 8 ASUS coverage-gap questions (Ryzen 8000/9000) and check each answer for a coverage notice, the manual revision, and no lane claims. | Coverage-notice rate; uncovered-CPU claims | 100%; 0 | Owners of newer CPUs on the ASUS board learn that its manual cannot answer for them. |
| O3 / NFR3 | Response latency | Cost and latency | Measure end-to-end time from question to answer across all 74 gold questions. | p90 latency | < 5 s | Fast enough for a planning tool. |
| O3 / NFR4 | Running cost | Cost and latency | Record model and API usage over the full gold-set run and convert it to cost. | Cost per 100 queries | < US$0.50 | The system runs within a student budget. |

NFR5 (maintainability) and RAI5 (copyright) are pass/fail checks with their own tests in `week2_requirements.md`, so they are not repeated here.

## Gold Set Composition (74 questions)

| Question type | MSI | Gigabyte | ASUS | Total |
|---|---|---|---|---|
| Slot with CPU | 8 | 10 | 6 (Ryzen 7000 only) | 24 |
| Two slots filled | 4 | 2 (no stated rule) | 4 | 10 |
| Spec lookup | 6 | 6 | 8 | 20 |
| *Answerable* | *18* | *18* | *18* | *54* |
| Coverage gap | – | – | 8 | 8 |
| Out of scope / not in documents | 4 | 4 | 4 | 12 |
| **Total** | **22** | **22** | **30** | **74** |

- The question mix for each manual follows what that manual contains. MSI and ASUS each state one sharing rule (MSI PDF pp. 18–19; ASUS p. 10), and Gigabyte states none, so per-type scores are not comparable across manuals. Questions built from a single rule also resemble each other, which can inflate that type's score. RAI4 compares per-manual totals (18 each), not types.
- The correct answer to a Gigabyte two-slot question gives each slot's specification and says that the manual lists no sharing rule between them. An answer that invents a lane reduction is scored as wrong (FR2).
- CPU-group questions include at least 3 "Phoenix" traps on MSI and Gigabyte: questions that use the 8000G codename, or name a model whose group a naive match would get wrong. All four 8000G APUs can appear, since all four AMD pages are in the corpus.
- The NFR6 subset (20 questions) is drawn from two-slot, CPU-group and coverage-gap questions.

## Correctness Rubric (NFR1)

An answer is correct only if every field that applies (slot state, PCIe generation, lane width, capacity or speed, conditions) matches the manual. One wrong field makes the whole answer wrong, because a builder acts on the whole answer.

## Baselines (reported, no threshold)

- **No-retrieval LLM**: the same 54 answerable questions, scored with the same rubric. This is the only like-for-like accuracy comparison, and it supplies the margin in NFR1.
- **Keyword search**: scored on whether the top-ranked passage contains the deciding footnote or row.
- **PCPartPicker**: scored on coverage, meaning whether it surfaces the issue at all, for the questions that fit its parts-list format.

## Reflection

**Which evaluation criterion is most important for determining whether the application will be useful to its intended users? Why?**

Answer correctness with the baseline margin (NFR1). If BoardCheck cannot clearly beat a plain chatbot on the same questions, a builder has no reason to use it. Citation support comes next, because it lets a builder check a correct answer against the manual.

*AI use: drafted with help from Claude (Anthropic). Quotes, figures and URLs were checked against the source documents by Claude and then independently by me, between 18 and 23 Oct 2026.*
