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
