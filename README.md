# Citation Rigor Checker

**Check whether a reference exists—and whether it supports what your manuscript says.**

An instruction-only [Agent Skill](https://agentskills.io/specification) for evidence-based academic citation audits. It separates bibliographic verification from claim-level review and makes missing evidence explicit.

The workflow lives in a single [`SKILL.md`](SKILL.md). No custom scripts, packages, or project-specific API keys are required. Your agent supplies the model, search tools, and document access; its normal usage costs and access limits still apply.

## What it checks

- **Bibliographic identity:** Titles, authors, identifiers, venues, tracks, dates, versions, and page ranges.
- **Claim support:** Whether each citation occurrence supports the manuscript's specific proposition—not just a related topic.
- **Method fidelity:** Equations, algorithms, assumptions, domain adaptations, and attribution.
- **Experimental context:** Datasets versus simulators, static replay versus interaction, metrics, and evaluation protocols.
- **Citation mapping:** Repeated citations, grouped references, numbering, missing entries, and ambiguous keys.
- **Evidence limits:** Primary-source evidence, confidence, access gaps, and unresolved questions.

It also handles high PMLR page numbers, main-track poster labels versus workshop publication status, event/publication year differences, and PDF extraction artifacts without treating these as automatic errors.

## Install for local use

Download this repository using GitHub's **Code → Download ZIP**, then extract it. Keep the skill folder named `citation-rigor-checker`.

For Codex, copy the folder into one of these locations:

- **Personal:** `~/.agents/skills/citation-rigor-checker/`
- **Project:** `<your-project>/.agents/skills/citation-rigor-checker/`
- **Windows personal:** `%USERPROFILE%\.agents\skills\citation-rigor-checker\`

The resulting folder must contain `SKILL.md` directly. Retain `LICENSE` when copying or redistributing the skill; `README.md` is useful documentation but is not needed for execution. Avoid accidental extra nesting such as `citation-rigor-checker/citation-rigor-checker/SKILL.md`.

In Codex CLI or the IDE extension, type `$citation-rigor-checker` or use `/skills` to select it. If it does not appear, restart Codex. See the [official skill documentation](https://learn.chatgpt.com/docs/build-skills) for current discovery paths and host-specific invocation. GitHub hosting alone does not install a skill. This repository is a standalone skill, not a plugin-directory package.

For another Agent Skills-compatible host, follow that host's installation instructions. Format compatibility does not guarantee identical tools or audit quality. You can also provide `SKILL.md` as workflow instructions in an assistant conversation, but that does not constitute a native skill installation.

## Usage examples

Attach or provide access to the files mentioned in each example. Example filenames are illustrative. Reports follow the user's requested language.

### Verify a reference list

```text
$citation-rigor-checker
Audit the attached references.bib for existence and bibliographic accuracy.
Use authoritative records and provide evidence links for your findings.
Keep unresolved references separate from identity mismatches.
Do not assess semantic alignment because no manuscript is provided.
```

### Audit a manuscript

```text
$citation-rigor-checker
Audit the attached manuscript.pdf and references.bib.
Map each citation occurrence to its reference and check the specific claim.
Separate bibliographic status from semantic support. Prioritize central
claims and report any unassessed material explicitly.
For major issues, suggest precise revisions with source locators.
```

### Review a methodological adaptation

```text
$citation-rigor-checker
Compare Section 3 of my draft with the attached source paper.
Check whether weighting acquisition functions is accurately described as
the source's posterior-ensemble method. Compare both equations and their
assumptions. Explain the adaptation boundary and suggest accurate wording.
```

### Work with limited access

```text
$citation-rigor-checker
Review only the supplied excerpts. Network access is unavailable.
Check citation mapping and internal consistency. Clearly distinguish what
the excerpts establish from what needs publisher records or full text.
Report in Korean. Do not infer fabrication from missing resources.
```

## What a report contains

1. Scope, input version, coverage counts, and a qualified verdict.
2. A reference register with identity, publication type, and metadata findings.
3. An occurrence audit linking manuscript claims to source evidence.
4. Prioritized reviewer questions and evidence-backed wording revisions.
5. An evidence ledger, access/search limitations, and next checks.

**Illustrative finding, not a real paper audit:**

> O002 · Section 4 · R001  
> Bibliographic status: Verified.  
> Semantic status: Not supported by inspected evidence.  
> The draft claims interactive simulator use, while the inspected source
> passage describes static dataset evaluation. Evidence: E004, Methods,
> paragraph 2. State the actual evaluation setup or supply evidence for
> interactive use.

Bibliographic results are counted per reference; semantic results are counted per proposition–source link. These totals need not match.

## Limits and responsible use

This is a review workflow, not a scholarly database, plagiarism detector, or guarantee of correctness. It does not establish who created a citation error or whether AI was involved. Search failure is not proof of fabrication. Verifying a DOI does not establish semantic support, and inspecting an abstract does not validate detailed equations.

Results depend on the host model, available tools, source access, and document quality. No full-text access means no claim of full-text verification. OCR ambiguities remain unresolved until checked against the rendered page or original source. Human authors remain responsible for final citation decisions.

Do not include confidential manuscripts, reviewer material, credentials, or personal data in public issues. Check your host's data handling before supplying unpublished work. A citation-audit request does not authorize publishing the manuscript or contacting its authors.

## Validation and contributions

`SKILL.md` includes eight synthetic behavioral acceptance examples covering publication edge cases, incorrect identifiers, repeated/grouped citations, method adaptations, OCR ambiguity, access limits, and suspected conflation.

These are expected-behavior fixtures, not an automated test suite or a measured accuracy benchmark. Packaging and required metadata have been checked; cross-host behavior and end-to-end citation accuracy have not been benchmarked.

Issues and pull requests are welcome. For a reproducible issue, include the host/model, a minimal public or synthetic input, actual versus expected behavior, and relevant source links. Do not submit private manuscripts or label real authors dishonest on the basis of an unresolved search.

## Repository layout

```text
citation-rigor-checker/
├── SKILL.md
├── README.md
└── LICENSE
```

## License

[MIT](LICENSE). You may use, modify, and redistribute this workflow, including commercially, subject to the license conditions. Preserve the copyright and permission notice. The license covers this repository's material; it does not grant rights to third-party papers, datasets, or manuscript content used during an audit.
