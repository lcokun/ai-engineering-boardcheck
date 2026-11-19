"""Week 4 data-quality checks on the Topic 3 Part B outputs (data/processed/).

Prints counts and record IDs only, plus headings of at most eight words, so the
output can be committed without republishing source text (RAI5).

Run from the repository root:
    uv run python evaluation/week4_quality_checks.py > docs/evidence/week4_checks.txt
"""
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from pypdf import PdfReader

REPO = Path(__file__).resolve().parent.parent
PROCESSED_DIR = REPO / "data" / "processed"
RAW_DIR = REPO / "data" / "raw"
MANIFEST = REPO / "data" / "week3_manifest.json"

MANUAL_IDS = ("S01", "S02", "S03")
AMD_IDS = ("S04", "S05", "S06", "S07", "S08", "S09")
SAMPLE_SEED = 4
RANDOM_SAMPLE_SIZE = 8
PURPOSIVE_PAGES = {"S01": (18, 19, 31), "S02": (9, 26), "S03": (6, 10)}
PURPOSIVE_AMD = ("S06", "S08")
GIGABYTE_BOX_PAGES = range(23, 31)
LABEL_SEARCH_LINES = 2
MAX_HEADING_WORDS = 8
ANOMALY_LIST_SIZE = 5
BOX = "□"
ROMAN_NUMERAL = re.compile(r"x{0,3}(ix|iv|v?i{0,3})")
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
FOOTNOTE_REF = re.compile(r"\S(\*{1,3})|\(Note\)")
FOOTNOTE_BODY = re.compile(r"^\s*(\*{1,3}|\(Note\))")
SHARING_RULE = re.compile(r"shar\w*\s+(the\s+)?bandwidth", re.IGNORECASE)
CPU_SERIES = {"Ryzen 9000": r"\b9000\b", "Ryzen 8000": r"\b8000\b|8500/\s?8300|Phoenix",
              "Ryzen 7000": r"\b7000\b"}


# ---------------------------------------------------------------- helpers

def roman_to_int(text: str) -> int | None:
    """Convert a lowercase Roman numeral (i to xxxix) to an int; return None if `text` is not one.

    >>> roman_to_int("iv")
    4
    >>> roman_to_int("xiv")
    14
    >>> roman_to_int("viii")
    8
    >>> roman_to_int("vi")
    6
    >>> roman_to_int("iiii") is None
    True
    >>> roman_to_int("ROG") is None
    True
    >>> roman_to_int("") is None
    True
    """
    if not text or not ROMAN_NUMERAL.fullmatch(text):
        return None
    values = {"i": 1, "v": 5, "x": 10}
    subtractive_pairs = text.count("iv") + text.count("ix")
    return sum(values[char] for char in text) - 2 * subtractive_pairs


def parse_page_label(line: str) -> tuple[str, int] | None:
    """Parse a printed page label into (segment, number); return None if `line` is not a label.

    Segments: "arabic" for a bare number or a number between dashes, "roman" for a
    lowercase Roman numeral, "chapter-<c>" for chapter-page labels such as "1-14".
    Surrounding whitespace is ignored. Anything else is not a label.

    >>> parse_page_label("16")
    ('arabic', 16)
    >>> parse_page_label("- 9 -")
    ('arabic', 9)
    >>> parse_page_label("  vi ")
    ('roman', 6)
    >>> parse_page_label("1-14")
    ('chapter-1', 14)
    >>> parse_page_label("2-24")
    ('chapter-2', 24)
    >>> parse_page_label("ROG STRIX B650-A GAMING WIFI") is None
    True
    >>> parse_page_label("Chapter 1: Product Introduction") is None
    True
    >>> parse_page_label("3 kgf·cm") is None
    True
    """
    stripped = line.strip()
    if re.fullmatch(r"\d+", stripped):
        return ("arabic", int(stripped))
    dashed = re.fullmatch(r"-\s*(\d+)\s*-", stripped)
    if dashed:
        return ("arabic", int(dashed.group(1)))
    chapter = re.fullmatch(r"(\d+)-(\d+)", stripped)
    if chapter:
        return (f"chapter-{int(chapter.group(1))}", int(chapter.group(2)))
    number = roman_to_int(stripped)
    if number is not None:
        return ("roman", number)
    return None


