#!/usr/bin/env python3
"""加工成立性(DFM)の簡易ゲート: 薄板への溝/ポケットの残肉 ≥ min_residual を custom_parts.json の dfm 値で検査(CP-07)。
dfm 未定義の部品は検査対象外(未検証として列挙)。残肉が足りなければ終了コード1。"""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f'{R}/model/custom_parts.json')); bad = 0; none = []
for x in d['parts']:
    m = x.get('dfm')
    if not m: none.append(x['id']); continue
    for nm, t, dep in (('ガスケット溝(縁フランジ)', m['flange_t'], m['groove_depth']), ('磁石ポケット(局所ボス)', m['magnet_boss_t'], m['magnet_pocket_depth']),
                       ('[参考]溝を薄板t%.1fに直接彫った場合' % m['sheet_t'], m['sheet_t'], m['groove_depth']), ('[参考]磁石を薄板に直接彫った場合', m['sheet_t'], m['magnet_pocket_depth'])):
        res = t - dep; ref = nm.startswith('[参考]'); ok = res >= m['min_residual']
        print(f"{x['id']} {nm}: 板厚{t} - 深さ{dep} = 残肉{res:.1f}mm (≥{m['min_residual']}) [{'OK' if ok else ('参考NG=この方法は不可' if ref else 'NG')}]")
        if not ref and not ok: bad += 1
print('dfm未定義(未検証)の部品:', ', '.join(none))
sys.exit(1 if bad else 0)
