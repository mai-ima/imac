#!/usr/bin/env python3
"""GA-01〜32 と R9 の全指摘(reports/R9_*.md)を tasks.json へID単位で登録/更新する(GA-14)。
状態は audit_control/resolutions.json(ID→{status,evidence,verification,decision})で上書き。無ければ triaged(未修正)。件数は reports のIDと一致をゲート化。"""
import json, os, re, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); AC = f'{R}/audit_control'; now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
T = json.load(open(f'{AC}/tasks.json', encoding='utf-8')); by = {t['id']: t for t in T['tasks']}
res = json.load(open(f'{AC}/resolutions.json', encoding='utf-8')) if os.path.exists(f'{AC}/resolutions.json') else {}
def upsert(i, title, sev, files, origin):
    t = by.get(i)
    if not t:
        t = dict(id=i, title=title, description=title, type='finding', origin=origin, requirement_ids=[], file_paths=files, severity=sev, size='S', impact='', dependencies=[], parent_id=None, status='triaged', history=[[now, 'triaged', 'import']], acceptance_criteria='再検証→修正→テスト→台帳更新', evidence=[], verification='', decision='', blocker_reason='', defer_reason='', next_action='')
        T['tasks'].append(t); by[i] = t
    r = res.get(i)
    if r and (t['status'] != r['status'] or not t['evidence']):
        t['status'] = r['status']; t['evidence'] = [r.get('evidence', '')]; t['verification'] = r.get('verification', ''); t['decision'] = r.get('decision', ''); t['history'].append([now, r['status'], 'resolution'])
        if r['status'] == 'blocked': t['blocker_reason'] = r.get('evidence', '')
        if r['status'] == 'deferred': t['defer_reason'] = r.get('evidence', '')
n = {}
for line in open(f'{AC}/reports/GA_2026-11-07_table.md', encoding='utf-8'):
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) >= 5 and c[0].startswith('GA-'): upsert(c[0], c[4], c[1], [x.strip('` ') for x in c[3].split(';')], 'GA_2026-11-07'); n['GA'] = n.get('GA', 0) + 1
for rep in ('R9_docs', 'R9_tools', 'R9_drawings'):
    for line in open(f'{AC}/reports/{rep}.md', encoding='utf-8'):
        m = re.match(r'\|\s*(R9[DTG]-F?\d+)\s*\|\s*(P\d|確認OK)\s*\|\s*([^|]*)\|?\s*([^|]*)', line)
        if m: upsert(m.group(1), (m.group(4).strip()[:140] or m.group(3).strip()[:140]), 'P3' if m.group(2) == '確認OK' else m.group(2), [m.group(3).strip()[:120]], rep); n[rep] = n.get(rep, 0) + 1
json.dump(T, open(f'{AC}/tasks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print('import', n, '/ 全タスク', len(T['tasks']), dict(Counter(t['status'] for t in T['tasks'])))
