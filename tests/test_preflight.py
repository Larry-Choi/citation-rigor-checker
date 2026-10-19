import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'benchmarks'))
from bibliography import BibError, Resolver, arxiv_value, audit, author_families, compare, doi_value, parse_bibtex
from evaluate import metrics


class BibtexTests(unittest.TestCase):
    def test_nested_quotes_concatenation_and_comments(self):
        text = '% ignored\n@comment{ignore {nested} content}\n@article(x, title={A {Nested} Title} # ": Part 2", year=2024, month=jan)'
        item = parse_bibtex(text)[0]
        self.assertEqual(item['title'], 'A {Nested} Title: Part 2')
        self.assertEqual(item['month'], 'January')

    def test_multiple_entries_and_escaped_quote(self):
        rows = parse_bibtex('@article{a,title="An \\"example\\""}\n@book{b,title={B}}')
        self.assertEqual([r['id'] for r in rows], ['a', 'b'])

    def test_duplicate_key_rejected(self):
        with self.assertRaises(BibError):
            parse_bibtex('@article{a,title={X}} @article{a,title={Y}}')

    def test_duplicate_field_rejected(self):
        with self.assertRaises(BibError):
            parse_bibtex('@article{a,title={X},title={Y}}')

    def test_macro_rejected(self):
        for text in ['@string{a={B}}', '@article{a,title=unknown}', '@preamble{"x"}']:
            with self.subTest(text=text), self.assertRaises(BibError):
                parse_bibtex(text)

    def test_inheritance_rejected(self):
        with self.assertRaises(BibError):
            parse_bibtex('@article{a,crossref={b}}')

    def test_truncated_input_rejected(self):
        for text in ['@article{a,title={X}', '@article{a,title="X}', 'unparsed junk']:
            with self.subTest(text=text), self.assertRaises(BibError):
                parse_bibtex(text)

    def test_organization_author_not_split(self):
        self.assertEqual(author_families('{Research and Development Group} and Choi, Larry'),
                         ['research and development group', 'choi'])


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.record = {'doi': '10.1234/test', 'title': 'A study of evidence', 'authors': ['Choi', 'Kim'],
                       'years': [2022, 2023], 'venue': 'Journal of Evidence', 'pages': '74089-74106'}
        self.entry = {'id': 'x', 'title': 'A Study of Evidence', 'author': 'Choi, Larry and Kim, A',
                      'year': '2022', 'journal': 'Journal of Evidence', 'pages': '74089--74106'}

    def test_clean_and_high_pagination(self):
        self.assertEqual(compare(self.entry, self.record)['status'], 'matched_metadata')

    def test_alternate_year_accepted(self):
        self.entry['year'] = '2023'
        self.assertEqual(compare(self.entry, self.record)['status'], 'matched_metadata')

    def test_wrong_year_and_venue_review(self):
        for field, value in [('year', '2030'), ('journal', 'An unrelated journal')]:
            with self.subTest(field=field):
                self.assertEqual(compare(dict(self.entry, **{field: value}), self.record)['status'], 'metadata_review')

    def test_wrong_identifier_identity(self):
        other = dict(self.record, title='Entirely unrelated work', authors=['Other'])
        self.assertEqual(compare(self.entry, other)['status'], 'identity_conflict')

    def test_composite_authors(self):
        self.entry['author'] = 'Other, Someone'
        self.assertEqual(compare(self.entry, self.record)['status'], 'identity_conflict')

    def test_no_record_is_unresolved(self):
        self.assertEqual(compare(self.entry, None)['status'], 'unresolved')

    def test_missing_metadata_cannot_match(self):
        self.entry.pop('author')
        self.assertEqual(compare(self.entry, self.record)['status'], 'metadata_review')

    def test_doi_normalization_and_invalid_input(self):
        self.assertEqual(doi_value('https://doi.org/10.1234/ABC'), '10.1234/abc')
        with self.assertRaises(ValueError):
            doi_value('not a doi')

    def test_arxiv_identifier_version(self):
        self.assertEqual(arxiv_value('https://arxiv.org/pdf/1706.03762v7.pdf'), '1706.03762v7')
        with self.assertRaises(ValueError):
            arxiv_value('../../private')


