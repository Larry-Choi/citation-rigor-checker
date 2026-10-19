# Source routing and declared coverage

The workflow is discipline-agnostic; its original examples emphasize ML/CS. Instructions to consult a source do not imply an API integration or validated coverage of that discipline. The bundled helper automates Crossref and arXiv metadata only. Full-text semantic judgments require appropriate language and subject expertise.

## Choose the source for the document

- **DOI-bearing articles:** Start with the resolving publisher record and the relevant registration agency. [Crossref](https://search.crossref.org/) supplies member-deposited metadata, which can be incomplete or wrong; corroborate conflicts against the version being cited. A Crossref 404 does not exclude a DOI registered with another agency.
- **ML/CS:** PMLR and official publisher/conference proceedings establish archival metadata; arXiv establishes a deposited preprint/version. OpenReview can describe several review and publication stages: identify venue, track, and decision rather than treating every submission as an accepted paper.
- **Biomedicine:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/) provides a subject-specific discovery route; inspect the publisher/source article and relevant correction notices. A database match is not evidence that a manuscript's clinical or causal claim is valid.
- **Korean-language research:** Search the original Korean title and author names in [KCI](https://www.kci.go.kr/), [RISS](https://www.riss.kr/), or [DBpia](https://www.dbpia.co.kr/), then inspect the journal, society, institutional repository, or actual distributed article. Distinguish journal articles, theses, and conference material. Regional records may establish details absent from Crossref. These are manual routes, not bundled API connectors; access restrictions remain applicable.
- **Books, humanities, and social sciences:** Use the publisher's edition/ISBN and institutional or national-library catalog, then the relevant chapter/page in that edition. For translated editions, compare original and translated titles without silently merging editions or page numbers.
- **Theses and reports:** Use the issuing university/institution and deposited version. A repository record establishes a deposit, not journal peer review.

## Names, dates, and access

Preserve Korean and other original-language metadata alongside romanized forms. Do not diagnose a different work solely from transliteration, translated titles, family-name ordering, initials, or lost diacritics. Multiple publication dates and accepted/preprint/final versions require a version-specific comparison. If the helper flags these, adjudicate them rather than publishing its flag as a confirmed error.

Do not imply that any one database is exhaustive. Indexing absence, a paywall, failed OCR, or an unsupported script cannot establish fabrication. Record the actual coverage and route remaining checks to a competent human when source language or subject matter cannot be evaluated reliably.
