#!/usr/bin/env python3
"""可動範囲の干渉検査: チルト(ヒンジ軸まわり)×首振り(垂直軸まわり)の全格子で、頭部の包絡(スラブ+ドーム、安全側の直方体)と
スタンド(足・首・首振りユニット)・机面の最小すき間を求める。公称AABB検査であり、実形状(STEP)・指挟み試験は UNVERIFIED。"""
import math, os, sys, itertools
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; H = MM.H; W = S['body_w']; slab = S['slab_t']; D = S['dome']; st = S['stand']; sw = S['swivel']
hz, hy = S['hinge']['axis_z_from_glass'], S['hinge']['axis_y']; sz = sw['axis_z_from_glass']
T0, T1 = S['hinge']['tilt_min_deg'], S['hinge']['tilt_max_deg']; SW = sw['range_deg']
drop = st['drop']; FT = 12.0; bad = 0
# 頭部包絡(座標: x左右, y下端=0で上, z前面ガラス=0で背面+): スラブ全幅 + ドーム(縁から最大厚)
def box(x0, x1, y0, y1, z0, z1): return list(itertools.product((x0, x1), (y0, y1), (z0, z1)))
head = box(-W / 2, W / 2, 0, H, 0, slab) + box(-(W / 2 - D['inset_left_right']), W / 2 - D['inset_left_right'], D['inset_bottom'], H - D['inset_top'], slab, D['total_t'])
def place(p, tilt, swv):
    x, y, z = p; a = math.radians(tilt)
    dy, dz = y - hy, z - hz
    # チルト: 上端が後ろへ(+)。軸x。 y' = dy·cos a - dz·sin a, z' = dz·cos a + dy·sin a
    y2 = hy + dy * math.cos(a) - dz * math.sin(a); z2 = hz + dz * math.cos(a) + dy * math.sin(a)
    th = math.radians(swv); r = z2 - sz
    return x * math.cos(th) + r * math.sin(th), y2, sz - x * math.sin(th) + r * math.cos(th)    # 垂直軸まわり
floor_y = -drop - FT           # 机面
foot_top = -drop
bad = 0; mn_foot = 1e9; mn_desk = 1e9; arg = None
for tilt in [T0 + i * (T1 - T0) / 11 for i in range(12)]:
    for swv in [-SW + i * (2 * SW) / 12 for i in range(13)]:
        low = min(place(p, tilt, swv)[1] for p in head)
        # 足上面(ヘッドが足の上方を回るので縦方向のすき間=最低点の高さ-足上面)。足の平面範囲外でも机面で保守的に判定
        mn_foot = min(mn_foot, low - foot_top)
        if low - foot_top < mn_foot + 1e-9: arg = (tilt, swv)
        mn_desk = min(mn_desk, low - floor_y)
need = 30.0     # 指が入る/物が挟まる最小すき間(足上面側): 30mm以上を設計基準(要: 指挟み試験)
print(f'頭部最低点の足上面からの最小すき間 {mn_foot:.1f}mm (チルト{arg[0]:+.0f}° 首振り{arg[1]:+.0f}°)、机面から {mn_desk:.1f}mm。設計基準 ≥{need}mm')
# ---- ネック(固定側)と頭部(ヒンジ軸まわりに回転)の掃引干渉: yz断面のSAT(貫入深さ)。x範囲が重ならない組は除外 ----
import json
BAL = json.load(open(f'{R}/model/balance.json')); BE = BAL['e']; ZC = -hz; HY = hy; SY = -drop + sw['stack_h']
def rect(x0, x1, y0, y1, z0, z1): return (x0, x1, [(y0, z0), (y1, z0), (y1, z1), (y0, z1)])
HEAD = {'ヒンジ底板': rect(-75, 75, 0, 22, -27, -25), 'ヒンジ左側板': rect(-75, -69, 0, 22, -61, -27), 'ヒンジ右側板': rect(69, 75, 0, 22, -61, -27),
        'ヒンジカバー': rect(-69, 69, 0, 22, -61, -59), '裏当て板': rect(-70, 70, 0, 22, -23, -20), '補強板': rect(-72, 72, 0, 22, -20, -16),
        '尾部レバー左': rect(-28, -24, HY - BE - 6, HY, ZC - 3, ZC + 3), '尾部レバー右': rect(24, 28, HY - BE - 6, HY, ZC - 3, ZC + 3),
        'ストッパピン左': rect(-32, -20, HY - 29 - 2.5, HY - 29 + 2.5, ZC - 2.5, ZC + 2.5), 'ストッパピン右': rect(20, 32, HY - 29 - 2.5, HY - 29 + 2.5, ZC - 2.5, ZC + 2.5)}
def octa(x0, x1, r=11):
    return (x0, x1, [(HY + r * math.cos(math.radians(k * 45 + 22.5)), ZC + r * math.sin(math.radians(k * 45 + 22.5))) for k in range(8)])