class ResolverTests(unittest.TestCase):
    def test_zero_budget_preserves_all_references(self):
        rows = [{'id': f'r{i}', 'doi': '10.1234/test'} for i in range(3)]
        with patch('urllib.request.urlopen') as fetch:
            result = audit(rows, Resolver(live=True, max_requests=0))
        fetch.assert_not_called()
        self.assertEqual(len(result['results']), 3)
        self.assertTrue(all(r['status'] == 'unresolved' for r in result['results']))

    def test_cache_reuse_and_offline_miss(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            self.assertEqual(Path(directory).resolve().parent, ROOT.resolve())
            resolver = Resolver(cache=directory, live=True)
            with patch('urllib.request.urlopen', return_value=io.BytesIO(b'{"message": {}}')) as fetch:
                self.assertEqual(resolver.fetch('https://api.crossref.org/test', 'crossref'), '{"message": {}}')
                self.assertEqual(resolver.fetch('https://api.crossref.org/test', 'crossref'), '{"message": {}}')
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(resolver.requests, 1)
            with self.assertRaises(RuntimeError):
                Resolver(cache=directory).fetch('https://api.crossref.org/missing', 'crossref')

    def test_http_failure_is_unresolved_not_fake(self):
        error = urllib.error.HTTPError('https://api.crossref.org/test', 404, 'Not found', {}, None)
        with patch('urllib.request.urlopen', side_effect=error):
            result = audit([{'id': 'x', 'doi': '10.1234/test'}], Resolver(live=True))
        self.assertEqual(result['results'][0]['status'], 'unresolved')

    def test_title_candidates_not_auto_verified(self):
        body = json.dumps({'message': {'items': [{'DOI': '10.1234/test', 'title': ['Exact title']}]}})
        with patch('urllib.request.urlopen', return_value=io.BytesIO(body.encode())):
            result = audit([{'id': 'x', 'title': 'Exact title'}], Resolver(live=True))
        self.assertEqual(result['results'][0]['status'], 'unresolved')
        self.assertEqual(len(result['results'][0]['candidates']), 1)

    def test_rate_limit_pauses_service(self):
        error = urllib.error.HTTPError('https://api.crossref.org/test', 429, 'Too many requests', {}, None)
        with patch('urllib.request.urlopen', side_effect=error) as fetch:
            result = audit([{'id': 'a', 'doi': '10.1234/test'}, {'id': 'b', 'doi': '10.1234/next'}], Resolver(live=True))
        self.assertEqual(fetch.call_count, 1)
        self.assertTrue(all(r['status'] == 'unresolved' for r in result['results']))

    def test_timeout_preserves_remaining_coverage(self):
        with patch('urllib.request.urlopen', side_effect=TimeoutError('timed out')):
            result = audit([{'id': 'a', 'doi': '10.1234/test'}], Resolver(live=True))
        self.assertEqual(result['coverage']['references_processed'], 1)
        self.assertEqual(result['results'][0]['status'], 'unresolved')
        self.assertEqual(result['request_log'][0]['result'], 'TimeoutError')

    def test_arxiv_wrong_version_is_unresolved(self):
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/1706.03762v6</id></entry></feed>'
        with patch('urllib.request.urlopen', return_value=io.BytesIO(atom)):
            result = audit([{'id': 'a', 'eprint': '1706.03762v7', 'archiveprefix': 'arXiv'}], Resolver(live=True))
        self.assertEqual(result['results'][0]['status'], 'unresolved')

    def test_arxiv_correct_version_is_recorded(self):
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/1706.03762v7</id><title>Attention Is All You Need</title><published>2017-06-12T00:00:00Z</published><author><name>Ashish Vaswani</name></author></entry></feed>'
        with patch('urllib.request.urlopen', return_value=io.BytesIO(atom)):
            result = audit([{'id': 'a', 'eprint': '1706.03762v7', 'archiveprefix': 'arXiv'}], Resolver(live=True))
        self.assertEqual(result['results'][0]['record']['arxiv'], '1706.03762v7')
        self.assertEqual(result['results'][0]['status'], 'metadata_review')


class SnapshotRegressionTests(unittest.TestCase):
    def test_frozen_corpus_coverage_repeatability_and_known_review(self):
        directory = ROOT / 'benchmarks'
        entries = parse_bibtex((directory / 'references.bib').read_text(encoding='utf-8'))
        snapshot = json.loads((directory / 'sources.json').read_text(encoding='utf-8'))
        gold = json.loads((directory / 'gold.json').read_text(encoding='utf-8'))
        with patch('urllib.request.urlopen') as fetch:
            first = audit(entries, Resolver(snapshot=snapshot))
            second = audit(entries, Resolver(snapshot=snapshot))
        fetch.assert_not_called()
        self.assertEqual(first, second)
        self.assertEqual({g['id'] for g in gold}, {r['id'] for r in first['results']})
        score = metrics(gold, [{'id': r['id'], 'status': r['status']} for r in first['results']])
        self.assertEqual(score['bibliographic']['total'], 40)
        self.assertEqual(score['bibliographic']['correct'], 39)


class EvaluationTests(unittest.TestCase):
    def test_missing_predictions_are_false_negatives(self):
        gold = [{'id': 'a', 'task': 'bibliographic', 'status': 'matched_metadata'},
                {'id': 'b', 'task': 'bibliographic', 'status': 'identity_conflict'}]
        score = metrics(gold, [{'id': 'a', 'status': 'matched_metadata'}])['bibliographic']
        self.assertEqual(score['accuracy'], 0.5)
        self.assertEqual(score['coverage'], 0.5)
        self.assertEqual(score['per_status']['identity_conflict']['fn'], 1)

    def test_unknown_and_duplicate_predictions_rejected(self):
        gold = [{'id': 'a', 'task': 'semantic', 'status': 'supported'}]
        for predictions in [[{'id': 'b', 'status': 'supported'}],
                            [{'id': 'a', 'status': 'supported'}] * 2,
                            [{'id': 'a', 'status': 'invented_label'}]]:
            with self.subTest(predictions=predictions), self.assertRaises(ValueError):
                metrics(gold, predictions)

    def test_false_positives_reduce_precision(self):
        gold = [{'id': 'a', 'task': 'semantic', 'status': 'supported'},
                {'id': 'b', 'task': 'semantic', 'status': 'contradicted'}]
        scores = metrics(gold, [{'id': 'a', 'status': 'supported'}, {'id': 'b', 'status': 'supported'}])
        self.assertEqual(scores['semantic']['per_status']['supported']['precision'], 0.5)


if __name__ == '__main__':
    unittest.main()
