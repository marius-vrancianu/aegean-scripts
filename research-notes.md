# Research notes (running log)

Dated entries, newest last. Append; never rewrite past entries. Corrections go in a new dated entry that references the old one.

---

## 2026-11-02 — Blinding breach on held-out documents KN Zg 57 / KN Zg 58 (Knossos ivory sceptre)

**Context.** Before committing to the A2.9 held-out test, we checked whether the sceptre contains any arithmetic at all. The plan was a narrow yes/no check (numerals? fractions? KU-RO/KI-RO/PO-TO-KU-RO? logograms?). The fetch tool returned the full text of the article to Claude rather than only the answers. Marius has read only the summary below, not the article.

**Source read.** Kanta, A., Nakassis, D., Palaima, T. G. & Perna, M. 2025. An archaeological and epigraphical overview of some inscriptions found in the Cult Center of the city of Knossos (Anetaki plot). *Ariadne* Suppl. 5, 27–43. doi:10.26248/ariadne.vi.1841. Open access, CC BY-NC-SA 4.0. Accessed 2026-11-02.

**What the article contains (and therefore what Claude has seen):**
- *Ring (KN Zg 57):* the authors state there are **no numerals on any face**. The ring has iconographic and logographic content: 12 animals, at least 10 vases (some with syllabograms in ligature), textile logograms and a series of hide logograms. Face B has six sign-groups plus three logograms. Face C has at least nine sign-groups. About 119 signs in total. The authors note few parallels between its sign-groups and other Linear A texts. Individual sign IDs are named in the palaeographic discussion, but **no sign-group is transliterated**.
- *Handle (KN Zg 58):* the authors call it an accounting text because it has numerals and fractions. The handle has a probable new sign and two Hieroglyphic-attested signs (*180, *181). Face δ has vases with ligatured signs, then units, then **six different fraction signs in sequence**. **No total word is reported.**
- *Fraction claim:* the authors say the six-sign sequence gives *relative* values that differ from all previous proposals, citing Corazza et al. 2021. The article does **not** say which six signs these are, what order they are in, or what values they imply.

**What has not been seen.** Transliterations of any sign-group; which fraction signs occur and in what order; any numeral values beyond "ten". None of these are in this article. They are expected in Kanta (ed.), *Anetaki II* (forthcoming).

**Consequences.**
1. A2.9 cannot be run as originally designed, because there are no totals. It is replaced by an ordering test (plan v1.1, A2.9).
2. Any value set that orders these signs as Corazza et al. 2021 does is now *expected* to fail the ordering test. A sceptre result counts as **confirmatory only for value sets that differ from Corazza's**, and the write-up must say so.
3. Minor contamination for A4: we now know *180 and *181 occur on the handle and that the ring's sign-groups have few parallels. Neither fact constrains sign-value predictions.
4. Remaining safeguards:
   - Freeze and hash all A2 and A4 predictions before reading *Anetaki II* or the Kanta–Perna paper "New light on the fractional system in the Linear A script" (2025 Madrid Mycenological Colloquium).
   - Do not read secondary discussions of the sceptre fractions until then.

**Process lesson.** WebFetch does not blind anything: whoever runs it sees the whole page. For future blinded checks, use one of these two approaches:
- (a) a separate agent that reads the source and returns only the pre-specified yes/no fields, kept away from the context in which predictions are made; or
- (b) Marius reads the source himself and the predictions are frozen before he discusses it.

Confidence that the summary above matches the article: high (read directly, pp. 37–42).

---

## 2026-11-04 — Repository set up (A1.1)

**Decisions (Marius, 2026-11-04):**
- One monorepo for the whole project. The public benchmark (A5.16) may be split into its own repo when it is published.
- The repo is **public** from the start.

**Consequences:**
- Third-party data is committed only if its licence allows redistribution. lineara.xyz has no licence file (checked 2026-11-04), so the repo holds a fetch script pinned to commit `9c81beba…` with a SHA-256, not the data. See `DATA_SOURCES.md`.
- Pre-registration works through git: a hypothesis file is registered when merged to `main` and is immutable afterwards. CI enforces this, and also enforces that this file is append-only (`tools/check_guardrails.py`).
- Most work will be done by Claude instances (claude.ai and Claude Code). `CLAUDE.md` is their contract; chat is not a source of truth.

**Not yet in the repo:** the Finding 001 code (`nulltest.py`, `run.py`, `run2.py`). Only the write-up was in the claude.ai project. Marius to add the scripts from wherever they were saved.

