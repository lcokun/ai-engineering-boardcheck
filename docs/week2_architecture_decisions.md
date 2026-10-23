# Architecture Decisions & Traceability — BoardCheck
Version: 1.0 · Week 2 · Amil Hakim Bin Anuar (A24AI0014)

Requirement IDs refer to `docs/week2_requirements.md`; evaluation criteria to `docs/week2_evaluation_criteria.md`. The diagram is `docs/week2_architecture_v1.png`.

## C1 — Simplest Architecture

**User (builder) → BoardCheck Interface → Language Model Service → Answer**

| Requirement | Supported by the simple flow? | Reason |
|---|---|---|
| FR1–FR3, NFR1 | No | The model has not read these manuals, and the slot rules are board-specific footnotes. |
| FR5, RAI1 | No | There is no source to cite. |
| FR4 | No | AMD calls all four 8000G parts "Phoenix", so matching by name puts the 8500G in the wrong group. |
| FR7, RAI3 | No | Nothing tells it which CPUs each manual revision covers. |
| FR6, RAI2 | Partly | An instruction can refuse obviously off-topic questions, but not questions that sound in scope and that the documents do not answer. |
| NFR3, NFR4 | Yes | One call is the fastest and cheapest path, which sets the budget the added components must fit within. |

The simple flow is also the no-retrieval baseline in NFR1, so V1 has to beat its own starting point.

## C2 — Architecture Needs

| Requirement ID | What does the requirement need? | Architecture Response |
|---|---|---|
| FR1–FR3, NFR1 | Access to the manuals' spec tables and footnotes | Knowledge Source + Knowledge Access |
| NFR2, RAI4 | The deciding footnote kept with its table row, for every manual layout | Document Pipeline (offline) |
| FR5, RAI1 | Every claim traceable to a document and page | Page provenance stored in the Knowledge Source; Citation Check before the response |
| FR4 | A CPU model mapped to each vendor's CPU group | CPU-Group Resolver |
| FR6, RAI2 | Refusal of unanswerable and out-of-scope questions | Scope & Coverage Control |
| FR7, RAI3 | Knowledge of which CPUs each manual revision covers | Coverage and revision metadata in the Knowledge Source, read by Scope & Coverage Control |
| NFR5 | A new manual added without reprocessing the others | The pipeline processes one document at a time; no new component |
| NFR3, NFR4, NFR6 | Latency, cost and consistent verdicts | Constraints on the existing flow (few stages, deterministic generation settings); no new component |
| RAI5 | No source text in the public repository | Pipeline outputs and the Knowledge Source stay outside the repository; no new component |
| Evaluation criteria | Evidence, answer, citations, latency and cost captured for each query | Evaluation Point |

## C3 — V1 Flow

Online:
1. The user asks a question in the **Interface**.
2. The **CPU-Group Resolver** identifies the board, the CPU and the vendor CPU group (FR4).
3. **Scope & Coverage Control** checks that the question is in scope and that the manual revision covers the CPU. If not, the system returns a refusal or a coverage notice (FR6, FR7).
4. **Knowledge Access** fetches the relevant table rows and their footnotes, with page provenance (FR1–FR3).
5. The **Language Model Service** writes the answer from that evidence only (NFR1).
6. **Citation Check** confirms that each citation points to evidence that was actually used (FR5).
7. The **Response** is an answer with citations and "derived" labels, a refusal, or a coverage notice.

Offline: the **Document Pipeline** turns the official PDFs and AMD pages (English section only) into table rows with their footnotes, page and revision, and stores them in the **Knowledge Source**.

The **Evaluation Point** logs the question, evidence, answer, citations, latency and cost for each query, which feeds gold-set scoring and the baselines.

## C4 — Architecture Decision Records

| # | Decision | Requirement / Constraint | Alternatives Considered | Selected Option | Trade-off Accepted |
|---|---|---|---|---|---|
| ADR 1 | Include knowledge access | FR1–FR3, NFR1, FR5 | Base model only; whole manual in a long context; keyword search; retrieval of relevant rows with page provenance | Retrieval with page provenance | More components, and a retrieval step that can miss the deciding row (measured by NFR2), for grounded and citable answers |
| ADR 2 | Keep footnotes attached to table rows | NFR2, RAI4 | Fixed-size text chunks; whole pages; table rows with their footnotes attached | Table-row units with attached footnotes and page | Layout-specific parsing for three vendors (more work, and harder for NFR5), for footnotes that stay with the slot they modify |
| ADR 3 | CPU-group mapping | FR4, FR5 | Let the language model infer the group; a third-party mapping (PCPartPicker notes, news sites); an alias table derived from AMD spec fields | Alias table derived from AMD's usable-lane and core fields, shown in the answer and labelled "derived" | Hand upkeep for every new CPU, and a mapping no document states outright, for a mapping whose inputs are all official and checkable |
| ADR 4 | Explicit scope and coverage control | FR6, FR7, RAI2, RAI3 | Prompt instruction only; explicit control step that reads coverage metadata | Explicit control before retrieval and generation | Some false refusals (capped at 10% by RAI2) and coverage metadata that must be kept current, for refusals that do not depend on the model noticing a gap |
| ADR 5 | Check citations before responding | FR5, RAI1 | Trust the model's citations; check only during evaluation; runtime check that each citation is in the evidence used | Runtime check | An extra step (within NFR3), and correct answers withheld when the page is wrong, for no citation reaching a builder that was not in the evidence |