def overlap_len(first: str, second: str) -> int:
    """Length of the longest suffix of `first` that is also a prefix of `second`.

    >>> overlap_len("abcdef", "defgh")
    3
    >>> overlap_len("abc", "xyz")
    0
    >>> overlap_len("aaaa", "aaab")
    3
    >>> overlap_len("", "abc")
    0
    >>> overlap_len("abc", "abc")
    3
    """
    limit = min(len(first), len(second))
    for size in range(limit, 0, -1):
        if first[-size:] == second[:size]:
            return size
    return 0


def letters(text: str) -> int:
    return sum(ch.isalpha() for ch in text)


def heading(text: str) -> str:
    """First line that is not a page label or the ASUS running header, cut to eight words."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not parse_page_label(stripped) and not stripped.startswith("ROG STRIX"):
            return " ".join(stripped.split()[:MAX_HEADING_WORDS])
    return ""


# ---------------------------------------------------------------- loading

def load_records() -> dict[str, list[dict]]:
    return {path.stem.split("_")[-1]: [json.loads(line) for line in path.open(encoding="utf-8")]
            for path in sorted(PROCESSED_DIR.glob("prepared_text_S0*.jsonl"))}


def page_ranges() -> dict[str, tuple[int, int]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {r["source_id"]: tuple(r["page_range"]) for r in manifest["records"] if r.get("page_range")}


def by_page(records: list[dict]) -> dict[int, list[dict]]:
    pages: dict[int, list[dict]] = defaultdict(list)
    for record in records:
        pages[record["page"]].append(record)
    return dict(pages)


# ---------------------------------------------------------------- checks

def report_population(data: dict[str, list[dict]]) -> None:
    print("== Population")
    for sid, records in data.items():
        unit = "chunks" if sid in MANUAL_IDS else "spec fields"
        print(f"{sid}: {len(records)} {unit}")
    manual = sum(len(data[s]) for s in MANUAL_IDS)
    amd = sum(len(data[s]) for s in AMD_IDS)
    print(f"Total: {manual + amd} records ({manual} manual chunks, {amd} AMD spec fields)\n")


def select_sample(data: dict[str, list[dict]], box_page: int) -> None:
    print("== Sample (purposive + seeded random)")
    purposive = []
    pages = dict(PURPOSIVE_PAGES)
    pages["S02"] = pages["S02"] + (box_page,)
    for sid, wanted in pages.items():
        first_chunks = {r["page"]: r for r in data[sid] if r["chunk_index"] == 1}
        purposive += [first_chunks[p]["record_id"] for p in wanted]
    for sid in PURPOSIVE_AMD:
        for record in data[sid]:
            field = record["spec_field"] or ""
            if "Codename" in field or ("PCIe" in field and "Lanes" in field):
                purposive.append(record["record_id"])
    pool = sorted(r["record_id"] for s in MANUAL_IDS for r in data[s] if r["record_id"] not in purposive)
    randoms = sorted(random.Random(SAMPLE_SEED).sample(pool, RANDOM_SAMPLE_SIZE))
    print(f"Purposive ({len(purposive)}): {', '.join(purposive)}")
    print(f"Random, seed {SAMPLE_SEED} ({len(randoms)}): {', '.join(randoms)}\n")


def report_reused_checks(data: dict[str, list[dict]], ranges: dict[str, tuple[int, int]]) -> None:
    print("== Reused Topic 3 checks (all records)")
    missing = []
    for sid, records in data.items():
        for r in records:
            base_ok = all(r.get(k) for k in ("source_id", "doc_title", "revision"))
            if sid in MANUAL_IDS:
                low, high = ranges[sid]
                locator_ok = isinstance(r["page"], int) and low <= r["page"] <= high
            else:
                locator_ok = bool(r["spec_field"])
            if not (base_ok and locator_ok):
                missing.append(r["record_id"])
    total = sum(len(v) for v in data.values())
    print(f"Locator + source metadata present: {total - len(missing)}/{total}; failures: {missing or 'none'}")
    manual = [r for s in MANUAL_IDS for r in data[s]]
    print(f"Max manual chunk length: {max(r['n_chars'] for r in manual)} chars")
    boxes = sum(r["text"].count(BOX) for v in data.values() for r in v)
    controls = sum(len(CONTROL_CHARS.findall(r["text"])) for v in data.values() for r in v)
    print(f"Residual {BOX} glyphs: {boxes}; residual control characters: {controls}\n")


def page_label(records: list[dict]) -> tuple[str, int] | None:
    first_lines = records[0]["text"].strip().splitlines()[:LABEL_SEARCH_LINES]
    for line in first_lines:
        label = parse_page_label(line)
        if label:
            return label
    return None


def check_v1_page_labels(data: dict[str, list[dict]]) -> None:
    print("== V1 (FR5): printed page label consistent with PDF page")
    for sid in MANUAL_IDS:
        labels = {page: page_label(recs) for page, recs in sorted(by_page(data[sid]).items())}
        offsets: dict[str, Counter] = defaultdict(Counter)
        for page, label in labels.items():
            if label:
                offsets[label[0]][page - label[1]] += 1
        expected = {segment: counts.most_common(1)[0][0] for segment, counts in offsets.items()}
        passed, failed, unverified = [], [], []
        for page, label in labels.items():
            if label is None:
                unverified.append(page)
            elif page - label[1] == expected[label[0]]:
                passed.append(page)
            else:
                failed.append((page, label))
        mapping = ", ".join(f"{seg}: PDF = printed + {off}" for seg, off in sorted(expected.items()))
        print(f"{sid}: pages {len(labels)} | pass {len(passed)} | fail {len(failed)} | N.V. {len(unverified)}")
        print(f"   mapping: {mapping}")
        print(f"   fails: {failed or 'none'}; N.V. pages: {unverified or 'none'}")
    print()


def footnote_levels(text: str) -> tuple[set[str], set[str]]:
    """Return (reference levels, body levels) in a chunk, e.g. ({'*', '(Note)'}, {'*'})."""
    refs: set[str] = set()
    bodies: set[str] = set()
    for line in text.splitlines():
        body = FOOTNOTE_BODY.match(line)
        if body:
            bodies.add(body.group(1))
            if body.group(1).startswith("*") and "**" in line[:12]:
                bodies.add("**")
            continue
        for match in FOOTNOTE_REF.finditer(line):
            refs.add(match.group(1) or "(Note)")
            if match.group(1) and "**" in line[match.end():match.end() + 4]:
                refs.add("**")
    return refs, bodies


def check_v2_footnotes(data: dict[str, list[dict]]) -> None:
    print("== V2 (NFR2): footnote reference and footnote body in the same chunk")
    for sid in MANUAL_IDS:
        pages = by_page(data[sid])
        links = passed = 0
        split, lost = [], []
        for page, records in sorted(pages.items()):
            levels = [footnote_levels(r["text"]) for r in records]
            for record, (refs, bodies) in zip(records, levels):
                for level in sorted(refs | bodies):
                    links += 1
                    if level in refs and level in bodies:
                        passed += 1
                        continue
                    missing_body = level in refs
                    other_has = any(level in (other_bodies if missing_body else other_refs)
                                    for (other_refs, other_bodies), other in zip(levels, records)
                                    if other is not record)
                    side = "body" if missing_body else "ref"
                    (split if other_has else lost).append(f"{record['record_id']} {level} missing {side}")
        print(f"{sid}: footnote links {links} | pass {passed} | split across chunks {len(split)} "
              f"| other half not found on page {len(lost)}")
        for item in split:
            print(f"   split: {item}")
        for item in lost:
            print(f"   review: {item}")
    print()


def report_uniqueness(data: dict[str, list[dict]]) -> None:
    print("== Uniqueness")
    texts = Counter(" ".join(r["text"].split()) for v in data.values() for r in v)
    dupes = {t: n for t, n in texts.items() if n > 1}
    print(f"Exact duplicate texts across all records: {len(dupes)} texts, {sum(dupes.values())} records")
    field_values = Counter()
    for sid in AMD_IDS:
        for r in data[sid]:
            field_values[r["text"].split(" | ", 1)[1]] += 1
    shared_all = sum(1 for n in field_values.values() if n == len(AMD_IDS))
    shared_some = sum(1 for n in field_values.values() if 1 < n < len(AMD_IDS))
    print(f"AMD section|field: value strings identical on all 6 pages: {shared_all}; on 2-5 pages: {shared_some}; "
          f"unique to one page: {sum(1 for n in field_values.values() if n == 1)}")
    for sid in MANUAL_IDS:
        total = sum(r["n_chars"] for r in data[sid])
        repeated = sum(overlap_len(a["text"], b["text"])
                       for recs in by_page(data[sid]).values() for a, b in zip(recs, recs[1:]))
        print(f"{sid}: overlap repeats {repeated} of {total} chars ({100 * repeated / total:.1f}%)")
    print()


def report_anomalies(data: dict[str, list[dict]]) -> None:
    print("== Anomalies (manual chunks)")
    manual = [r for s in MANUAL_IDS for r in data[s]]
    shortest = sorted(manual, key=lambda r: r["n_chars"])[:ANOMALY_LIST_SIZE]
    print("Shortest: " + ", ".join(f"{r['record_id']} ({r['n_chars']} chars)" for r in shortest))
    ratio = sorted(manual, key=lambda r: letters(r["text"]) / max(r["n_chars"], 1))[:ANOMALY_LIST_SIZE]
    print("Lowest letter ratio: " + ", ".join(
        f"{r['record_id']} ({letters(r['text']) / r['n_chars']:.2f})" for r in ratio) + "\n")


def report_coverage(data: dict[str, list[dict]]) -> None:
    print("== Coverage (manual chunks mentioning each CPU series / a lane-sharing rule)")
    for sid in MANUAL_IDS:
        counts = {name: sum(1 for r in data[sid] if re.search(pattern, r["text"]))
                  for name, pattern in CPU_SERIES.items()}
        sharing = [r["record_id"] for r in data[sid] if SHARING_RULE.search(r["text"])]
        print(f"{sid}: {counts} | sharing-rule chunks: {sharing or 'none'}")
    print()


def gigabyte_box_pages() -> dict[int, tuple[int, int, int]]:
    """Per page: (box tokens dropped, letters inside dropped tokens, letters in raw text)."""
    reader = PdfReader(RAW_DIR / "manuals" / "mb_manual_b650-aorus-elite-ax_1204_e.pdf")
    result = {}
    for page in GIGABYTE_BOX_PAGES:
        raw = reader.pages[page - 1].extract_text() or ""
        dropped = [token for token in raw.split() if BOX in token]
        result[page] = (len(dropped), sum(letters(t) for t in dropped), letters(raw))
    return result


def report_box_stripping(data: dict[str, list[dict]], box_stats: dict[int, tuple[int, int, int]]) -> None:
    print(f"== Pipeline-induced loss: Gigabyte pp. {GIGABYTE_BOX_PAGES.start}-{GIGABYTE_BOX_PAGES.stop - 1} "
          f"({BOX} token stripping)")
    pages = by_page(data["S02"])
    for page, (tokens, lost_letters, raw_letters) in box_stats.items():
        recs = pages.get(page, [])
        kept = sum(letters(r["text"]) for r in recs) - sum(
            letters(a["text"][len(a["text"]) - overlap_len(a["text"], b["text"]):]) for a, b in zip(recs, recs[1:]))
        title = heading(recs[0]["text"]) if recs else "(no records)"
        print(f"p.{page}: {tokens} tokens dropped, {lost_letters} letters inside them | "
              f"raw letters {raw_letters}, prepared letters {kept} | heading: {title}")
    print()


def main() -> None:
    data = load_records()
    box_stats = gigabyte_box_pages()
    unsampled = [p for p in box_stats if p not in PURPOSIVE_PAGES["S02"]]
    box_page = max(unsampled, key=lambda p: box_stats[p][0])
    report_population(data)
    select_sample(data, box_page)
    report_reused_checks(data, page_ranges())
    check_v1_page_labels(data)
    check_v2_footnotes(data)
    report_uniqueness(data)
    report_anomalies(data)
    report_coverage(data)
    report_box_stripping(data, box_stats)


if __name__ == "__main__":
    main()