---

## 2026-11-04 — Held-out sceptre records found inside the lineara.xyz snapshot

**What:** the pinned lineara.xyz snapshot already contains records `KNZg57a`, `KNZg57b` (support "ivory object", 17 characters of `parsedInscription` each, so apparently partial) and `KNZg58` (support "ivory object", empty `parsedInscription`). Image rights point to the Kanta et al. 2025 *Ariadne* paper. Found while setting up the repo. **Only the metadata fields listed here were printed; the inscription text was not displayed.**

**Consequences:**
1. Every corpus builder must filter through `data/heldout.txt` (loaded by `aegean.corpus.heldout`). The three IDs are listed there.
2. The KU-RO / KI-RO / PO-TO-KU-RO counts reported on 2026-11-02 (34 / 12 / 2) were exact-word matches over the whole file. None of the matched sides is a Knossos document, so the sceptre records did not contribute to them.
3. **Finding 001** (2026-10-28) used the same source and probably included these records' sign-groups among its 696 unique sign-groups. This does not affect Finding 001's conclusion: it is a null test with no predictions about the sceptre, and at most a handful of sign-groups are involved. It should still be checked when the code is moved in, and the finding re-run with the exclusion for the record.
4. Any future source (SigLA, Younger) must be checked for the sceptre on ingest, and its IDs added to `data/heldout.txt` before anything else is done with it.

---

## 2026-11-04 — Finding 001 code restored and reproduced (A1.1 complete)

- The Finding 001 scripts were recovered verbatim from the 2026-10-28 chat's tool calls and committed under `experiments/finding-001/original/`.
- Re-running them on pinned inputs reproduces every reported figure exactly.
- **Correction to the entry above ("Held-out sceptre records…", item 3):** excluding the sceptre records leaves the output byte-identical. They contributed nothing to Finding 001.
- Two reporting gaps in Finding 001 are now documented in its addendum. Neither changes the conclusion:
  - the unreported random-syllable-string null;
  - a lower-case bug that makes `run.py`'s Linear B figure (0.608) the wrong one to cite.
- openscriptures HebrewLexicon pinned at `21c9add1…` (CC BY 4.0).

---

## 2026-11-04 — Merge policy

Decided with Marius:
- `main` requires a PR and passing CI. Force-pushes and deletions are blocked. **No required approvals**, because agents open PRs under Marius's account and GitHub does not let an author approve their own PR.
- Routine PRs may auto-merge on green CI.
- Marius merges by hand any PR that touches:
  - `hypotheses/`, where merging is the act of pre-registration;
  - `findings/`, which are claims;
  - the rules: `CLAUDE.md`, the guardrails script, `.github/`, `data/heldout.txt`.
- The rule is written in `CLAUDE.md` → Workflow → Merging. GitHub cannot enforce it for a single account, so it relies on agents following it.

---

## 2026-11-04 — corpus-v0.1 built; a small held-out leak

**Decision (Marius):** A2 proceeds on a provisional, single-source release, corpus-v0.1 (lineara.xyz only, L0). All A2 results on it carry that caveat and are re-run on corpus-v1.0.

**Build:**
- 1,718 documents and 3,883 entry lines.
- Deterministic: rebuilding gives the same SHA-256, recorded in `data/processed/corpus-v0.1/MANIFEST.json`.
- The JSONL itself is regenerated, not committed (see DATA_SOURCES, lineara.xyz licence).

**Source problems found while building:**
- duplicate ID `KH101`;
- incomplete damage marking;
- entry-based line breaks;
- the data file's public-domain header.

All are documented in `DATA_SOURCES.md`.

**Held-out leak (minor):** while diagnosing a JSON parse error, a Python error message printed a 30-character excerpt of record `KNZg57b`, which included **two signs** of the sceptre ring text. My diagnostic parsed all records before applying the exclusion. Only Claude (this session) saw them; Marius did not.
- Impact: negligible for A2, since the ring has no numerals. For A4, two signs out of about 119 do not constrain any sign-value prediction, but they count as seen.
- Fix: the builder now drops held-out IDs by name before parsing any record (`aegean.corpus.lineara.iter_raw_records`).
- Rule for future agents: never run whole-file diagnostics on a source that contains held-out records. Filter first.

---

## 2026-11-04 — V7 (Corazza et al. 2021) and V3 (DAMOS) checked

