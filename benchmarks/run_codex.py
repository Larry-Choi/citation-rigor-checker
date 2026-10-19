"""Run isolated, tool-free Codex CLI evaluation sessions (no API-key handling).

Model and reasoning settings must be explicit. This consumes the signed-in
account's ordinary model usage. Inputs must be public/synthetic and pre-exported.
Raw runtime logs stay in the specified local raw directory, not in the report.
"""
import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompts', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--isolation-dir', type=Path, required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--reasoning-effort', required=True)
    parser.add_argument('--cli', default='codex')
    parser.add_argument('--timeout', type=int, default=240)
    parser.add_argument('--include-old-skill', action='store_true', help='Three conditions, three repeats, balanced position order')
    args = parser.parse_args()
    if args.out.exists() and list(args.out.glob('*.json')):
        parser.error('Output directory already has results; use a fresh directory')
    for directory in [args.out, args.raw, args.isolation_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    if list(args.isolation_dir.iterdir()):
        parser.error('The isolation directory must be empty (no repository or gold files)')
    args.out, args.raw, args.prompts = args.out.resolve(), args.raw.resolve(), args.prompts.resolve()
    schema = {'type': 'object', 'properties': {'predictions': {'type': 'array', 'items': {
        'type': 'object', 'properties': {'id': {'type': 'string'}, 'status': {'type': 'string', 'enum': [
            'matched_metadata', 'metadata_review', 'identity_conflict', 'unresolved',
            'supported', 'partially_supported', 'contradicted', 'not_supported', 'not_assessed']},
            'reason': {'type': 'string'}}, 'required': ['id', 'status', 'reason'], 'additionalProperties': False}}},
        'required': ['predictions'], 'additionalProperties': False}
    schema_path = args.raw / 'response-schema.json'
    schema_path.write_text(json.dumps(schema), encoding='utf-8', newline='\n')
    manifest = json.loads((args.prompts / 'manifest.json').read_text(encoding='utf-8'))
    cli_version = subprocess.check_output([args.cli, '--version'], text=True, encoding='utf-8').strip()
    order = [('baseline', 1), ('skill', 1), ('skill', 2), ('baseline', 2), ('baseline', 3), ('skill', 3)]
    if args.include_old_skill:
        order = [(condition, repeat) for repeat, conditions in enumerate([
            ['baseline', 'old_skill', 'skill'], ['old_skill', 'skill', 'baseline'],
            ['skill', 'baseline', 'old_skill']], start=1) for condition in conditions]
    runs = []
    for condition, repeat in order:
        name = f'{condition}-{repeat}'
        prompt_bytes = (args.prompts / f'{condition}.txt').read_bytes()
        answer = args.raw / (name + '-answer.json')
        command = [args.cli, 'exec', '--ignore-user-config', '--disable', 'shell_tool', '--disable', 'multi_agent',
                   '-c', 'web_search="disabled"', '-c', f'model_reasoning_effort="{args.reasoning_effort}"',
                   '--model', args.model, '--sandbox', 'read-only', '--skip-git-repo-check', '--ephemeral',
                   '--json', '--output-schema', str(schema_path), '--output-last-message', str(answer), '-']
        started = datetime.now(timezone.utc).isoformat()
        clock = time.monotonic()
        timed_out = False
        with (args.raw / (name + '.jsonl')).open('wb') as stdout, (args.raw / (name + '.stderr')).open('wb') as stderr:
            process = subprocess.Popen(command, cwd=args.isolation_dir.resolve(), stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
            try:
                process.communicate(prompt_bytes, timeout=args.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                timed_out = True
        usage, tools, errors = None, [], []
        for line in (args.raw / (name + '.jsonl')).read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('type') == 'turn.completed':
                usage = event.get('usage')
            item_type = event.get('item', {}).get('type', '')
            if item_type in {'command_execution', 'mcp_tool_call', 'web_search', 'file_change'}:
                tools.append(item_type)
            if event.get('type') in {'error', 'turn.failed'}:
                errors.append(event.get('message') or event.get('error', {}).get('message', 'runtime error'))
        run = {'condition': condition, 'repeat': repeat, 'model_alias': args.model,
               'reasoning_effort': args.reasoning_effort, 'cli_version': cli_version,
               'started_at': started, 'wall_seconds': round(time.monotonic()-clock, 3),
               'returncode': process.returncode, 'timed_out': timed_out, 'observed_tool_events': tools,
               'usage': usage, 'prompt_sha256': hashlib.sha256(prompt_bytes).hexdigest(),
               'manifest': manifest, 'valid_tool_free_run': process.returncode == 0 and not timed_out and not tools and answer.exists(),
               'runtime_errors': errors}
        predictions = json.loads(answer.read_text(encoding='utf-8'))['predictions'] if answer.exists() and not tools else []
        payload = {'run': run, 'predictions': predictions}
        (args.out / (name + '.json')).write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
        runs.append(run)
        print(json.dumps({'run': name, 'valid': run['valid_tool_free_run'], 'seconds': run['wall_seconds'],
                          'predictions': len(predictions), 'errors': errors}), flush=True)
        if not run['valid_tool_free_run']:
            # A failed environment is not a model result. Do not spend five more
            # calls on the same setup failure; preserve the attempted run.
            break
    (args.out/'run-manifest.json').write_text(json.dumps({'order': order, 'runs': runs}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
