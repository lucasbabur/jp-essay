<div align="center">

<img src="assets/icon.png" alt="jp-essay icon" width="180">

# jp-essay

**A Claude Code skill that runs Jordan Peterson's essay process, adapted to how models write.**

Question, reading list, outline, bad draft, outline from memory, reorder, rewrite, ask again.

[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-D97757?style=flat-square)](https://docs.claude.com/en/docs/claude-code/skills)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/runs_with-uv-DE5FE9?style=flat-square)](https://docs.astral.sh/uv/)
[![Languages](https://img.shields.io/badge/essays-en_%7C_pt-1F2A44?style=flat-square)](#usage)
[![npm](https://img.shields.io/npm/v/jp-essay?style=flat-square&color=CB3837)](https://www.npmjs.com/package/jp-essay)
[![License: MIT](https://img.shields.io/badge/license-MIT-8a857c?style=flat-square)](LICENSE)

**[Website](https://jpessay.com/)** · **[Read a sample essay](https://jpessay.com/sample.html)**

</div>

---

Peterson's [writing guide](https://essay.app/guide) is built for students, whose problem is skipping the work: no question, no reading, no outline, one draft. A model has the opposite problem. It does every step fluently and still produces generic prose: no claim worth arguing, no specifics, inflated words, hedged verdicts and an ending that summarizes. `jp-essay` keeps Peterson's steps and aims each one at the model's failure. A script checks every step, so the model can't skip one and say it's done, and no model grades the prose, because models asked to judge writing barely beat chance and reward overwriting.

> **Not affiliated with Jordan Peterson.** `jp-essay` is an independent project. Jordan B. Peterson has not reviewed or endorsed it. It is an iteration of the method in his writing guide, adapted for AI agents.

## Contents

- [How it works](#how-it-works)
- [Install](#install)
- [Usage](#usage)
- [Scientific edition](#scientific-edition)
- [What you get](#what-you-get)
- [Sample essay](#sample-essay)
- [The gates](#the-gates)
- [Development](#development)
- [Credits](#credits)
- [License](#license)

## How it works

You answer one short form at the start. After that the skill runs on its own until the essay is finished.

| # | Peterson's step | How the model runs it | Why it changed |
|---|---|---|---|
| 1 | **Question** | One question a reader could answer two ways, plus who the reader is. You confirm it. | The reader decides what to explain, which kills glossary clutter. |
| 2 | **Reading list** | A research subagent gathers facts, scenes, numbers and verbatim quotes, questioning from a skeptic's, a newcomer's and an expert's point of view. Your own records count for essays about you. | Specifics are the cure for genericness. |
| 3 | **Outline** | A thesis that answers the reader's own question (what to do, not what the studies found), a carrier (the person or case the reader follows) and a puzzle the ending answers, then one sentence per paragraph. A critic attacks it. | Peterson's ten per thousand words is the centre, not a quota. |
| 4 | **Bad draft** | Written straight through by one author in a smart friend's voice, carried by the case, 15% long, with at most one named study per paragraph and the figures that make each claim concrete; extra detail goes to short footnotes. | No sentence quotas per paragraph: they make a model write choppy sentences. The study budget keeps a well-researched essay from reading like a literature review. |
| 5 | **Outline from memory** | A fresh reader reads the draft once and outlines it from memory, and says where it would have stopped reading by choice. | A model can't forget its own draft, so someone else remembers. Understanding a paragraph isn't the same as wanting to read the next one. |
| 6 | **Reorder** | Recall and outline compared; a new outline; paragraphs, then sentences, reordered and rebuilt on it. | Structure is fixed before sentences, so no polish is spent on paragraphs that move or vanish. |
| 7 | **Rewrite sentences** | An editor marks flawed spans at four levels of resolution (word, sentence, paragraph, essay). Each gets three genuinely different versions, or a reason it stands. | Three versions of every sentence makes a model change good sentences; three versions of the flawed ones doesn't. |
| 8 | **Fact-check** | A fact-checker marks every claim supported, fixed or cut against the notes, and changes nothing else. | Easy prose makes claims feel truer, so accuracy gets its own pass and never restyles. Not in Peterson. |
| 9 | **Can it be better?** | A second cold read. Done when its recall matches the outline and the reader would have kept reading. | One round: every further round of self-revision drifts from the essay's intent. |

## Install

You need [Claude Code](https://docs.claude.com/en/docs/claude-code) and [uv](https://docs.astral.sh/uv/). The checker declares its own Python dependencies.

```bash
npx jp-essay@latest
```

That installs both `/jp-essay` and `/jp-essay-scientific` into `~/.claude/skills`. Start a new Claude Code session and they're there. To update later, run `npx jp-essay@latest --force`. `npx jp-essay doctor` checks that Claude Code and uv are installed.

To track the repo instead, clone it:

```bash
git clone https://github.com/lucasbabur/jp-essay ~/.claude/skills/jp-essay && ~/.claude/skills/jp-essay/install.sh
```

Update a clone with `git -C ~/.claude/skills/jp-essay pull`.

## Usage

```text
/jp-essay Why do we procrastinate on things we care about? 1200 en
```

```text
/jp-essay <question or topic> [word count] [language]
```

- **Length:** at least 500 words, 1,000 by default. The length is a ceiling: the final essay lands between 90% of the target and the target.
- **Language:** `en` or `pt`. The default is the language you asked in.

## Scientific edition

`/jp-essay-scientific` runs the same process for an academic reader. Sources must be published works, drafts mark borrowed claims with `[@id]`, and the essay ends with in-text citations and a reference list in your style (APA by default, ABNT and others on request).

```text
/jp-essay-scientific What made dinosaurs dominate the land? 1500 en APA
```

## What you get

Each essay gets its own folder under `~/Documents/essays/<slug>/`:

```text
what-made-dinosaurs-dominate-land/
├── question.md        # question, reader, length, language (+ style if scientific)
├── sources.md         # material: facts, scenes, numbers, verbatim quotes
├── research.md        # three readers' questions, the strongest objection, gaps
├── outline.md         # the thesis, then one claim per paragraph
├── outline-review.md  # APPROVED, or numbered objections
├── draft.md           # the bad draft
├── reader.md          # a cold reader's outline from memory, and what it took away
├── outline-2.md       # the outline the essay follows after the recall
├── draft-2.md         # the draft rebuilt and reordered on it
├── edits.md           # flawed spans, by level of resolution
├── rewrites.md        # three versions of each flawed span, or why it stands
├── facts.md           # every claim: supported, fixed or cut
├── reader-2.md        # the last cold read
└── final.md           # the finished essay ✦
```

## Sample essay

[*Do We Sleep to Wash the Brain?*](examples/do-we-sleep-to-wash-the-brain.md) came out of one unedited run with a 500-word ceiling. It follows the reader through the morning after an all-nighter, across a 2013 study, a 2024 study that contradicts it, a sleep-deprivation experiment in Oslo and a 2025 twist. The fact-check covered 32 claims and fixed one. [Read it on the website](https://jpessay.com/sample.html).

## The gates

`check.py` checks only what a script can see. A step counts as done when its gate prints `PASS`:

```bash
~/.claude/skills/jp-essay/check.py <gate> <essay-dir>
```

| Gate | Checks |
|------|--------|
| `question` | Question, reader, length ≥ 500 and language present |
| `sources` | At least three sources, notes on each, every link fetched or local file found |
| `outline` | A thesis sentence; one point per 80 to 250 words; every cited id exists |
| `draft` | Length up to 15% over; no headings; mechanical tells |
| `recall` | One recall sentence per paragraph, in the reader's own words; all eight report sections |
| `outline2` | The new outline is well formed and `draft-2.md` has one paragraph per point |
| `rewrite` | One block per flawed span; three distinct versions or a reason; every choice reaches `final.md` |
| `facts` | Every claim in the fact-check is supported (with a source id), fixed or cut, and supported claims are in `final.md` |
| `final` | Title; length between 90% of the target and the target; quotes verbatim from the notes; mechanical tells; citations in scientific mode |

The mechanical tells are AI vocabulary, filler, stock openers, "serves as", "not X but Y", dashes used as punctuation, duplicated sentences, three sentences in a row with the same opening, and a summary closing paragraph. Quoted source text is exempt. Warnings flag paragraphs with more than five figures, sentences over 40 words, staged run-ups ("And the result?"), paragraph-ending fragments, curly quotes and heavy use of parentheses.

## Development

```bash
uv run --with pytest==8.3.4 --with pysbd==0.3.4 --with httpx==0.28.1 pytest -q test_check.py
npm test   # the npx installer
```

Publishing a GitHub release publishes the package to npm (`.github/workflows/publish.yml`).

The website, [jpessay.com](https://jpessay.com/), is `landing/`, deployed on Vercel. Preview it with `python3 -m http.server -d landing 8774 --bind 127.0.0.1`.

## Credits

The process follows Jordan B. Peterson's [Writing Guide](https://essay.app/guide), adapted for a model. The adaptations draw on [Chakrabarty et al. (CHI 2025)](https://arxiv.org/abs/2409.14509) on how editors fix model prose, [STORM](https://arxiv.org/abs/2402.14207) on perspective-driven research, and [AI-Slop to AI-Polish](https://arxiv.org/abs/2504.07532) on why models can't grade writing. The style rules draw on Steven Pinker's classic style, Paul Graham's essays on writing, George Orwell's six rules and ASD-STE100's one-word-per-meaning rule. The tells draw on Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), [humanizer](https://github.com/blader/humanizer) and [stop-slop](https://github.com/hardikpandya/stop-slop). This project is independent and is not affiliated with or endorsed by any of them. The icon is an abstract figure, not a portrait of anyone.

## License

[MIT](LICENSE)