NECK = {'左側板(本体)': rect(-62, -56, SY, -16, ZC - 17, ZC + 11), '右側板(本体)': rect(56, 62, SY, -16, ZC - 17, ZC + 11),
        '左ストリップ': rect(-62, -56, -16, HY, ZC - 4, ZC + 4), '右ストリップ': rect(56, 62, -16, HY, ZC - 4, ZC + 4), '左軸ボス': octa(-62, -56), '右軸ボス': octa(56, 62),
        '前カバー': rect(-60, 60, SY, -3, ZC + 24, ZC + 26), '後カバー': rect(-60, 60, SY, -3, ZC - 26, ZC - 24),
        'バンパ(+40°側)左': rect(-32, -28.5, HY - 29 * math.cos(math.radians(40)) - 4, HY - 29 * math.cos(math.radians(40)) + 4, ZC + 21.4, ZC + 23.8),
        'バンパ(+40°側)右': rect(28.5, 32, HY - 29 * math.cos(math.radians(40)) - 4, HY - 29 * math.cos(math.radians(40)) + 4, ZC + 21.4, ZC + 23.8),
        '受けポスト(-15°側)左': rect(-32, -28.5, HY - 29 * math.cos(math.radians(-15)) - 4, HY - 29 * math.cos(math.radians(-15)) + 2, ZC - 15.5, ZC - 9.5),
        '受けポスト(-15°側)右': rect(28.5, 32, HY - 29 * math.cos(math.radians(-15)) - 4, HY - 29 * math.cos(math.radians(-15)) + 2, ZC - 15.5, ZC - 9.5)}
def rot(poly, a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); out = []
    for (y, z) in poly:
        dy, dz = y - HY, z - ZC; out.append((HY + dy * c + dz * s_, ZC + dz * c - dy * s_))
    return out
def pen(P, Q):
    """凸多角形P,Qの最小貫入深さ(重なり無しなら0)。SAT。"""
    best = 1e9
    for poly in (P, Q):
        for i in range(len(poly)):
            (y1, z1), (y2, z2) = poly[i], poly[(i + 1) % len(poly)]; ny, nz = z2 - z1, -(y2 - y1); L = math.hypot(ny, nz)
            if L == 0: continue
            ny, nz = ny / L, nz / L
            pa = [y * ny + z * nz for y, z in P]; pb = [y * ny + z * nz for y, z in Q]
            o = min(max(pa), max(pb)) - max(min(pa), min(pb))
            if o <= 0: return 0.0
            best = min(best, o)
    return best
worst = {}
tilts = [T0 + i * (T1 - T0) / 110 for i in range(111)]
for hn, (hx0, hx1, hp) in HEAD.items():
    for nn, (nx0, nx1, np_) in NECK.items():
        if hx1 <= nx0 or nx1 <= hx0: continue
        for a in tilts:
            d = pen(rot(hp, a), np_)
            stop_pair = ('ストッパピン' in hn and ('バンパ' in nn or '受けポスト' in nn))
            lim = 1.2 if stop_pair and (a <= T0 + 2.5 or a >= T1 - 2.5) else 0.05      # ゴムの圧縮代1.2mmまで許容(端のみ)
            if d > lim: worst[(hn, nn)] = max(worst.get((hn, nn), 0), d)
for (hn, nn), d in sorted(worst.items(), key=lambda kv: -kv[1])[:12]: print(f'[NG ] 掃引干渉 {hn} × {nn}: 最大貫入 {d:.1f}mm'); bad += 1
# ストッパが実際に両端で効くか(ピンとバンパ/ポストの距離が端で ≤1mm 以内に接触するか)
for lab, a, nm in (('-15°端', T0, '受けポスト(-15°側)'), ('+40°端', T1, 'バンパ(+40°側)')):
    pin = rot(HEAD['ストッパピン右'][2], a); q = NECK[nm + '右'][2]
    d = pen(pin, q); gap = min(math.hypot(py - qy, pz - qz) for py, pz in pin for qy, qz in q)
    print(f'ストッパ{lab}: 貫入 {d:.2f}mm / 角点間距離 {gap:.1f}mm (接触=貫入0〜1mm か、角点間距離で目視確認)')
print('ヒンジ側の動的すき間: 頭部ヒンジ側板(x±69〜75)とネック側板(x±56〜62)のx方向すき間=7mm(4〜25mmの挟み込み域。側面ガード/指挟み試験が必要: U53)')
if bad: print('総合: NG(掃引干渉あり)'); sys.exit(1)
ok = mn_foot >= need; print('総合:', 'OK(AABB/断面近似。実形状・指挟み試験はUNVERIFIED)' if ok else 'NG'); sys.exit(0 if ok else 1)