### Rationale

**ADR 1.** The base model has not read these manuals; that is the simple flow in C1. The long-context option is weak: the English section of the MSI manual alone is about 55 pages (PDF pp. 3–57), and in MMLongBench-Doc the best model reached 42.7% F1 on long PDFs. Keyword search cannot bridge "Phoenix" and "8500/8300".

**ADR 2.** Fixed-size chunks split a footnote from the row it modifies, and whole pages mix several unrelated tables.

**ADR 3.** AMD names all four 8000G parts "Phoenix", but its usable-lane field lines up with Gigabyte's groups (Gigabyte manual p. 9):

| Gigabyte group | PCIEX16 | M2A_CPU | M2B_CPU | CPU lanes used | AMD usable lanes |
|---|---|---|---|---|---|
| Phoenix 2 | x4 | x4 | x2 | 10 | 8500G and 8300G: 10 |
| Phoenix 1 | x8 | x4 | x4 | 16 | 8600G and 8700G: 16 |

MSI names the models directly ("8700/8600/8400", "8500/8300"), so its groups map by name. With an 8500 it uses only 8 of the 10 lanes (M2_2 is disabled), so the lane check rests on Gigabyte alone. A CPU whose group cannot be derived from the corpus, such as the 8700F on the Gigabyte board, is refused.

**ADR 4.** The ASUS manual says nothing about Ryzen 8000/9000. Retrieval still returns the closest ASUS rows, so the model cannot see the gap from the evidence alone.

**ADR 5.** The runtime check confirms that a citation points to evidence that was actually used. Whether the cited page supports the claim is still judged during evaluation (RAI1).

**Deferred to Topics 3–5:** a hosted model API or a self-hosted model on Colab (cost, latency and vendor dependency), and the specific parser, retrieval method and interface.

## Initial Requirements Traceability Matrix

| Objective | Requirement | Evaluation Criterion | Architecture Element | Later Evidence |
|---|---|---|---|---|
| O1 | FR1–FR3, NFR1 | Answer correctness ≥ 80%, ≥ 20 pp over baseline | Knowledge Access + Language Model Service | Gold-set score against the no-retrieval baseline |
| O1 | FR5, RAI1 | Citation presence 100%, support ≥ 95% | Citation Check; page provenance in the Knowledge Source | Citation audit of the gold-set run |
| O2 | NFR2 | Evidence recall ≥ 90% | Document Pipeline | Evidence recall per manual |
| O2 | FR4 | Mapping accuracy 100% | CPU-Group Resolver | Results on Ryzen 8000 and Phoenix-trap questions |
| O2 | FR6, RAI2 | Correct refusals ≥ 90%, false refusals ≤ 10% | Scope & Coverage Control | Results on the 20 unanswerable and 54 answerable questions |
| O2 | FR7, RAI3 | Coverage notice 100% | Scope & Coverage Control + coverage metadata | Results on the 8 ASUS coverage-gap questions |
| O3 | RAI4 | Per-manual gap ≤ 15 pp | Evaluation Point | Per-manual score table |
| O3 | NFR3, NFR4, NFR6 | p90 < 5 s; < US$0.50 per 100 queries; consistency ≥ 95% | Evaluation Point (logs) | Latency and cost logs; three-run comparison |

## Final Review Checklist

- **Does each major component support a requirement or evaluation need?** Yes. C2 maps each one, and every component in the diagram carries its requirement IDs.
- **Is any important data source, safety control or evaluation point missing?** Coverage metadata is the easy one to miss, and it sits in the Knowledge Source. No privacy control is needed because the system collects no personal data.
- **Has any technology or component been added without justification?** No technology is named; components are labelled by function.
- **Is there a simpler architecture that could still satisfy the requirements?** The Citation Check could exist only in evaluation, but citation failures would then reach users (ADR 5). The CPU-Group Resolver could be a prompt instruction, which ADR 3 rejects.

## Reflection

**Which architecture decision involved the most important trade-off? Which requirement drove it, and what trade-off was accepted?**

ADR 4. RAI2 and RAI3 drove it: the system must not answer when the manual is silent. False refusals are accepted up to 30%, because a wrong compatibility answer can cost a builder money, while a wrongly refused question only sends them back to the manual.

*AI use: drafted with help from Claude (Anthropic). Quotes, figures and URLs were checked against the source documents between 18 and 23 Oct 2026.*
