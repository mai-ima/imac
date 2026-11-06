#!/usr/bin/env python3
"""転倒安定性(v9: チルト×首振りの全格子)。質量/重心は tools/massmodel.py(layout由来, 推定)。
頭部重心を ヒンジ軸まわりチルト → 垂直首振り軸まわりスイベル の順に動かし、足(長方形)に対する重心の余裕を方向別に求める。
支持多角形=4個のゴム脚の外接長方形、重心余裕10mmを差し引く。上端(地面から約0.5m)を水平に押して転倒する力 F = m·g·(重心から足縁までの距離)/上端高さ。目標: 前≥25N・後≥20N・左右≥30N。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; hm, cz, cy, _ = MM.head_cg(); ms = MM.stand_mass()
hz, hy = S['hinge']['axis_z_from_glass'], S['hinge']['axis_y']; st = S['stand']; sw = S['swivel']
T0, T1 = S['hinge']['tilt_min_deg'], S['hinge']['tilt_max_deg']; SW = sw['range_deg']; sz = sw['axis_z_from_glass']
FOOT_IN = 24 - 10      # ゴム脚(Ø20)の外縁は足の縁から14mm内側(脚中心は縁から24mm)。支持多角形=4脚の外接長方形
CG_TOL = 10.0          # 重心位置の不確かさ[mm](質量/重心は推定。実測まで安全側に余裕として差し引く)
front = hz - st['foot_front'] + FOOT_IN; back = hz + st['foot_back'] - FOOT_IN; half_w = st['foot_w'] / 2 - FOOT_IN
ground_y = -st['drop'] - 12; top_h = (MM.H - ground_y) / 1000.0
mt = hm + ms; zs = (front + back) / 2
print(f"ディスプレイ部 {hm:.1f}kg + スタンド(首振りユニット込み) {ms:.1f}kg = {mt:.1f}kg / 頭部重心 z={cz:.0f} y={cy:.0f} / ヒンジ軸 z={hz} y={hy} / 首振り軸 z={sz} / 足 z={front:.0f}〜{back:.0f} 幅{st['foot_w']} / 上端高さ {top_h*1000:.0f}mm")
GOAL = dict(front=25, back=20, side=30)
worst = {'front': 1e9, 'back': 1e9, 'side': 1e9}; arg = {}; min_tip_deg = 1e9; min_cord = 1e9
h_cg = (cy - ground_y) / 1000.0     # 頭部重心の机面からの高さ[m](全体重心の高さは足の質量で少し下がるため安全側)
tilts = [T0 + i * (T1 - T0) / 11 for i in range(12)]; swivs = [-SW + i * (2 * SW) / 12 for i in range(13)]
def cg(tilt, swv):
    a = math.radians(tilt); dz = cz - hz; dy = cy - hy
    zc = hz + dz * math.cos(a) + dy * math.sin(a)                  # チルト後の頭部重心z(後ろへ倒すと増える)
    r = zc - sz; th = math.radians(swv)
    x, z = r * math.sin(th), sz + r * math.cos(th)                 # 垂直軸まわりスイベル(軸は足内、スタンド側質量は軸上=足中央付近)
    tx = (hm * x) / mt; tz = (hm * z + ms * zs) / mt
    return tx, tz
print('チルト\\首振り  ' + ' '.join(f'{s:+5.0f}' for s in swivs[::2]) + '   (最小転倒力[N]: 前/後/横の最小)')
for t in tilts:
    row = []
    for s_ in swivs:
        tx, tz = cg(t, s_)
        mf, mb = tz - front - CG_TOL, back - tz - CG_TOL; ml = half_w - abs(tx) - CG_TOL
        Ff, Fb, Fs = (mt * 9.81 * m / 1000 / top_h for m in (mf, mb, ml))
        for k, v in (('front', Ff), ('back', Fb), ('side', Fs)):
            if v < worst[k]: worst[k] = v; arg[k] = (t, s_)
        min_tip_deg = min(min_tip_deg, math.degrees(math.atan(min(mf, mb, ml) / 1000.0 / h_cg)))
        min_cord = min(min_cord, mt * 9.81 * min(mf, mb, ml) / 1000.0 / ((60 - ground_y) / 1000.0))      # 背面インレット(下端から約60mm)を横に引く力
        row.append(min(Ff / GOAL['front'], Fb / GOAL['back'], Fs / GOAL['side']))
    print(f'{t:+6.1f}°      ' + ' '.join(f'{x*100:5.0f}' for x in row[::2]) + '  (目標比%)')
ok = True
for k, lbl in (('front', '前'), ('back', '後'), ('side', '横')):
    good = worst[k] >= GOAL[k]; ok &= good
    print(f"最悪 {lbl}: {worst[k]:.0f}N(目標≥{GOAL[k]}N) @チルト{arg[k][0]:+.0f}° 首振り{arg[k][1]:+.0f}° [{'OK' if good else 'NG'}]")
ok &= min_tip_deg >= 10.0
print(f'傾斜安定(IEC 62368-1 の10°傾斜に相当): 全格子の最小転倒角 {min_tip_deg:.1f}° (≥10° で [{"OK" if min_tip_deg>=10 else "NG"}])。ACコードを横に引いた場合の転倒力 最小≈{min_cord:.0f}N(情報。コード固定クランプは U54)')
print('総合:', 'OK(全格子で目標達成。質量/重心は推定=UNVERIFIED)' if ok else 'NG(目標未達: 足寸法/バラスト/首振り範囲の見直しが必要)')
sys.exit(0 if ok else 1)
