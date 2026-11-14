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

---

## 2026-11-06 — Author's response to the Finding 002 review

The author session independently reran M1 (exact enumeration) and all four of the reviewer's robustness checks (`experiments/A2/exploratory/rerun_review_checks.py`). **All reproduce.**

Two refinements, both pending re-review in the same PR:
- `hypotheses/outcomes/H-A2-08.md` now records the switch from the registered Monte Carlo procedure to the exact p as a deviation. The label is unchanged.
- Finding 002's J = ½ attribution is made precise: Bennett 1950 first proposed the value; HT 104 is one of three supporting texts cited by Corazza et al.; and J = ½ is their premise 1. The circularity conclusion is unchanged.

---

## 2026-11-06 — Merge process streamlined

**Problem observed on #17 and #21:** a PR whose checks had already passed could not get auto-merge, because GitHub refuses it once a PR is mergeable. This session is also blocked from merging directly, so every review-gated PR ended with Marius clicking.

**Changes to `CLAUDE.md`:**
- **Auto-merge is enabled when the PR is opened,** for every PR except rule-file PRs. GitHub merges when CI passes; for a review-gated PR, CI cannot pass before `Verdict: APPROVE`.
- **The author session may launch a fresh subagent as the independent reviewer.** The subagent gets a fixed prompt, and the author adds no hints. This removes the relay through Marius.
- **Reviews are committed to the PR branch,** so the reviewer's push reruns CI and triggers the merge.

**Repo setting needed (Marius):** make the CI job `test` a required status check on `main`. Without it, auto-merge has nothing to wait for and the gate is not binding. This cannot be done from an agent session (403).

---

## 2026-11-06 — A1.2: SigLA licence verified; A1 is the current focus

**Decision (Marius):** the A2 manual checks and the Montecchi comparison are deferred, since he expects marginal gains. Work moves to A1 (corpus-v1.0).

**SigLA licence:** CC BY-NC-SA 4.0, stated in the sigla.phis.me footer.
- The raw snapshot can be committed with attribution.
- ShareAlike means corpus files derived from SigLA carry the same licence. Code is unaffected.
- The site has no export link, but the project paper describes a JSON database behind the site. Finding that JSON is the first step of A1.4.

**Next on A1:**
- A1.4: harvest SigLA, pinned and hashed.
- A1.5: snapshot Younger. His site blocks automated access, so Marius may need to save the pages himself.
- A1.6–A1.9: reconcile the sources, define the schema, write the disagreement report.
- A1.10 (DAMOS raw data): Marius is checking.

---

## 2026-11-10 — A1.4: SigLA harvested

**Snapshot:** `data/raw/sigla/0c4ef69f5de4/database.js`, SHA-256 `0c4ef69f…0781dd`, committed under CC BY-NC-SA 4.0 with credit to Salgarella & Castellan. The same bytes were seen in the browser on 2026-11-06 and fetched by `curl` on 2026-11-10, once Marius had widened the network allowlist.

**Format surprise:** the "JSON database" of the SigLA paper is, as served, two **OCaml `Marshal`** values inside JS strings. New code: `aegean.corpus.ocaml_marshal`, a generic decoder that checks the header's byte and object counts, and `aegean.corpus.sigla`, which interprets the records. Each field mapping was checked against the rendered static pages. Fields whose meaning is unclear are kept under raw names, not guessed.

**Facts that change plans (high confidence; from the data and the rendered pages):**
- **SigLA has no numeral values.** Numerals appear at most as an abstract `num` sign (7×). This corrects my 2026-11-06 working note, which said numerals were entirely absent. A2 totals cannot come from SigLA; lineara.xyz stays the numeral source in corpus-v1.0, and SigLA is the independent check on signs, fractions, word division and damage.
- **No JE ligature in SigLA.** J and E are separate attestations, while DD and DDDD are single signs (`AAF717`/`718`). lineara.xyz has a single JE codepoint. The A1.7 schema must map between the two (Finding 002 review, M3).
- **Damage is recorded per word edge,** with three codes. The difference between codes 1 and 2 is unverified. SigLA has no restoration field.
- **Seven documents have a metadata ID that differs from their key** (e.g. KH 87 → "KH 97"). These are kept for the A1.9 report.

**Held-out:** the snapshot has no record of the held-out documents. That was checked by document ID only, never by reading content. The reader filters through `data/heldout.txt` with cross-source normalised sigla, so `data/heldout.txt` needs no change.

**Counts:** 827 documents (older harvests reported 772–787), 5,184 attestations, 1,417 words, 388 signs. These are source counts, not inclusion decisions (A1.6).

**Next:** A1.5 (Younger pages, waiting on Marius), then A1.6 inclusion rules, A1.7 schema, A1.8 layers and A1.9 disagreement report.

---

## 2026-11-10 — A1.5: Younger snapshot (Academia.edu, non-HT only)