- **Corazza et al. 2021 did not fit fraction values to tablet totals.** As far as a web-fetch summary of the open PDF shows (to be verified against the PDF):
  - their values come from six premises solved exhaustively, with the solutions ranked by frequency, typology and optimality;
  - HT 104 and PE 1 appear only as support;
  - no per-tablet constraint list or supplementary data exists.

  Consequence: "reproduce Corazza" (A2.3) means reproducing their solution counts and ranking. H-A2-01 (do their values make the tablet totals more consistent than random value sets do?) is a new test. Given the inventory, at most about 12 KU-RO totals are usable, so its power will be low and the pre-registration must say so.
- **DAMOS:** content CC BY-NC-SA 4.0. Only word-search results can be downloaded, as CSV. A bulk release is planned but not available. The Linear B validation set for A2.4 needs either word-search exports plus the online texts, or a data request to the editor.
- **Not done:** the `corpus-v0.1` git tag. Creating tags or releases is outside what this session is permitted to do. Marius to create it on commit `fc87559`. Results cite `corpus-v0.1 @ fc87559` either way.

---

## 2026-11-04 — Session handoff (state of A2)

**Done:**
- corpus-v0.1 (`fc87559`, rebuilt from a fresh clone to the same hash);
- A2.1 parser;
- A2.2 rule-based inventory;
- V3 and V7 checked;
- pre-registration batch 1 (H-A2-04, H-A2-07) opened as PR #7, **awaiting Marius's merge**.

**Next, in order:**
1. **A2.2 completion.** Check every inventory row with class `complete`, `complete-scope-unclear` or `damaged` against its GORILA facsimile (lineara.xyz `images/<ID>-Facsimile.jpg` at 9c81beba; view in scratch, do not commit). Record legibility per quantity and any corpus errata.
2. **Verify the Corazza et al. 2021 details against the PDF:** the six premises, Table 8, and whether descending order is a premise. H-A2-07's secondary test depends on this.
3. **After PR #7 merges:** run H-A2-07 (value-free, quick), then H-A2-04 (needs the HT 122a/b GORILA check from step 1).
4. **Register H-A2-01/02/03/05** with scope and tolerance rules informed by step 1. Their power will be low, since at most about 12 KU-RO totals are intact; say so in the files.
5. **A2.4 Linear B validation set** via DAMOS word-search CSV (*to-so*), or ask the editor.

**Open items for Marius:**
- the `corpus-v0.1` tag on `fc87559` (this session cannot create tags);
- the repo licence (deferred; DAMOS NC-SA terms matter for it).

---

## 2026-11-05 — First A2 results: H-A2-07 supported, H-A2-04 inconclusive

- **Corazza et al. 2021 verified from the PDF** (supplied by Marius in the claude.ai project; not in the repo). Notes: `docs/references/corazza-2021-notes.md`. Descending order is their **premise 5**, so any order test under their values is circular. The solution counts and Table 8 match what was recorded on 2026-11-04.
- **H-A2-07 (fraction order): supported.** No pair of fraction signs is ever written in both orders on corpus-v0.1. Measured over 41 adjacent pairs, C = 1.00, p < 0.0001. Most pairs are singletons; the six repeated pairs (22 occurrences) all agree.

  Exploratory, n = 1 each: three orders clash with Corazza's values. Two are known reading disputes (ZA 8 "E J", Corazza n. 3; KH 86 "A B B" vs their "A A"). One, **HT 34 "2 H K"**, is unverified. If it is right, it would put H above 1/10, against their tentative H = 1/16. This is a lead for H-A2-05, to check against GORILA and Younger before use.
- **H-A2-04 (HT 122 grand total): inconclusive by rule.** KU-RO 31 (a) + KU-RO 65 (b) = 96, but PO-TO-KU-RO reads 97. The last units of the 97 touch edge damage in the GORILA facsimile. A human second count of the strokes would help. For H-A2-01/02/03: the tolerance rules must handle off-by-one totals explicitly.

**Next:**
1. GORILA check of the remaining KU-RO candidate rows (A2.2 completion). This is the main input for registering H-A2-01/02/03/05.
2. Find Montecchi 2009 and 2013 (calculation errors in Linear A totals). They are the direct prior work and appear to be paywalled.
3. Register H-A2-01/02/03/05, then H-A2-06.

---

## 2026-11-05 — HT 122b entries looked at before the totals tests were registered (disclosure)

