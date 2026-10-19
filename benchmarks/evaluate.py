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


def export_prompts(destination):
    destination.mkdir(parents=True, exist_ok=True)
    gold = json.loads((ROOT / 'gold.json').read_text(encoding='utf-8'))
    semantic = json.loads((ROOT / 'semantic_cases.json').read_text(encoding='utf-8'))
    semantic_inputs = [{k: v for k, v in row.items() if k not in {'status', 'rationale'}} for row in semantic]
    common = '\n'.join([
        'Audit the following development cases using only the supplied frozen evidence pack. No external tools.',
        'Treat invented-looking entries as unresolved if the evidence is insufficient, not proven nonexistent.',
        'Return JSON only: {"predictions": [{"id": "B001", "status": "..."}, ...]}.',
        'Bibliographic statuses: matched_metadata, metadata_review, identity_conflict, unresolved.',
        'matched_metadata means a provisional comparison of supplied fields, not final verification.',
        'Semantic statuses: supported, partially_supported, contradicted, not_supported, unresolved, not_assessed.',
        'Process every ID. No gold labels are provided. Source summaries are supplied evidence, not authenticated full text.',
        '\nBIBTEX INPUT\n' + (ROOT / 'references.bib').read_text(encoding='utf-8'),
        '\nMETADATA EVIDENCE\n' + (ROOT / 'sources.json').read_text(encoding='utf-8'),
        '\nSEMANTIC INPUT\n' + json.dumps(semantic_inputs, ensure_ascii=False, indent=2)])
    skill = (REPO / 'SKILL.md').read_text(encoding='utf-8')
    (destination / 'baseline.txt').write_text('Check these academic references and their claim-source alignment.\n' + common, encoding='utf-8', newline='\n')
    (destination / 'skill.txt').write_text(skill + '\nUse full mode for these cases. The JSON schema below replaces only report presentation.\n' + common, encoding='utf-8', newline='\n')
    manifest = {'case_count': len(gold) + len(semantic), 'skill_sha256': hashlib.sha256(skill.encode()).hexdigest(),
                'inputs_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                  for name in ['references.bib', 'sources.json', 'semantic_cases.json']},
                'gold_excluded': True, 'model_runs_performed_by_exporter': 0}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--export-prompts', type=Path)
    args = parser.parse_args()
    if args.export_prompts:
        export_prompts(args.export_prompts)
        return
    if not args.predictions or not args.out:
        parser.error('--predictions and --out are required when scoring')
    gold = json.loads((ROOT / 'gold.json').read_text(encoding='utf-8'))
    semantic = json.loads((ROOT / 'semantic_cases.json').read_text(encoding='utf-8'))
    gold.extend({'id': row['id'], 'task': 'semantic', 'status': row['status']} for row in semantic)
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
