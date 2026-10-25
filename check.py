#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pysbd==0.3.4", "httpx==0.28.1"]
# ///
"""Gate checks for the jp-essay skill: check.py <gate> <dir>. Exit 0 and PASS = gate passed.
Gates check what a script can see (format, length, links, verbatim quotes, mechanical AI tells);
taste belongs to the reader and editor subagents."""

import difflib
import re
import sys
import warnings as pywarnings
from pathlib import Path

import httpx

pywarnings.filterwarnings("ignore", category=SyntaxWarning)  # pysbd 0.3.4 regex escapes
import pysbd  # noqa: E402

LANGS = ("en", "pt")

# Mechanical AI tells. Each entry is a regex matched case-insensitively on the essay body.
TELLS = {
    "en": {
        "AI vocabulary": r"\b(delve[sd]?|tapestry|testament to|pivotal|underscores?|showcas\w*|foster\w*|garner\w*|"
                         r"multifaceted|intricate|interplay|realm|landscape of|ever-evolving|seamless\w*|"
                         r"leverag\w*|utiliz\w*|crucial|vibrant|enduring legacy|navigat\w* the complexit\w*)\b",
        "filler phrase": r"\b(it is important to note|it should be noted|it's worth noting|needless to say|"
                         r"in today's world|throughout history|at the end of the day|it goes without saying|"
                         r"in conclusion|in this essay|plays a (crucial|key|vital|pivotal) role|in order to|"
                         r"due to the fact that)\b",
        "stock opener": r"(^|[.!?]\s+)(here's the thing|the truth is|make no mistake|let's dive|let's be clear|"
                        r"imagine a world|in a world where|picture this)\b",
        "fancy 'is'": r"\b(serves as|stands as|acts as a testament)\b",
        "'not X but Y'": r"\bnot (just|only|merely|simply)\b[^.!?]{0,80}\bbut\b|"
                         r"\b(isn't|is not|wasn't|was not)\b[^.!?;]{1,60}[;,.]\s*(it's|it is|it was)\b",
    },
    "pt": {
        "AI vocabulary": r"\b(tapeçaria|testemunho de|crucial|multifacetad\w*|intrincad\w*|"
                         r"cenário em constante|alavanc\w*|potencializ\w*|vibrante|legado duradouro|"
                         r"mergulh\w* (fundo|profundamente)|desbrav\w*)\b",
        "filler phrase": r"(é importante (ressaltar|notar|destacar)|vale (ressaltar|destacar|lembrar)|"
                         r"nos dias (de hoje|atuais)|ao longo da história|desnecessário dizer|em conclusão|"
                         r"no final das contas|neste ensaio|papel (fundamental|crucial)|é válido lembrar|"
                         r"a fim de que|devido ao fato de)",
        "stock opener": r"(^|[.!?]\s+)(a verdade é que|não se engane|imagine um mundo|vamos mergulhar)\b",
        "fancy 'is'": r"\b(serve como|figura como|se configura como)\b",
        "'not X but Y'": r"\bnão (é |era |foi |são )?(apenas|só|somente|meramente)\b[^.!?]{0,80}\bmas\b|"
                         r"\bnão (é|era|foi)\b[^.!?;]{1,60}[;,.]\s*(é|era|foi)\b",
    },
}
SUMMARY_CLOSE = {"en": r"^(in short|in sum|ultimately|in the end|all in all|to sum up|overall)\b",
                 "pt": r"^(em suma|em resumo|no fim|enfim|em última análise|portanto, em)\b"}

failures: list[str] = []
warnings: list[str] = []
fail, warn = failures.append, warnings.append


def read(d: Path, name: str) -> str:
    p = d / name
    if not p.exists():
        fail(f"{name} is missing")
        return ""
    return p.read_text(encoding="utf-8")


def meta(d: Path) -> dict[str, str]:
    text = read(d, "question.md")
    out = {}
    for key in ("Question", "Reader", "Words", "Language", "Style"):
        if m := re.search(rf"^{key}:\s*(.+)$", text, re.M):
            out[key.lower()] = m.group(1).strip()
        elif key != "Style":
            fail(f"question.md lacks a '{key}:' line")
    return out


