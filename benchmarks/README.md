# Evaluation: real BibTeX, normalization regressions, and paired model runs

## Findings

The corrected helper routes the six reported formatting cases from **5 identity-conflict flags to 0**. [Before/after output](results/normalization-regression.json).

It also flags a real title typo in the imported GPflow bibliography: **Variatinoally → Variationally**, case R009. [Caught-issues example](../examples/caught-issues.md).

The paired model pilot completed on **2026-10-19**, with `gpt-6.1-sol`, medium reasoning, Codex CLI `0.163.0-alpha.10.2`, and three repeats per condition:

- **Bibliography, 19 cases:** baseline correct counts 13/14/13; skill 13/14/13. Both average 70.2% label agreement. Mean macro-F1: **0.7809 baseline / 0.6699 skill**.
- **Semantics, 15 cases:** both conditions scored 15/15 in every repeat, macro-F1 **1.0000**. The new passages still have a ceiling effect.
- **Coverage:** every run returned all 34 predictions. No tool-use events were observed.
- **Mean wall time:** 23.08 seconds baseline; 27.25 seconds skill.
- **Mean input/output tokens:** baseline 19,103 / 1,183; skill 23,265 / 1,386. Cached-input tokens are recorded separately in the run files.

**This pilot did not demonstrate an overall advantage for the skill.** Bibliographic identity-conflict precision improved from 0.667 to 1.000, but other routing decisions worsened; that isolated improvement does not overturn the overall result. All repeats and disagreements are retained.

[Aggregate results](comparison/summary.json) · [Run manifest](comparison/run-manifest.json) · [Raw baseline response](comparison/baseline-1.json) · [Raw skill response](comparison/skill-1.json)

## Dataset

### Bibliographic cases

[originals.bib](real-world/originals.bib) preserves nine entries from the actual GPflow documentation bibliography, including protected capitalization, TeX accents, particles, venue abbreviations, preprint labels, and the observed title typo. The input entries are imported from an immutable upstream Git blob. The candidate records were inspected separately on JMLR, PMLR, NeurIPS, and arXiv pages.

[provenance.json](real-world/provenance.json) records the upstream URL, blob ID, SHA-256, and selected keys. [records.json](real-world/records.json) contains the separately recorded primary metadata. [bibliographic_cases.json](real-world/bibliographic_cases.json) contains 19 cases: nine upstream entries, six surface variants, two wrong candidates, an author-only discrepancy, and one unavailable-record control. [gold.json](real-world/gold.json) stores labels and reasons separately.

The six Korean/romanized-name and other reported regression cases are [synthetic fixtures](../tests/fixtures/legitimate_variants.json), kept separate from the real BibTeX set.

### Semantic cases

[evidence.json](real-world/evidence.json) contains six short verbatim primary-source passages, URLs, and locators. Mathematical typography is rendered as plain text. Each claim is judged against its supplied passage, not the unseen full paper.

[semantic_cases.json](real-world/semantic_cases.json) contains 15 constructed claims: 3 supported, 4 partially supported, 3 not supported, 2 contradicted, 2 unresolved, and 1 not assessed. Examples test comparator expansion, experimental time versus worst-case complexity, dataset-to-deployment generalization, fixed-parameter asymptotics, and a global-optimality claim. [semantic_gold.json](real-world/semantic_gold.json) holds the annotations.

### Previous set

The previous 40-entry copy-and-mutate corpus remains in this directory for parser/comparison regression testing. Its 39/40 result from the earlier release is retired as performance evidence. It does not measure the skill's added value.

## Reproduce checks and scores

From the repository root, using Python 3.10+:

```bash
python -m unittest discover -s tests -v
python benchmarks/check_real_world.py
python benchmarks/summarize.py
```

The helper's recorded candidate comparison is [real-world-preflight.json](results/real-world-preflight.json). It agrees with 18/19 routing labels, with zero identity-conflict flags on the 15 upstream/surface-variant cases. Its disagreement at R002 concerns whether the GPflow author spelling should be accepted after normalization or sent for review; this is an annotation boundary requiring independent adjudication.

`summarize.py` scores all six model responses, computes per-status precision/recall/F1 and coverage, and retains paired skill-minus-baseline differences for every repeat. Missing predictions count as false negatives. A class with no predicted positives uses precision=0. Gold annotations are hashed with the summary.

## Re-run the paired model experiment

Export the inputs and schema contract:

```bash
python benchmarks/evaluate.py --export-prompts benchmarks/runs/prompts
```

The baseline receives a short audit instruction; the skill condition additionally receives the frozen SKILL.md instructions. Both receive the same evidence, case IDs, allowed output statuses, and output format. The old common instruction telling models how to classify invented-looking references was removed. Gold labels and rationales are excluded from the prompt packets.

The CLI runner uses six fresh ephemeral sessions, an empty working directory, disabled shell/search/multi-agent tools, and fixed order baseline-1, skill-1, skill-2, baseline-2, baseline-3, skill-3. It checks observed tool events and stops on an environment failure. Model calls use the signed-in account's ordinary usage allowance.

```bash
python benchmarks/run_codex.py --prompts benchmarks/runs/prompts --out benchmarks/runs/comparison --raw benchmarks/runs/raw --isolation-dir benchmarks/runs/empty --model gpt-6.1-sol --reasoning-effort medium
```

The output and isolation directories should be fresh. Raw runtime logs remain local. Use the actual model/settings you intend to test; the example above reproduces this pilot's requested model alias and effort.

Score an individual exported response:

```bash
python benchmarks/evaluate.py --predictions benchmarks/comparison/baseline-1.json --out benchmarks/runs/recheck.json
```

Run files record the requested model alias, CLI version, reasoning effort, input/skill hashes, latency, token usage, observed tool events, and all predictions. Backend snapshot ID, temperature, and sampling seed were not exposed by this CLI. The model alias and shared runtime instructions are part of the recorded host context.

## Limitations and next experiment

The cases were selected during development, not sampled from a target population; related cases share sources. Gold labels await independent human adjudication, particularly benign formatting versus review routing. This frozen-passage experiment does not measure retrieval quality, full-paper coverage, actual Korean-paper accuracy, or transfer across models/hosts. The semantic ceiling prevents a claim of added semantic rigor. The next useful evaluation needs independently annotated, longer multi-passage cases with mixed supporting and limiting evidence, grouped citations, source/version conflicts, and held-out papers. Predefine the routing rubric, freeze it before execution, and report all conditions even when the skill ties or loses.
