#!/usr/bin/env python3
"""audit_control/reports/R12_model_*.md の表(| MDA-001 | P0 | 対象 | 問題 | 根拠 | 修正案 |)を tasks.json へ取り込む(既存IDは更新しない)。"""
import json, re, glob, datetime, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); p = f'{R}/audit_control/tasks.json'; T = json.load(open(p, encoding='utf-8'))
have = {t['id'] for t in T['tasks']}; now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); base = T['tasks'][-1]; n = 0
for f in sorted(glob.glob(f'{R}/audit_control/reports/R12_model_*.md')):
    for line in open(f, encoding='utf-8'):
        m = re.match(r'\|\s*(MD[A-D]-\d+)\s*\|\s*(P[0-3])\s*\|(.*)\|\s*$', line)
        if not m or m.group(1) in have: continue
        cols = [c.strip() for c in m.group(3).split('|')]
        obj, prob = (cols[0], cols[1]) if len(cols) >= 2 else ('', m.group(3))
        fix = cols[-1] if len(cols) >= 4 else ''
        d = {k: (([] if isinstance(v, list) else '' if isinstance(v, str) else v) if k in ('evidence', 'verification', 'history', 'file_paths', 'requirement_ids', 'dependencies', 'acceptance_criteria') else v) for k, v in base.items()}
        d.update(id=m.group(1), title=(obj + ': ' + prob)[:120], description=' | '.join(cols)[:1500], severity=m.group(2), status='triaged', parent_id='QUAL-06', history=[[now, 'triaged', f'R12取込({os.path.basename(f)})']], evidence=[f'audit_control/reports/{os.path.basename(f)}'], next_action=fix[:300])
        T['tasks'].append(d); have.add(d['id']); n += 1
json.dump(T, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('imported', n)
