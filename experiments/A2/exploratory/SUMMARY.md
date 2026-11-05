# EXPLORATORY census of all accounting markers (generated)

corpus-v0.1, code 6f41219. **Not a pre-registered test.** See research-notes 2026-11-05.

## KU-RO — value set `corazza2021`

| Scope | Damage class | exact | near_miss_one_stroke | mismatch | unvalued | empty_scope | no_total |
|---|---|---|---|---|---|---|---|
| S1 | clean | 2 | 1 | 3 | 0 | 0 | 0 |
| S1 | damaged | 7 | 2 | 14 | 0 | 6 | 2 |
| S2 | clean | 0 | 1 | 4 | 0 | 0 | 0 |
| S2 | damaged | 5 | 1 | 23 | 0 | 1 | 2 |

## KU-RO — value set `schrijver2014`

| Scope | Damage class | exact | near_miss_one_stroke | mismatch | unvalued | empty_scope | no_total |
|---|---|---|---|---|---|---|---|
| S1 | clean | 2 | 1 | 3 | 0 | 0 | 0 |
| S1 | damaged | 7 | 2 | 14 | 0 | 6 | 2 |
| S2 | clean | 0 | 1 | 4 | 0 | 0 | 0 |
| S2 | damaged | 5 | 1 | 23 | 0 | 1 | 2 |

## KI-RO — value set `corazza2021`

| Scope | Damage class | exact | near_miss_one_stroke | mismatch | unvalued | empty_scope | no_total |
|---|---|---|---|---|---|---|---|
| S1 | clean (parser only) | 0 | 0 | 2 | 2 | 1 | 4 |
| S1 | damaged (parser only) | 0 | 0 | 3 | 0 | 2 | 2 |
| S2 | clean (parser only) | 0 | 0 | 2 | 0 | 0 | 3 |
| S2 | damaged (parser only) | 0 | 0 | 6 | 2 | 0 | 3 |

## KI-RO — value set `schrijver2014`

| Scope | Damage class | exact | near_miss_one_stroke | mismatch | unvalued | empty_scope | no_total |
|---|---|---|---|---|---|---|---|
| S1 | clean (parser only) | 0 | 0 | 2 | 2 | 1 | 4 |
| S1 | damaged (parser only) | 0 | 0 | 3 | 0 | 2 | 2 |
| S2 | clean (parser only) | 0 | 0 | 2 | 0 | 0 | 3 |
| S2 | damaged (parser only) | 0 | 0 | 6 | 2 | 0 | 3 |

## PO-TO-KU-RO — value set `corazza2021`

| Scope | Damage class | exact | near_miss_one_stroke | mismatch | unvalued | empty_scope | no_total |
|---|---|---|---|---|---|---|---|
| P1 | damaged | 0 | 1 | 0 | 0 | 1 | 0 |
| P2 | damaged | 0 | 0 | 2 | 0 | 0 | 0 |

## PO-TO-KU-RO — value set `schrijver2014`

| Scope | Damage class | exact | near_miss_one_stroke | mismatch | unvalued | empty_scope | no_total |
|---|---|---|---|---|---|---|---|
| P1 | damaged | 0 | 1 | 0 | 0 | 1 | 0 |
| P2 | damaged | 0 | 0 | 2 | 0 | 0 | 0 |

## Exact matches and one-stroke near misses (primary scopes S1/P1)

| Doc | Marker | Total | Entries | Damage | Corazza | Schrijver |
|---|---|---|---|---|---|---|
| HT102 | KU-RO | 1060 | 7 | damaged | near_miss_one_stroke (-10) | near_miss_one_stroke (-10) |
| HT104 | KU-RO | 95 | 3 | damaged | exact (0) | exact (0) |
| HT117a | KU-RO | 10 | 10 | clean | exact (0) | exact (0) |
| HT119 | KU-RO | 160 | 9 | clean | near_miss_one_stroke (1) | near_miss_one_stroke (1) |
| HT11b | KU-RO | 180 | 5 | damaged | exact (0) | exact (0) |
| HT122b | PO-TO-KU-RO | 97 | 2 | damaged | near_miss_one_stroke (1) | near_miss_one_stroke (1) |
| HT25b | KU-RO | 52 | 2 | damaged | exact (0) | exact (0) |
| HT85a | KU-RO | 66 | 7 | damaged | exact (0) | exact (0) |
| HT88 | KU-RO | 6 | 6 | clean | exact (0) | exact (0) |
| HT89 | KU-RO | 87 | 5 | damaged | exact (0) | exact (0) |
| HT94a | KU-RO | 110 | 5 | damaged | near_miss_one_stroke (-1) | near_miss_one_stroke (-1) |
| HT94b | KU-RO | 5 | 5 | damaged | exact (0) | exact (0) |
| HT9b | KU-RO | 24 | 7 | damaged | exact (0) | exact (0) |

## KI-RO relations (exploratory; 3 relations per KI-RO/KU-RO pair)

- `corazza2021`: 11 KI-RO/KU-RO pairs; a_kiro_eq_its_entries: {'mismatch': 4, 'unvalued': 4, 'empty': 3}; b_kuro_eq_all_minus_kiro: {'mismatch': 7, 'unvalued': 4}; c_kuro_eq_all_plus_kiro: {'mismatch': 7, 'unvalued': 4}
- `schrijver2014`: 11 KI-RO/KU-RO pairs; a_kiro_eq_its_entries: {'mismatch': 4, 'unvalued': 4, 'empty': 3}; b_kuro_eq_all_minus_kiro: {'mismatch': 7, 'unvalued': 4}; c_kuro_eq_all_plus_kiro: {'mismatch': 7, 'unvalued': 4}
