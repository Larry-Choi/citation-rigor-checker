#!/usr/bin/env python3
"""Conservative metadata preflight, not a final citation or semantic verdict.

Python 3.10+, standard library only. Snapshot mode makes zero network requests.
BibTeX subset: braced/quoted/numeric values, nested braces, concatenation,
comments and month names. Reject macros, preambles and crossref inheritance
instead of silently dropping or guessing fields. No TeX is executed.
"""
import argparse
import difflib
import hashlib
import json
import platform
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


class BibError(ValueError):
    pass


def parse_bibtex(text):
    text = text.lstrip('\ufeff')
    entries, keys, pos = [], set(), 0
    months = dict(zip('jan feb mar apr may jun jul aug sep oct nov dec'.split(),
                      'January February March April May June July August September October November December'.split()))

    def skip():
        nonlocal pos
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
            elif text[pos] == '%':
                end = text.find('\n', pos)
                pos = len(text) if end < 0 else end + 1
            else:
                break

    def delimited(opener):
        nonlocal pos
        closer = '}' if opener == '{' else '"'
        pos += 1
        start, depth = pos, 0
        while pos < len(text):
            char = text[pos]
            if char == '\\':
                pos += 2
                continue
            if char == '{':
                depth += 1
            elif char == '}' and depth:
                depth -= 1
            elif char == closer and depth == 0:
                result = text[start:pos]
                pos += 1
                return result
            pos += 1
        raise BibError('Unterminated value or comment')

    def value():
        nonlocal pos
        pieces = []
        while True:
            skip()
            if pos >= len(text):
                raise BibError('Missing field value')
            if text[pos] in '{"':
                pieces.append(delimited(text[pos]))
            else:
                found = re.match(r'[\w.+:/-]+', text[pos:])
                if not found:
                    raise BibError(f'Invalid value near offset {pos}')
                token = found[0]
                pos += len(token)
                if token.isdecimal():
                    pieces.append(token)
                elif token.lower() in months:
                    pieces.append(months[token.lower()])
                else:
                    raise BibError(f'Unsupported bare macro {token!r}; expand it before auditing')
            skip()
            if pos < len(text) and text[pos] == '#':
                pos += 1
            else:
                return ''.join(pieces)

    while True:
        skip()
        if pos >= len(text):
            return entries
        found = re.match(r'@([A-Za-z]+)\s*([({])', text[pos:])
        if not found:
            raise BibError(f'Expected a BibTeX entry near offset {pos}')
        kind, opener = found[1].lower(), found[2]
        pos += found.end()
        closer = ')' if opener == '(' else '}'
        if kind == 'comment':
            if opener == '{':
                pos -= 1
                delimited('{')
            else:
                raise BibError('Use braced @comment entries')
            continue
        if kind in {'string', 'preamble'}:
            raise BibError(f'@{kind} is unsupported; export expanded BibTeX first')
        skip()
        found = re.match(r'([^\s,{}()]+)\s*,', text[pos:])
        if not found:
            raise BibError('Missing entry key or comma')
        key = found[1]
        if key in keys:
            raise BibError(f'Duplicate BibTeX key: {key}')
        keys.add(key)
        pos += found.end()
        item = {'id': key, 'entry_type': kind}
        while True:
            skip()
            if pos < len(text) and text[pos] == closer:
                pos += 1
                break
            found = re.match(r'([\w-]+)\s*=\s*', text[pos:])
            if not found:
                raise BibError(f'Invalid field in {key!r} near offset {pos}')
            field = found[1].lower()
            if field in item or field in {'crossref', 'xdata'}:
                raise BibError(f'Duplicate/reserved/inherited field {field!r} in {key!r}')
            pos += found.end()
            item[field] = value()
            skip()
            if pos < len(text) and text[pos] == ',':
                pos += 1
            elif pos >= len(text) or text[pos] != closer:
                raise BibError(f'Missing separator in {key!r}')
        entries.append(item)


