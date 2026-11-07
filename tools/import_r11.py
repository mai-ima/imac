#!/usr/bin/env python3
"""audit_control/reports/R11_*.md の表(| ID | 重大度 | ファイル | 問題 | 対応 |)を tasks.json へ取り込む(既存IDは更新しない)。"""
import json, re, glob, datetime, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); p = f'{R}/audit_control/tasks.json'; T = json.load(open(p, encoding='utf-8'))
have = {t['id'] for t in T['tasks']}; now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); base = T['tasks'][-1]; n = 0
for f in sorted(glob.glob(f'{R}/audit_control/reports/R11_*.md')):
    for line in open(f, encoding='utf-8'):
        m = re.match(r'\|\s*((?:MAN|EST)-\d+)\s*\|\s*(P[0-3])\s*\|([^|]*)\|(.*)\|([^|]*)\|\s*$', line)
        if not m or m.group(1) in have: continue
        i, sev, file_, prob, act = m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip(), m.group(5).strip()
        st = 'in_review' if act.startswith('修正済') else 'blocked' if ('BLOCKED' in act or 'UNVERIFIED' in act and '未' in act[:6]) else 'triaged'
        d = {k: (([] if isinstance(v, list) else '' if isinstance(v, str) else v) if k in ('evidence', 'verification', 'history', 'file_paths', 'requirement_ids', 'dependencies', 'acceptance_criteria') else v) for k, v in base.items()}
        d.update(id=i, title=prob[:120], description=prob, severity=sev, status=st, history=[[now, st, f'R11取込({os.path.basename(f)}): {act[:160]}']], file_paths=[file_], evidence=[f'audit_control/reports/{os.path.basename(f)}'] if st == 'in_review' else [], next_action='' if st == 'in_review' else act[:200])
        if st == 'in_review': d['verification'] = ['再監査で確認(超厳格)']
        T['tasks'].append(d); have.add(i); n += 1
json.dump(T, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('imported', n)
