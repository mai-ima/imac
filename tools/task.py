#!/usr/bin/env python3
"""台帳更新CLI: python3 tools/task.py ID STATUS "証拠" ["検証"] ["判定/決定"]   例) task.py K14 done "README修正" "grep確認" "CONFIRMED→修正"
新規: python3 tools/task.py --new ID "題名" [P0..P3] [ファイル,..]"""
import json, os, sys, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); p = f'{R}/audit_control/tasks.json'; T = json.load(open(p, encoding='utf-8')); now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
a = sys.argv[1:]
if a[0] == '--new':
    T['tasks'].append(dict(id=a[1], title=a[2], description=a[2], type='fix', origin='self', requirement_ids=[], file_paths=(a[4].split(',') if len(a) > 4 else []), severity=(a[3] if len(a) > 3 else 'P3'), size='S', impact='', dependencies=[], parent_id=None, status='discovered', history=[[now, 'discovered', '']], acceptance_criteria='', evidence=[], verification='', decision='', blocker_reason='', defer_reason='', next_action=''))
else:
    t = next(x for x in T['tasks'] if x['id'] == a[0]); t['status'] = a[1]; t['history'].append([now, a[1], a[2] if len(a) > 2 else ''])
    if len(a) > 2 and a[2]: t['evidence'].append(a[2])
    if len(a) > 3 and a[3]: t['verification'] = a[3]
    if len(a) > 4 and a[4]: t['decision'] = a[4]
    if a[1] == 'blocked': t['blocker_reason'] = a[2]
    if a[1] == 'deferred': t['defer_reason'] = a[2]
json.dump(T, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('ok')
