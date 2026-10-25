# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest==8.3.4", "pysbd==0.3.4", "httpx==0.28.1"]
# ///
"""Fixture tests for check.py. Run: uv run --script test_check.py"""

import subprocess
import sys
from pathlib import Path

import pytest

CHECK = Path(__file__).with_name("check.py")
WORDS = 1000

SENTENCES = [
    "Resolutions fail because they ask for a new identity overnight.",
    "Habits resist that.",
    "A smoker of twenty years does not wake up changed on the first of January, whatever the calendar promises.",
    "The cue stays.",
    "So does the reward the old routine delivered for years.",
    "Willpower is a poor replacement for a changed kitchen.",
    "Most people learn this by February.",
]
LABELS = ["amber", "birch", "cedar", "delta", "ember", "fjord", "grove", "heron", "iris", "juniper",
          "kestrel", "linden", "maple", "nectar", "onyx", "pine", "quartz", "rowan", "sage", "tern"]


def para(i: int, extra: str = "") -> str:
    s = [f"{v.rstrip('.')} near {LABELS[i]}." for v in SENTENCES]
    s[2] = s[2].rstrip(".") + f"{extra}."
    return " ".join(s)


def essay(n_words: int = 1050, extra: str = "") -> str:
    per = len(para(0).split())
    return "\n\n".join(para(i, extra) for i in range(round(n_words / per)))


def write(d: Path, name: str, text: str) -> None:
    (d / name).parent.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(text, encoding="utf-8")


def run(gate: str, d: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(CHECK), gate, str(d)], capture_output=True, text=True)


NOTES = "Habits are loops of cue, routine and reward. " * 4 + '"keystone habits start a process that transforms everything"'


@pytest.fixture
def d(tmp_path: Path) -> Path:
    """A plain essay folder whose sources need no network."""
    write(tmp_path, "question.md",
          f"Question: Why do resolutions fail?\nReader: a curious friend\nWords: {WORDS}\nLanguage: en\n")
    write(tmp_path, "me.md", "notes")
    src = "".join(f"## {sid}\nLink: {link}\nNotes:\n{NOTES}\n\n" for sid, link in
                  [("duhigg-2012", str(tmp_path / "me.md")), ("clear-2018", "conversation"),
                   ("wood-2019", "conversation")])
    write(tmp_path, "sources.md", src)
    write(tmp_path, "outline.md", "Thesis: Resolutions fail because they skip the cue.\n\n"
          + "".join(f"{i}. Resolutions fail for reason number {i}. [duhigg-2012, clear-2018]\n" for i in range(1, 9)))
    return tmp_path


@pytest.fixture
def sci(d: Path) -> Path:
    write(d, "question.md",
          f"Question: Why do resolutions fail?\nReader: a psychology student\nWords: {WORDS}\nLanguage: en\nStyle: APA\n")
    write(d, "sources.md", "".join(
        f"## {sid}\nLink: https://example.invalid/{sid}\nCite: ({name}, {year})\n"
        f"Reference: {name}, C. ({year}). The power of habit. Random House.\nNotes:\n{NOTES}\n\n"
        for sid, name, year in [("duhigg-2012", "Duhigg", 2012), ("clear-2018", "Clear", 2018),
                                ("wood-2019", "Wood", 2019)]))
    return d


def test_question_pass(d):
    assert run("question", d).returncode == 0


def test_question_needs_reader_and_length(d):
    write(d, "question.md", "Question: Why?\nWords: 300\nLanguage: en\n")
    out = run("question", d).stdout
    assert "'Reader:'" in out and "≥ 500" in out


def test_sources_accept_local_files_and_conversation(d):
    r = run("sources", d)
    assert r.returncode == 0, r.stdout


def test_sources_reject_missing_local_file(d):
    write(d, "sources.md", (d / "sources.md").read_text().replace(str(d / "me.md"), "/nowhere/me.md"))
    assert "does not exist" in run("sources", d).stdout


def test_sources_unreachable_link(d):
    write(d, "sources.md", (d / "sources.md").read_text().replace("conversation", "https://example.invalid/x", 1))
    assert "unreachable" in run("sources", d).stdout


