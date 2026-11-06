#!/usr/bin/env python3
"""全(現行)ファイルを走査して docs/PROJECT-SUMMARY.md を生成する: ディレクトリ別の役割と件数、主要ファイルの一行要約、現行の主要数値(spec.jsonから)、未確認件数、ゲート結果。
archive/ は件数のみ。手で直さず再生成する(常設ループの各周で実行)。"""
import json, os, re, subprocess, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = [f for f in subprocess.check_output(['git', '-c', 'core.quotepath=off', 'ls-files'], cwd=R, text=True).split('\n') if f]
cur = [f for f in files if '/archive/' not in f and not f.startswith('archive/')]
arch = len(files) - len(cur)
def first(f):
    p = os.path.join(R, f)
    try: t = open(p, encoding='utf-8').read(4000)
    except Exception: return ''
    if f.endswith('.py'):
        m = re.search(r'"""(.*?)"""', t, re.S); return (m.group(1).strip().split('\n')[0] if m else '')[:110]
    if f.endswith('.md'):
        m = re.search(r'^#\s+(.+)$', t, re.M); return m.group(1)[:110] if m else ''
    if f.endswith('.sh'): return (t.split('\n')[1] if t.startswith('#!') else t.split('\n')[0]).lstrip('# ')[:110]
    return ''
by = {}
for f in cur: by.setdefault(f.split('/')[0] if '/' in f else '(root)', []).append(f)
S = json.load(open(f'{R}/model/spec.json')); B = json.load(open(f'{R}/model/balance.json'))
unv = sum(1 for l in open(f'{R}/docs/unverified-tracker.md', encoding='utf-8') if l.startswith('| U'))
o = [f'# プロジェクト要約(自動生成 {datetime.date.today()})', '', '`tools/gen_project_summary.py` が全ファイルを走査して生成。手で直さない。', '',
     '## 1. 現行の主要数値(model/spec.json)',
     f"- 本体: 幅{S['body_w']}mm×スラブ厚{S['slab_t']}mm、ドーム総厚{S['dome']['total_t']}mm(内奥行{S['dome']['total_t']-S['slab_t']-S['pod']['wall']}mm。ポンプ垂直出口ホース用)",
     f"- スタンド: 足{S['stand']['foot_w']}×{S['stand']['foot_depth']}mm、ballast {S['stand']['ballast_kg']}kg、チルト{S['hinge']['tilt_min_deg']:+g}〜{S['hinge']['tilt_max_deg']:+g}°、首振り±{S['swivel']['range_deg']:g}°、ヒンジ軸 z={S['hinge']['axis_z_from_glass']}",
     f"- バランサ: s={B['s']} e={B['e']} 最長側{B['F0_longest_total']/2:.0f}N/本 p={B['p']}、摩擦保持{S['hinge']['friction_hold_Nm']}N·m±{S['hinge']['friction_tol_pct']:g}%、操作力目標≦{S['hinge']['op_target_N']:g}N",
     f"- 未確認事項(U台帳): {unv}件(docs/unverified-tracker.md)", '',
     f'## 2. ファイル構成(git追跡 {len(files)}件 = 現行 {len(cur)} + 履歴archive {arch})', '', '| ディレクトリ | 現行件数 | 役割 |', '|---|---|---|']
role = {'model': '単一源データ(spec/layout/parts/custom_parts/balance/pump/cables…)', 'tools': '生成器・計算・検査ゲート', 'blender': '3Dモデル生成(build_imac_pc_v8.py/hardware_v8.py)', 'docs': '仕様・設計書・調査・監査記録', 'drawings': '図面(SVG/DXF/PDF入力)', 'viewer': 'Three.jsビューア+GLB', 'render': 'レンダリング画像', 'handoff': '業者提出パッケージ', 'audit_output': '監査台帳・指摘一覧', 'cad': 'OpenSCAD', 'concept': 'コンセプト画像', 'archive': '旧版(削除せず保存)'}
for k in sorted(by): o.append(f"| {k} | {len(by[k])} | {role.get(k, '')} |")
o += ['', '## 3. 主要ファイル(一行要約)', '']
for d in ('tools', 'model', 'docs', 'docs/mechanisms', 'docs/spec', 'blender'):
    rows = [(f, first(f)) for f in sorted(cur) if (os.path.dirname(f) == d) and f.endswith(('.py', '.md', '.sh', '.json'))]
    if not rows: continue
    o += [f'### {d}/', '']
    for f, s in rows: o.append(f"- `{os.path.basename(f)}`" + (f" — {s}" if s else ''))
    o.append('')
open(f'{R}/docs/PROJECT-SUMMARY.md', 'w', encoding='utf-8').write('\n'.join(o) + '\n'); print('summary', len(cur), 'current files')
