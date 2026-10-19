# Citation Rigor Checker

**A real paper can still be the wrong citation. Check both existence and claim support.**

An [Agent Skill](https://agentskills.io/specification) that audits references against scholarly records and maps manuscript claims to the passages that support—or fail to support—them.

Start with a quick **lite report**, request a **full reviewer audit**, or use the optional Python helper for cached metadata preflight. The instruction workflow also works without scripts.

[Read an executed public-paper audit](examples/attention-audit.md) · [Inspect the benchmark and results](benchmarks/README.md) · [Open the skill](SKILL.md)

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

This is a standalone skill for local installation, not a plugin-directory package. Other Agent Skills hosts may load it using their own installation and invocation conventions. Compatibility is a packaging claim; end-to-end behavior has not been validated across hosts. GitHub hosting alone does not install the skill.

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

Lite reports keep two axes—bibliography and claim support—with short findings and evidence locators. Full reports add the reference register, occurrence audit, source ledger, and reviewer notes. Both state actual coverage. See the [worked example](examples/attention-audit.md).

## Optional metadata helper

Python 3.10+, standard library only. Run from this directory:

```bash
# Replay frozen public metadata without network access:
python scripts/bibliography.py benchmarks/references.bib --snapshot benchmarks/sources.json --out preflight.json

# Explicit live lookups, with request budget and cached responses:
python scripts/bibliography.py references.bib --live --max-requests 40 --out preflight.json
```

The helper parses a documented BibTeX subset, resolves Crossref DOIs and arXiv eprints, compares fields, and returns no-ID title-search candidates. Unsupported BibTeX macros/inheritance fail explicitly. It does not verify semantic support; a metadata match is provisional. See [helper behavior and limitations](references/helper.md).

Fixed inputs and a frozen metadata snapshot enable deterministic replay. Live search results and model judgments can vary. The instruction workflow needs no Python; actual searches and source reading use the host's tools and normal usage limits.

## Scope by discipline and language

The workflow can route to publisher records, subject indexes, and institutional repositories. [Source routing](references/sources.md) includes Korean-language KCI/RISS/DBpia checks, biomedical PubMed checks, and books/theses alongside ML/CS sources. These are guidance routes; the bundled API helper automates **Crossref and arXiv only**. Multilingual and domain-specific accuracy has not been benchmarked.

## Validation status

The repository includes executable engineering tests, 40 synthetic metadata cases built from eight frozen public records, six semantic evaluation cases, a per-status precision/recall scorer, and paired baseline/skill prompt export.

The measured metadata preflight run agreed with intended routing labels on **39/40** cases. The disagreement and per-status metrics are published in the [benchmark report](benchmarks/README.md). This small development-set result is not an estimate of real-world audit accuracy. **Baseline-versus-skill model comparisons have not been run**, and no semantic-model score or accuracy advantage is claimed.

```bash
python -m unittest discover -s tests -v
python benchmarks/evaluate.py --export-prompts benchmarks/runs/prompts
```

The [public-paper example](examples/attention-audit.md) inspects two references and three selected citation links in *Attention Is All You Need*. It demonstrates execution and scope reporting; it is not a full-paper audit or independent validation.

## Evidence and privacy

An unavailable record or failed search does not prove fabrication. Detailed semantic checks need the relevant source text; OCR ambiguity needs visual/source confirmation. Human authors make the final citation decisions. Keep confidential manuscripts, reviewer material, and personal data out of public issues and unauthorized external services.

## Contribute

Useful contributions include independently adjudicated cases, harder negatives, additional languages, host compatibility reports, and paired model runs with complete settings and evidence. For bugs, provide a minimal public/synthetic input, actual versus expected behavior, and the host/model or Python version. See the [evaluation protocol](benchmarks/README.md) before claiming a performance improvement.

## License

[MIT](LICENSE). Preserve the copyright and permission notice when reusing this repository's material. Referenced papers, datasets, and manuscripts retain their own rights and terms.