def test_scientific_sources_need_published_links(sci):
    write(sci, "sources.md", (sci / "sources.md").read_text().replace("https://example.invalid/clear-2018", "conversation"))
    assert "published sources" in run("sources", sci).stdout


def test_outline_pass(d):
    r = run("outline", d)
    assert r.returncode == 0, r.stdout


def test_outline_needs_thesis_range_and_known_ids(d):
    write(d, "outline.md", "1. Only one point is here. [ghost-1999]\n")
    out = run("outline", d).stdout
    assert "'Thesis:'" in out and "needs 4–12" in out and "[ghost-1999] matches no source" in out


def test_draft_pass(d):
    write(d, "draft.md", essay(1100))
    r = run("draft", d)
    assert r.returncode == 0, r.stdout


def test_draft_too_long(d):
    write(d, "draft.md", essay(1400))
    assert "needs 1000–1150" in run("draft", d).stdout


def test_tells_are_caught(d):
    bad = (para(0, ", and this is a testament to grit") + " It is not just a habit, but a way of life near x."
           + " The cue matters — always near y.")
    write(d, "draft.md", essay(1000) + "\n\n" + bad)
    out = run("draft", d).stdout
    assert "AI vocabulary: 'testament to'" in out
    assert "'not X but Y'" in out
    assert "dash '—'" in out


def test_tells_ignore_quoted_source_text(d):
    write(d, "draft.md", essay(1050, ', and Duhigg called it "a crucial and pivotal habit loop"'))
    assert "AI vocabulary" not in run("draft", d).stdout


def test_duplicate_sentences_and_openers(d):
    write(d, "draft.md", essay(1050) + "\n\nThe cue stays near amber. The cue stays near amber. The end comes. The rest.")
    out = run("draft", d).stdout
    assert "duplicated sentence" in out and "three sentences in a row open with 'the'" in out


def test_run_up_and_closing_fragment_warn(d):
    write(d, "draft.md", essay(1050) + "\n\nHe set a rule near zinc. And the result? It held near zinc for a decade. It held.")
    out = run("draft", d).stdout
    assert "staged run-up 'And the result?'" in out and "ends on the fragment 'It held.'" in out


def test_summary_close_fails(d):
    write(d, "final.md", "# Why resolutions fail\n\n" + essay(1000) + "\n\nIn short, habits win near zinc.")
    assert "opens as a summary" in run("final", d).stdout


def test_final_pass(d):
    write(d, "final.md", "# Why resolutions fail\n\n" + essay(950))
    r = run("final", d)
    assert r.returncode == 0, r.stdout


def test_final_fabricated_quote(d):
    write(d, "final.md", "# T\n\n" + essay(1050, ', as he said, "habits are the whole of character"'))
    assert "quotation not in any source's notes" in run("final", d).stdout


def test_final_verbatim_quote_passes(d):
    write(d, "final.md", "# T\n\n" + essay(1050, ', since "keystone habits start a process that transforms everything"'))
    assert "quotation not in" not in run("final", d).stdout


def test_plain_final_rejects_markers_and_references(d):
    write(d, "final.md", "# T\n\n" + essay(1050, " [@duhigg-2012]") + "\n\n## References\n\nDuhigg, C. (2012).\n")
    out = run("final", d).stdout
    assert "has a References section" in out and "carries [@id] source markers" in out


def test_scientific_draft_needs_known_markers(sci):
    write(sci, "draft.md", essay(1050, " [@ghost-1999]"))
    assert "[@ghost-1999] matches no source" in run("draft", sci).stdout


def test_scientific_final_pass(sci):
    body = essay(950, " (Duhigg, 2012)")
    write(sci, "final.md", f"# Why resolutions fail\n\n{body}\n\n## References\n\nDuhigg, C. (2012). The power of habit. Random House.\n")
    r = run("final", sci)
    assert r.returncode == 0, r.stdout


def test_scientific_final_reference_mismatch(sci):
    body = essay(1050, " (Duhigg, 2012)")
    write(sci, "final.md", f"# T\n\n{body}\n\n## References\n\nSomeone, A. (1999). Other book.\n")
    out = run("final", sci).stdout
    assert "Reference line is not in References" in out and "matches no cited source" in out