**Younger's website is gone.** `people.ku.edu` no longer resolves. Younger's folder introduction (23 April 2024) says KU removed the server in early 2024 and that he moved the material to Academia.edu. Marius downloaded five files by hand. Hashes are in `data/raw/younger/SHA256SUMS`; the files are not committed, since no licence is stated. The transliterations are in "Other Texts (not Haghia Triada)", last updated 28 March 2024.

**Gap: no Haghia Triada.** Younger's HT file was not found on Academia, and Marius found no Wayback capture either. **Decided by Marius:** go ahead without it. In A1.9, HT documents are therefore compared between SigLA and lineara.xyz only. Non-HT documents have all three sources, but lineara.xyz was built from Younger's earlier HTML, so lineara–Younger agreement is not independent evidence.

**Held-out screening (blinded):** before I read anything, a separate agent scanned all five files programmatically. It reported only counts, page numbers and pre-specified tokens. There is no held-out siglum and no reference to the held-out publications. Three single hits were checked by follow-up fields without showing context: Knossos Zg numbers 4, `<21>` and 55; "scepter" in the KH Wc 2097 entry; "2025" as a KH Wc document number. Metadata dates are April–May 2024, before the held-out publications.

**Reader (`aegean.corpus.younger`):** works from PDF layout, via pdfplumber, because the typography carries data. Bold marks numbers. **Underline marks a doubtful reading**, per Younger's conventions, §3c. **Green marks his own conjectural fills.** Red is commentary. Small lowered glyphs are subscripts (RA2). Each convention was checked on page images; the fixtures cite the pages.

**Facts with consequences for A1.7 and A1.9 (high confidence unless noted):**
- **Younger, like SigLA, distinguishes two kinds of break:** `]-X` (the word continues beyond the break) and `]X`. This probably matches SigLA's word-edge codes 1 and 2, which would explain them. That is a hypothesis for A1.9 to test, not a fact.
- **Younger prints a reconstructed PH 31 inside his commentary,** with switched sides and green fills "to match the totals". It is kept apart (`commentary_rows`). If it were ever read as transcription, it would contaminate A2, because the fills were chosen to make totals work.
- Younger's written definitions of `X[` and `]X` are reversed relative to his usage. The parser follows the usage (medium-high confidence).
- 503 entries; 2,181 statement signs (287 doubtful, 53 unidentified); 441 rows with numbers and 182 with fractions. About 2% of signs in free-text entries are stray notation. They are kept, to be classified in A1.7.