While Marius was checking the HT 122b facsimile, we compared side b's entries with its KU-RO. In corpus-v0.1, side b's surviving entries are 7] (damaged), 2, 2, 2, 2 = **15**, against **KU-RO 65**. The KU-RO is not the sum of anything visible on that side. The edges where the entries sit are damaged, so lost entries are the likeliest explanation, but that is an inference.

Consequences:
- H-A2-04 only tested subtotals against the grand total (31 + 65 vs 97). It said nothing about whether the subtotals match their own entries. HT 122 is less reliable than the "grand total" label suggests.
- **H-A2-01 and H-A2-03 (and any totals census) must list in their "What I already know" sections:** the HT 122b entry sum (15 vs 65), and the HT 104 sum (45 J + 20 J + 29 = 95 under J = 1/2, known from the literature).
- Marius's own count of the HT 122b PO-TO-KU-RO read "97, possibly 96". This independently supports the "partly intact" judgement in the H-A2-04 outcome.
- lineara.xyz entry lines are not physical lines: several short entries share one physical line on HT 122b. Anyone checking a facsimile against corpus-v0.1 should expect this.

---

## 2026-11-05 — H-A2-08 census run: inconclusive; most totals untestable

- **Step 1 (GORILA checks) was committed before any summing** (`a151ae3`), then the code (`8de0b44`), then the run. Departures from the protocol are in the checks README.
- **Result:** under strict, cautious rules only **5 of 37 KU-RO totals are testable**: 23 damaged, 7 with fractions, 2 without a total. Of the 5, 2 are exact (HT 117a, HT 88), 1 is off by one (HT 119, 159 vs 160), and 2 are inconsistent (HT 118, ZA 15b). p = 0.049, so **inconclusive** by the frozen rule.
- **Both inconsistencies look like scope failures.** ZA 15b's KU-RO sits below a ruled-off heading and probably totals entries on its other side. On HT 118, the KU-RO 30 probably covers only part of the seven entries above it (sum 50). A commodity- or section-based scope rule is the obvious next idea, but it is now post hoc for these tablets. It may only be registered as a new hypothesis, with its test data specified in advance (e.g. corpus-v1.0 additions, or KI-RO lists).
- **Cheapest way to strengthen this:** a second, human check of the five testable rows, and of a sample of the "damaged" ones, where the cautious standard may have excluded good tablets.

**Next:**
1. GORILA check of the KI-RO rows (for H-A2-03).
2. Register H-A2-01/02 (fraction value sets) and H-A2-03 (KI-RO). The 7 fraction-bearing totals from this census are their test set, and they are equally few, so the files must say how little power they have.
3. Obtain Montecchi 2009 and 2013.

---

## 2026-11-05 — Exploratory full census (all markers, damaged rows and fractions included)

**Requested by Marius** after H-A2-08 came out inconclusive. Full write-up: `experiments/A2/exploratory/README.md`.

**Consequence for pre-registration:** fraction totals have now been evaluated under the Corazza and Schrijver value sets. **H-A2-01/02 can no longer be blind tests on corpus-v0.1.** They can only be confirmed on new material: corpus-v1.0 additions, or the sceptre with H-A2-06. Given the result below, this costs little.

**Results (exploratory):**
- **KU-RO, primary scope:** 9 of 37 exact, plus 3 off by one stroke. Over the 29 comparable rows, the chance baseline expects 0.48 exact matches (p < 0.0001). Caveat: possible circularity through editorial restorations, since 7 of the 9 exact matches are on rows marked damaged.
- **Most mismatches have a visible cause:** lost entries on broken sides, a running total (HT 127b: 292 = 156 + 136), or a scope rule that catches the wrong list.
- **The totals cannot discriminate between fraction value sets.** No testable total involves B, D, K, H, A or the L series. On corpus-v0.1, totals constrain only J and E.
- **KI-RO:** none of the three naive relations holds in 11 pairs. KI-RO rows are not yet GORILA-checked.

**Comparisons run here:** for KU-RO and PO-TO-KU-RO, one per scope and value set; for KI-RO, 3 relations × 2 value sets × 11 pairs. All are exploratory and none counts as a hypothesis test.

---

## 2026-11-06 — A2 wrapped up on corpus-v0.1; status for the next session

