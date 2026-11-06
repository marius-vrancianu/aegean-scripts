# Data sources

Every dataset used anywhere in this repo is listed here before it is used. Fields: what it is, exact version, licence (verified or not), whether we may redistribute it, transcription conventions, and known problems.

## lineara.xyz (Linear A Explorer)
- **What:** `LinearAInscriptions.js`, a JavaScript data file with one record per inscription: `parsedInscription` (Unicode Linear A / Aegean numbers), `words`, `transliteratedWords`, `translatedWords`, `site`, `support`, `scribe`, `context` (period), `findspot`, image links.
- **Source:** https://github.com/mwenge/lineara.xyz (data pipeline in https://github.com/mwenge/LinearA). Built from the GORILA scans (École française d'Athènes) and John Younger's transliterations and commentary.
- **Pinned version:** commit `9c81beba669a4ffec3f5b29d4e7748d02c060eff`; file SHA-256 `9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e` (1,609,512 bytes). Fetched 2026-11-02.
- **Licence:** the repo has no LICENSE file, but the data file itself opens with a **public-domain dedication** ("The author disclaims copyright to this source code. In place of a legal notice, here is a blessing…", the SQLite blessing; seen 2026-11-04). That covers the maintainer's own work. It cannot cover the underlying GORILA transcriptions and images (École française d'Athènes). We still fetch rather than commit the file. Derived L0 corpus files are also regenerated, not committed, until A1.12 settles this. Open item V2 / A1.3.
- **Conventions:** GORILA sigla as document names (e.g. `HT104`, sides as `HT122a`). `transliteratedWords` uses Linear B homomorph values (L1). `translatedWords` contains interpretive glosses and converts fractions to numbers. **Neither may be used as L0 input.**
- **Known issues:** derived source; readings must be checked against GORILA / SigLA (A1.9).
  - **Damage marking is incomplete.** U+1076B (lacuna) marks some broken edges. Other damage appears only as editorial brackets in `transliteratedWords` (e.g. HT 104 `TE+RO[`), or not at all: HT 104 lines 3–4 lie in a stippled damage band in the GORILA facsimile but carry no flag. corpus-v0.1 records both signals; neither is complete.
  - The line breaks in `words` follow lineara's entry segmentation, not always the tablet's physical lines.
  - **Ruled lines** (horizontal rulings dividing sections) appear to be encoded as a token "—" (U+2014). The token sits exactly where rulings are drawn on HT 117a, ZA 15b, HT 130 and HT 131b (checked against GORILA facsimiles 2026-11-06). This is an inferred convention, medium-high confidence.
  - Two records share the ID `KH101` (one empty). The builder keeps the non-empty one.
  - The snapshot includes the held-out sceptre records (KNZg57a, KNZg57b, KNZg58), which are excluded by name before parsing. Exact-token counts on this snapshot: KU-RO in 34 document sides, KI-RO in 12, PO-TO-KU-RO in 2 (HT 122a/b).

## SigLA — The Signs of Linear A
- **Source:** https://sigla.phis.me (Salgarella & Castellan).
- **Licence:** **CC BY-NC-SA 4.0**, verified 2026-11-06 in the site footer, which says the dataset and drawings are available under it.
  - **Redistribution** is allowed, so the raw snapshot may be committed.
  - **Attribution:** credit Salgarella & Castellan.
  - **NonCommercial:** no commercial use.
  - **ShareAlike:** corpus files derived from SigLA must carry the same licence, including corpus-v1.0 if it contains SigLA data. Code that only processes the data is not affected. Each derived file needs a licence notice.
- **Access:** no download or export link on the site. The project paper (https://sigla.phis.me/paper.html) says the site can be downloaded and run locally, and that its data is a JSON database built from the drawing files. A1.4 should find that JSON rather than scrape HTML pages.
- **Not yet used.**

## DAMOS — Database of Mycenaean at Oslo (Linear B control corpus)
- **Source:** https://damos.hf.uio.no
- **Licence:** content **CC BY-NC-SA 4.0**, software GPL-3.0 (damos.hf.uio.no/about/database, checked 2026-11-04). Anything derived from DAMOS texts must carry NC-SA terms, which constrains the repo's eventual licence choice.
- **Access:** no bulk download yet. Aurora 2024 (*Ariadne* Suppl. 5, p. 157): "Downloading possibilities are currently limited to downloading word search results", as CSV. A full release (TXT and EpiDoc XML) is stated as "the ultimate goal".
- **Options for A2.4 / A3 / A4:**
  - (a) word-search CSV exports (e.g. *to-so*, the Linear B "total" word) plus the online texts of the matching tablets, used within NC-SA terms;
  - (b) ask the editor (Federico Aurora, UiO) for a data extract.

  Not yet used.

## NeuroDecipher data (Luo, Cao & Barzilay 2019)
- **Source:** https://github.com/j-luo93/NeuroDecipher, `data/` (Linear B–Greek cognates, 919 pairs; Ugaritic–Hebrew from Snyder et al. 2010). **Licence not yet checked** (A5.1). Not yet used.

## Corazza, Ferrara, Montecchi, Tamburini & Valério 2021 (fraction values)
- **What:** "The mathematical values of fraction signs in the Linear A script: A computational, statistical and typological approach", *Journal of Archaeological Science* 125:105214.
- **Open copy:** https://cris.unibo.it/retrieve/e1dcb336-9b0e-7715-e053-1705fe0a6cc9/Montecchi_JAS_125_2021.pdf, CC BY-NC-ND 4.0. Cite it; do not commit it or derivatives of its text.
- **Contents relevant to A2.** Verified from the PDF on 2026-11-05. Full notes, with page references: `docs/references/corazza-2021-notes.md`. The points below match the PDF:
  - Six premises encoded in MiniZinc and solved with Gecode. Simulation 1 gave 2,172,836 solutions; Simulation 2 (without L) gave 3,794,740. The solutions were ranked by frequency-vs-divisibility, ambiguity of combinations, typology, and an optimality score (best 0.67094).
  - Final values (Table 8): J 1/2, E 1/4, F 1/8, B 1/5, D 1/6, K 1/10, L2 1/20, L3 1/30, L4 1/40, L6 1/60, H 1/16 (tentative), A 1/24 (tentative). W, X, Y, Ω and L were left unvalued.
  - **No per-tablet list of totals used as constraints.** HT 104 and PE 1 are cited as support for J = 1/2. HT 123b, the MM II Phaistos tablets and several uncertain readings were excluded. No error tolerance is stated.
  - No supplementary data or code link was found.

## openscriptures HebrewLexicon (used in Finding 001)
- **Source:** https://github.com/openscriptures/HebrewLexicon, `HebrewStrong.xml`. CC BY 4.0. Pinned at commit `21c9add13bc727d3a951361778e97e3ff7afd1ce`, sha256 `a628f4f89f8bdaf2483fd3faf1abc8653cc6717758dfc9f24beb7571d9bdd0c4`. The 2026-10-28 fetch used `master` without recording a commit; reproducing Finding 001 exactly on this pin confirms the same content. Fetched by `experiments/finding-001/reproduce.py`.

## Kanta, Nakassis, Palaima & Perna 2025 (Knossos sceptre overview) — HELD OUT
- doi:10.26248/ariadne.vi.1841, CC BY-NC-SA 4.0. Descriptive only, no sign-by-sign text. **Held-out material: do not read or ingest** (see `CLAUDE.md`).
