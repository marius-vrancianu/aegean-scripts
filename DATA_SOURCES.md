# Data sources

Every dataset used anywhere in this repo is listed here before it is used. Fields: what it is, exact version, licence (verified or not), whether we may redistribute it, transcription conventions, and known problems.

## lineara.xyz (Linear A Explorer)
- **What:** `LinearAInscriptions.js`, a JavaScript data file with one record per inscription: `parsedInscription` (Unicode Linear A / Aegean numbers), `words`, `transliteratedWords`, `translatedWords`, `site`, `support`, `scribe`, `context` (period), `findspot`, image links.
- **Source:** https://github.com/mwenge/lineara.xyz (data pipeline in https://github.com/mwenge/LinearA). Built from the GORILA scans (École française d'Athènes) and John Younger's transliterations and commentary.
- **Pinned version:** commit `9c81beba669a4ffec3f5b29d4e7748d02c060eff`; file SHA-256 `9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e` (1,609,512 bytes). Fetched 2026-11-02.
- **Licence:** **none found.** The repo has no LICENSE file (checked 2026-11-04), which by default means all rights reserved. **Do not commit the file.** Use `data/raw/lineara.xyz/fetch.py`. Open item V2 / A1.3: ask the maintainer.
- **Conventions:** GORILA sigla as document names (e.g. `HT104`, sides as `HT122a`). `transliteratedWords` uses Linear B homomorph values (L1). `translatedWords` contains interpretive glosses and converts fractions to numbers. **Neither may be used as L0 input.**
- **Known issues:** derived source; readings must be checked against GORILA / SigLA (A1.9). Exact-token counts on this snapshot: KU-RO in 34 document sides, KI-RO in 12, PO-TO-KU-RO in 2 (HT 122a/b).

## SigLA — The Signs of Linear A
- **Source:** https://sigla.phis.me (Salgarella & Castellan).
- **Licence:** reported as CC BY-NC-SA 4.0 by third parties; **not yet verified on the site** (V1 / A1.2). Not yet used.

## DAMOS — Database of Mycenaean at Oslo (Linear B control corpus)
- **Source:** https://damos.hf.uio.no. Online browse and search; raw-data release was "being developed" per Aurora 2024. **Availability and terms not yet established** (V3 / A1.10). Not yet used.

## NeuroDecipher data (Luo, Cao & Barzilay 2019)
- **Source:** https://github.com/j-luo93/NeuroDecipher, `data/` (Linear B–Greek cognates, 919 pairs; Ugaritic–Hebrew from Snyder et al. 2010). **Licence not yet checked** (A5.1). Not yet used.

## openscriptures HebrewLexicon (used in Finding 001)
- **Source:** https://github.com/openscriptures/HebrewLexicon, `HebrewStrong.xml`. CC BY 4.0. Fetched 2026-10-28; commit not recorded (to be added when Finding 001 code is moved in).

## Kanta, Nakassis, Palaima & Perna 2025 (Knossos sceptre overview) — HELD OUT
- doi:10.26248/ariadne.vi.1841, CC BY-NC-SA 4.0. Descriptive only, no sign-by-sign text. **Held-out material: do not read or ingest** (see `CLAUDE.md`).