**Done this session:**
- **Restoration check (exploratory addendum):** only 1 of the 9 exact KU-RO matches (HT 85a) involves a number the edition marks as damaged. The circularity risk is small but not excluded. Younger's site blocks bots, so a manual check is needed for that part.
- **H-A2-06 registered**, value-free sceptre test. The frozen corpus order graph is in the file. It waits for *Anetaki II*.
- **H-A2-09 registered** (R0, running-total R1 and section R2 scope rules). It may only be tested on documents not in corpus-v0.1, and will probably end up descriptive only.
- **Finding 002:** a summary of A2 on corpus-v0.1.
- **`docs/manual-checks/A2-checklist.md`:** a prioritised list for a human second reading.
- **lineara.xyz convention found:** "—" (U+2014) marks ruled lines (DATA_SOURCES).

**Open on A2 (nothing urgent):**
- the human second check (Marius, at leisure);
- a GORILA check of the KI-RO rows;
- Montecchi 2009/2013;
- A2.4 Linear B validation (needs DAMOS);
- H-A2-06 when *Anetaki II* appears;
- re-run everything on corpus-v1.0;
- an independent review of Finding 002 by a separate Claude instance, as `CLAUDE.md` requires for findings. Not yet done.

**Suggested next topic:** either A1 (corpus-v1.0: SigLA licence and harvest, reconciliation; this unblocks re-running A2 and gives A3/A4 better data) or A5.C (the spelling channel, which needs only Linear B data and can start now). See plan §0.5.

---

## 2026-11-06 — Independent review of Finding 002

A separate Claude instance reviewed Finding 002, as `CLAUDE.md` requires. Full text: `docs/reviews/finding-002-review.md`.

**Verdict:** accept after corrections. The fixed fraction order (H-A2-07) and "totals behave like totals" (exploratory census) both survive the reviewer's robustness checks.

**Corrections required (not yet made):**
- **H-A2-08** is "not supported" by its frozen rule. The exact permutation p is 6/120 = 0.0500; the reported 0.049 was Monte Carlo noise. The test could only have been "supported" with 5 of 5 exact matches. This makes it uninformative, not evidence against KU-RO = total.
- **"Supports J = ½" is circular.** HT 104 is the text J = ½ was derived from, and it is the only exact total with a fraction sign. No exact total contains E.
- **"No pair in both orders" is false as written.** ZA 8 has E J, against 31 J E hidden in the ligature codepoint. The order regularity is Bennett's observation and Corazza's premise 5; H-A2-07 replicates it.
- Six minor wording and caveat points: site clustering, linearisation of stacked signs, KI-RO denominators, the damage-mark source, exploratory p-values, and the 1s rosters.

---

## 2026-11-06 — Corrections to Finding 002 applied (review M1–M3, m1–m6)

This follows the review entry above (`docs/reviews/finding-002-review.md`).
- **H-A2-08 relabelled "not supported".** `census.permutation_test` now computes the exact p and the minimum attainable p for n ≤ 8 (code `b0e0aba`), and the results were regenerated. The exact p is 0.0500, against the 0.049 Monte Carlo estimate. The minimum attainable p was 0.05, so the test had no power. The outcome file records the correction in place.
- **Finding 002:**
  - the J = ½ support claim is removed (circular via HT 104);
  - the "both orders" claim is reworded, with credit to Bennett and Corazza premise 5 and the ligature sensitivity check;
  - site clustering, linearisation and KI-RO denominators are stated;
  - the exploratory p is flagged as post hoc, with the reviewer's robustness checks.
- **`hypotheses/TEMPLATE.md`:** a power check is now required in every decision rule.
- **`docs/manual-checks/A2-checklist.md`:** Priority 4 added (the order of stacked fraction signs).
- **Lesson for future registrations:** check the minimum attainable p before freezing a decision rule, and do not report Monte Carlo p-values that sit on a threshold.

---

## 2026-11-06 — Merge policy changed: review-gated auto-merge for hypotheses and findings

**Decided by Marius.** PRs that touch `hypotheses/` or `findings/` no longer need his manual merge. They auto-merge once an independent Claude review file ending in `Verdict: APPROVE` is in the PR and CI passes. See `CLAUDE.md` → Merging.

**What stays manual:** rule files (`CLAUDE.md`, `tools/check_guardrails.py`, `.github/`, `data/heldout.txt`).

**Why:** the review of Finding 002 found three errors that the independent review caught, not the manual merge. The review is kept as the gate.

**Not enforced by CI yet.** A guardrail check that a review-gated PR contains or links a review with APPROVE would itself be a rule change. If wanted, it is a separate hand-merge PR.
