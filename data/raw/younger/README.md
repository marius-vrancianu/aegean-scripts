# John G. Younger's Linear A transliterations (Academia.edu, 2024)

**Not committed.** Academia.edu states no licence, so the files stay in the gitignored `academia-2024/` folder. This folder commits only `SHA256SUMS`, this README and `fetch.py`, which verifies a manual download.

## Why Academia, not the old website

Younger's site at `people.ku.edu/~jyounger/LinearA/` **no longer exists**: the domain does not resolve (`NXDOMAIN`, 2026-11-10). His folder introduction (23 April 2024) says KU removed the server in early 2024 and that he moved the material to Academia.edu as PDF and DOCX files. Marius found no Wayback Machine capture of the Haghia Triada page.

## Files (downloaded by Marius, logged in, 2026-11-10)

| File (`academia-2024/`) | Academia item | Younger's own date | PDF creation | Used |
|---|---|---|---|---|
| `Linear_A_Texts_in_phonetic_transcription.pdf` (132 pp.) | [120182370](https://www.academia.edu/120182370/Linear_A_Texts_in_phonetic_transcription_Other_Texts_not_Haghia_Triada), "Other Texts (not Haghia Triada)" | last update 28 March 2024 | 2024-05-29 | **yes**: the transliterations |
| `Linear_A_Texts_and_Inscriptions_in_phonetic_transcription.pdf` (53 pp.) | [117949876](https://www.academia.edu/117949876/Linear_A_Texts_and_Inscriptions_in_phonetic_transcription), introduction and commentary | last update 8 April 2024 | 2024-04-23 | conventions only (section 3c) |
| `Linear_A_Updates.pdf` (7 pp.) | [120182423](https://www.academia.edu/120182423/Linear_A_Updates) | last update 23 April 2024 | 2024-05-29 | dated corrections, for A1.9 |
| `Younger_JG_Linear_A_folder_introduction.docx` | [117949722](https://www.academia.edu/117949722/Younger_JG_Linear_A_folder_introduction) | 23 April 2024 | 2024-04-23 | provenance only |
| `Linear_A_Lexicon.pdf` (86 pp.) | Younger's Academia profile | n/a | 2024-05-29 | **not used** (interpretive, L1+) |

The PDF creation dates (Ghostscript 9.26) are probably Academia's processing, i.e. upload dates.

**Missing: the Haghia Triada texts.** The folder introduction lists six files, but neither the HT texts nor the syllabary could be found on Academia (medium confidence that they were never posted). So **Younger covers non-HT documents only.** For HT, corpus-v1.0 has two sources, SigLA and lineara.xyz. A1.9 must state this, and must also state that lineara.xyz was built from Younger's earlier HTML pages, so lineara–Younger agreement is not independent.

## Held-out screening

Before anyone read the files, a separate agent scanned all five programmatically (CLAUDE.md, blinded checks). It returned only match counts, page numbers and a few pre-specified tokens. Result: **no occurrence of the held-out documents' sigla** (`data/heldout.txt`), and no reference to their publications. The Knossos `Zg` documents named are numbers 4, 21 (`<21>`) and 55. The single "scepter" is in the KH Wc 2097 entry (a seal-motif description). These checks are recorded in research-notes 2026-11-10.

## Reading the PDF

Typography carries meaning that plain-text extraction (`pdftotext`) loses, so `aegean.corpus.younger` reads characters with font, colour and position via **pdfplumber 0.11.10** (`pip install -e ".[pdf]"`):

| Typography | Meaning | Evidence |
|---|---|---|
| bold black | numbers; the siglum of an entry heading | pages 15, 121 |
| black, or blue for a few hyperlinked headings (KH 100) | data | p. 43 |
| red | Younger's commentary | p. 121 |
| magenta | scribe, Schoep 2002 type | p. 121 |
| blue, not bold | table column headers | p. 121 |
| **underline** (thin filled rectangle) | "the reading of SIGN is doubtful" | introduction §3c; ZA 9, KH 3, KH 5 |
| **green** | Younger's **conjectural** fills of lacunae ("to match the totals") | p. 98 (PH 31) |
| small lowered glyph (7.9 pt vs 12) | subscript in sign values: RA2, PA3 | ZA 10, AP Za 2 |
| long thin rectangle | ruled line | KH 3 |

**Epigraphic conventions** (introduction §3c), as used in the tables:
- `]X` break before; `]-X` break before, word continues beyond it;
- `X[` break after; `X-[` break after, word continues beyond it;
- underline: doubtful reading;
- `[[X]]`: erased but legible;
- `<X>`: once extant, now lost and supplied (restoration);
- `-•-` / `[•]`: unidentified sign;
- `[ • • • ]`: lacuna, with Younger's estimate of lost signs;
- `•`: word divider or transaction marker.

Younger's written definitions of `X[` and `]X` read the reverse of standard usage. His usage is standard (ARKH 1a.1 `]TA-PI`), and the parser follows the usage.

**Commentary tables are not transcription.** After his commentary, Younger sometimes prints a reconstructed version of a tablet (PH 31: switched sides, green fills). Rows printed after the commentary starts go to `commentary_rows`, never `rows`.

## Parse statistics (`Linear_A_Texts_in_phonetic_transcription.pdf`)

503 entries (309 tables, 194 free-text inscriptions) from 52 site prefixes; 1,914 rows; 2,181 statement signs. Of those signs, 287 are doubtful, 53 unidentified, 4 erased and 2 restored. 441 rows have numbers, 182 fractions, 624 logograms; 27 ruled lines. 6 entries are empty in the source ("text not given", cross-references). Conjectural (green) signs occur only in `commentary_rows` (PH 31: 101 rows), never in `rows`.

**Known residue** (about 2% of statement signs): stray notation in free-text entries read as sign values (`vest.`, `or`, `ca.`, `(retrograde):`, numerals in inscriptions). These are kept, not dropped; A1.7/A1.9 classify them.

Fixtures checked against page images: `tests/test_corpus_younger.py`.
