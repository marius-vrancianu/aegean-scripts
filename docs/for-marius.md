# For Marius

Your inbox. Two lists: decisions that are yours, and work that cannot be done from a session. Agents add and remove items in the PR that raises or settles them (CLAUDE.md → Marius's part). Everything here can be handled in the GitHub web interface or in a chat session; nothing asks you to run code.

Last updated: 2026-11-12.

## Decisions for you

| # | Since | Question | Why it is yours | Until decided |
|---|---|---|---|---|
| D1 | 2026-11-11 | **Gold set (A8.1): confirm or change the grades** in `docs/reports/A8.1-gold-set.md`, in particular whether the grade C items stay out of scoring. | The grades decide what counts as a right answer for A8.8. | The set stays a draft; A8.2, A8.3 and A8.8 do not start against it. |
| D2 | 2026-11-11 | **Resampling (A1.14): one source per document, or per-sign draws?** The harness picks one source per document, so a document's disputed signs move together. Per-sign draws need sign-level alignment and create readings no editor proposed. | It is an interpretation of plan §0.7. | The per-document version is used. |
| D3 | 2026-11-12 | **What to work on next.** Plan §0.6 gives A9.1–A9.2 (claims audit) and A5.17 (benchmark Tier 1) as the next items that do not need Linear B. | Direction. | Nothing new is started. |

## External work

| # | Since | What | Why a session cannot do it | Blocks |
|---|---|---|---|---|
| E1 | 2026-11-10 | **A1.10: Linear B control corpus (DAMOS).** Check whether a bulk export exists or request one. | Yours by assignment; involves contacting the maintainers. | Stage 2 of plan §0.6 (A3.4, A8.6–A8.8, A4, A9.3). |
| E2 | 2026-11-11 | **V10: blinded read of the Greek Reporter page** (https://greekreporter.com/2026/01/15/reconstruct-linear-a-crack-language/). Wanted: author; any publication it cites; the method in one sentence; the corpus used; whether it reports any quantitative validation. The page shows a photograph of the held-out sceptre, so please do not paste its text into a session: answer the five points only. | The fetch needs an approval in the session, and the page shows held-out material. | Closing V10; nothing else. |
| E3 | 2026-11-11 | **Gold set: check the literature rows against their publications** (`data/gold-input/literature-items.tsv`), and identify the *Minos* article behind six attestations (link in the file). | No primary source could be read from a session. | Freezing the gold set (with D1). |
| E4 | 2026-11-11 | **Younger's PDFs** — set aside by you on 2026-11-12. They are on Academia.edu behind a login and have no licence; this repository is public, so they cannot be uploaded here. | Login; licence. | The Younger column in the A1.11 report and in the gold set; confirming the witnesses hash of corpus-v1.0. |
| E5 | 2026-11-10 | **A1.15 (optional): message to the lineara.xyz maintainer** about the probable errors and the licence question. An agent drafts it when you ask. | Only you write to other people. | A1.3 (licence). |

## Settings only you can change

| # | Since | What | Steps |
|---|---|---|---|
| S1 | 2026-11-12 | **Protect frozen-prediction tags.** A held-out document can be released only against a tag named `predictions-…`. Such a tag should not be movable or deletable. | **Settings → Rules → Rulesets → `corpus-tags` → Target tags → Add target → Include by pattern** → `predictions-*` → **Save changes**. |

## Rule-file PRs merged since 2026-11-12

To undo one: open the PR → **Revert** → the revert PR merges under the same rules.

| PR | Date | What changed | Weakens a guardrail? |
|---|---|---|---|
| #38 | 2026-11-12 | No manual merges; rule files review-gated; guardrail script run from `main`; held-out lock in CI; held-out code added to the rule files | **Yes**: rule changes no longer need your merge (your instruction, 2026-11-12). Also stronger in four places: review gate no longer accepts an approval from another PR; removed held-out lines need a `predictions-` tag; the guardrail script cannot approve its own change; `load.py`, `heldout.py`, `split.py` are now rule files. |

## Small things an agent will do without asking, unless you object

- Add a `Type: confirmatory / exploratory` line to `hypotheses/TEMPLATE.md` (rule 10 and the loader gate rely on it). Review-gated PR.
- Comparison of the A1.11 position table with Packard's published figures, once a source for them is available.
- Four strengthenings of the guardrail script that the second review of #38 recommended (each a review-gated PR; none started):
  - **N7** a verdict line with a condition after it ("APPROVE once …") is read as an approval; accept only a bare verdict line.
  - **N8** an approval does not expire when the author pushes again; require that no commit to a gated path is newer than the approving review.
  - **N9** changing one character in an old approving review still opens the gate; require the review to name the PR number.
  - **N10** the held-out lock checks a tag's name, not what it points to; require the tag to be an ancestor of `main`.
- Try a second workflow on `pull_request_target` (GitHub takes it from `main`, not from the PR) that runs the guardrail script, to narrow the gap for PRs that edit the workflow. Untested; review-gated PR.
