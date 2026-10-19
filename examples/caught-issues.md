# Caught issues: a real bibliography typo and an injected overclaim

## 1. An observed typo in a public BibTeX file

The GPflow bibliography entry `hensman2015mcmc` contains **Variatinoally** in its title. The [official NeurIPS record](https://proceedings.neurips.cc/paper/2015/hash/6b180037abbebea991d8b1232f8a8ca9-Abstract.html) uses **Variationally**.

The original entry is preserved in [originals.bib](../benchmarks/real-world/originals.bib). Its upstream file, immutable Git blob ID, and hash are recorded in [provenance.json](../benchmarks/real-world/provenance.json). This is an error in that bibliography entry, not an accusation about the paper or authors.

Executed helper result: case **R009 → metadata_review**. Title spelling needs correction; the aligned author list does not justify an identity-conflict flag. See the [recorded comparison output](../benchmarks/results/real-world-preflight.json).

Suggested edit: replace the misspelled word with the spelling in the proceedings. Retain the original entry as audit input and apply the correction only to a separate revised reference list.

## 2. A deliberately injected overclaim

Test draft:

> Artemev et al. show better predictive performance at comparable training time than every Gaussian-process inference method, with strictly subcubic worst-case training complexity for all kernels.

This paragraph was constructed for this repository. It is not a quotation from a published manuscript.

The [cited abstract](https://proceedings.mlr.press/v139/artemev21a.html) reports a comparison with other conjugate-gradient approaches. The exact inspected passage is stored once as **P2** in [evidence.json](../benchmarks/real-world/evidence.json).

- **Comparison scope → partially_supported:** The stated experimental advantage has support; extending the comparator set to every GP method overstates that evidence.
- **Complexity guarantee → not_supported:** Comparable experimental training time does not establish a universal worst-case complexity bound.

A bounded revision:

> Artemev et al. report improved predictive performance over other conjugate-gradient approaches at comparable training time in their experiments.

The source passage does not justify retaining the general complexity claim. A theorem with its assumptions would be needed to support it.

These judgments concern the supplied passage. The executed model predictions for the corresponding semantic cases are available in [the comparison results](../benchmarks/comparison/run-manifest.json); the gold annotations are separate in [semantic_gold.json](../benchmarks/real-world/semantic_gold.json).

## 3. Normal-looking differences that should not become identity errors

The six [reported formatting regressions](../tests/fixtures/legitimate_variants.json) cover TeX accents, name particles, romanized/Korean names, unsegmented Korean names, omitted subtitles, and venue abbreviations. The old release produced five identity-conflict flags; the corrected helper produces none. Accents and particles can match, while transliteration and omitted fields remain reviewable. See the [before/after output](../benchmarks/results/normalization-regression.json).
