#!/usr/bin/env python3
"""台帳の機械検査: done に証拠/検証があるか、依存IDが実在するか、重複IDなし、file_coverage が git 管理ファイルを網羅するか。"""
import csv, json, os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); AC = f'{R}/audit_control'
T = json.load(open(f'{AC}/tasks.json', encoding='utf-8'))['tasks']; ids = [t['id'] for t in T]; bad = []
if len(ids) != len(set(ids)): bad.append('タスクID重複')
for t in T:
    if t['status'] == 'done' and not (t['evidence'] and t['verification']): bad.append(f"{t['id']}: done だが evidence/verification なし")
    if t['status'] in ('blocked',) and not t['blocker_reason']: bad.append(f"{t['id']}: blocked の理由なし")
    if t['status'] in ('deferred',) and not t['defer_reason']: bad.append(f"{t['id']}: deferred の理由なし")
    for d in t['dependencies']:
        if d not in ids: bad.append(f"{t['id']}: 依存 {d} が存在しない")
files = {x for x in subprocess.check_output(['git', 'ls-files', '-co', '--exclude-standard'], cwd=R, text=True).split('\n') if x and os.path.isfile(f'{R}/{x}')}
cov = {r['path'] for r in csv.DictReader(open(f'{AC}/file_coverage.csv', encoding='utf-8'))}
miss_all = files - cov
miss_arch = {f for f in miss_all if '/archive/' in f or f.startswith('archive/')}      # 旧版自動退避(pre-commit)は新規発生のため警告のみ(台帳へは次回 init で登録)
miss = miss_all - miss_arch
if miss_arch: print(f'[WARN] file_coverage に未登録の archive ファイル {len(miss_arch)} 件(init で登録)')
if miss: bad.append(f'file_coverage に未登録 {len(miss)} 件(例 {sorted(miss)[:3]}) → tools/audit_control_init.py を実行')
import re, glob
rep_ids = set()
for f in glob.glob(f'{AC}/reports/R9_*.md') + glob.glob(f'{AC}/reports/R10_*.md'):
    rep_ids |= set(re.findall(r'^\|\s*(R9[DTG]-F?\d+)\s*\|', open(f, encoding='utf-8').read(), re.M))
miss_r = sorted(rep_ids - set(ids))
if miss_r: bad.append(f'監査指摘 {len(miss_r)} 件が tasks.json に未登録(例 {miss_r[:3]}) → python3 tools/ledger_import.py')
from collections import Counter
print('tasks', dict(Counter(t['status'] for t in T)), '/ sev', dict(Counter(t['severity'] for t in T)))
rows = list(csv.DictReader(open(f'{AC}/file_coverage.csv', encoding='utf-8'))); print('files', len(rows), dict(Counter(r['status'] for r in rows)))
for b in bad: print('[FAIL]', b)
sys.exit(1 if bad else 0)