def test_scientific_final_leftover_markers(sci):
    write(sci, "final.md", "# T\n\n" + essay(1050, " [@duhigg-2012]") + "\n\n## References\n\nx\n")
    assert "markers not converted" in run("final", sci).stdout


def test_portuguese_tells(d):
    write(d, "question.md", f"Question: Por que resoluções falham?\nReader: um amigo\nWords: {WORDS}\nLanguage: pt\n")
    write(d, "draft.md", essay(1000) + "\n\nÉ importante ressaltar que não é apenas um hábito, mas uma vida.")
    out = run("draft", d).stdout
    assert "filler phrase" in out and "'not X but Y'" in out


def reader(n: int, copy: str = "") -> str:
    recall = "".join(f"{i}. Paragraph {i} argued that resolutions fail for its own reason.\n" for i in range(1, n + 1))
    return (f"## Recall\n{recall}{copy}\n## Claim\nHabits beat resolutions.\n## Lost\nNowhere.\n"
            "## Stop\nNowhere.\n## Unclear\nNothing.\n## Enjoyed\nThe amber cue.\n## Remember\nThe cue stays near amber.\n## Doubt\nThe kitchen claim.\n")


def test_recall_pass(d):
    text = essay(1050)
    write(d, "draft.md", text)
    write(d, "reader.md", reader(len(text.split("\n\n"))))
    r = run("recall", d)
    assert r.returncode == 0, r.stdout


def test_recall_count_copy_and_sections(d):
    text = essay(1050)
    write(d, "draft.md", text)
    write(d, "reader.md", reader(2, "3. The cue stays near birch.\n").replace("## Doubt\nThe kitchen claim.\n", ""))
    out = run("recall", d).stdout
    assert "recall sentences for" in out and "copied verbatim" in out and "'## Doubt'" in out


def test_outline2_pass_and_paragraph_mismatch(d):
    write(d, "outline-2.md", (d / "outline.md").read_text())
    ps = essay(1050).split("\n\n")
    text = "\n\n".join(" ".join(ps[i:i + 2]) for i in range(0, len(ps), 2))
    n = len(text.split("\n\n"))
    write(d, "draft-2.md", text)
    out = run("outline2", d).stdout
    assert f"{n} paragraphs for 8 outline-2.md points" in out
    write(d, "outline-2.md", "Thesis: Resolutions fail because they skip the cue.\n\n"
          + "".join(f"{i}. Resolutions fail for reason number {i}. [duhigg-2012]\n" for i in range(1, n + 1)))
    r = run("outline2", d)
    assert r.returncode == 0, r.stdout


def rewrite_files(d: Path, chosen: str, final_text: str) -> None:
    write(d, "draft-2.md", "Habits resist that near amber. Willpower is a poor replacement for a changed kitchen near amber.")
    write(d, "edits.md", '1. Span: "Habits resist that near amber."\n   Category: Sentence, 3\n   Replacement: DELETE\n   Gain: x\n'
          '2. Span: "a changed kitchen"\n   Category: Word, 2\n   Replacement: "a new kitchen"\n   Gain: y\n'
          "\n## Unsupported claims\nNone.\n")
    write(d, "rewrites.md", '### 1\nSpan: "Habits resist that near amber."\n- v1: Habits push back near amber.\n'
          f"- v2: The old routine fights any change you plan.\n- v3: DELETE\nChosen: {chosen}\n\n"
          '### 2\nSpan: "a changed kitchen"\nRejected: the kitchen is the concrete image the paragraph needs.\n')
    write(d, "final.md", final_text)


def test_rewrite_pass(d):
    rewrite_files(d, "DELETE", "# T\n\nWillpower is a poor replacement for a changed kitchen near amber.")
    r = run("rewrite", d)
    assert r.returncode == 0, r.stdout


def test_rewrite_chosen_must_reach_final(d):
    rewrite_files(d, "Habits push back near amber.", "# T\n\nWillpower is a poor replacement for a changed kitchen near amber.")
    assert "chosen version is not in final.md" in run("rewrite", d).stdout


