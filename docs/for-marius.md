# For Marius

Your inbox. Two lists: decisions that are yours, and work that cannot be done from a session. Agents add and remove items in the PR that raises or settles them (CLAUDE.md → Marius's part). Everything here can be handled in the GitHub web interface or in a chat session; nothing asks you to run code.

Last updated: 2026-11-14.

## Decisions for you

| # | Since | Question | Why it is yours | Until decided |
|---|---|---|---|---|
| D1 | 2026-11-11 | **Gold set (A8.1): confirm or change the grades** in `docs/reports/A8.1-gold-set.md`, in particular whether the grade C items stay out of scoring. | The grades decide what counts as a right answer for A8.8. | The set stays a draft; A8.2, A8.3 and A8.8 do not start against it. |
| D2 | 2026-11-11 | **Resampling (A1.14): one source per document, or per-sign draws?** The harness picks one source per document, so a document's disputed signs move together. Per-sign draws need sign-level alignment and create readings no editor proposed. | It is an interpretation of plan §0.7. | The per-document version is used. |

## External work

| # | Since | What | Why a session cannot do it | Blocks |
|---|---|---|---|---|
| E1 | 2026-11-10 | **A1.10: Linear B control corpus (DAMOS).** Check whether a bulk export exists or request one. | Yours by assignment; involves contacting the maintainers. | Stage 2 of plan §0.6 (A3.4, A8.6–A8.8, A4, A9.3). |
| E2 | 2026-11-11 | **V10: blinded read of the Greek Reporter page** (https://greekreporter.com/2026/01/15/reconstruct-linear-a-crack-language/). Wanted: author; any publication it cites; the method in one sentence; the corpus used; whether it reports any quantitative validation. The page shows a photograph of the held-out sceptre, so please do not paste its text into a session: answer the five points only. | The fetch needs an approval in the session, and the page shows held-out material. | Closing V10; nothing else. |
| E3 | 2026-11-11 | **Gold set: check the literature rows against their publications** (`data/gold-input/literature-items.tsv`), and identify the *Minos* article behind six attestations (link in the file). | No primary source could be read from a session. | Freezing the gold set (with D1). |
| E5 | 2026-11-10 | **A1.15 (optional): message to the lineara.xyz maintainer** about the probable errors and the licence question. An agent drafts it when you ask. | Only you write to other people. | A1.3 (licence). |

## Settings only you can change

Nothing open. (S1, protecting `predictions-*` tags, was done on 2026-11-14 and checked through the API.)

## Rule-file PRs merged since 2026-11-12

To undo one: open the PR → **Revert** → the revert PR merges under the same rules.

| PR | Date | What changed | Weakens a guardrail? |
|---|---|---|---|
| #38 | 2026-11-12 | No manual merges; rule files review-gated; guardrail script run from `main`; held-out lock in CI; held-out code added to the rule files | **Yes**: rule changes no longer need your merge (your instruction, 2026-11-12). Also stronger in four places: review gate no longer accepts an approval from another PR; removed held-out lines need a `predictions-` tag; the guardrail script cannot approve its own change; `load.py`, `heldout.py`, `split.py` are now rule files. |

## Settled recently

- **Next task (was D3), 2026-11-14.** You chose the false-positive benchmark, A5.17 (Tier 1). Started the same day: the benchmark code and the port of the Finding 001 matcher are in `src/aegean/benchmark/` (how it works: `docs/benchmark.md`). Nothing has been run on Linear A yet; the protocol is registered first (`hypotheses/H-A5-01.md`, review in `docs/reviews/H-A5-01-review.md`). The same PR added the `Type:` line to `hypotheses/TEMPLATE.md`.
- **For your information, no action needed: the null in Finding 001 was not quite fair** (research-notes 2026-11-14, "A5.17"). Its random lexicons gave the matcher about 12% more targets than the real Hebrew lexicon, which tilted the comparison against Hebrew. The benchmark uses a corrected null. I expect the conclusion of Finding 001 to hold; the registered run will say.
- **Younger's PDFs (was E4), 2026-11-14.** You put the five files in the private repository `marius-vrancianu/aegean-scripts-private`, folder `Younger/`. All five hashes match; the rebuilt witnesses reproduce the corpus-v1.0 hash. Sessions fetch them with `data/raw/younger/fetch.py --from`. Please keep that repository private and leave the files in place.

## Small things an agent will do without asking, unless you object

- Comparison of the A1.11 position table with Packard's published figures, once a source for them is available.
- An addendum to Finding 001 saying that its null was larger than the real lexicon as the matcher sees it, with the corrected figures from the H-A5-01 run. Review-gated PR, after that run.
- Four strengthenings of the guardrail script that the second review of #38 recommended (each a review-gated PR; none started):
  - **N7** a verdict line with a condition after it ("APPROVE once …") is read as an approval; accept only a bare verdict line.
  - **N8** an approval does not expire when the author pushes again; require that no commit to a gated path is newer than the approving review.
  - **N9** changing one character in an old approving review still opens the gate; require the review to name the PR number.
  - **N10** the held-out lock checks a tag's name, not what it points to; require the tag to be an ancestor of `main`.
- Try a second workflow on `pull_request_target` (GitHub takes it from `main`, not from the PR) that runs the guardrail script, to narrow the gap for PRs that edit the workflow. Untested; review-gated PR.
