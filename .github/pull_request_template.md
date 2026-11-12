**Merge:** merges when CI is green / **Review-gated: `docs/reviews/…`** (touches `hypotheses/`, `findings/` or a rule file; see CLAUDE.md → Merging). A review-gated PR must *start* with the Review-gated line.

**Task ID:** A?.? — (title)

**What this does:**

**Layer:** L0 / L1 / L2 (plan §0.1)

**Hypotheses:** pre-registered in `hypotheses/H-…` (merged in PR #…) / none (infrastructure)

**Null model and known-script validation:** what was run, or why not applicable

**Corpus version:** tag + commit

**Result:** positive / negative / infrastructure only — link to `findings/…` if any

**Checklist**
- [ ] No raw data committed without a redistribution-compatible licence
- [ ] No held-out material read or committed (KN Zg 57/58, frozen split)
- [ ] Plan checkbox updated
- [ ] Anything I (an LLM) proposed is labelled as a hypothesis, not a finding
- [ ] Next steps / open questions noted for whoever resumes this
- [ ] Review-gated PRs: independent review file linked, ending in `Verdict: APPROVE`
- [ ] Rule-file PRs: no guardrail weakened, or the weakening is stated first and Marius's instruction is cited
- [ ] `docs/for-marius.md` updated if this raises or settles something for him