def test_rewrite_needs_versions_and_matching_blocks(d):
    rewrite_files(d, "DELETE", "# T\n\nHabits resist that near amber.")
    write(d, "rewrites.md", '### 1\nSpan: "Habits resist that near amber."\n- v1: A b c.\n- v2: A b c!\nChosen: DELETE\n')
    out = run("rewrite", d).stdout
    assert "1 blocks for 2 edits.md entries" in out and "2 versions, needs ≥ 3" in out
    assert "chose DELETE but the span is still in final.md" in out


@pytest.fixture
def page():
    """A local web page whose body is set per test."""
    import http.server
    import threading

    body = {"html": b""}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body["html"])

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield body, f"http://127.0.0.1:{server.server_port}/"
    server.shutdown()


def abnt_source(d: Path, url: str) -> None:
    write(d, "question.md", "Question: Por quê?\nReader: um professor\nWords: 1000\nLanguage: pt\nStyle: ABNT\n")
    write(d, "sources.md", f"## duhigg-2012\nLink: {url}\nCite: (DUHIGG, 2012)\n"
          "Reference: DUHIGG, Charles. O poder do hábito: por que fazemos o que fazemos. Rio de Janeiro: Objetiva, 2012.\n"
          "Notes:\n" + "Hábitos são laços de gatilho, rotina e recompensa. " * 6 + "\n")


def test_abnt_title_matches_right_page(d, page):
    body, url = page
    body["html"] = "<h1>O poder do hábito</h1>".encode()
    abnt_source(d, url)
    assert "wrong link" not in run("sources", d).stdout


def test_abnt_title_flags_wrong_page(d, page):
    body, url = page
    body["html"] = b"<h1>Dinosaurs of the Triassic</h1>"
    abnt_source(d, url)
    assert "wrong link" in run("sources", d).stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


def test_footnotes_excluded_from_length_and_matched(d):
    text = essay(1050)
    first, rest = text.split("\n\n", 1)
    note = "Duhigg tracked one smoker for a year near amber."
    write(d, "draft.md", f"{first}[^1]\n\n{rest}\n\n[^1]: {note}")
    r = run("draft", d)
    assert r.returncode == 0, r.stdout
    write(d, "draft.md", f"{first}[^1][^2]\n\n{rest}\n\n[^1]: {note}\n[^3]: {note}")
    out = run("draft", d).stdout
    assert "[^2] has no definition" in out and "[^3] is defined but never marked" in out


def test_footnotes_capped_and_figures_warned(d):
    text = essay(1050)
    first, rest = text.split("\n\n", 1)
    write(d, "draft.md", f"{first} It cost 12%, 30, 41, 8, 9 and 7.5 points[^1].\n\n{rest}\n\n[^1]: " + "A long aside near amber. " * 50)
    out = run("draft", d).stdout
    assert "footnotes run" in out and "paragraph 1 carries 6 figures" in out


def test_final_over_target_fails(d):
    write(d, "final.md", "# Why resolutions fail\n\n" + essay(1100))
    assert "needs 900–1000" in run("final", d).stdout


def test_facts_pass_and_failures(d):
    text = essay(950)
    write(d, "final.md", "# Why resolutions fail\n\n" + text)
    first = text.split("\n\n")[0].split(". ")[0]
    write(d, "facts.md", f'1. Claim: "{first}"\nVerdict: supported\nSource: duhigg-2012\n\n'
          '2. Claim: "Resolutions fail in 99 percent of cases"\nVerdict: cut\n')
    r = run("facts", d)
    assert r.returncode == 0, r.stdout
    write(d, "facts.md", f'1. Claim: "{first.replace(chr(34), chr(92) + chr(34))}"\nVerdict: supported\nSource: duhigg-2012\n')
    assert run("facts", d).returncode == 0  # backslash-escaped quotes are tolerated
    write(d, "facts.md", '1. Claim: "Resolutions fail in 99 percent of cases"\nVerdict: supported\nSource: nobody-2020\n')
    out = run("facts", d).stdout
    assert "not in sources.md" in out and "not in final.md" in out
