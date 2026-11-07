#!/usr/bin/env python3
"""R9指摘の自動再判定: 報告の『原文』(「…」引用)が、指摘された現行ファイルにまだ存在するかをgrepする。
存在しなければ 'in_review'(原文は解消。人間/再監査で確認)、存在すれば 'triaged' のまま(未修正)。git ls-files の現行ファイルのみ対象。"""
import json, os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); AC = f'{R}/audit_control'
T = json.load(open(f'{AC}/tasks.json', encoding='utf-8')); files = subprocess.check_output(['git', 'ls-files'], cwd=R, text=True).split('\n')
cur = [f for f in files if f and '/archive/' not in f and not f.startswith(('archive/', 'audit_control/', 'audit_output/')) and f.endswith(('.md', '.py', '.json', '.svg', '.html', '.txt', '.csv', '.sh'))]
cache = {}
def txt(f):
    if f not in cache:
        try: cache[f] = open(f'{R}/{f}', encoding='utf-8').read()
        except Exception: cache[f] = ''
    return cache[f]
res = json.load(open(f'{AC}/resolutions.json', encoding='utf-8')); n_ok = n_open = n_na = 0
rep = {}
for r_ in ('R9_docs', 'R9_tools', 'R9_drawings'):
    for line in open(f'{AC}/reports/{r_}.md', encoding='utf-8'):
        m = re.match(r'\|\s*(R9[DTG]-F?\d+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|', line)
        if m: rep[m.group(1)] = (m.group(3), m.group(4))
for t in T['tasks']:
    i = t['id']
    if i not in rep or i in res or t['status'] not in ('triaged', 'discovered'): continue
    path_col, quote_col = rep[i]; qs = [q.strip() for q in re.findall(r'[「`]([^」`]{8,80})[」`]', quote_col)]
    paths = [p for p in cur if any(seg and seg in p for seg in re.findall(r'[\w./-]+\.\w{2,4}', path_col))]
    if not qs or not paths: n_na += 1; continue
    found = [q for q in qs if any(q in txt(p) for p in paths)]
    if found: n_open += 1; continue
    res[i] = dict(status='in_review', evidence=f'報告の原文引用{len(qs)}件が現行の指摘ファイルに存在しない(自動grep: r9_autocheck)', verification='tools/r9_autocheck.py', decision='要再監査で確認'); n_ok += 1
json.dump(res, open(f'{AC}/resolutions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'原文消滅(in_review化) {n_ok} / 原文残存(未修正) {n_open} / 判定不能 {n_na}')
