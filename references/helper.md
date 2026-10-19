# Optional metadata preflight

Requires Python 3.10+; uses only the standard library. Run from the repository/installed skill directory, or give an absolute path to the script. It reads the BibTeX input and writes a separate JSON report; it never rewrites references or executes TeX.

```bash
# Offline, with a fixed metadata snapshot:
python scripts/bibliography.py benchmarks/references.bib --snapshot benchmarks/sources.json --out preflight.json

# Explicit online mode, bounded requests and reusable response cache:
python scripts/bibliography.py references.bib --live --max-requests 40 --cache .citation-cache --out preflight.json
```

Online mode sends DOI/arXiv identifiers or no-ID titles to public services. Use only authorized inputs. Crossref DOI lookups use its [REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/); arXiv eprint lookups use its [Atom API](https://info.arxiv.org/help/api/user-manual.html). The script is sequential, caches successful responses with retrieval times, and paces requests. Rate limits and failures produce unresolved items rather than nonexistent-paper verdicts. It does not purchase access, follow arbitrary submitted URLs, retrieve full texts, or call OpenAlex/KCI/RISS/DBpia APIs.

## Supported BibTeX subset

Accepts ordinary entries with braced, quoted, or numeric values, nested braces, concatenation (`#`), month constants, `%` line comments, and braced `@comment` entries. Preserves original field strings in output. Rejects duplicate keys/fields, unresolved bare macros, `@string`, `@preamble`, `crossref`/`xdata` inheritance, and malformed input. Export expanded entries from a full BibTeX/BibLaTeX processor when using those features. This is a documented subset parser, not a replacement for a complete BibTeX implementation. TeX accents and complex personal-name syntax are not fully interpreted; inspect resulting review flags manually.

## Provisional statuses

- `matched_metadata`: Compared fields agree after conservative normalization. This excludes semantic verification, comprehensive version/authorship authentication, retraction checks, and publication-status adjudication.
- `metadata_review`: Missing fields or differences in title, author list, year, venue, volume, or pages need review. A journal abbreviation or alternate edition can be legitimate.
- `identity_conflict`: A large title difference or first-author conflict with the identifier's record warrants inspection. This is not an allegation of fabrication.
- `unresolved`: No usable record, discovery candidates only, invalid identifier, API failure, cache miss, or exhausted request budget.

Fuzzy title similarity is a deterministic triage heuristic with a fixed 0.85 conflict threshold; it is not a calibrated probability. This threshold has not been validated on a held-out multilingual corpus. No-ID live queries return up to three discovery candidates, never automatically approve the top hit. First/last-name parsing and translated titles are deliberately conservative and can produce false flags. The preflight never assesses an occurrence's semantic support.

Use fixed snapshots for exact replay. Live API contents can change; caches can become stale. Keep input/snapshot hashes, retrieval dates, and manual adjudications when reporting an audit. A request count is a network count, not a count of references verified. Parsing failure exits with code 2; a completed report can contain unresolved cases and exits with code 0, so inspect the statuses rather than using the exit code as an approval signal.
