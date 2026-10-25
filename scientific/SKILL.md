---
name: jp-essay-scientific
disable-model-invocation: true
description: Write a cited academic essay with Jordan Peterson's essay process, adapted to how models write, ending in in-text citations and a reference list.
argument-hint: "<question or topic> [word count] [language] [citation style]"
---

Write a scientific essay answering `$ARGUMENTS`. Read `~/.claude/skills/jp-essay/SKILL.md` and run its steps and gates with the changes below. Where a change and that file disagree, the change wins, and every subagent a change touches gets the changed rule in its brief.

## Changes

- **Step 1, Question.** Also settle the citation style (default APA) in the same `AskUserQuestion` call, and add a fifth line `Style: APA|ABNT|…` to `question.md`. That line switches `check.py` into scientific mode. The default reader is an academic one: a student or researcher in a neighbouring field.
- **Step 2, Reading list.** Sources are published works only: no local files and no `conversation`. Brief the research subagent with this format per source: `## <id>`, `Link: <url or DOI>`, `Cite: <in-text citation exactly as it will appear>`, `Reference: <full entry in the agreed style>`, and `Notes:` on its own line followed by the source's findings, methods, sample sizes and short verbatim quotes.
- **Style.** An academic reader wants precision more than ease. Use the field's exact term and keep it; scope each claim to what the evidence shows (population, method, effect size); keep hedges that report a real limit of the evidence. Pass this paragraph with `style.md`, and it wins where they differ.
- **Step 4, Bad draft.** Mark every claim taken from a source with its id, `[@id]`, only where that source's notes support it.
- **Steps 6 and 7.** Keep every `[@id]` on the claim it supports through `draft-2.md` and the rewrites. When writing `final.md`, replace each `[@id]` with that source's `Cite:` text and end with a `## References` section listing the `Reference:` line of every cited source.
- **Final report.** Give the number of sources cited.