def decode_latex(text):
    """Decode common bibliographic accents; never execute TeX."""
    letters = {'ss': 'ß', 'ae': 'æ', 'AE': 'Æ', 'oe': 'œ', 'OE': 'Œ',
               'aa': 'å', 'AA': 'Å', 'o': 'ø', 'O': 'Ø', 'l': 'ł', 'L': 'Ł',
               'i': 'ı', 'j': 'ȷ'}
    marks = dict(zip(['"', "'", '`', '^', '~', '=', '.', 'u', 'v', 'H', 'c', 'k', 'b', 'd', 'r'],
                     ['\u0308', '\u0301', '\u0300', '\u0302', '\u0303', '\u0304', '\u0307', '\u0306', '\u030c', '\u030b', '\u0327', '\u0328', '\u0331', '\u0323', '\u030a']))
    text = re.sub(r'\\(?:textit|textbf|emph|mathrm|mathbf)\s*', '', text)
    text = re.sub(r'\\(ss|ae|AE|oe|OE|aa|AA|o|O|l|L|i|j)(?![A-Za-z])', lambda m: letters[m[1]], text)
    accent = re.compile(r'''\\(["'`^~=.uvHckbdr])\s*(?:\{([^{}])\}|([A-Za-zıȷ]))''')
    def apply_accent(match):
        char = (match[2] or match[3]).replace('ı', 'i').replace('ȷ', 'j')
        return unicodedata.normalize('NFC', char + marks[match[1]])
    text = accent.sub(apply_accent, text)
    return text.replace('{', '').replace('}', '')


def normalize(text):
    text = unicodedata.normalize('NFKD', decode_latex(text)).casefold()
    # Recompose non-Latin scripts after removing accent marks.
    text = unicodedata.normalize('NFC', ''.join(c for c in text if not unicodedata.combining(c)))
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in text).split())


def doi_value(value):
    value = urllib.parse.unquote(value.strip())
    value = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value, flags=re.I)
    if not re.fullmatch(r'10\.\d{4,9}/\S+', value):
        raise ValueError('Malformed DOI; supply the identifier without citation punctuation')
    return value.lower()


def arxiv_value(value):
    value = re.sub(r'^(?:https?://arxiv\.org/(?:abs|pdf)/|arxiv:\s*)', '', value.strip(), flags=re.I)
    value = re.sub(r'\.pdf$', '', value)
    if not re.fullmatch(r'(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?', value):
        raise ValueError('Malformed arXiv identifier')
    return value


def author_families(value):
    # Split only top-level "and", retaining a braced organization as one author.
    parts, depth, start = [], 0, 0
    for match in re.finditer(r'\{|\}|\s+and\s+', value):
        token = match[0]
        if token == '{':
            depth += 1
        elif token == '}':
            depth -= 1
        elif depth == 0:
            parts.append(value[start:match.start()].strip())
            start = match.end()
    parts.append(value[start:].strip())
    # Without a comma, retain the name: guessing the last token loses particles
    # and invents family-name boundaries in Korean and other naming systems.
    return [normalize(p.split(',')[0] if ',' in p else p)
            for p in parts if p]


PARTICLES = {'van', 'von', 'der', 'den', 'de', 'del', 'di', 'da', 'du', 'la', 'le', 'ten', 'ter', 'bin', 'al'}


def name_relation(left, right):
    if left == right:
        return 'compatible'
    left_tokens = {t for t in left.split() if t not in PARTICLES and len(t) > 1}
    right_tokens = {t for t in right.split() if t not in PARTICLES and len(t) > 1}
    if left_tokens & right_tokens:
        return 'compatible'
    # A transliteration or an unsegmented name is not negative identity evidence.
    if not left_tokens or not right_tokens or any(ord(c) > 127 for c in left + right):
        return 'uncertain'
    return 'different'


def title_relation(submitted, record):
    title = normalize(submitted)
    main = record.get('title', '')
    subtitle = record.get('subtitle') or []
    subtitle = [subtitle] if isinstance(subtitle, str) else subtitle
    variants = {normalize(main), normalize(main + ': ' + ': '.join(subtitle))}
    if not title or not normalize(main):
        return 'missing', None
    if title in variants:
        return 'exact', 1.0
    ratio = max(difflib.SequenceMatcher(None, title, v).ratio() for v in variants)
    for variant in variants:
        shortest = min((title, variant), key=len)
        if (len(shortest.split()) >= 2 or len(shortest) >= 8) and (
                title.startswith(variant + ' ') or variant.startswith(title + ' ')):
            return 'abbreviated', ratio
    return ('similar' if ratio >= 0.85 else 'different'), ratio