def scientific(m: dict[str, str]) -> bool:
    """A `Style:` line is jp-essay-scientific: cited sources and a References section."""
    return bool(m.get("style"))


def target(m: dict[str, str]) -> int:
    return int(m["words"]) if m.get("words", "").isdigit() else 1000


def lang(m: dict[str, str]) -> str:
    base = m.get("language", "en").split("-")[0].lower()
    return base if base in LANGS else "en"


def words(text: str) -> int:
    return len(re.findall(r"[\w'’-]+", re.sub(r"\[@[\w-]+\]", "", text)))


def sentences(text: str, language: str) -> list[str]:
    seg = pysbd.Segmenter(language={"pt": "es"}.get(language, language), clean=False)  # pysbd has no pt
    return [s.strip() for s in seg.segment(text) if s.strip()]


def norm(s: str) -> str:
    s = re.sub(r"\[@[\w-]+\]", "", s).translate(str.maketrans("‘’“”«»", "''\"\"\"\""))
    return re.sub(r"\s+", " ", s).strip().lower()


def split_refs(text: str) -> tuple[str, str]:
    parts = re.split(r"^##\s*(?:References|Referências)\s*$", text, maxsplit=1, flags=re.M | re.I)
    return parts[0], parts[1] if len(parts) > 1 else ""


FOOTNOTE_DEF = r"^\[\^([\w-]+)\]:\s*"


def blocks(text: str) -> list[str]:
    body, _ = split_refs(text)
    body = re.sub(r"\A# [^\n]*\n", "", body)  # the title line, even when no blank line follows
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def paragraphs(text: str) -> list[str]:
    """Body paragraphs, without footnote definitions or footnote markers."""
    return [re.sub(r"\[\^[\w-]+\]", "", p) for p in blocks(text) if not re.match(FOOTNOTE_DEF, p)]


def footnotes(text: str) -> dict[str, str]:
    notes = "\n".join(p for p in blocks(text) if re.match(FOOTNOTE_DEF, p))
    parts = re.split(FOOTNOTE_DEF, notes, flags=re.M)[1:]
    return {parts[i]: " ".join(parts[i + 1].split()) for i in range(0, len(parts), 2)}


def source_ids(d: Path) -> dict[str, dict[str, str]]:
    out = {}
    for e in re.split(r"^## ", read(d, "sources.md"), flags=re.M)[1:]:
        sid = e.splitlines()[0].strip()
        fields = {k.lower(): v.strip() for k, v in re.findall(r"^(Link|Cite|Reference):\s*(.+)$", e, re.M)}
        notes = re.split(r"^Notes:\s*$", e, maxsplit=1, flags=re.M)
        fields["notes"] = notes[1] if len(notes) > 1 else ""
        out[sid] = fields
    return out


def outline_range(m: dict[str, str]) -> tuple[int, int]:
    """Points the outline may have: one per 80 to 250 target words, never fewer than three."""
    t = target(m)
    return max(3, round(t / 250)), max(4, round(t / 80))


# ---- shared checks ----------------------------------------------------------

def check_body(text: str, m: dict[str, str], name: str) -> list[str]:
    """Structure, tells and source markers shared by the draft and the final essay. Returns paragraphs."""
    language = lang(m)
    body, refs = split_refs(text)
    for line in re.sub(r"\A# [^\n]*\n", "", body).splitlines():
        if line.startswith("#"):
            fail(f"{name}: heading inside the body: '{line[:60]}'")
    paras = paragraphs(text)
    prose = "\n\n".join(paras)
    has_markers = re.search(r"\[@[\w-]+\]", prose)
    if has_markers and not scientific(m):
        fail(f"{name}: carries [@id] source markers, which only a scientific essay has")
    if refs and not scientific(m):
        fail(f"{name}: has a References section, which only a scientific essay has")
    check_tells(prose, language, name)
    notes = footnotes(text)
    markers = {mk for p in blocks(text) if not re.match(FOOTNOTE_DEF, p) for mk in re.findall(r"\[\^([\w-]+)\]", p)}
    for fid in sorted(markers - set(notes)):
        fail(f"{name}: footnote marker [^{fid}] has no definition")
    for fid in sorted(set(notes) - markers):
        fail(f"{name}: footnote [^{fid}] is defined but never marked in the text")
    if notes:
        check_tells("\n\n".join(notes.values()), language, f"{name} footnotes")
        if (n := words(" ".join(notes.values()))) > 0.2 * target(m):
            fail(f"{name}: footnotes run {n} words, over a fifth of the target; cut to what a curious reader would check")
    for k, p in enumerate(paras, 1):
        figures = [f for f in re.findall(r"\d[\d,.]*%?", p) if not re.fullmatch(r"(1[89]|20)\d\d", f)]
        if len(figures) > 5:
            warn(f"{name}: paragraph {k} carries {len(figures)} figures; keep those the reader would repeat, footnote the rest")
    return paras


