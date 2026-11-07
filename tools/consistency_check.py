#!/usr/bin/env python3
"""全ファイル矛盾検出: 正規値(model/*.json)と、現行の docs/drawings/py/svg/viewer 内の数値記述を突き合わせる。
履歴文書・archive は対象外(FAIL にしない)。 FAIL があれば終了コード1。"""
import json, re, subprocess, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json'))
B = json.load(open(f'{R}/model/balance.json'))
H = S['hinge']; ST = S['stand']
def n(x): return f'{x:g}'
# (名前, 正規値, 抽出パターン(group1=数値), 説明)
FACTS = [
 ('ドーム総厚', S['dome']['total_t'], r'(?:ドーム|筐体|本体)?総厚\s*[=:≒約]?\s*(\d{2,3}(?:\.\d+)?)\s*mm'),
 ('ヒンジ軸z', H['axis_z_from_glass'], r'ヒンジ軸\s*(?:は|を)?\s*z\s*[=＝]\s*(\d+(?:\.\d+)?)'),
 ('ヒンジ軸z(別表記)', H['axis_z_from_glass'], r'axis_z(?:_from_glass)?\s*[=:]\s*(\d+(?:\.\d+)?)'),
 ('チルト下限', H['tilt_min_deg'], r'チルト\s*([-−]?\d+)\s*[°゜]?\s*[〜~]\s*\+?\d+'),
 ('チルト上限', H['tilt_max_deg'], r'チルト\s*[-−]?\d+\s*[°゜]?\s*[〜~]\s*\+?(\d+)'),
 ('摩擦保持', H['friction_hold_Nm'], r'摩擦(?:ヒンジ)?(?:合計|保持)?\s*(\d+(?:\.\d+)?)\s*N[·・⋅.]?m'),
 ('操作力目標', H.get('op_target_N', 25), r'操作力(?:目標)?[^。\n]{0,12}[≦<=＜]\s*(\d+)\s*N'),
 ('ばね s', B['s'], r'(?<![A-Za-z_])s\s*=\s*(\d{2})\s*mm?\b'),
 ('ばね F0(2本)', B['F0_longest_total'], r'F0\s*=\s*(\d{3,4})\s*N'),
 ('ばね最長側(1本)', B['F0_longest_total'] / 2, r'最長側(?:荷重)?\s*(\d{3})\s*N'),
 ('ばね最大(1本)', round(B['F0_longest_total'] * (1 + B['p']) / 2), r'最大\s*(\d{3})\s*N\s*/\s*本'),
 ('キーホール溝幅', S['fits']['keyhole_slot_w'], r'(?:細溝|溝)\s*W\s*(\d+(?:\.\d+)?)'),
 ('吊りピン肩径', S['fits']['pin_shoulder_d'], r'肩\s*(?:径)?\s*Ø\s*(\d+(?:\.\d+)?)'),
 ('尾部レバー長', S['neck']['lever_len'], r'尾部レバー\s*[(（]?\s*長さ\s*(\d+)'),
 ('足の幅', ST['foot_w'], r'足(?:の)?(?:幅|寸法)?\s*(\d{3})\s*[×x]\s*\d{3}'),
 ('足の奥行', ST['foot_depth'], r'足(?:の)?(?:幅|寸法)?\s*\d{3}\s*[×x]\s*(\d{3})'),
]
HIST = ('docs/audit-log.md','docs/selection-','docs/research-','docs/source-status','docs/unverified-tracker','docs/bom-final','docs/logo-catalog',
        'docs/spec/performance-benchmark','docs/spec/gaming-requirements','docs/tilt-swivel-design.md','docs/joint-analysis.md','blender/build_imac_pc_v6.py',
        'tools/check_sources.py','tools/stale_check.py','tools/consistency_check.py','docs/PRINCIPLES.md','tests/')
SKIPCTX = r'旧|比較|変更前|before|supersed|置換|廃止|履歴|stale|旧版|から変更|→|仮置き|従来|v[0-9]+まで|Appendix'
fails=[]; warns=[]
files = [f for f in subprocess.check_output(['git','ls-files','-co','--exclude-standard'],cwd=R,text=True).split('\n')
         if f and '/archive/' not in f and not f.startswith(('archive/','audit_output/','audit_control/','handoff/','render/','concept/'))
         and f.endswith(('.py','.json','.md','.html','.svg','.csv','.sh'))]
for f in files:
    if f.endswith('glb.txt') or f.startswith('viewer/imac_pc'): continue
    try: t=open(f'{R}/{f}',encoding='utf-8').read()
    except Exception: continue
    for name,val,pat in FACTS:
        for m in re.finditer(pat,t):
            try: v=float(m.group(1).replace('−','-'))
            except ValueError: continue
            if abs(v-float(val))<1e-6: continue
            ctx=t[max(0,m.start()-50):m.end()+50].replace('\n',' ')
            if re.search(SKIPCTX,ctx): continue
            if name=='操作力目標' and re.search('首振り',ctx): continue   # 首振りの目標は別(20N)
            (warns if f.startswith(HIST) else fails).append(f'{f}: {name} 正規={n(val)} だが記述={n(v)}: …{ctx}…')
# リンク切れ(md 相対リンク)
for f in files:
    if not f.endswith('.md'): continue
    t=open(f'{R}/{f}',encoding='utf-8').read(); d=os.path.dirname(f)
    for m in re.finditer(r'\]\((?!https?:|#|mailto:)([^)\s#]*[./][^)\s#]*)',t):
        p=os.path.normpath(os.path.join(R,d,m.group(1)))
        if not os.path.exists(p): fails.append(f'{f}: リンク切れ {m.group(1)}')
# spec 内部の自己矛盾
if S['pod']['total_t']!=S['dome']['total_t']: fails.append('spec.pod.total_t != dome.total_t')
dh=re.search(r'z\s*=\s*(\d+)',H.get('doc',''))
if dh and float(dh.group(1))!=H['axis_z_from_glass']: fails.append(f"spec.hinge.doc の z={dh.group(1)} が axis_z_from_glass={H['axis_z_from_glass']} と不一致")
print(f'FAIL {len(fails)} / WARN {len(warns)}')
for x in fails: print('[FAIL]',x)
for x in warns[:60]: print('[WARN]',x)
sys.exit(1 if fails else 0)
