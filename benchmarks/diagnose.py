"""Reproduce v1 error decomposition without overwriting v1 labels/results."""
import hashlib
import json
from pathlib import Path
from evaluate import load_gold, metrics, score_views

ROOT = Path(__file__).resolve().parent


def main():
    old = load_gold('real-world')
    revised = [g for g in load_gold('adjudicated-v2') if g['id'] != 'R020']
    runs = {}
    for condition in ['baseline', 'skill']:
        for repeat in [1, 2, 3]:
            name = f'{condition}-{repeat}'
            payload = json.loads((ROOT/'comparison'/(name+'.json')).read_text(encoding='utf-8'))
            predictions = payload['predictions']
            without = [g for g in old if g['id'] != 'R019']
            runs[name] = {
                'original': metrics(old, predictions),
                'remove_access_design_case_only': metrics(without, [p for p in predictions if p['id'] != 'R019']),
                'retrospective_adjudicated': score_views(revised, predictions),
                'disagreements_with_original': [dict(p, original_status=next(g['status'] for g in old if g['id']==p['id']))
                    for p in predictions if p['status'] != next(g['status'] for g in old if g['id']==p['id'])]}
    by_id = []
    for g in old:
        if g['task'] != 'bibliographic':
            continue
        predictions = {}
        for condition in ['baseline','skill']:
            predictions[condition] = [next(p['status'] for p in json.loads((ROOT/'comparison'/f'{condition}-{repeat}.json').read_text(encoding='utf-8'))['predictions'] if p['id']==g['id']) for repeat in [1,2,3]]
        by_id.append({'id':g['id'], 'old_status':g['status'],'v2_status':next(x['status'] for x in revised if x['id']==g['id']), 'predictions':predictions})
    result = {'analysis':'Retrospective development diagnosis; not new model runs or independent gold adjudication.',
              'original_gold_sha256':hashlib.sha256((ROOT/'real-world/gold.json').read_bytes()).hexdigest(),
              'runs':runs,'bibliographic_case_predictions':by_id}
    (ROOT/'diagnosis-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    for condition in ['baseline','skill']:
        for view in ['original','remove_access_design_case_only','retrospective_adjudicated']:
            scores = [runs[f'{condition}-{i}'][view] for i in [1,2,3]]
            if view == 'retrospective_adjudicated':
                scores = [s['primary'] for s in scores]
            print(condition,view,'macro-F1',round(sum(s['bibliographic']['macro_f1'] for s in scores)/3,6), 'correct',[s['bibliographic']['correct'] for s in scores])
    print(json.dumps(by_id,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