def check_tells(prose: str, language: str, name: str) -> None:
    own = re.sub(r"[\"“][^\"“”]*[\"”]", '"…"', prose)  # quoted source text is not the author's choice
    for label, pattern in TELLS[language].items():
        for hit in sorted({m.group(0).strip() for m in re.finditer(pattern, own, re.I | re.M)}):
            fail(f"{name}: {label}: '{hit[:60]}'")
    for dash in sorted(set(re.findall(r"—|\s–\s|\s--\s", prose))):
        fail(f"{name}: dash '{dash.strip()}' used as punctuation; use a period or a comma")
    sents = sentences(prose, language)
    seen = set()
    for s in sents:
        key = re.sub(r"\W+", " ", norm(s)).strip()
        if key in seen:
            fail(f"{name}: duplicated sentence '{s[:60]}…'")
        seen.add(key)
    sents = [s for s in sents if s.split()]
    openers = [s.split()[0].lower().strip(",.;:\"'") for s in sents]
    for i in range(len(openers) - 2):
        if openers[i] == openers[i + 1] == openers[i + 2] and (i == 0 or openers[i - 1] != openers[i]):
            fail(f"{name}: three sentences in a row open with '{openers[i]}', from '{sents[i][:50]}…'")
    for s in sents:
        if words(s) > 40:
            warn(f"{name}: {words(s)}-word sentence '{s[:60]}…'")
    for q in re.findall(r"(?:^|[.!]\s+)([A-Z][^.?!\n]{0,40}\?)\s+[A-Z]", prose, re.M):
        warn(f"{name}: staged run-up '{q}'; state the point directly")
    for i, p in enumerate(prose.split("\n\n"), 1):
        tail = sentences(p, language)[-1:] if p.strip() else []
        if tail and words(tail[0]) <= 4 and len(sentences(p, language)) > 1:
            warn(f"{name} paragraph {i}: ends on the fragment '{tail[0]}'; is it earning the weight?")
    if (n := prose.count("(")) > 3:
        warn(f"{name}: {n} parentheses; fold the aside into the sentence or cut it")
    if re.search(r"[“”‘’]", prose):
        warn(f"{name}: curly quotes; use straight quotes")
    last = prose.split("\n\n")[-1] if prose else ""
    if re.match(SUMMARY_CLOSE[language], last, re.I):
        fail(f"{name}: the last paragraph opens as a summary ('{last[:30]}…'); end on the point, not a recap")


def check_quotes(prose: str, ids: dict, name: str) -> None:
    notes = norm(" ".join(f["notes"] for f in ids.values()))
    for q in re.findall(r"[\"“]([^\"“”]+)[\"”]", prose):
        if words(q) >= 5 and norm(q).strip(" .,;:") not in notes:
            fail(f"{name}: quotation not in any source's notes: '{q[:60]}…'")


def check_length(prose: str, low: float, high: float, name: str) -> None:
    n = words(prose)
    if not low <= n <= high:
        fail(f"{name}: {n} words, needs {round(low)}–{round(high)}")


# ---- gates ------------------------------------------------------------------

def gate_question(d: Path) -> None:
    m = meta(d)
    if m.get("question") and not m["question"].endswith("?"):
        fail("question.md: Question must end with '?'")
    if m.get("language", "").split("-")[0].lower() not in LANGS:
        fail(f"question.md: Language must be one of {', '.join(LANGS)}")
    if not m.get("words", "").isdigit() or int(m["words"]) < 500:
        fail("question.md: Words must be a number ≥ 500")