def compare(entry, record):
    if not record:
        return {'status': 'unresolved', 'reasons': ['No usable record; not evidence of nonexistence']}
    reasons, missing = [], []
    title_state, ratio = title_relation(entry.get('title', ''), record)
    authors = author_families(entry.get('author', ''))
    source_authors = [normalize(a) for a in record.get('authors', [])]
    first_author = name_relation(authors[0], source_authors[0]) if authors and source_authors else 'uncertain'
    if title_state == 'different' and first_author == 'different':
        return {'status': 'identity_conflict', 'title_similarity': ratio,
                'reasons': ['Both title and first-author signals conflict with the resolved record; inspect versions/names manually']}
    if ratio is None:
        missing.append('title')
    elif title_state != 'exact':
        reasons.append('Title is shortened, differs, or may be translated; review the complete title/subtitle')
    if not authors or not source_authors:
        missing.append('authors')
    elif len(authors) != len(source_authors) or any(name_relation(a, b) != 'compatible' for a, b in zip(authors, source_authors)):
        reasons.append('Author list differs, is abbreviated, or has unresolved naming/transliteration differences')
    years = {str(y) for y in record.get('years', [])}
    if not entry.get('year') or not years:
        missing.append('year')
    elif entry['year'] not in years:
        reasons.append('Year differs from available publication dates; inspect version/event year')
    venue = entry.get('journal') or entry.get('booktitle', '')
    if not venue or not record.get('venue'):
        missing.append('venue')
    elif normalize(venue) != normalize(record['venue']):
        reasons.append('Venue differs; abbreviations and alternate versions require review')
    for field, source_field in [('volume', 'volume'), ('pages', 'pages')]:
        if entry.get(field) and record.get(source_field):
            if normalize(entry[field].replace('--', '-')) != normalize(str(record[source_field])):
                reasons.append(f'{field} differs')
    if missing:
        reasons.append('Missing comparison fields: ' + ', '.join(missing))
    return {'status': 'metadata_review' if reasons else 'matched_metadata',
            'title_similarity': ratio, 'reasons': reasons}


class Resolver:
    def __init__(self, snapshot=None, cache=None, live=False, max_requests=50):
        self.records = snapshot.get('records', []) if snapshot is not None else None
        self.cache = Path(cache) if cache else None
        self.live, self.max_requests, self.requests = live, max_requests, 0
        self.log, self.last_request, self.blocked_services = [], 0.0, set()

    def fetch(self, url, service):
        cache_file = self.cache / (hashlib.sha256(url.encode()).hexdigest() + '.json') if self.cache else None
        if cache_file and cache_file.exists():
            payload = json.loads(cache_file.read_text(encoding='utf-8'))
            self.log.append({'url': url, 'result': 'cached', 'retrieved_at': payload['retrieved_at']})
            return payload['body']
        if not self.live:
            raise RuntimeError('Offline cache miss')
        if service in self.blocked_services:
            raise RuntimeError(f'{service} is paused after a rate-limit/service failure; resume later')
        if self.requests >= self.max_requests:
            raise RuntimeError('Network request budget exhausted')
        # Sequential, paced requests; no unbounded retries. A retry consumes budget.
        delay = (3.1 if service == 'arxiv' else 1.1) - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)
        self.requests += 1
        self.last_request = time.monotonic()
        request = urllib.request.Request(url, headers={'User-Agent': 'citation-rigor-checker/0.2 (metadata preflight)'})
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                body = response.read(8_000_001)
                if len(body) > 8_000_000:
                    raise RuntimeError('Response exceeds 8 MB limit')
                body = body.decode('utf-8')
        except urllib.error.HTTPError as error:
            self.log.append({'url': url, 'result': f'HTTP {error.code}'})
            if error.code in (429, 503):
                self.blocked_services.add(service)
                raise RuntimeError(f'Service rate limited/unavailable (HTTP {error.code}); stop and resume later') from error
            raise
        except OSError as error:
            self.log.append({'url': url, 'result': type(error).__name__, 'detail': str(error)})
            raise
        payload = {'retrieved_at': datetime.now(timezone.utc).isoformat(), 'body': body}
        if cache_file:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(payload), encoding='utf-8', newline='\n')
        self.log.append({'url': url, 'result': 'fetched', 'retrieved_at': payload['retrieved_at']})
        return body

    def resolve(self, entry):
        doi = doi_value(entry['doi']) if entry.get('doi') else None
        arxiv = arxiv_value(entry['eprint']) if entry.get('eprint') and (entry.get('archiveprefix', '').lower() == 'arxiv' or not entry.get('archiveprefix')) else None
        if self.records is not None:
            if doi:
                matches = [r for r in self.records if r.get('doi') == doi]
            elif arxiv:
                matches = [r for r in self.records if r.get('arxiv') == arxiv]
            else:
                matches = [r for r in self.records if normalize(r['title']) == normalize(entry.get('title', ''))]
            return (matches[0] if len(matches) == 1 else None), []
        if doi:
            url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='')
            msg = json.loads(self.fetch(url, 'crossref'))['message']
            if msg.get('DOI', '').lower() != doi:
                raise RuntimeError('Crossref returned an unexpected DOI')
            years = sorted({msg[k]['date-parts'][0][0] for k in ['published', 'published-print', 'published-online', 'issued'] if k in msg and msg[k].get('date-parts')})
            return {'doi': msg['DOI'].lower(), 'title': msg.get('title', [''])[0],
                    'subtitle': msg.get('subtitle', []),
                    'authors': [a.get('family') or a.get('name', '') for a in msg.get('author', [])],
                    'years': years, 'venue': msg.get('container-title', [''])[0],
                    'volume': msg.get('volume'), 'pages': msg.get('page'), 'source_url': url}, []
        if arxiv:
            url = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode({'id_list': arxiv})
            root = ET.fromstring(self.fetch(url, 'arxiv'))
            ns = {'a': 'http://www.w3.org/2005/Atom'}
            item = root.find('a:entry', ns)
            if item is None or '/abs/' not in item.findtext('a:id', '', ns):
                return None, []
            actual_id = item.findtext('a:id', '', ns).rsplit('/abs/', 1)[-1]
            if re.sub(r'v\d+$', '', actual_id) != re.sub(r'v\d+$', '', arxiv):
                raise RuntimeError('arXiv returned an unexpected identity')
            if re.search(r'v\d+$', arxiv) and actual_id != arxiv:
                raise RuntimeError('arXiv returned a different version than requested')
            return {'arxiv': actual_id, 'title': ' '.join(item.findtext('a:title', '', ns).split()),
                    'authors': [a.findtext('a:name', '', ns) for a in item.findall('a:author', ns)],
                    'years': [int(item.findtext('a:published', '', ns)[:4])],
                    'venue': 'arXiv', 'source_url': url}, []
        if not entry.get('title'):
            return None, []
        url = 'https://api.crossref.org/works?' + urllib.parse.urlencode({'query.title': entry['title'], 'rows': 3})
        items = json.loads(self.fetch(url, 'crossref'))['message']['items']
        # Discovery candidates are never silently promoted to a verified identity.
        return None, [{'doi': i.get('DOI'), 'title': i.get('title', [''])[0],
                       'title_similarity': difflib.SequenceMatcher(None, normalize(entry['title']), normalize(i.get('title', [''])[0])).ratio()}
                      for i in items]


