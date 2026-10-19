# A bounded audit of a public arXiv manuscript

Audit date: 2026-10-19. Mode: lite, targeted manual source inspection by the authoring assistant. This is an executed example, not a held-out evaluation or a finding that the manuscript contains fabricated citations.

## Scope and coverage

Manuscript: Vaswani et al., [Attention Is All You Need, arXiv:1706.03762v7](https://arxiv.org/html/1706.03762v7).

The manuscript lists 40 references. This example deliberately inspects **2 reference identities and 3 selected occurrence–source links**. All remaining references and occurrences are outside scope and unassessed; no whole-paper verdict is implied. Selection: one architecture claim, one positional-representation attribution, and one optimizer attribution. The full paper's occurrence count was not enumerated.

Result: the three scoped propositions have source support. The optimizer example illustrates an explicitly disclosed adaptation, not a source default. No critical correction is supported within this narrow scope.

## Reference identities

- **R009 / manuscript [9]:** Gehring, Auli, Grangier, Yarats, and Dauphin, *Convolutional Sequence to Sequence Learning*, cited as arXiv:1705.03122v2 (2017). Bibliography: **OK for inspected identity fields**. The [exact preprint PDF](https://arxiv.org/pdf/1705.03122v2) was inspected. The [PMLR record](https://proceedings.mlr.press/v70/gehring17a.html) additionally establishes the archival publication at ICML 2017, volume 70, pages 1243–1252; it does not replace the manuscript's cited preprint version.
- **R020 / manuscript [20]:** Kingma and Ba, *Adam: A Method for Stochastic Optimization*, cited as ICLR 2015. Bibliography: **OK for identity**. The [arXiv record](https://arxiv.org/abs/1412.6980) reports a 2014 initial submission and ICLR 2015 publication; the [v9 PDF](https://arxiv.org/pdf/1412.6980v9) identifies the conference paper on its cover. This audit did not independently inspect an ICLR proceedings record. A 2014 preprint date alone does not invalidate the 2015 conference citation.

## Occurrence checks

**O001 — Section 2, architecture attribution, [9] within a grouped citation**

- Scoped proposition, paraphrased: ConvS2S uses convolutional building blocks.
- Claim support: **OK**. R009, Section 3, PDF page 2, describes convolutional encoder and decoder states.
- Evidence: E002, direct text. The other members of the citation group are not evaluated here; this result validates only the link to [9].

**O002 — Section 3.5, learned positional representations, [9]**

- Scoped proposition, paraphrased: learned positional embeddings are a relevant prior design.
- Claim support: **OK, scoped**. R009, Section 3.1, PDF page 2, specifies absolute position embeddings added to word embeddings; Section 5.4 discusses their ablation.
- Evidence: E002, direct text. This supports the design attribution, not equivalence of the complete architectures or a claim that [9] independently establishes the manuscript's results.

**O003 — Section 5.3, optimizer choice, [20]**

- Scoped proposition, paraphrased: training uses Adam with stated custom settings.
- Claim support: **OK with an explicit adaptation**. The draft states beta_2=0.98 and epsilon=1e-9. Adam's Algorithm 1 lists beta_2=0.999 and epsilon=1e-8 as suggested defaults.
- Evidence: E001, Section 5.3; E003, Algorithm 1, PDF page 2. Different settings do not invalidate attribution when the draft supplies its actual settings. This example does not rederive the update equations or reproduce training.

## Reviewer pass

Potential question: does citing Adam imply using its default hyperparameters?

Evidence-backed response: the manuscript supplies its settings, so the scoped attribution does not claim default equivalence. If another draft says “unchanged original defaults,” it would need correction. No revision to this inspected sentence is warranted on this basis alone.

## Evidence and checkpoint

- **E001:** [Manuscript v7 HTML](https://arxiv.org/html/1706.03762v7), Sections 2, 3.5, 5.3, and References; directly inspected.
- **E002:** [ConvS2S v2](https://arxiv.org/pdf/1705.03122v2), Sections 3/3.1/5.4; directly inspected text. [PMLR metadata](https://proceedings.mlr.press/v70/gehring17a.html) used separately for archival identity.
- **E003:** [Adam v9](https://arxiv.org/pdf/1412.6980v9), cover and Algorithm 1; directly inspected text. [arXiv metadata](https://arxiv.org/abs/1412.6980) used for date/version context.

All links were inspected on the audit date. These notes use paraphrases; copyrighted full texts are linked, not bundled. There was no equation-level OCR disagreement in the scoped checks; rendered-page comparison was not performed. Confidence is limited to these inspected propositions and fields. The historical version of Adam used by the manuscript's authors is not pinned in its reference entry; v9 is the explicitly identified comparison version here.

Checkpoint: R009/R020 inspected; O001–O003 complete; all other references/occurrences unassessed. To extend this example, enumerate the complete occurrence map before claiming full coverage, then apply the skill's budget and priority queue. This assistant-authored report has not received independent human adjudication.
