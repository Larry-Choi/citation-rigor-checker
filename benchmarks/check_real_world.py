"""Replay the separately sourced candidate-record comparisons; no network/model."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from bibliography import compare
from evaluate import load_gold, metrics


def main():
    directory = ROOT/'benchmarks/real-world'
    records = json.loads((directory/'records.json').read_text(encoding='utf-8'))
    cases = json.loads((directory/'bibliographic_cases.json').read_text(encoding='utf-8'))
    predictions = []
    for case in cases:
        result = compare(case['entry'], records.get(case['candidate_record_id']))
        predictions.append({'id':case['id'], **result})
    gold = load_gold('real-world')
    score = metrics(gold, predictions)
    benign = [r['id'] for r in gold if r.get('kind') in {'upstream_original','surface_variant'}]
    output = {'run':{'condition':'deterministic_candidate_comparison','model':None},
              'predictions':predictions, 'metrics':score,
              'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [directory/'records.json', directory/'bibliographic_cases.json']},
              'non_conflicting_case_count':len(benign),
              'identity_flags_on_non_conflicting_cases':[r['id'] for r in predictions if r['id'] in benign and r['status']=='identity_conflict']}
    (ROOT/'benchmarks/results/real-world-preflight.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'bibliographic':score['bibliographic'],'identity_flags_on_non_conflicting_cases':output['identity_flags_on_non_conflicting_cases']},indent=2))


if __name__ == '__main__':
    main()
