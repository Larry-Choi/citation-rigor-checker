# Citation Rigor Checker

**English** · [한국어](README.ko.md)

**Reuse a structured citation-checking workflow without rewriting a long prompt every time.**

An [Agent Skill](https://agentskills.io/specification) that packages instructions for reference checks, claim–source comparison, evidence recording, and coverage reporting. Invoke it with your files and requested scope; the saved instructions provide the detailed procedure.

The practical value is less repeated prompt writing and a shared procedure across audits. You can reuse the same expectations for evidence, uncertainty, citation mapping, and reporting instead of reconstructing them for each paper. Actual model adherence and output quality still vary.

**Accuracy superiority is not established.** The recorded development comparison tied with a baseline that received explicit task and label definitions. Neither reduced prompt-writing effort nor real-world workflow consistency has been measured in a user study. [Inspect the results and limitations](benchmarks/README.md).

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

### Start with a short request

```text
$citation-rigor-checker
Check manuscript.pdf and references.bib in lite mode. Report in English.
```

The skill supplies the detailed verification procedure. Add budget, scope, and reporting preferences when needed, as in the examples below.

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

The first pilot's lower skill score involved benign-formatting labels and an invalid unavailable-record control. [Case-by-case diagnosis in Korean](benchmarks/DIAGNOSIS.ko.md) separates actual entry defects from ambiguous labels and evidence-design errors; all original runs remain public.

**Nine new runs completed:** baseline, unchanged original skill, and revised skill, three repeats each, `gpt-6.1-sol`, medium reasoning, the same frozen packet and shared label definitions, with no tool use. Primary bibliographic macro-F1: **1.000 / 1.000 / 1.000**, respectively, on 18 unambiguous cases. Two ambiguous cases are scored separately as sensitivity checks. Semantic macro-F1: **1.000 / 1.000 / 1.000** on 15 cases. [Full results, per-status precision/recall, cost, protocol, and all responses](benchmarks/README.md).

These are development cases, and semantic ceiling effects persist. This comparison does not demonstrate a general skill advantage. The earlier 40-entry copy-and-mutate set remains an engineering regression suite.

The revised skill used a mean **23,802 input tokens**, versus **19,005** for the baseline, about **25% more**. Saved instructions reduce what you type; they still enter the model context and can increase usage and cost.

Engineering checks also retain the six formatting regressions (**5 severe identity flags before the helper fix, 0 after**) and a real public-BibTeX typo, `Variatinoally` versus `Variationally`. These illustrate specific checks, not general accuracy. [Regression output](benchmarks/results/normalization-regression.json) · [Inputs and findings](examples/caught-issues.md).

```bash
python -m unittest discover -s tests -v
python benchmarks/check_real_world.py
python benchmarks/evaluate.py --export-prompts benchmarks/runs/prompts
```

## Limitations

- **Fallible output:** The model can miss errors, flag legitimate citations, misread a source, or fail to follow the workflow. A clean report does not certify correctness, completeness, originality, or publication readiness. A failed search does not prove fabrication.
- **Evidence and access:** Paywalls, missing versions, incomplete metadata, OCR, and host tools limit coverage. The helper is a provisional metadata comparison; token overlap does not authenticate an author. The workflow does not replace reading the relevant primary sources or independent scholarly review.
- **Limited evaluation:** This small development pilot uses session-authored labels without independent adjudication. Semantic passages have a ceiling effect; the model is an alias rather than a pinned snapshot. Whole-manuscript retrieval, multilingual and cross-host accuracy, time savings, and workflow consistency are unvalidated. Korean name regressions are synthetic formatting tests.
- **Resource and privacy constraints:** Long inputs can exceed context or usage limits; loading the skill and using tools consume resources. Users must ensure they are authorized to share manuscripts and source material with their chosen services. Keep confidential material out of public issues and unauthorized external services.

## User responsibility and disclaimer

Treat every result as assistance for your own review. **You are responsible for checking primary sources, verifying suggested edits, and making all final citation, submission, and publication decisions.** Do not rely on the report alone to allege fabrication or misconduct.

The skill, helper, examples, and reports are provided **as is**, without warranties of accuracy, completeness, fitness for a particular purpose, or error-free operation. **To the fullest extent permitted by applicable law, the authors and copyright holders disclaim liability for claims, damages, or other liability arising from use of or reliance on this project**, including citation errors, omissions, and submission or publication outcomes. See the [MIT LICENSE](LICENSE) for the governing terms and the [official license text](https://opensource.org/license/mit). This notice does not exclude liability that applicable law does not allow to be excluded.

## Contribute

Useful contributions include independently adjudicated cases, harder negatives, additional languages, host compatibility reports, and paired model runs with complete settings and evidence. For bugs, provide a minimal public/synthetic input, actual versus expected behavior, and the host/model or Python version. See the [evaluation protocol](benchmarks/README.md) before claiming a performance improvement.

## License

[MIT](LICENSE). Preserve the copyright and permission notice when reusing this repository's material. Referenced papers, datasets, and manuscripts retain their own rights and terms.
