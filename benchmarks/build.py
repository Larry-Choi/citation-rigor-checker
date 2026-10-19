"""Rebuild a small, transparent development set from frozen public metadata."""
import copy
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build():
    sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))['records']
    cases = []
    for i, source in enumerate(sources):
        clean = {'title': source['title'], 'author': source['author_bibtex'],
                 'year': str(source['years'][0]), 'journal': source['venue'], 'doi': source['doi']}
        for mutation, status in [('clean', 'matched_metadata'), ('wrong_doi', 'identity_conflict'),
                                 ('wrong_year', 'metadata_review'), ('wrong_venue', 'metadata_review')]:
            item = copy.deepcopy(clean)
            if mutation == 'wrong_doi':
                item['doi'] = sources[(i + 1) % len(sources)]['doi']
            elif mutation == 'wrong_year':
                item['year'] = str(max(source['years']) + 7)
            elif mutation == 'wrong_venue':
                item['journal'] = 'International Review of Synthetic Citation Experiments'
            cases.append((item, status, mutation, source['doi']))
        if i < 4:
            composite = copy.deepcopy(clean)
            composite['author'] = sources[(i + 1) % len(sources)]['author_bibtex']
            cases.append((composite, 'identity_conflict', 'composite_authors', source['doi']))
        else:
            fake = {'title': f'Unified evidence calibration for scholarly reasoning systems {i}',
                    'author': 'Example, Researcher', 'year': '2024',
                    'journal': 'Synthetic Evaluation Proceedings'}
            cases.append((fake, 'unresolved', 'invented_fixture', None))
    random.Random(20261019).shuffle(cases)
    bib, gold = [], []
    for i, (item, status, mutation, source) in enumerate(cases, 1):
        key = f'B{i:03}'
        fields = ',\n'.join(f'  {k} = {{{v}}}' for k, v in item.items())
        bib.append(f'@article{{{key},\n{fields}\n}}')
        gold.append({'id': key, 'task': 'bibliographic', 'status': status,
                     'mutation': mutation, 'source_doi': source})
    (ROOT / 'references.bib').write_text('\n\n'.join(bib) + '\n', encoding='utf-8')
    (ROOT / 'gold.json').write_text(json.dumps(gold, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(gold)} cases from {len(sources)} frozen records')


if __name__ == '__main__':
    build()
