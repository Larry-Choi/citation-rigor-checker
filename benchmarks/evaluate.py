"""Score exported predictions; export matched baseline/skill prompt packs.

No model API calls are made. Prediction files contain {run: {...}, predictions:
[{id, status}, ...]}. Missing predictions count as abstentions and false negatives.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def metrics(gold, predictions):
    gold_by_id = {g['id']: g for g in gold}
    by_id = {}
    for row in predictions:
        if row['id'] in by_id or row['id'] not in gold_by_id:
            raise ValueError('Duplicate or unknown prediction ID: ' + row['id'])
        task = gold_by_id[row['id']]['task']
        allowed = {'bibliographic': {'matched_metadata', 'metadata_review', 'identity_conflict', 'unresolved'},
                   'semantic': {'supported', 'partially_supported', 'contradicted', 'not_supported', 'unresolved', 'not_assessed'}}[task]
        if row['status'] not in allowed:
            raise ValueError(f'Invalid {task} status: {row["status"]}')
        by_id[row['id']] = row['status']
    output = {}
    for task in sorted({g['task'] for g in gold}):
        subset = [g for g in gold if g['task'] == task]
        labels = sorted({g['status'] for g in subset} | {by_id[g['id']] for g in subset if g['id'] in by_id})
        per_label = {}
        for label in labels:
            tp = sum(g['status'] == label and by_id.get(g['id']) == label for g in subset)
            fp = sum(g['status'] != label and by_id.get(g['id']) == label for g in subset)
            fn = sum(g['status'] == label and by_id.get(g['id']) != label for g in subset)
            precision = tp / (tp + fp) if tp + fp else 0.0
            recall = tp / (tp + fn) if tp + fn else 0.0
            per_label[label] = {'tp': tp, 'fp': fp, 'fn': fn, 'precision': precision, 'recall': recall,
                                'f1': 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
                                'support': tp + fn}
        missing = [g['id'] for g in subset if g['id'] not in by_id]
        correct = sum(by_id.get(g['id']) == g['status'] for g in subset)
        output[task] = {'total': len(subset), 'predicted': len(subset) - len(missing),
                        'coverage': (len(subset) - len(missing)) / len(subset),
                        'correct': correct, 'accuracy': correct / len(subset),
                        'macro_f1': sum(v['f1'] for v in per_label.values()) / len(per_label),
                        'per_status': per_label, 'missing_ids': missing}
    return output


def score_views(gold, predictions):
    """Separate primary unambiguous cases from strict and set-valued sensitivity."""
    primary = [g for g in gold if not g.get('exclude_from_primary')]
    ids = {g['id'] for g in primary}
    # Validate the complete response before filtering; never hide invalid IDs.
    strict = metrics(gold, predictions)
    by_id = {g['id']: g for g in gold}
    accepted = [dict(p, status=by_id[p['id']]['status'])
                if p['status'] in by_id[p['id']].get('accepted_statuses', []) else p
                for p in predictions]
    return {'primary': metrics(primary, [p for p in predictions if p['id'] in ids]),
            'all_strict_secondary': strict,
            'acceptable_set_secondary': metrics(gold, accepted),
            'excluded_ids': [g['id'] for g in gold if g.get('exclude_from_primary')]}


def load_gold(dataset):
    if dataset in {'real-world', 'adjudicated-v2'}:
        directory = ROOT / dataset
        return json.loads((directory / 'gold.json').read_text(encoding='utf-8')) + json.loads((directory / 'semantic_gold.json').read_text(encoding='utf-8'))
    gold = json.loads((ROOT / 'gold.json').read_text(encoding='utf-8'))
    semantic = json.loads((ROOT / 'semantic_cases.json').read_text(encoding='utf-8'))
    return gold + [{'id': row['id'], 'task': 'semantic', 'status': row['status']} for row in semantic]


def export_prompts(destination, dataset='real-world'):
    destination.mkdir(parents=True, exist_ok=True)
    if dataset not in {'real-world', 'adjudicated-v2'}:
        raise ValueError('Model comparison exports use the real-world set; legacy is regression-only')
    directory = ROOT / dataset
    files = ['bibliographic_cases.json', 'records.json', 'semantic_cases.json', 'evidence.json']
    packet = {name.removesuffix('.json'): json.loads((directory / name).read_text(encoding='utf-8')) for name in files}
    rubric = (directory / 'rubric.txt').read_text(encoding='utf-8') if dataset == 'adjudicated-v2' else ''
    common = '\n'.join([
        'Audit these bibliography entries against the supplied candidate records and the attributed claims against the supplied source passages. Use only this packet. No tools.',
        'Return JSON only: {"predictions": [{"id": "R001", "status": "...", "reason": "short evidence-based explanation"}, ...]}.',
        'Bibliographic statuses: matched_metadata, metadata_review, identity_conflict, unresolved.',
        'Semantic statuses: supported, partially_supported, contradicted, not_supported, unresolved, not_assessed.',
        'Label scope: metadata states concern the supplied candidate fields; semantic states concern support from the supplied passage, not the whole unseen paper. Assess each ID.',
        *([rubric] if rubric else []),
        '\nINPUT PACKET\n' + json.dumps(packet, ensure_ascii=False, indent=2)])
    skill = (REPO / 'SKILL.md').read_text(encoding='utf-8')
    (destination / 'baseline.txt').write_text('Check these academic references and their claim-source alignment.\n' + common, encoding='utf-8', newline='\n')
    (destination / 'skill.txt').write_text(skill + '\nUse full mode for these cases. The JSON schema below replaces only report presentation.\n' + common, encoding='utf-8', newline='\n')
    if dataset == 'adjudicated-v2':
        old_skill = (ROOT / 'comparison/SKILL.original.txt').read_text(encoding='utf-8')
        (destination / 'old_skill.txt').write_text(old_skill + '\nUse full mode for these cases. The JSON schema below replaces only report presentation.\n' + common, encoding='utf-8', newline='\n')
    manifest = {'dataset': dataset, 'case_count': len(load_gold(dataset)), 'skill_sha256': hashlib.sha256(skill.encode()).hexdigest(),
                'inputs_sha256': {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in files},
                'gold_excluded': True, 'model_runs_performed_by_exporter': 0}
    if rubric:
        manifest['rubric_sha256'] = hashlib.sha256(rubric.encode()).hexdigest()
        manifest['original_skill_sha256'] = hashlib.sha256(old_skill.encode()).hexdigest()
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--export-prompts', type=Path)
    parser.add_argument('--dataset', choices=['real-world', 'adjudicated-v2', 'legacy'], default='real-world')
    args = parser.parse_args()
    if args.export_prompts:
        export_prompts(args.export_prompts, args.dataset)
        return
    if not args.predictions or not args.out:
        parser.error('--predictions and --out are required when scoring')
    gold = load_gold(args.dataset)
    payload = json.loads(args.predictions.read_text(encoding='utf-8'))
    if 'results' in payload:  # Direct metadata preflight output, with no semantic predictions.
        predictions = [{'id': r['id'], 'status': r['status']} for r in payload['results']]
        run = {'condition': 'deterministic_preflight', 'model': None, 'semantic_run': False}
    else:
        predictions, run = payload['predictions'], payload.get('run', {})
    result = {'run': run, 'metrics': metrics(gold, predictions),
              'note': 'Development-set results only. Missing cases are penalized. Zero predicted positives use precision=0. No evidence of a prompt advantage without actual matched model runs.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result['metrics'], indent=2))


if __name__ == '__main__':
    main()