def audit(entries, resolver):
    results = []
    for entry in entries:
        try:
            record, candidates = resolver.resolve(entry)
            result = compare(entry, record)
            result.update({'record': record, 'candidates': candidates})
        except (ValueError, RuntimeError, OSError, KeyError, ET.ParseError, IndexError) as error:
            result = {'status': 'unresolved', 'reasons': [f'{type(error).__name__}: {error}']}
        result.update({'id': entry['id'], 'submitted': entry, 'semantic_status': 'not_assessed'})
        results.append(result)
    return {'schema_version': 1, 'scope': 'bibliographic_preflight_only', 'results': results,
            'coverage': {'references_total': len(entries), 'references_processed': len(results),
                         'network_requests': resolver.requests, 'network_budget': resolver.max_requests},
            'request_log': resolver.log,
            'warning': 'matched_metadata is a provisional field comparison, not final verification or semantic support. Snapshot misses and API failures do not prove nonexistence.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bibtex', type=Path)
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--cache', type=Path, default=Path('.citation-cache'))
    parser.add_argument('--live', action='store_true', help='Send public identifiers/titles to Crossref/arXiv; otherwise cache-only')
    parser.add_argument('--max-requests', type=int, default=50)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.max_requests < 0 or args.snapshot and args.live:
        parser.error('Budget must be nonnegative; choose snapshot OR live mode')
    try:
        entries = parse_bibtex(args.bibtex.read_text(encoding='utf-8'))
    except (BibError, OSError) as error:
        parser.exit(2, f'BibTeX input error: {error}\n')
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8')) if args.snapshot else None
    output = audit(entries, Resolver(snapshot, args.cache, args.live, args.max_requests))
    output['input_sha256'] = hashlib.sha256(args.bibtex.read_bytes()).hexdigest()
    output['implementation_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output['python_version'] = platform.python_version()
    if args.snapshot:
        output['snapshot_sha256'] = hashlib.sha256(args.snapshot.read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(output['coverage']))


if __name__ == '__main__':
    main()
