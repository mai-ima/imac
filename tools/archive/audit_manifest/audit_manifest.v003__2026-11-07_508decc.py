#!/usr/bin/env python3
"""全ファイル台帳(SHA-256/種別/役割/検証状態)を audit_output/01_FULL_FILE_MANIFEST.csv に出力。
'content_verified' は自動検査(旧値走査/構文)を通ったものだけ true。人手/監査で開いた分は別途 review 列で管理。"""
import csv, hashlib, subprocess, os, json, ast, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = subprocess.check_output(['git', 'ls-files'], cwd=R, text=True).split('\n')
def kind(p):
    if '/archive/' in p or p.startswith('archive/'): return 'ARCHIVE(旧版)'
    if p.startswith('model/'): return 'CANON(正規データ)' if p.endswith('.json') else 'MODEL'
    if p.startswith('tools/'): return 'TOOL(生成/検証)'
    if p.startswith(('drawings/', 'render/', 'viewer/imac_pc.glb', 'blender/imac_pc')): return 'GENERATED(生成物)'
    if p.startswith('docs/'): return 'DOC'
    if p.startswith(('blender/', 'cad/', 'concept/', 'viewer/')): return 'SOURCE(手書きソース)'
    return 'OTHER'
def syntax(p):
    if not p.endswith(('.py', '.json', '.svg')): return 'binary_or_text_not_parsed'
    try:
        t = open(os.path.join(R, p), encoding='utf-8').read()
        if p.endswith('.py'): ast.parse(t); return 'syntax_ok'
        if p.endswith('.json'): json.loads(t); return 'syntax_ok'
        if p.endswith('.svg'): import xml.dom.minidom as m; m.parseString(t.encode()); return 'syntax_ok'
    except Exception as e: return 'SYNTAX_FAIL:' + str(e)[:60]
    return 'not_checked'
# custom_parts.json の型検査(寸法は数値のみ、features/mates/tests/open は文字列のリスト)
type_errs = []
for x in json.load(open(f'{R}/model/custom_parts.json'))['parts']:
    if not all(isinstance(v, (int, float)) for v in x['size']): type_errs.append(f"{x['id']}: size が数値でない")
    if x['t'] is not None and not isinstance(x['t'], (int, float)): type_errs.append(f"{x['id']}: t が数値でない")
    for k in ('features', 'mates', 'open'):
        if k in x and not (isinstance(x[k], list) and all(isinstance(i, str) and len(i) > 1 for i in x[k])): type_errs.append(f"{x['id']}: {k} が文字列リストでない")
for e in type_errs: print('[TYPE]', e)
rows = []
for p in files:
    if not p or not os.path.isfile(os.path.join(R, p)): continue
    if p == 'audit_output/01_FULL_FILE_MANIFEST.csv': continue      # 自己参照(自分のハッシュ)は除外=実行のたびに差分が出る無限ループの原因
    b = open(os.path.join(R, p), 'rb').read()
    rows.append(dict(path=p, kind=kind(p), size=len(b), sha256=hashlib.sha256(b).hexdigest(), automated_check=syntax(p),
                     content_reviewed_by_human_or_agent='NO'))
os.makedirs(f'{R}/audit_output', exist_ok=True)
with open(f'{R}/audit_output/01_FULL_FILE_MANIFEST.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows), '件', 'type_errs=', len(type_errs), dict(Counter(r['kind'] for r in rows)), 'syntax_fail=', sum(r['automated_check'].startswith('SYNTAX') for r in rows))

sys.exit(1 if type_errs else 0)
