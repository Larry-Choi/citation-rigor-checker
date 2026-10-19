# Evaluation: real BibTeX, normalization regressions, and paired model runs

## V2: diagnose first, then compare all three conditions

The original lower skill score was not sufficient evidence of worse citation judgment. See the [Korean case-by-case diagnosis](DIAGNOSIS.ko.md) and [reproducible decomposition](diagnosis-v1.json). Both conditions had exactly 13/14/13 correct bibliography labels. R003/R004 penalized equivalent arXiv representations; R007/R014 were venue-style boundaries; R002/R012 permit defensible alternative labels. R019 was labelled unavailable even though its matching record was in the packet. Removing only R019 reverses the original macro-F1 ranking: baseline 0.7079, skill 0.7908. That sensitivity analysis does not establish a skill advantage.

The actual title typo, year discrepancy, shortened substantive title, and two wrong-candidate cases were caught by both conditions on every repeat. Both noticed the author-only discrepancy; they used different severity labels. The baseline had never received the conservative label definition. V2 gives every condition the same operational definitions, resolves the evidence-availability bug, excludes two ambiguous IDs from primary scoring, and tests the unchanged original skill alongside the revision. The skill revision resolves contradictory abbreviation guidance and distinguishes missing links from unavailable evidence.

**Nine fresh model runs completed, three per condition**, gpt-6.1-sol, medium reasoning. Primary bibliography has **18 cases** (R002/R012 excluded before execution); all 15 semantic cases are retained:

- **Baseline:** bibliography [18, 18, 18] / 18, mean macro-F1 **1.0000**; semantics [15, 15, 15] / 15, mean macro-F1 **1.0000**. Mean wall time 22.25s; input/output tokens 19005/1115.
- **Original skill:** bibliography [18, 18, 18] / 18, mean macro-F1 **1.0000**; semantics [15, 15, 15] / 15, mean macro-F1 **1.0000**. Mean wall time 24.06s; input/output tokens 23607/1330.
- **Revised skill:** bibliography [18, 18, 18] / 18, mean macro-F1 **1.0000**; semantics [15, 15, 15] / 15, mean macro-F1 **1.0000**. Mean wall time 24.57s; input/output tokens 23802/1437.

Secondary sensitivity uses all 20 bibliography cases, including both ambiguous IDs:

- Baseline: all-case strict macro-F1 1.0000; acceptable-set macro-F1 1.0000.
- Original skill: all-case strict macro-F1 1.0000; acceptable-set macro-F1 1.0000.
- Revised skill: all-case strict macro-F1 1.0000; acceptable-set macro-F1 1.0000.

Every run returned all 35 predictions, with no observed tool events or runtime errors. Per-status precision/recall/F1, all repeats, and paired differences are in [summary.json](comparison-v2/summary.json); [run-manifest.json](comparison-v2/run-manifest.json) records settings/hashes, timing, and usage. Original and revised skills were frozen before execution; [the protocol](adjudicated-v2/PROTOCOL.md) specifies the balanced three-condition order. Cases are related and repeats are not independent new papers.

The common rubric makes this a comparison **beyond explicit task/label definitions**, not against an entirely unguided baseline. Changes to the rubric/dataset prevent causal before-versus-after claims from v1. The old-skill control measures the incremental revision under v2 conditions. Identical scores do not prove identical reasoning or universal equivalence. Semantic ceiling effects persist; longer documents, retrieval and independently annotated held-out cases remain untested.

### Reproduce V2

```bash
python -m unittest discover -s tests -v
python benchmarks/diagnose.py
python benchmarks/summarize.py --dataset adjudicated-v2 --directory benchmarks/comparison-v2 --include-old-skill
```

To perform new model calls rather than re-score saved predictions, choose fresh directories:

```bash
python benchmarks/evaluate.py --dataset adjudicated-v2 --export-prompts benchmarks/runs/v2-prompts
python benchmarks/run_codex.py --prompts benchmarks/runs/v2-prompts --out benchmarks/runs/v2-comparison --raw benchmarks/runs/v2-raw --isolation-dir benchmarks/runs/v2-empty --model gpt-6.1-sol --reasoning-effort medium --include-old-skill
python benchmarks/summarize.py --dataset adjudicated-v2 --directory benchmarks/runs/v2-comparison --include-old-skill
```

The runner consumes the signed-in account's model allowance. The exporter makes no model calls. Gold/accepted sets are excluded from all prompts. `comparison/SKILL.original.txt` preserves the exact v1 skill hash; root `SKILL.md` is the revision. [Adjudication changes](adjudicated-v2/adjudication.json) explain every revised label. R019 tests recovery from the available packet; new synthetic R020 tests genuinely missing evidence without claiming fabrication. The candidate comparison helper remains a conservative preflight and is not an implementation of this model task's packet-wide link recovery.

## V1 historical scores under the original rubric

The corrected helper routes the six reported formatting cases from **5 identity-conflict flags to 0**. [Before/after output](results/normalization-regression.json).

It also flags a real title typo in the imported GPflow bibliography: **Variatinoally → Variationally**, case R009. [Caught-issues example](../examples/caught-issues.md).

The paired model pilot completed on **2026-10-19**, with `gpt-6.1-sol`, medium reasoning, Codex CLI `0.163.0-alpha.10.2`, and three repeats per condition:

- **Bibliography, 19 cases:** baseline correct counts 13/14/13; skill 13/14/13. Both average 70.2% label agreement. Mean macro-F1: **0.7809 baseline / 0.6699 skill**.
- **Semantics, 15 cases:** both conditions scored 15/15 in every repeat, macro-F1 **1.0000**. The new passages still have a ceiling effect.
- **Coverage:** every run returned all 34 predictions. No tool-use events were observed.
- **Mean wall time:** 23.08 seconds baseline; 27.25 seconds skill.
- **Mean input/output tokens:** baseline 19,103 / 1,183; skill 23,265 / 1,386. Cached-input tokens are recorded separately in the run files.

**This pilot did not demonstrate an overall advantage for the skill.** Bibliographic identity-conflict precision was 0.667 versus 1.000, but the original routing labels and R019 access control were subsequently found to be flawed. The V2 diagnosis above supersedes the original interpretation of a skill loss. All repeats and disagreements are retained.

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

The B032 prefix regression is now fixed: `Deep learning` with a DOI resolving to `Human-level control through deep reinforcement learning` is an identity conflict, not a shortened-title review. Word-set inclusion was replaced by a word-boundary prefix check. [Before/after output](results/title-prefix-regression.json) records B032 as the only status change among the 40 legacy cases; all six legitimate-variant and 19 GPflow candidate-case statuses are unchanged. The current legacy replay agrees with all 40 labels, an engineering check rather than an accuracy estimate. Saved model comparisons were not re-run or altered for this helper-only fix.

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