def gate_sources(d: Path) -> None:
    ids = source_ids(d)
    m = meta(d)
    if len(ids) < 3:
        fail(f"sources.md: {len(ids)} sources, needs ≥ 3")
    with httpx.Client(follow_redirects=True, timeout=20, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for sid, f in ids.items():
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", sid):
                fail(f"source '{sid}': id must be short kebab case")
            if words(f["notes"]) < 30:
                fail(f"source '{sid}': Notes need ≥ 30 words")
            link = re.sub(r"^doi:\s*", "", f.get("link", ""), flags=re.I)
            if link.startswith("10."):
                link = f"https://doi.org/{link}"
            if link.startswith(("/", "~")):
                if not Path(link).expanduser().exists():
                    fail(f"source '{sid}': local file {link} does not exist")
                if scientific(m):
                    fail(f"source '{sid}': a scientific essay cites published sources, not local files")
                continue
            if link == "conversation":
                if scientific(m):
                    fail(f"source '{sid}': a scientific essay cites published sources, not the conversation")
                continue
            if scientific(m):
                for key in ("cite", "reference"):
                    if not f.get(key):
                        fail(f"source '{sid}': no '{key.title()}:' line")
            if not link.startswith("http"):
                fail(f"source '{sid}': Link must be a URL, DOI, local path or 'conversation', got '{link}'")
                continue
            try:
                r = client.get(link)
            except httpx.HTTPError as exc:
                fail(f"source '{sid}': link unreachable ({type(exc).__name__})")
                continue
            if r.status_code in (401, 403, 429):
                warn(f"source '{sid}': link returned HTTP {r.status_code} (bot wall); verify by hand")
            elif r.status_code >= 400:
                fail(f"source '{sid}': link returns HTTP {r.status_code}")
            elif "pdf" not in r.headers.get("content-type", ""):
                # Title: after "(Year)." in APA; after the "SURNAME, Name." author block in ABNT.
                ref = f.get("reference", "")
                title = (re.search(r"\(\d{4}[a-z]?\)\.\s*([^.]+)", ref)
                         or re.match(r"[A-ZÀ-Ý][A-ZÀ-Ý' -]+,[^.]+\.\s*([^.:]+)", ref))
                title_words = re.findall(r"[A-Za-zÀ-ÿ]{5,}", title.group(1) if title else "")
                page = r.text.lower()
                hits = sum(w.lower() in page for w in set(title_words))
                if len(set(title_words)) >= 2 and hits < 2:
                    fail(f"source '{sid}': page shows {hits} of the title's words; wrong link?")


def check_outline(d: Path, name: str) -> list[str]:
    m = meta(d)
    text = read(d, name)
    thesis = re.search(r"^Thesis:\s*(.+)$", text, re.M)
    if not thesis or not re.search(r"[.?!]$", thesis.group(1)):
        fail(f"{name}: needs a 'Thesis:' line holding one full sentence")
    points = re.findall(r"^\d+\.\s+(.+)$", text, re.M)
    low, high = outline_range(m)
    if not low <= len(points) <= high:
        fail(f"{name}: {len(points)} points, needs {low}–{high} for {target(m)} words")
    for i, p in enumerate(points, 1):
        claim = re.sub(r"\s*\[[\w, -]+\]\s*$", "", p)
        if not re.search(r"[.?!]$", claim) or words(claim) < 4:
            fail(f"{name} point {i}: must be a full sentence ending in . ? or !")
    ids = set(source_ids(d))
    for sid in sorted({s.strip() for group in re.findall(r"\[([\w, -]+)\]\s*$", text, re.M)
                       for s in group.split(",")} - ids):
        fail(f"{name}: [{sid}] matches no source in sources.md")
    return points


def gate_outline(d: Path) -> None:
    check_outline(d, "outline.md")


def gate_draft(d: Path) -> None:
    m = meta(d)
    t = target(m)
    text = read(d, "draft.md")
    paras = check_body(text, m, "draft.md")
    check_length(" ".join(paras), t, 1.15 * t, "draft.md")
    if scientific(m):
        ids = source_ids(d)
        markers = set(re.findall(r"\[@([\w-]+)\]", text))
        if not markers:
            fail("draft.md: no [@id] source markers")
        for sid in sorted(markers - set(ids)):
            fail(f"draft.md: marker [@{sid}] matches no source in sources.md")


READER_SECTIONS = ("Recall", "Claim", "Lost", "Stop", "Unclear", "Enjoyed", "Remember", "Doubt")


def gate_recall(d: Path) -> None:
    m = meta(d)
    language = lang(m)
    text = read(d, "reader.md")
    sections = dict(re.findall(r"^##\s*(\w+)\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S))
    for sec in READER_SECTIONS:
        if not sections.get(sec, "").strip():
            fail(f"reader.md: no '## {sec}' section, or it is empty")
    recall = re.findall(r"^\d+\.\s+(.+)$", sections.get("Recall", ""), re.M)
    paras = paragraphs(read(d, "draft.md"))
    if len(recall) != len(paras):
        fail(f"reader.md: {len(recall)} recall sentences for {len(paras)} paragraphs in draft.md")
    draft = {norm(s) for s in sentences(" ".join(paras), language)}
    remembered = sections.get("Remember", "")
    copied = [s for s in sentences(" ".join(recall) + " " + sections.get("Claim", ""), language)
              if norm(s) in draft and norm(s) not in norm(remembered)]
    if copied:
        fail(f"reader.md: {len(copied)} recall sentences copied verbatim from draft.md; recall in your own words")


def gate_outline2(d: Path) -> None:
    m = meta(d)
    t = target(m)
    points = check_outline(d, "outline-2.md")
    paras = check_body(read(d, "draft-2.md"), m, "draft-2.md")
    if len(paras) != len(points):
        fail(f"draft-2.md: {len(paras)} paragraphs for {len(points)} outline-2.md points")
    check_length(" ".join(paras), t, 1.15 * t, "draft-2.md")


def quoted_field(block: str, key: str) -> str:
    m = re.search(rf'^\s*{key}:\s*"(.*)"\s*$', block, re.M)
    return m.group(1).replace('\\"', '"') if m else ""  # tolerate backslash-escaped quotes


def gate_rewrite(d: Path) -> None:
    draft2 = norm(read(d, "draft-2.md"))
    final = norm(read(d, "final.md"))
    entries = re.split(r"^\d+\.\s+(?=Span:)", read(d, "edits.md").split("## Unsupported")[0], flags=re.M)[1:]
    if not entries:
        fail("edits.md: no numbered 'Span:' entries")
    blocks = re.split(r"^###\s*\d+\s*$", read(d, "rewrites.md"), flags=re.M)[1:]
    if len(blocks) != len(entries):
        fail(f"rewrites.md: {len(blocks)} blocks for {len(entries)} edits.md entries")
    for k, b in enumerate(blocks, 1):
        span = quoted_field(b, "Span")
        if not span:
            fail(f'rewrites.md block {k}: no \'Span: "…"\' line')
        elif norm(span) not in draft2:
            fail(f"rewrites.md block {k}: the span is not in draft-2.md: '{span[:50]}'")
        if rejected := re.search(r"^Rejected:\s*(.+)$", b, re.M):
            if words(rejected.group(1)) < 4:
                fail(f"rewrites.md block {k}: give the reason the span stands, not a label")
            continue
        versions = [v.strip() for v in re.findall(r"^- v\d+:\s*(.+)$", b, re.M)]
        if len(versions) < 3:
            fail(f"rewrites.md block {k}: {len(versions)} versions, needs ≥ 3 or a 'Rejected:' reason")
        elif max(difflib.SequenceMatcher(None, norm(a), norm(c), autojunk=False).ratio()
                 for j, a in enumerate(versions) for c in versions[j + 1:]) > 0.9:
            fail(f"rewrites.md block {k}: two versions differ only cosmetically")
        chosen = re.search(r"^Chosen:\s*(.+)$", b, re.M)
        if not chosen:
            fail(f"rewrites.md block {k}: no 'Chosen:' line")
        elif chosen.group(1).strip() == "FOOTNOTE":
            if span and norm(span) in norm(" ".join(paragraphs(read(d, "final.md")))):
                fail(f"rewrites.md block {k}: chose FOOTNOTE but the span is still in final.md's body")
        elif chosen.group(1).strip() == "DELETE":
            if span and norm(span) in final:
                fail(f"rewrites.md block {k}: chose DELETE but the span is still in final.md")
        elif norm(chosen.group(1).strip().strip('"')) not in final:
            fail(f"rewrites.md block {k}: the chosen version is not in final.md")


def gate_final(d: Path) -> None:
    m = meta(d)
    t = target(m)
    text = read(d, "final.md")
    ids = source_ids(d)
    if not re.match(r"# \S", text):
        fail("final.md: first line must be a '# ' title")
    elif words(text.splitlines()[0]) > 9:
        fail("final.md: title over eight words")
    paras = check_body(text, m, "final.md")
    prose = " ".join(paras)
    body, refs = split_refs(text)
    if scientific(m):
        if not refs.strip():
            fail("final.md: no '## References' section")
        if leftover := re.findall(r"\[@[\w-]+\]", body):
            fail(f"final.md: {len(leftover)} [@id] markers not converted to citations")
        for f in ids.values():  # in-text citations do not count toward the length
            if f.get("cite"):
                prose = prose.replace(f["cite"], "")
        cited = [sid for sid, f in ids.items() if f.get("cite") and f["cite"] in body]
        if not cited:
            fail("final.md: cites no source from sources.md")
        for sid in cited:
            if norm(ids[sid].get("reference", "")) not in norm(refs):
                fail(f"final.md: {sid} is cited but its Reference line is not in References")
        allowed = {norm(ids[sid].get("reference", "")) for sid in cited}
        for line in refs.splitlines():
            if line.strip() and norm(line.lstrip("-* ")) not in allowed:
                fail(f"final.md: References line matches no cited source: '{line.strip()[:60]}'")
    check_length(prose, 0.9 * t, t, "final.md")  # the length is a ceiling
    check_quotes(" ".join(paras + list(footnotes(text).values())), ids, "final.md")


def gate_facts(d: Path) -> None:
    """facts.md: every factual claim in final.md checked against the notes, never restyled."""
    ids = set(source_ids(d))
    final = norm(" ".join(paragraphs(read(d, "final.md")) + list(footnotes(read(d, "final.md")).values())))
    entries = re.split(r"^\d+\.\s+(?=Claim:)", read(d, "facts.md"), flags=re.M)[1:]
    if not entries:
        fail("facts.md: no numbered 'Claim:' entries")
    for k, e in enumerate(entries, 1):
        claim = quoted_field(e, "Claim")
        verdict = re.search(r"^Verdict:\s*(supported|fixed|cut)\b", e, re.M)
        if not claim:
            fail(f'facts.md entry {k}: no \'Claim: "…"\' line')
        if not verdict:
            fail(f"facts.md entry {k}: Verdict must be supported, fixed or cut")
            continue
        v = verdict.group(1)
        if v in ("supported", "fixed"):
            srcs = {x.strip() for x in re.findall(r"^Source:\s*(.+)$", e, re.M)[:1] for x in x.split(",")}
            if not srcs:
                fail(f"facts.md entry {k}: a {v} claim needs a 'Source:' id")
            for sid in sorted(srcs - ids):
                fail(f"facts.md entry {k}: source '{sid}' is not in sources.md")
        if v == "supported" and claim and norm(claim) not in final:
            fail(f"facts.md entry {k}: the supported claim is not in final.md: '{claim[:50]}'")
        if v == "cut" and claim and norm(claim) in final:
            fail(f"facts.md entry {k}: marked cut but still in final.md: '{claim[:50]}'")


GATES = {name[5:]: fn for name, fn in globals().items() if name.startswith("gate_")}


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in GATES:
        sys.exit(f"usage: check.py <{'|'.join(GATES)}> <dir>")
    gate, d = sys.argv[1], Path(sys.argv[2]).expanduser()
    GATES[gate](d)
    for w in warnings:
        print(f"WARN  {w}")
    for f in failures:
        print(f"FAIL  {f}")
    print(f"{gate}: {'FAIL' if failures else 'PASS'} ({len(failures)} failures, {len(warnings)} warnings)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
