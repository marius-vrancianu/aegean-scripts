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
  - **Found in A1.9** (`docs/reports/A1.9-source-disagreements.md`):
    - The **Arkhanes tablets ARKH 1–7 and ARG Zg 1 have the site "Arkhalkhori"**. This is a lineara.xyz error: the prefix `ARKH` is Arkhanes.
    - **AB022 (CAP) appears where SigLA and Younger both have AB021 (OVIS)**, 13–14 times, through the codepoint `AB022F`; it needs checking on GORILA.
    - The man sign is encoded with Unicode's merged `A100-102` codepoint, normalised to AB100.
  - The snapshot includes the held-out sceptre records (KNZg57a, KNZg57b, KNZg58), which are excluded by name before parsing. Exact-token counts on this snapshot: KU-RO in 34 document sides, KI-RO in 12, PO-TO-KU-RO in 2 (HT 122a/b).

## SigLA — The Signs of Linear A
- **Source:** https://sigla.phis.me (Salgarella & Castellan).
- **Licence:** **CC BY-NC-SA 4.0**, verified 2026-11-06 in the site footer, which says the dataset and drawings are available under it.
  - **Redistribution** is allowed, so the raw snapshot may be committed.
  - **Attribution:** credit Salgarella & Castellan.
  - **NonCommercial:** no commercial use.
  - **ShareAlike:** corpus files derived from SigLA must carry the same licence, including corpus-v1.0 if it contains SigLA data. Code that only processes the data is not affected. Each derived file needs a licence notice.