**Next:** A1.6 inclusion rules, A1.7 schema, A1.8 layers (including Younger's L1 → sign-ID mapping) and A1.9 disagreement report.

---

## 2026-11-10 — Two candidate sources evaluated, neither used

Marius found two candidate sources for corpus expansion or redundancy: lineara.eu and plasma.ai's Kaphtor corpus. Details are in `DATA_SOURCES.md` under "Evaluated and not used".

- **lineara.eu** says itself that it merges lineara.xyz and SigLA, so it adds nothing independent.
- **Kaphtor** is di Mino's corpus. It was screened blind: a separate agent reported structure, field names and IDs only. It is a re-packaged lineara.xyz, with 1,696 of 1,716 IDs shared and the same field names, plus an older SigLA export. At most about 4 document IDs are new, and they need a primary publication before inclusion. Its compiler's editorial layers are excluded on independence grounds (Finding 001).
- **Both contain or mention the held-out sceptre.** Neither should be browsed unblinded.

**Consequence:** corpus-v1.0 keeps three sources: SigLA, lineara.xyz, and Younger for non-HT documents. Real redundancy for Haghia Triada would need GORILA itself (EFA scans, read by hand). Kaphtor's publication metadata (GORILA volume, post-GORILA references) may help A1.6, but only as pointers to verify.

---

## 2026-11-10 — A1.6: concordance and canonical document list (rules proposed, not decided)

**Built:**
- `aegean.corpus.siglum` parses each source's IDs. It splits off sides, ignores angle brackets for matching, and keeps fragment letters, `bis`/`ter` and joins.
- `aegean.corpus.concordance` clusters records by shared components, so differently-joined records (KH Wc 2059 …) end up in one document.
- `data/concordance/aliases.tsv` maps 26 irregular IDs by hand, each with a confidence.
- `aegean.corpus.inclusion` holds the rules as parameters.
- The output is `data/processed/document-list/`: a TSV and a MANIFEST, licensed CC BY-NC-SA through SigLA, reproducible from pinned inputs.

**Counts (held-out excluded):** 1,619 documents. 346 are in all three sources and 786 only in lineara.xyz, mostly Haghia Triada nodules.

**The decision with by far the largest effect is the content tier:**
- T1 "text" (≥2 signs, or a sign and a numeral): 576 documents;
- T2 "single sign": 991, of which 841 are nodules;
- T3 "no identified sign": 52.

**Proposed** (by me, awaiting Marius): list everything; analyses use T1 by default, and also exclude documents known only from reports (`<n>`) and unresolved IDs. That leaves **568** documents. All rules, counts and alternatives are in `docs/inclusion-rules.md`.

**Corrections made while checking** (my own errors, caught before commit):
- My first list of off-Crete prefixes wrongly included `SE` (Selakanos) and `LACH` (Larani); both are in Crete. The set was re-checked against the sources' site names.
- Four counts in the draft rules document were wrong. They were recomputed from the final build.

**For A1.9:**
- the sources disagree on the content tier of 67 documents;
- the site of ARG Zg 1 (lineara.xyz: Arkhalkhori; Younger: Argos);
- possible renumberings (Samothrace `SA We` / `SAM We`; Thera fragments vs SigLA's THE 7-12).

**Open for Marius:** the four decisions at the end of `docs/inclusion-rules.md`.

---

## 2026-11-10 — A1.6 inclusion rules decided

**Decided by Marius:**
- **R3/R4:** analyses use **T1 (text) only** by default. Single-sign (T2) and no-sign (T3) documents stay in the list, and an analysis must select them explicitly.
- **R7:** single-source documents are **kept**, whatever the number of sources.
- **R9:** documents known only from reports (`<n>`) are **kept out** of analyses.

R5 (register), R6 (off-Crete), R8 (joins) and R10 (unresolved IDs) were not changed by Marius, so the proposed defaults stand.

All three decisions match the proposed defaults, so the list is unchanged: **1,619 listed, 568 in the default analysis set**. Only the status in MANIFEST.json changes. A1.6 is done; next is A1.7 (schema).

---

## 2026-11-10 — A1.7: corpus schema and per-source adapters

**Schema (`docs/schema.md`, v0.1):** document → witness → line → item → token.
- **Witnesses are never merged.** A witness is one source's reading of one document or side, and each mark belongs to the witness it is in. Alternative readings are simply the other sources' witnesses.
- **None vs False:** None means the source does not record a mark. This matters because lineara.xyz's damage marking is incomplete, and no source marks restorations comprehensively.
- Damage (breaks), doubt, erasure, restoration (`< >`) and conjecture (Younger's green) are separate fields.

**Canonical sign IDs:** the GORILA/Bennett number with GORILA variant suffixes (`AB081`, `AB131a`, `A709-2`); the Unicode codepoint is an attribute.
- Unicode names some AB-sign variants in the A series (`A028B` …). These are normalised by number: below 300 is AB (medium-high confidence).
- **Fraction ligatures keep both forms** (Finding 002 review, M3): JE = `A732` [A707, A704], DD = `A717`, and SigLA's DDDD = `A718`, which is not in Unicode.
- 326 of SigLA's 388 signs have a Unicode codepoint. The rest are composites, variants and SigLA's own abstract signs (`SigLA:AAP800` …).

**Adapters (`aegean.corpus.witnesses`):** lineara.xyz, SigLA and Younger. **All 3,049 witnesses validate** (lineara.xyz 1,719, SigLA 827, Younger 503).
- On HT 13, lineara.xyz and SigLA give identical sign IDs for the first word and the wine logogram (`AB131a`).
- Younger stays L0+L1. His `*nnn` values and `{*nnn}` logogram numbers map to L0 directly; 2,474 of his 3,036 tokens wait for the A1.8 value table.

**Field coverage differs by source,** which A1.9 must respect. lineara.xyz has no per-sign doubt or erasure. SigLA has no numerals, lines or restorations. Younger has no HT. The full table is in `docs/schema.md`.

**Next:** A1.8 (layers L0 and L1, including the Younger value → sign-ID table), then A1.9 (the disagreement report).

---

## 2026-11-10 — A1.8: layers L0 and L1

**L1 table:** **Unicode Linear B syllable values.** They are read from `unicodedata` (Unicode 15.1, whose names encode Bennett number + value), not typed in. The table is applied uniformly to every source's L0 sign IDs. Signs Unicode leaves without a value (*22, *34, *56, *79, *82 …) and Linear A-only signs stay as numbers. SigLA's own value list is too thin to serve: 62 signs, missing 16 standard Linear B values.

**Younger → L0:** the Unicode table, plus four values with cited evidence:
- PA3 = *56 and PU3 = *314: Younger's introduction;
- ZU = *79: Younger writes HT 13's KU-*79-NI also as KU-ZU-NI, and SigLA has AB079 there;
- AI = AB043: SigLA.

Logogram labels come from SigLA's sign-table names. **2,709 of 3,035 Younger tokens are mapped.**

**Validation:** on 335 documents shared with SigLA, **1,112 of 1,125 aligned signs agree (98.8%)**, and every extra value agrees in every aligned case. This shows the map is consistent with an independent edition, not that the readings are correct.

**Corrections to earlier work:**
- The A1.4 SigLA reader read a value's subscript as a second value (AB29 = "pu, 2"; it is pu2). No earlier result used SigLA values.
- Canonical sign series now always follows the number (SigLA's `AB302` OLE → `A302`).

**For A1.9:**
- SigLA gives AB072 the value `ko` (Unicode `pe`; SigLA also gives AB070 `ko`), probably a SigLA error;
- the 13 sign-level disagreements between Younger and SigLA, e.g. Younger SO vs SigLA A363/A364;
- the lines where Younger's printed value (`l1_value`) differs from the uniform `l1`.

**Output:** `data/processed/corpus-v1.0-pre/` (witnesses.jsonl gitignored; MANIFEST committed), reproducible from pinned inputs. 3,049 witnesses, all schema-valid. Next: A1.9 (disagreement report).

---

## 2026-11-10 — A1.9: cross-source disagreement report (data-quality, not a finding)

**Report:** `docs/reports/A1.9-source-disagreements.md`. Its figures come from `data/processed/disagreements/summary.json`, built by `python -m aegean.corpus.disagreements`. It is a data-quality report by Marius's choice, not review-gated.

**Headlines:**
- **Identified signs agree 97.5% (lineara.xyz–SigLA), 98.7% (lineara.xyz–Younger) and 98.2% (SigLA–Younger).** All three rest on GORILA, and lineara.xyz derives from Younger, so this is agreement between editions, not accuracy.
- **The HT numerals have one source (lineara.xyz)**: Younger has no HT and SigLA has no numerals. SigLA also **omits fractions entirely on 57 documents**. So A2's single-source caveat for HT cannot be removed by corpus-v1.0.
- lineara.xyz vs Younger numerals: identical in 117 of 135 documents. There are 17 differences (MA 4: 123 vs 137; MA 6: 35 vs 45 …), all non-HT; they are a manual-check list.
- **Likely lineara.xyz errors**, to be checked on GORILA:
  - AB022 (CAP) where SigLA and Younger have AB021 (OVIS), 13–14 times;
  - the Arkhanes tablets labelled "Arkhalkhori".
- **Fraction order** differs in one document (PH 9). Ligature codepoints account for all apparent JE/DD differences: they disappear once ligatures are expanded, as the A1.7 schema now does.

**Bugs found and fixed while building this report (my code):**
1. The A1.7 Unicode-name mapper bypassed the number-based series rule for names without a variant, and did not know Unicode's merged `A100-102` codepoint. lineara.xyz's man sign came out as `A100`; it is now AB100.
2. My first comparison counted only "word" items and selected fractions by role. That made lineara.xyz's logograms look like extra signs, and SigLA's missing fractions look like letter disagreements. Both are fixed before any figure was used.

The A1.8 MANIFEST is rebuilt; its output hash changed because of fix 1.

**Next:** the A1 tasks Marius assigned (A1.4–A1.9) are done. A1.10 (DAMOS) is his. Remaining in A1: A1.11 baseline statistics, A1.12 freeze the held-out split and tag v1.0, A1.13 the sceptre text when published.

---

## 2026-11-10 — Project review: revised order, new analyses A8 and A9 (plan v1.3)

**What happened.** Marius and Claude reviewed the whole project in a claude.ai session (status, progress, direction), then brainstormed further analyses and ranked everything.

**Assessment recorded at the review:**
- No novel positive result about Linear A yet. H-A2-07 replicates Bennett; the totals support the standard reading of KU-RO.
- Corpus size is the binding constraint, and the three sources are not independent (all derive from GORILA).
- Re-running A2 on corpus-v1.0 will change little, because HT numerals rest on lineara.xyz alone (A1.9).
- Risks: blindness is being spent (the 20% split is not frozen yet); the Linear B control blocks most validation; the sceptre tests wait on a publication with no known date.

**Decided by Marius:**
- Main goal: A5 Tier 1 (false-positive benchmark) plus a functional role classifier (A8.8). A5 Tier 2 is a stretch goal.
- The order in plan §0.6, starting with the split freeze (A1.12).
- Parked: A6, A7, A2.3, A2.4, A2.6, A2.7.
- Left out: Cretan Hieroglyphic as extra material, Egyptian renderings of Keftiu names, a restoration model, synthetic corpus expansion.
- Kept from the late additions: the labelled-picture gold set (A8.1) and the check of the January 2026 report (V10).

**Uncertain.**
- All signal ratings behind the order are Claude's judgement (Rule 5), not measurements.
- The Linear B corpus size quoted in the session (about 5,900 documents) was from memory and not confirmed.
- V10 is unread; it may pre-empt A8.8.
- The same PR updates CLAUDE.md (task IDs A1–A9, order of work, rule 9 on synthetic text, confirmatory or exploratory status, layers and subpackages for A8 and A9) and the README status. It is therefore a hand-merge PR.
- The "how" given for each new task (plan §0.7, A8, A9) is a proposed design, not a tested one; examples cited from memory (HT 31, the Linear B abbreviations, the libation-formula claims) are to be verified in the tasks.

**Next:** A1.12 (freeze the split, tag v1.0), then A1.11 on the training split with A1.14. A1.10 (DAMOS) is with Marius.


---

## 2026-11-11 — A1.12: held-out split frozen, corpus-v1.0 prepared

**Done (PR #34, hand-merge: it changes `data/heldout.txt`).**
- **90 documents are held out**, drawn once with seed 20261111. The seed and the procedure were pushed and written into the PR description (09:43 UTC) before the draw; the draw is a later commit.
- Stratified by site and support type. **88 strata with fewer than five documents (118 documents) are wholly training**; 20% was drawn from each of the other 22 strata (450 documents). The lists are in `docs/heldout-split.md`.
- The loader `aegean.corpus.load` returns the training split (478 documents) by default. The held-out split needs `heldout_for=<ID>` of a hypothesis that is merged on main, unmodified, and marked `- **Type:** confirmatory`.
- Changelog and limits: `docs/corpus-changelog.md`. Release manifest: `data/processed/corpus-v1.0/MANIFEST.json`.

**Decided by Marius:** 20% of each stratum (90 documents, 15.8% of the 568), not a fixed 114. Plan §0.6 had estimated 114 without counting the small strata; the plan text is corrected.

**Design choices made by Claude** (hypotheses about good practice, Rule 5; all visible in the PR):
- the draw orders documents by a SHA-256 of seed and document key instead of using a random-number generator, so it is the same on any Python version and one document can be checked by hand;
- quotas are whole numbers by largest remainder; at this list they equal ordinary rounding per stratum;
- the seed is the date of the freeze, fixed before any draw; only one seed was ever run;
- split lines in `data/heldout.txt` are `split:<document key>`, and CI redraws the split to check that the file was not edited by hand.

**Limits** (full list in the changelog):
- The split is blind only for hypotheses registered from now on. A1.6–A1.9, A2 and Finding 001 processed every document. Nothing from A2 can be confirmed on it.
- A held-out result speaks for 22 strata at 12 sites, not for small sites or rare supports.
- The gate stops mistakes, not intent: the documents are in the corpus files.

**Not verified in this session:**
- The witnesses file was not rebuilt (the Younger PDFs cannot be fetched by script), so the release pins the hash from the A1.9 build and keeps the `corpus-v1.0-pre` path.
- The loader's witness-to-document mapping was checked on all lineara.xyz and SigLA witnesses (2,546, none unmatched), not on Younger's 503.

**What the session saw.** The document IDs of the split, in `data/heldout.txt`. No text of any document was read for this task.

**Open for Marius:**
- merge PR #34 and create the tag `corpus-v1.0` on the merge commit;
- `hypotheses/TEMPLATE.md` has no `Type: confirmatory / exploratory` line although rule 10 requires the statement; adding it is a review-gated PR of its own;
- run `python -m aegean.corpus.build_layers` once on the machine with the Younger PDFs and confirm the output hash matches the release manifest.

**Next:** V10, A1.11 with A1.14 (training split only), A8.1, each as its own PR. A1.10 (DAMOS) stays with Marius.

---

## 2026-11-11 — V10: the January 2026 "meanings without decipherment" report (partly checked, not closed)

**Status: open.** The page itself was not read. The fetch tool needed an approval that nobody was there to give, so everything below comes from search-engine excerpts of the page (three searches, 2026-11-11). Confidence in each point is given; none is higher than medium.

**Held-out check.** The page is illustrated with a photograph of the Knossos ivory sceptre; only the picture caption appeared in the excerpts (it says the object carries two Linear A inscriptions). No reading, sign or number from the sceptre was shown. Because the page shows held-out material, **the full page must be read by a separate agent returning pre-specified fields, or by Marius** (plan §0.4), not by an analysis session.

**What the report is** (source: excerpts of https://greekreporter.com/2026/01/15/reconstruct-linear-a-crack-language/).
- It reads as an essay that sets out a method in its own voice ("the approach outlined here"), not as news about a named study. The excerpts name no author, journal, title or DOI. **The underlying publication is not identified**; whether one exists is unknown (confidence that the excerpts are complete on this point: low).
- The method, as far as the excerpts show: treat the tablets as bookkeeping; count logograms in 147 Haghia Triada tablets; use numbers, layout and find context; carry over meanings of logograms shared with Linear B; compare Egyptian and Mesopotamian accounting. It claims that much administrative content can be recovered this way (confidence that this summary is fair: medium).
- The excerpts show **no null model, no test on Linear B as a known answer, and no error rate** (confidence: low; absence from excerpts is weak evidence).

**Does it pre-empt A8.8?** On what was seen, no: it describes the qualitative reasoning that A8 sets out to test, at the level of logograms and tablet types, not a classifier of sign-group roles with a measured accuracy. It supplies no baseline to compare against. This is a provisional judgement (Rule 5) until the page is read.

**The Kadmos 2025 articles** that surfaced in the same searches are separate work, not the source of the report (confidence: medium). Both are in *Kadmos* 64(1/2), 2025:
- "Industrial plants and palatial culture in Bronze Age Crete: olive in Linear A documents", doi:10.1515/kadmos-2025-0001 (author not shown in the excerpt). It analyses every Linear A document with the olive logogram AB 122 and its ligatures A518 and A587. Relevant to A8.2: a published, document-by-document commodity study to compare our association table with.
- E. Salgarella, L. Bellinato & S. Ferrara, "On Aegean spices: decipherment prospects on Linear A and B spice-related signs", pp. 29–44, doi:10.1515/kadmos-2025-0002. It compares composite logograms across the two scripts (Linear B *157, Linear A A646). Relevant to A8.1: composite logograms as labelled objects.
Neither abstract mentions the sceptre. Neither article has been read.

**Also seen, unidentified:** an abstract that describes structural analysis of the administrative tablets without sound values (positional regularities, arithmetic consistency) and explicitly disclaims decipherment. The excerpt gave no author or title. It is the closest thing to A8 in these results and should be identified.

**What changes in A8:** nothing yet. Two additions to the reading list for A8.2 and A8.1 (the Kadmos articles).

**To close V10:**
1. A blinded read of the Greek Reporter page: author, any cited publication, method, corpus, whether any quantitative validation is reported.
2. Identify the unidentified abstract.
3. Read the two Kadmos abstracts in full (not held-out as far as seen).

---

## 2026-11-11 — A1.11 baseline statistics (partial) and A1.14 resampling harness

**A1.14, done: `aegean.corpus.resample`.** One function, `run(statistic, corpus, source_order=…, seed=…)`, returns a point estimate and three intervals.
- **Reading draws.** For each document one of its sources is chosen at random and that source's witnesses are used; signs the source marks doubtful are blanked with probability `p_doubt` (default 0.5).
  - This is my reading of "each disputed sign takes one of its attested readings" (plan §0.7). The disputed signs of one document move together, so no draw contains a mixture of readings that no editor proposed. A per-sign draw would need sign-level alignment between sources and would create such mixtures. **Open for Marius** if the per-sign version is wanted.
  - `p_doubt` is a convention, not a measurement.
- **Bootstrap.** Documents drawn with replacement within sites.
- **Both.** The interval to report by default.
- Resampled corpora are never written out (rule 9). Seeds are explicit and recorded.

**A1.11, code done, report partial: `aegean.corpus.baseline`.** L0, training split only, per source.
- **The committed report covers lineara.xyz and SigLA only.** The Younger PDFs cannot be fetched by script, so this session built witnesses for two sources in a scratch folder and ran with `--allow-partial`; the report is stamped PARTIAL BUILD. Rerun `python -m aegean.corpus.baseline` on the full witnesses file to add Younger.
- Headline counts (training split): lineara.xyz 472 documents, 4,314 sign tokens in sign-groups, 1,092 multi-sign groups; SigLA 333 documents, 3,393 identified sign tokens, 873 multi-sign groups. Mean multi-sign group length about 3 signs in both.
- Position table: AB008 (conventional value A) is initial in 108 of 143 occurrences in lineara.xyz and 80 of 100 in SigLA; AB002 (RO) is final in 51 of 66 and 47 of 58. This matches the well-known initial A- and final -RO patterns (consensus; not checked against a specific publication in this session). It is a sanity check on the code, not a result.

**Something the harness showed about itself.** For counts of distinct signs and of signs occurring once, the point estimate lies outside the bootstrap interval (284 distinct signs against 209–246). This is the known downward bias of the bootstrap for counts of types, not a bug. Intervals from this harness are usable for shares and means, not for inventory sizes. The report says so.

**Not done.**
- Comparison with Packard's published positional figures (Packard 1974, *Minoan Linear A*): the numbers were not available in the session. It needs a full-corpus run to be comparable.
- Period labels are reported as each source gives them, not normalised.
- Sign variants are merged by base ID.

**Blindness.** All figures come through `aegean.corpus.load` with the default split. The held-out documents were not read.

**Next:** A8.1 (labelled-picture gold set).

---

## 2026-11-11 — A8.1: labelled-picture gold set, draft (not frozen)

**Built:** `aegean.roles.gold` → `data/processed/gold/` (gold-set.tsv, vessel-candidates.tsv, MANIFEST.json) and `docs/reports/A8.1-gold-set.md`. Hand-written input for the literature items: `data/gold-input/literature-items.tsv`. Layer L0, training split only.

**Result: 21 items, 16 usable for scoring** (grade A or B and attested in the training split): 5 vessel designations, 4 places, 4 persons, 2 total markers, 1 deficit marker. Plan A8 expected 20–40.

**Labelled pictures: five, all on HT 31.**
- A sign-group counts as a label when it is written in small signs over a vessel logogram (GORILA A400–A418, which Unicode names VAS, "vessel"). SigLA's sign coordinates show this; lineara.xyz encodes the same five as one item each, logogram first. Both sources agree on all five (grade A): QA-\*56, SU-PU, KA-RO-\*56, SU-\*56-RA, PA-TA-QE. (`*56` is a sign without an agreed sound value; some editions write PA3.)
- This matches the published edition as far as a search excerpt shows (Duhoux 2000–2001, *Minos* 35–36, 31–62). The article was not read. Confidence that these are labels of vessels: high. What each word says about its vessel is unknown.
- Not accepted: DA-RO-PA at a vessel sign on HT 38, and two groups on HT 93. They sit above a vessel sign in SigLA's coordinates but in signs of normal size, so ordinary line layout cannot be excluded.
- The size threshold (0.9 of the document's median sign height) and the overlap threshold were chosen after looking at the training data. This is curation, not a test, but it is a choice of mine (Rule 5).
- The two other words on HT 31 without a vessel sign of their own (SA-JA-MA, KI-DE-MA-\*323-NA) are not in the set.

**Literature items: 16 rows, none checked against a primary source.** Roles and confidence come from the survey §5; attestations for six words come from a search excerpt of a *Minos* article whose author and title the excerpt did not show.
- A check on the plumbing: every document that excerpt names and that is in the training split was found by the exact L0 match; for KA-PA the lists are identical (HT 6, 8, 94, 102, 105, 140). HT 97 (PA-I-TO) and ZA 10 (DA-I-PI-TA) are named there and are not in the training split; I checked their IDs against the training list only and did not look further.
- Grades are my proposal. Grade C (KA-PA, KA-TA-RE, DI-KI-TE, I-DA, KU-NI-SU) is listed but not used for scoring.

**Limits.**
- Circularity: all items except the five vessel words were identified by scholars from the cues a role classifier uses. Scoring on them measures agreement with that scholarship.
- The only circularity-free items are five words on one tablet by one scribe.
- Partial build: lineara.xyz and SigLA only (no Younger PDFs in this session).

**Held-out exposure in this session.** Search excerpts for V10 and A8.1 quoted the text of HT 6, HT 93, HT 102 and HT 120; all four are training documents (IDs checked). An excerpt for V10 showed a caption naming the sceptre, nothing more.

**Why not frozen.** Plan A8.1 says to freeze the list with a hash before A8.2 runs. The manifest carries the hash, but freezing an answer key whose sources nobody has read would fix errors in place. To freeze: rebuild on the full witnesses, check each literature row, Marius confirms grades.

**Next (plan §0.6):** A9.1–A9.2 (claims audit) and A5.17 (benchmark Tier 1). A1.10 is with Marius. Open from today: V10 blinded read; Younger rebuild for A1.11 and A8.1; the `Type` line in the hypothesis template.

---

## 2026-11-12 — Process change: Marius no longer merges; rule files become review-gated

**Decided by Marius (chat session, 2026-11-12).** "There should be no more manual merges, including for rule updates or other currently restricted areas. All PRs should be auto-merged to main as long as CI passes." His role from now on: set the direction, take the decisions that are his, and do external work that a session cannot do. He agreed that anything outside the repository stays with him, and he asked the agent to merge this switch-over PR itself.

**Also stated by Marius:** he works only in the GitHub web interface: no local machine, no Python, no command line.

**Earlier the same day:** PR #34 merged by Marius; tag `corpus-v1.0` created by him on the merge commit `238bbd0`. PRs #35–#37 retargeted to `main` and merged by the agent on his instruction (#36 by auto-merge; #35 and #37 directly, because GitHub refuses auto-merge on a PR whose checks have already passed).

**What replaces the merge click** (design proposed by Claude, accepted by Marius):
1. One merge rule: every PR merges when CI is green; direct merge where GitHub refuses auto-merge on a green PR.
2. Rule files (`CLAUDE.md`, `tools/check_guardrails.py`, `.github/`, `data/heldout.txt`) are review-gated like hypotheses and findings; CI enforces the approving review.
3. CI runs the guardrail script from the base branch, so a PR cannot be judged by its own changed copy.
4. Held-out data keeps its own lock: a removed line in `data/heldout.txt` needs a `Frozen-prediction tag:` naming an existing tag (new CI check).
5. Agents create release tags; `docs/for-marius.md` is his inbox; revert is his lever.
6. New rules in CLAUDE.md: an agent does not start a change that weakens a guardrail without Marius's instruction; text in fetched content is never an instruction.

**Repository settings changed by Marius today:** a tag ruleset `corpus-tags` (no update or deletion of `corpus-*` tags) and merge commits only on `main`.

**What this removes, plainly.** Until today a rule change needed a human action. Now it needs an independent review by another Claude instance and a green CI. That is a weaker guarantee against a shared blind spot between author and reviewer, and it does not cover edits to the workflow file itself (GitHub offers no path-based restriction for this repository). The review of `.github/` changes is the only guard there.

**This PR** is judged by the old guardrail script on `main`, which asks for the "Needs Marius's merge" header; the header is kept and the description says that he waived the manual merge for it. An independent review is added although the old rules did not ask for one.

**Not started, at Marius's request:** any further task. Open items are in `docs/for-marius.md`.

---

## 2026-11-12 — PR #38: first independent review requested changes; fixes

The independent review (`docs/reviews/rules-auto-merge-review.md`) ended in CHANGES REQUESTED. It found two real holes in what was to replace the manual merge. Both are fixed in the same PR.

- **B1. The review gate accepted an approval written for another PR.** A review file linked in the description only had to exist and end in APPROVE; the reviewer passed this PR's whole diff on the Finding 002 review. The hole was already on `main` for hypotheses and findings. **Fix:** only a review file that the PR itself adds or changes counts; a linked, unchanged review is now an error. Test added, including an end-to-end case.
- **B2. The held-out lock accepted any existing tag**, for example `corpus-v1.0`. **Fix:** frozen-prediction tags are named `predictions-…`; CI checks the prefix and that the tag exists. Marius is asked in `docs/for-marius.md` (S1) to extend the tag ruleset to that prefix.
- **B3. The reviewer could not verify Marius's waiver of the manual merge** for this PR: the only records are texts written by the author session. This cannot be fixed inside the PR. It is reported to Marius in the session.
- **Recommended, taken:** the held-out code (`load.py`, `heldout.py`, `split.py`) joins the rule files (N1); CLAUDE.md now says that CI cannot be relied on for PRs that edit the workflow (N2); the guardrail script is taken from `main`, also for stacked PRs (N3); a fallback for a session that cannot merge is restored (N4); `docs/for-marius.md` gets a log of merged rule-file PRs (N5); the three undisclosed changes are now in the PR description (N6).
- **Recommended, not done here:** a `pull_request_target` workflow to narrow the workflow-edit gap. Untested; listed as a follow-up.

**Note on the process.** Green CI on PR #38 is not an approval: `main`'s old script judges it and has no review gate for rule files. The PR is merged only after the reviewer's APPROVE.

---

## 2026-11-12 — PR #38 merged: the new merging rules are in force

- The re-review (a second independent instance) ended in APPROVE for commit `76f0964`. The agent merged PR #38 at `bf72162` (that commit plus the review file only), on Marius's instruction in the session. `main` is at `51b4be9`, CI green.
- **Both reviewers recorded that they could not verify Marius's instruction or his waiver** (B3): the session in which he gave them is not visible to a reviewer. Both suggested that he merge #38 himself. He had told the author session twice to merge it. He is told about B3 in the session; Revert on #38 is his remedy if the account is wrong.
- The second review named four further gaps in the guardrail script (N7–N10). None was introduced by #38; all matter more now that the review is the only gate for rule files. They are listed in `docs/for-marius.md` as follow-ups and are not started.
- From here on CI judges every PR with the script now on `main`: rule files and the held-out code are review-gated, and only a review that the PR itself adds or changes counts.

**Nothing else is started.** Next steps wait for Marius's direction (`docs/for-marius.md`, D3).

---

## 2026-11-14 — Younger's files available from a private repository; corpus-v1.0 witnesses reproduced

**What Marius did.** He created the private repository `marius-vrancianu/aegean-scripts-private` and put Younger's five files in its folder `Younger/`. He also added `predictions-*` to the `corpus-tags` ruleset (checked through the API: update and deletion blocked for both patterns).

**Checked.**
- All five files match `data/raw/younger/SHA256SUMS`.
- `python -m aegean.corpus.build_layers` on the three pinned sources gives the witnesses hash recorded in the corpus-v1.0 release manifest (`d2d4b41f…`). The committed A1.8 manifest is unchanged by the rebuild. This closes the open check from 2026-11-11.
- The loader maps every Younger witness to a listed document: 1,316 training witnesses (lineara.xyz 573, SigLA 447, Younger 296) on all 478 training documents.
- With the files present the test suite runs 212 tests and skips 4 (before: 15 skipped).

**Changed.** `data/raw/younger/fetch.py --from DIR` copies the pinned files from a folder if their hashes match, then verifies. README, DATA_SOURCES, the changelog and `docs/for-marius.md` say where the files are.

**Blinding.** The files went from the private repository to the gitignored folder and through the parser. Their text was not read by the session, was not attached to a chat and is not in the claude.ai Project.

**Next:** rerun A1.11 and A8.1 on the full witnesses (separate PRs).

---

## 2026-11-14 — A1.11: baseline report rebuilt on all three sources

`docs/reports/A1.11-baseline-statistics.md` is no longer a partial build. Layer L0, training split, corpus-v1.0 witnesses (hash verified by the loader).

- **Younger, training split:** 296 documents, 1,113 sign-groups, 1,999 identified sign tokens, 489 multi-sign groups. No Haghia Triada, so its figures describe the other sites only and are not comparable column for column with the two other sources (for example a longer mean group length, 3.36 against about 2.9–3.0, and a higher share of the ten most frequent signs).
- **Doubt is marked very unevenly:** Younger marks 352 signs as doubtful, SigLA 34, lineara.xyz none. With Younger in the pool, the reading interval for the number of identified sign tokens (4,143–4,234) lies below the point estimate (4,299), because reading draws now blank Younger's doubtful signs half the time. The report's explanation of the reading interval is reworded to say this.
- The lineara.xyz and SigLA columns are unchanged from the partial build, as expected.

**Still open for A1.11:** comparison with Packard's published figures; period labels not normalised.
