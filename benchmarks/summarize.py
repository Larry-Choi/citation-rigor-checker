"""Score every saved repeat for two or three conditions, without selection."""
import hashlib
import json
import statistics
import argparse
from pathlib import Path
from evaluate import load_gold, metrics, score_views

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT/'comparison')
    parser.add_argument('--dataset', choices=['real-world','adjudicated-v2'], default='real-world')
    parser.add_argument('--include-old-skill', action='store_true')
    args = parser.parse_args()
    directory = args.directory
    gold = load_gold(args.dataset)
    conditions = ['baseline','old_skill','skill'] if args.include_old_skill else ['baseline','skill']
    runs = []
    for condition in conditions:
        for repeat in [1,2,3]:
            name = f'{condition}-{repeat}'
            payload = json.loads((directory/(name+'.json')).read_text(encoding='utf-8'))
            assert payload['run']['valid_tool_free_run'], f'Invalid run: {name}'
            views = score_views(gold,payload['predictions'])
            score = views['primary']
            runs.append({'name':name,'run':payload['run'],'metrics':score,'views':views})
            (directory/(name+'-metrics.json')).write_text(json.dumps(views,indent=2)+'\n',encoding='utf-8',newline='\n')
    assert len({r['run']['model_alias'] for r in runs}) == 1
    assert len({r['run']['reasoning_effort'] for r in runs}) == 1
    assert len({json.dumps(r['run']['manifest'],sort_keys=True) for r in runs}) == 1
    summary = {'dataset':args.dataset,'case_count':len(gold),'repeat_count':3,
               'primary_excluded_ids':[g['id'] for g in gold if g.get('exclude_from_primary')],
               'model_alias':runs[0]['run']['model_alias'], 'reasoning_effort':runs[0]['run']['reasoning_effort'],
               'cli_version':runs[0]['run']['cli_version'], 'conditions':{},'paired_skill_minus_baseline':[],
               'annotation_sha256':hashlib.sha256(json.dumps(gold,ensure_ascii=False,sort_keys=True).encode()).hexdigest()}
    for condition in conditions:
        subset = [r for r in runs if r['run']['condition']==condition]
        assert len({r['run']['prompt_sha256'] for r in subset}) == 1
        result = {'wall_seconds_mean':statistics.mean(r['run']['wall_seconds'] for r in subset),
                  'tasks':{}, 'tool_events_total':sum(len(r['run']['observed_tool_events']) for r in subset)}
        usage = [r['run']['usage'] for r in subset]
        result['usage_mean'] = {key:statistics.mean(u[key] for u in usage) for key in ['input_tokens','cached_input_tokens','output_tokens'] if all(u and key in u for u in usage)}
        result['secondary'] = {view:{task:{'accuracy_mean':statistics.mean(r['views'][view][task]['accuracy'] for r in subset),
                'macro_f1_mean':statistics.mean(r['views'][view][task]['macro_f1'] for r in subset)} for task in ['bibliographic','semantic']}
                for view in ['all_strict_secondary','acceptable_set_secondary']}
        for task in ['bibliographic','semantic']:
            scores = [r['metrics'][task] for r in subset]
            labels = sorted({label for s in scores for label in s['per_status']})
            result['tasks'][task] = {
                'total_per_repeat':scores[0]['total'],
                'correct_by_repeat':[s['correct'] for s in scores],
                'accuracy_mean':statistics.mean(s['accuracy'] for s in scores),
                'macro_f1_mean':statistics.mean(s['macro_f1'] for s in scores),
                'coverage_mean':statistics.mean(s['coverage'] for s in scores),
                'per_status_mean':{label:{key:statistics.mean(s['per_status'].get(label,{}).get(key,0) for s in scores) for key in ['precision','recall','f1']} for label in labels}}
        summary['conditions'][condition] = result
    for repeat in [1,2,3]:
        pair = {r['run']['condition']:r for r in runs if r['run']['repeat']==repeat}
        summary['paired_skill_minus_baseline'].append({'repeat':repeat,**{
            task:pair['skill']['metrics'][task]['macro_f1']-pair['baseline']['metrics'][task]['macro_f1'] for task in ['bibliographic','semantic']},
            **({'skill_minus_old_skill':{task:pair['skill']['metrics'][task]['macro_f1']-pair['old_skill']['metrics'][task]['macro_f1'] for task in ['bibliographic','semantic']}} if args.include_old_skill else {})})
    (directory/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
