# Tells

The editor's checklist, arranged by Peterson's levels of resolution: the right word, in the right sentence, in the right paragraph, in the right essay. Professional editors fixing model prose spend nearly all their edits on the first eight categories below; the essay-level ones are what a whole-essay read adds. Mark a span only when you can name its level, its category and what the replacement gains. Most fixes replace or delete; an insertion is right only where the reader would stall.

**Strong** tells justify an edit on sight. **Weak** tells justify an edit only when two or more sit in the same paragraph, since any one of them alone is ordinary prose.

## Word

1. **Cliché and stock phrasing.** Strong: phrases seen a thousand times ("a testament to", "the tip of the iceberg", "go to die"); AI vocabulary (delve, tapestry, pivotal, underscore, showcase, foster, multifaceted, realm, landscape, vibrant, crucial); fancy ways to say "is" or "has" (serves as, stands as, boasts); stock openers ("Here's the thing", "The truth is", "Imagine a world"). Fix: the plain word, or cut.
2. **Awkward word choice.** Weak: a synonym rotated in for a term already named; an adverb propping up a weak verb; jargon nouns where a plain one exists (vector, substrate, leverage, paradigm); a key term used but never pinned down. Fix: the exact word, used consistently.

## Sentence

3. **Poor sentence structure.** Strong: "not X but Y" or "it isn't X, it's Y" denying a claim nobody made; a staged run-up that delays the point ("And the result? It held."); a one-line dramatic fragment that ends a paragraph; three items forced into a list; three sentences in a row with the same opening. Strong: a trailing -ing clause ("..., highlighting the need for..."), which instruction-tuned models write at five times the human rate. Weak: a long sentence the reader must reread; passive voice hiding an actor who matters; a verb turned into a noun ("made a decision"). Fix: one direct sentence.
4. **Tense and person slips.** Strong: a shift in tense or point of view without a reason. Fix: the essay's tense and person.

## Paragraph

5. **Purple prose and forced images.** Strong: an image that is false or misleading about the thing it describes; two or more images piled in one paragraph; a mixed image. A comparison that fits and is true stands, even when a literal phrase could do the job, because it is often what the reader remembers. Fix: the literal statement, or one image instead of several.
6. **Unnecessary exposition.** Strong: a definition the reader in `Reader:` does not need ("Python, a programming language"); restating what the previous sentence showed; explaining the joke. Fix: delete.
7. **Lack of specificity.** Strong: a claim with no specific behind it; vague attribution ("experts say", "research shows"). Fix: one specific from the notes, preferably a case, a scene or an example the reader can picture; a number only if the reader would repeat it to a friend. Never propose a number just because the notes hold one.
8. **Too many studies.** Strong: more than one named study in a paragraph; a number the reader would not repeat to a friend (a percentage to the decimal, a sample size, a second statistic for the same point); a chain of caveats about a study's method. Fix: keep the one study and the one number that carry the paragraph's claim, and `DELETE` the rest or mark it `FOOTNOTE` when a curious reader would want to check it.

## Essay

9. **Order.** A paragraph that does not follow from the one before, or a point made before the reader has what it needs. Fix: move it, and say where.
10. **Drift.** A paragraph that argues something other than the thesis, or a sentence that concedes the thesis away without saying so; a paragraph about the research for its own sake (a study's method, a side finding) that the reader's decision does not turn on. Fix: cut it, or make the concession explicit.
11. **Ending.** A closing summary, a moral tacked on, or an ending that reports a finding and leaves the reader's question unanswered. Fix: end on the answer, what this reader should do or believe and when.
12. **Closed puzzle.** The verdict stated in the opening paragraph, or a sentence of settled certainty before the evidence has been shown. Fix: open the gap instead, and move the verdict to the end.

**Unsupported claims** are listed apart from these: any fact, number or quote the notes in `sources.md` do not hold. A scene the reader is plainly asked to imagine and practical advice that follows from the evidence are not claims.

## Examples

These come from essays this skill produced, so they show the failures it is prone to.

- Span: "wanted an AI, software that learns from examples, that could spot leaking pipes, but no dataset, a collection of examples an AI learns from, of such pipes was available." Category: Paragraph, 6 Unnecessary exposition. Replacement: "wanted software that could spot leaking pipes in photos, but nobody had photographed enough leaking pipes to train it."
- Span: "Your verdict on the result was shorter: \"And it held.\"" Category: Sentence, 3 Poor sentence structure. Replacement: DELETE (the previous sentence already says the rule stands).
- Span: "The trackers were hothouse plants, dead once you stopped watering; the rules grew outside, unwatered." Category: Paragraph, 5 Purple prose. Replacement: "The trackers needed you every day; the rules needed nothing."
- Span: "Keep the pen loose." Category: Essay, 10 Ending. Replacement: DELETE (a moral tacked onto the ending).
- Span: "The same move shaped your public work." Category: Word, 2 Awkward word choice. Replacement: "The same split shows in your public work." ("move" was never defined)
- Span: "Studies show that habits play a crucial role in success." Category: Paragraph, 7 Lack of specificity. Replacement: "One study found that 43% of daily behavior is habitual." (from the notes)
- Span: "On a standard test of how hard they could breathe out, their scores rose from 63.9% to 76.3% of the normal level for their age and size, while the neutral writers showed no change." Category: Paragraph, 8 Too many studies. Replacement: "Four months later they were breathing measurably better; the people who wrote about neutral topics were not." (the decimals go to a footnote)
- Span: "A 2014 trial with 116 young adults found" Category: Paragraph, 8 Too many studies. Replacement: DELETE (the paragraph already named one review; a second study queued behind it turns the essay into a literature review)