- **Access:** no download or export link on the site. The project paper (https://sigla.phis.me/paper.html) calls the data a "JSON database". In fact the site loads **`https://sigla.phis.me/database.js`**, which holds two **OCaml `Marshal` values** (`signs`, `data`) inside JS string literals, not JSON. Decoded by `aegean.corpus.ocaml_marshal` and `aegean.corpus.sigla`; no scraping needed.
- **Pinned version:** `data/raw/sigla/0c4ef69f5de4/database.js`, **committed** (licence allows it). SHA-256 `0c4ef69f5de4cc3d9382cca782c1cf47e2ca1be40696bcfc8e97514f9b0781dd`, 2,199,743 bytes, server Last-Modified 2026-10-27, fetched 2026-11-10. Verify with `python data/raw/sigla/fetch.py`.
- **Contents:** 827 documents, 5,184 sign attestations, 1,417 words, 388 distinct signs. Field layout and how each field was checked: `data/raw/sigla/README.md`. No record of the held-out documents.
- **Conventions and known issues** (A1.4, 2026-11-10):
  - **No numeral values.** Numerals appear at most as an abstract `num` sign (`AAP800`, 7×). lineara.xyz stays the numeral source.
  - **Fractions:** `AAF701–718`. DD (`AAF717`) and DDDD (`AAF718`) are single signs; **there is no JE ligature**, so J and E are separate attestations. lineara.xyz has a single JE codepoint (A732), so the two sources tokenise these differently.
  - **Damage** is a per-word edge code (0 intact, 1 rendered `]-`/`-[`, 2 rendered `]`/`[`). The difference between 1 and 2 is not documented.
  - **Uncertain reading** is a per-sign flag. Erasures are flagged. Unidentified signs (`[?]`) and unclassified signs are kept as attestations without a sign ID. There is no restoration field.
  - **Conventional values** in the sign table are L1. They never enter attestations.
  - **Metadata ID differs from the key** in 7 documents (e.g. KH 87 → "KH 97", PH Wa 52 → "PE Wa 52"). Both are kept, for A1.9.
  - **Found in A1.9:** SigLA **omits all fractions on 57 documents** where lineara.xyz and Younger have them (KH 1, KH 10, KH 11, ARKH 1 …). It marks fewer word-edge breaks than the other sources. It gives AB072 the value `ko` (Unicode Linear B `pe`; also `ko` for AB070). It has more signs on tablets than the other editions (e.g. HT 29, HT 10, HT 49). The hypothesis is that SigLA draws damaged signs the others omit.
  - Period and support are free text with spelling variants (`Libation Table` / `Libation table`; `''`, `n/a`, `unknown`). They are normalised in A1.6/A1.7, not at ingest.
- **Citation:** Salgarella, E. & Castellan, S. (2020–). *SigLA: The Signs of Linear A. A palæographical database.* https://sigla.phis.me. Paper: https://sigla.phis.me/paper.html.

## John G. Younger, Linear A Texts in phonetic transcription (Academia.edu, 2024)
- **What:** Younger's transliterations with commentary, in tables of side.line, statement, logogram, number and fraction, plus free-text inscriptions. They are based on GORILA, with Younger's normalisation from 1994 and continual updates since.
- **Where:** the old site `people.ku.edu/~jyounger/LinearA/` **no longer exists** (domain gone, checked 2026-11-10; KU removed the server in early 2024, per Younger's folder introduction). Younger moved the material to Academia.edu as PDFs. Files, item URLs and hashes are in `data/raw/younger/README.md` and `SHA256SUMS`; Marius downloaded them by hand on 2026-11-10.
- **Used:** "Other Texts (not Haghia Triada)", last update 28 March 2024, 132 pp., SHA-256 `05305bc5…907201`.
- **Missing: the Haghia Triada texts.** The HT file was not found on Academia, and Marius found no Wayback capture of it. **Younger covers non-HT documents only.**
- **Licence:** none stated, so all rights are reserved by default. The files are not committed; `fetch.py` verifies a manual download.
- **Layer:** L1. Signs are given by Linear B values (KU-RO; *301 for signs without one). Mapping to sign IDs belongs to A1.8.
- **Reader:** `aegean.corpus.younger` (pdfplumber). Typography carries data that plain-text extraction loses:
  - bold = numbers;
  - **underline = doubtful reading**;
  - **green = Younger's conjectural restorations**;
  - red = commentary;
  - lowered small glyphs = subscripts (RA2).

  Details and evidence: `data/raw/younger/README.md`.
- **Known issues:**
  - Younger's written definitions of `X[` and `]X` are reversed relative to his own (standard) usage; the parser follows the usage.
  - Reconstruction tables in the commentary (PH 31) are kept apart from the transcription.
  - About 2% of statement signs in free-text entries are stray notation.
  - **Not independent of lineara.xyz**, which was built from Younger's earlier HTML pages.
- **Held-out:** before anyone read the files, a separate agent screened all of them, returning counts only. No held-out siglum occurs in them.

## Evaluated and not used (2026-11-10)
Recorded so nobody re-does the check. Neither source adds independent readings.

### lineara.eu
- **What:** a presentation site ("Built 2026-10-17"; no named maintainer) showing 753 of a stated 1,883 documents as tracings, with a search and download page (https://lineara.eu/search/).
- **Not used, because it is derived:** its footer says the corpus data is merged from lineara.xyz and SigLA, which are already sources here. No site-wide licence is stated.
- **Held-out:** the site mentions the Knossos sceptre (checked by yes/no only). Any future use needs blinded handling.

### Kaphtor (plasma-ai/kaphtor; T. di Mino, "Opening Linear A", plasma.ai, 2026-10-22)
- **What:** the corpus, lexicon and tools behind di Mino's Semitic ("Ya Diktu") reading, the method tested in Finding 001.
  - Code: Apache-2.0.
  - Own data: CC BY 4.0.
  - SigLA-derived parts: CC BY-NC-SA 4.0.
  - lineara.xyz-derived parts: no licence.
- **Screened blind on 2026-11-10** at commit `4b60a47030eb`. A separate agent reported structure, field names and document IDs only, then deleted the clone.
- **Not used as a source, because it is a re-packaged lineara.xyz:**
  - `data/linear-a/corpus.json` (1,716 documents, held-out excluded) uses lineara.xyz's own field names (`transcription`, `words`, `transliteratedWords` …).
  - **1,696 of its IDs are in our lineara.xyz snapshot.**
  - Its SigLA layer comes from an older SigLA export (802 documents, against 827 in ours).
  - Only 9 IDs are absent from all three of our sources. About half are spelling variants (`KNZb27` vs `KN Zb <27>`); at most about 4 look new: HT Wa 1071, HT Wa 1072, PK Zb X, SKO Zc 2. They enter corpus-v1.0 only with a primary publication.
  - "RILA-S1" is a source in name for only 2 records. Its 66 `post_gorila_publication` documents are all in lineara.xyz already.
- **Editorial independence:** the compiler is the proponent of a reading that Finding 001 found indistinguishable from chance matching. His corrections, readings, segmentations and translations must not enter the corpus.
- **Possible metadata use (CC BY 4.0 parts only), for A1.6:** `gorila_volume` (1,478 records), `source_provenance`, and the `rila_s1` status field (142 records). These are pointers to check against the publications, not facts.
- **Held-out:** the repository contains three records of the held-out documents, sourced to the 2024/2025 *Ariadne* publication, plus wiki pages about them. **Do not browse or clone it unblinded.** Any use must go through a separate agent that drops those records first.

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
