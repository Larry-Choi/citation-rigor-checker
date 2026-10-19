# Development benchmark and paired model protocol

This directory separates **deterministic metadata preflight**, **synthetic semantic cases**, and **actual model comparisons**. Only the first has measured results in this revision. No baseline-versus-skill model gain is claimed.

## Dataset

- `sources.json`: eight frozen Crossref bibliographic records across ML, biology, and research reporting, with primary API URLs and retrieval timestamps. Only selected metadata is included, not abstracts or full texts.
- `references.bib`: 40 entries generated from those records: 8 unmodified entries, 8 wrong DOIs, 8 changed years, 8 changed venues, 4 composite-author entries, and 4 invented fixtures.
- `gold.json`: separate intended labels and mutation provenance. An invented fixture's label is **unresolved**, never proof of nonexistence. Snapshot absence is not a search of the world's literature.
- `semantic_cases.json`: six assistant-authored cases: two supported, two contradicted, and two unresolved. Four use paraphrases from identified public papers; two test missing access/OCR ambiguity. These claims are evaluation constructions, not accusations of errors in the published papers.

The bibliographic target is a **preflight routing state**, not a fully verified publication. The development labels are authoring-assistant annotations, have not been independently adjudicated, and are not a held-out research benchmark. Only three of the six full semantic statuses are represented. No multilingual, PDF-extraction, comprehensive mapping, or large-document accuracy claim follows from this set.

## Reproduce the deterministic run

From the repository root, with Python 3.10+:

```bash
python -m unittest discover -s tests -v
python benchmarks/build.py
python scripts/bibliography.py benchmarks/references.bib --snapshot benchmarks/sources.json --out benchmarks/results/preflight.json
python benchmarks/evaluate.py --predictions benchmarks/results/preflight.json --out benchmarks/results/metrics.json
```

The snapshot run uses no network. `build.py` fixes the random seed at 20261019. Input/snapshot hashes are stored with the preflight output. `results/metrics.json` contains per-status precision, recall, F1, support, coverage, and missing IDs.

### Measured result, 2026-10-19

On these 40 synthetic metadata cases, preflight routing agreed with the intended label on **39/40 (97.5%)**, with **macro-F1 0.9758** and **40/40 coverage**. This is a small, deliberately simple development-set regression check—not an estimate of real-world citation-audit accuracy.

- `matched_metadata`: precision 1.0000, recall 0.8750, support 8.
- `metadata_review`: precision 0.9412, recall 1.0000, support 16.
- `identity_conflict`: precision 1.0000, recall 1.0000, support 12.
- `unresolved`: precision 1.0000, recall 1.0000, support 4.

The disagreement is **B039**, the unmodified PRISMA record. The generated BibTeX renders its group author without protective braces; the helper's conservative personal-name interpretation routes it to review. This exposes a corporate-author export/parsing boundary, not an actual error in the paper. The case and prediction are retained rather than hiding the discrepancy or adjusting the classifier to force a perfect score. Correctly braced organization names are covered separately by a unit test. The fixture should be reviewed before using it as a formal research gold label.

The helper does not assess semantic support: **0/6 semantic predictions were made**. The scorer penalizes missing predictions with zero recall and reports their IDs. Those zeros are not a measured LLM semantic score. Unit-test totals are engineering checks, not independent examples of successful paper auditing.

Engineering validation: **29 automated tests passed** on Python 3.12.14 during authoring, including a frozen 40-entry replay check. A separate two-request live smoke check resolved the Crossref DOI but the arXiv API timed out and was recorded as unresolved. The arXiv response parser/version checks passed mocked tests; live arXiv success is not established by that smoke check. The public-paper example used browser-readable primary sources independently of the helper.

## Run an honest baseline-versus-skill comparison

Export prompt packs without gold labels:

```bash
python benchmarks/evaluate.py --export-prompts benchmarks/runs/prompts
```

`baseline.txt` contains a short audit instruction. `skill.txt` adds the exact current skill instructions. Both receive identical inputs, frozen evidence, and output schema; neither receives `gold.json` or semantic rationales. The export manifest records input and skill hashes. No model is executed by this command.

1. Run the two conditions in fresh isolated sessions. Keep model/version, host, tool policy, reasoning/temperature settings, and context capacity fixed. The frozen-evidence protocol disables external tools. For a separate live-retrieval experiment, give both conditions identical retrieval/request budgets and record the source snapshots; do not pool its scores with frozen-evidence scores.
2. Use at least three independent repeats per condition when feasible; randomize condition order. Keep the evaluator/gold outside the model's accessible context, and do not grant an agent repository access that lets it read the gold files. Prompt export alone cannot enforce isolation.
3. Record run date, condition, exact model and host versions, settings, skill/input hashes, completion/failure, wall time, token counts when available, and tool-call counts. If the host cannot expose a number, mark it unavailable. Do not invent zero usage.
4. Save each output separately in the following format, with one prediction per case:

```json
{
  "run": {
    "condition": "baseline",
    "model": "record-the-actual-model-version",
    "host": "record-the-actual-host-version",
    "tools": "disabled",
    "repeat": 1
  },
  "predictions": [
    {"id": "B001", "status": "unresolved"},
    {"id": "S001", "status": "supported"}
  ]
}
```

The JSON above illustrates the shape only; it is not a result and its B001 status is not an expected answer. Include all 46 case IDs in a real run.

```bash
python benchmarks/evaluate.py --predictions benchmarks/runs/baseline-1.json --out benchmarks/runs/baseline-1-metrics.json
python benchmarks/evaluate.py --predictions benchmarks/runs/skill-1.json --out benchmarks/runs/skill-1-metrics.json
```

5. Report per-status precision/recall/F1, macro-F1, coverage, and abstention/failure rates separately for bibliography and semantics. Missing predictions remain false negatives; they are not dropped. Zero predicted positives use precision=0. Include per-repeat results and paired differences, not a selected best run. Do not interpret this tiny correlated development set as a population estimate.

Before a workshop/demo paper, recruit independent domain annotators, resolve annotation disagreements, add naturally occurring and harder negative cases, hold out sources (not just mutated entries), expand missing semantic classes and languages, and measure retrieval/time costs on a larger manuscript. The current set is appropriate for development and protocol debugging, not claims of superiority.
