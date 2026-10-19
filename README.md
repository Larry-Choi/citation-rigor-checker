# Citation Rigor Checker

**Check references and claims without rejecting normal bibliographic variants.**

An [Agent Skill](https://agentskills.io/specification) that audits references against scholarly records and maps manuscript claims to the passages that support—or fail to support—them.

**Caught in public BibTeX:** `Variatinoally` in a GPflow bibliography entry differs from `Variationally` in the proceedings. A separate draft test catches a comparison stretched from conjugate-gradient methods to every GP method. [See the inputs, evidence, and findings](examples/caught-issues.md).

**Fixed regression:** TeX accents, name particles, Korean/romanized names, omitted subtitles, and venue abbreviations produced **5 severe identity flags in 6 fixtures** before the fix and **0 after**. [Before/after results](benchmarks/results/normalization-regression.json).

Start with a quick **lite report**, request a **full reviewer audit**, or use the optional Python helper for cached metadata preflight. The instruction workflow also works without scripts.

[See caught issues](examples/caught-issues.md) · [Inspect the paired experiment](benchmarks/README.md) · [Open the skill](SKILL.md)

## What you get

- Separate answers to **“Does this reference match a real work?”** and **“Does it support this claim?”**
- Citation-by-citation mapping, including repeated and grouped citations.
- Checks for altered methods, misleading result attribution, and dataset/simulator confusion.
- A bounded work queue: full-list bibliographic preflight first, then central claims, borrowed methods, comparative results, and background.
- Evidence locators, precise revision suggestions, and a visible list of unchecked items.

High PMLR pagination, main-track poster labels, publication-year differences, and ambiguous PDF symbols receive source checks rather than automatic error flags.

## Install

Download **Code → Download ZIP**, extract it, and rename the extracted folder `citation-rigor-checker`. Copy that folder to a local skill location below. Keep `SKILL.md` directly inside it; include `scripts/` and `references/` for the optional helper and extended guidance, and retain `LICENSE`.

### Codex

- Personal: `~/.agents/skills/citation-rigor-checker/`
- Project: `<project>/.agents/skills/citation-rigor-checker/`
- Windows personal: `%USERPROFILE%\.agents\skills\citation-rigor-checker\`

Invoke with `$citation-rigor-checker` in Codex CLI/IDE, or select it from `/skills`. Restart if a newly installed skill does not appear. See [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).

### Claude Code

- Personal: `~/.claude/skills/citation-rigor-checker/`
- Project: `<project>/.claude/skills/citation-rigor-checker/`
- Windows personal: `%USERPROFILE%\.claude\skills\citation-rigor-checker\`

Invoke with `/citation-rigor-checker`. See [Claude Code's skill documentation](https://code.claude.com/docs/en/skills) for discovery, reload behavior, and cloud-session differences.

This repository contains a standalone skill for local installation. Other Agent Skills hosts use their own discovery paths and invocation conventions.

## Try it

Attach the files or make them accessible to your agent. These examples use Codex invocation; in Claude Code replace the first line with `/citation-rigor-checker`.

### Quick reference check

```text
$citation-rigor-checker
Use lite mode on the attached references.bib.
Check every entry's identity and metadata within a 40-request budget.
Show evidence links and what remains unchecked. No manuscript is supplied,
so mark claim support Not assessed. Report in Korean.
```

### Reviewer audit with an explicit budget

```text
$citation-rigor-checker
Use full mode on manuscript.pdf and references.bib.
Inventory all references and citation occurrences. Attempt bibliographic
preflight across the reference list, then prioritize contribution claims,
borrowed methods/equations, and comparative experimental claims.
Use at most 60 external requests and 10 distinct source full texts.
Save a coverage checkpoint and suggest precise revisions for major issues.
```

### Check an adaptation

```text
$citation-rigor-checker
Compare Section 3 of my draft with the attached source.
Check whether changes to the estimator and assumptions are disclosed
accurately. Distinguish the original contribution from our adaptation.
```

### Offline review

```text
$citation-rigor-checker
Review the supplied excerpts only. Network access is unavailable.
Check citation mapping and internal consistency. Explain which claims
need additional source passages; leave unavailable evidence unresolved.
```

Lite reports keep two axes—bibliography and claim support—with short findings and evidence locators. Full reports add the reference register, occurrence audit, source ledger, and reviewer notes. Both state actual coverage. See the [caught-issues example](examples/caught-issues.md) and [bounded public-paper audit](examples/attention-audit.md).

## Optional metadata helper

Python 3.10+, standard library only. Run from this directory:

```bash
# Replay frozen public metadata without network access:
python scripts/bibliography.py benchmarks/references.bib --snapshot benchmarks/sources.json --out preflight.json

# Explicit live lookups, with request budget and cached responses:
python scripts/bibliography.py references.bib --live --max-requests 40 --out preflight.json
```

The helper parses a documented BibTeX subset, resolves Crossref DOIs and arXiv eprints, compares fields, and returns no-ID title-search candidates. It decodes common TeX accents, preserves name particles, compares subtitles, and routes one-signal disagreements to review. Unsupported BibTeX macros/inheritance fail explicitly. See [helper documentation](references/helper.md).

Fixed inputs and a frozen metadata snapshot enable deterministic replay. Live search results and model judgments can vary. The instruction workflow needs no Python; actual searches and source reading use the host's tools and normal usage limits.

## Scope by discipline and language

The workflow can route to publisher records, subject indexes, and institutional repositories. [Source routing](references/sources.md) includes Korean-language KCI/RISS/DBpia checks, biomedical PubMed checks, and books/theses alongside ML/CS sources. The bundled API helper automates **Crossref and arXiv**.

## Validation status

The current pilot uses **19 bibliographic cases** from nine actual GPflow BibTeX entries and separately inspected primary records, plus **15 passage-level semantic cases** covering all six statuses. The previous copy-and-mutate 40-entry set is retained for engineering regression checks.

**Six model runs completed:** baseline and skill, three repeats each, `gpt-6.1-sol`, medium reasoning, identical frozen inputs, no tool use. Mean bibliographic macro-F1 was **0.781 baseline / 0.670 skill**; semantic macro-F1 was **1.000 for both**. This pilot found no overall skill advantage and retained a semantic ceiling effect. Full responses, per-status precision/recall, timing, token usage, and paired results are in the [experiment report](benchmarks/README.md).

```bash
python -m unittest discover -s tests -v
python benchmarks/check_real_world.py
python benchmarks/evaluate.py --export-prompts benchmarks/runs/prompts
```

## Limitations

This is a small development pilot with session-authored labels, not independently adjudicated research evidence. Semantic passages remain too easy to distinguish the two conditions. The model name is an alias rather than a pinned backend snapshot. The suite does not establish whole-manuscript retrieval, multilingual, or cross-host accuracy. Korean name regressions are synthetic formatting tests. The helper's metadata comparison is provisional; token overlap does not authenticate an author. Source access, OCR quality, and host tools affect semantic judgments, and a failed search does not prove fabrication. Human authors make final citation decisions. Keep confidential material out of public issues and unauthorized external services.

## Contribute

Useful contributions include independently adjudicated cases, harder negatives, additional languages, host compatibility reports, and paired model runs with complete settings and evidence. For bugs, provide a minimal public/synthetic input, actual versus expected behavior, and the host/model or Python version. See the [evaluation protocol](benchmarks/README.md) before claiming a performance improvement.

## License

[MIT](LICENSE). Preserve the copyright and permission notice when reusing this repository's material. Referenced papers, datasets, and manuscripts retain their own rights and terms.
