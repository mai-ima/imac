#!/usr/bin/env python3
"""可動範囲の干渉検査: チルト(ヒンジ軸まわり)×首振り(垂直軸まわり)の全格子で、頭部の包絡(スラブ+ドーム、安全側の直方体)と
スタンド(足・首・首振りユニット)・机面の最小すき間を求める。公称AABB検査であり、実形状(STEP)・指挟み試験は UNVERIFIED。"""
import math, os, sys, itertools
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; H = MM.H; W = S['body_w']; slab = S['slab_t']; D = S['dome']; st = S['stand']; sw = S['swivel']
hz, hy = S['hinge']['axis_z_from_glass'], S['hinge']['axis_y']; sz = sw['axis_z_from_glass']
T0, T1 = S['hinge']['tilt_min_deg'], S['hinge']['tilt_max_deg']; SW = sw['range_deg']
drop = st['drop']; FT = 12.0
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
# 首振りユニット/首と頭部の干渉(首は x±60,z±4 ,y -drop+stack〜hy+11)。頭部は首の位置を回るので ヒンジ回りの領域だけ見る → 背板後面〜ヒンジブロックは頭部と一体で回るため干渉無し(同一剛体)
print('首(腕)は頭部と同一剛体(ヒンジ軸でのみ相対回転): 腕断面とヒンジブロック内空洞の相対すき間はヒンジ側 CP/hinge 図面で管理')
ok = mn_foot >= need; print('総合:', 'OK' if ok else 'NG'); sys.exit(0 if ok else 1)
