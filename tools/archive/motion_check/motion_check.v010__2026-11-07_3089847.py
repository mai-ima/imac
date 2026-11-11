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
# ---- ネック(固定側)と頭部(ヒンジ軸まわりに回転)の掃引干渉: yz断面のSAT(貫入深さ)。寸法は model/spec.json の neck/hinge/balance から導出(部品ごとの手入力を避ける) ----
import json
BAL = json.load(open(f'{R}/model/balance.json')); BE, BS = BAL['e'], BAL['s']; ZC = -hz; HY = hy; NK = S['neck']; SY = -drop + sw['stack_h']; SYS = SY + NK['base_t']
PO = 29.0; cosd = lambda a: math.cos(math.radians(a))
def rect(x0, x1, y0, y1, z0, z1): return (x0, x1, [(y0, z0), (y1, z0), (y1, z1), (y0, z1)])
def circ(x0, x1, r, n=32, cy=None, cz=None):      # 外接多角形(実円より小さくならない)
    rr = r / math.cos(math.pi / n); return (x0, x1, [(HY + rr * math.cos(2 * math.pi * k / n + math.pi / n), ZC + rr * math.sin(2 * math.pi * k / n + math.pi / n)) for k in range(n)])
px0, px1 = NK['pad_x']
HEAD = {'スラブ(前面ガラス+パネル+チン)': rect(-W / 2, W / 2, 0, H, -slab, 0),
        'ヒンジ底板': rect(-75, 75, 0, 22, ZC - 20 + 0.0 - 7 + 0, ZC + 0), }
HEAD = {'スラブ(前面ガラス+パネル+チン)': rect(-W / 2, W / 2, 0, H, -slab, 0), 'ヒンジ底板': rect(-75, 75, 0, 22, -27, -25), 'ヒンジ左側板': rect(-75, -69, 0, 22, -61, -27), 'ヒンジ右側板': rect(69, 75, 0, 22, -61, -27),
        'ヒンジカバー': rect(-69, 69, 0, 22, -61, -59), '裏当て板': rect(-70, 70, 0, 22, -23, -20), '補強板': rect(-72, 72, 0, 22, -20, -16),
        '尾部レバー左': rect(-29, -24, HY - NK['lever_len'], HY, ZC - NK['lever_w'] / 2, ZC + NK['lever_w'] / 2), '尾部レバー右': rect(24, 29, HY - NK['lever_len'], HY, ZC - NK['lever_w'] / 2, ZC + NK['lever_w'] / 2),
        }
BAL_CAMT = S['hinge']['balance_cam']['cam_t_mm']
# カム板(R9T-001: ヒンジブロック底面 yl=-10 に取付、x=±14, t6)。カム面=ローラ接触点軌跡(頭部座標 zl=-r sinψ, yl=-r cosψ, r=ρ(ψ)-ローラ半径)
CS = BAL['cam_surface_head_frame']      # 実カム面(頭部座標 zl,yl。ストッパ範囲±余長を含む)
for sx, nm in ((-14, '左'), (14, '右')):
    for i in range(len(CS) - 1):
        (_, z0, y0), (_, z1, y1) = CS[i], CS[i + 1]
        HEAD[f'カム板{nm}{i}'] = rect(sx - BAL_CAMT / 2, sx + BAL_CAMT / 2, HY + min(y0, y1), HY - 10, ZC + min(z0, z1), ZC + max(z0, z1))
NECK = {'ネック基台': rect(-NK['base_half_x'], NK['base_half_x'], SY, SYS, ZC + NK['base_z'][0], ZC + NK['base_z'][1]),
        '左側板(本体)': rect(-NK['side_x'][1], -NK['side_x'][0], SYS, NK['body_top'], ZC + NK['side_z'][0], ZC + NK['side_z'][1]), '右側板(本体)': rect(NK['side_x'][0], NK['side_x'][1], SYS, NK['body_top'], ZC + NK['side_z'][0], ZC + NK['side_z'][1]),
        '左ストリップ': rect(-NK['side_x'][1], -NK['side_x'][0], NK['body_top'], HY, ZC - NK['strip_w'] / 2, ZC + NK['strip_w'] / 2), '右ストリップ': rect(NK['side_x'][0], NK['side_x'][1], NK['body_top'], HY, ZC - NK['strip_w'] / 2, ZC + NK['strip_w'] / 2),
        '左軸ボス': circ(-NK['side_x'][1], -NK['side_x'][0], NK['boss_r']), '右軸ボス': circ(NK['side_x'][0], NK['side_x'][1], NK['boss_r']),
        '前ストッパ受けタブ': rect(NK['tab_x'][0], NK['tab_x'][1], NK['cover_top'], NK['tab_y_top'], ZC + NK['front_cover_z'][0], ZC + NK['front_cover_z'][1]),
        'タイプレート': rect(-NK['side_x'][0], NK['side_x'][0], NK['tie_y'][0], NK['tie_y'][1], ZC + NK['tie_z'][0], ZC + NK['tie_z'][1]),
        '前カバー': rect(-60, 60, SYS, NK['cover_top'], ZC + NK['front_cover_z'][0], ZC + NK['front_cover_z'][1]), '後カバー': rect(-60, 60, SYS, NK['cover_top'], ZC + NK['back_cover_z'][0], ZC + NK['back_cover_z'][1]),
        'ゴムパッド(+40°側)左': rect(-px1, -px0, NK['tab_y_top'] - 6, NK['tab_y_top'], ZC + NK['pad_up_z'][0], ZC + NK['pad_up_z'][1]),
        'ゴムパッド(+40°側)右': rect(px0, px1, NK['tab_y_top'] - 6, NK['tab_y_top'], ZC + NK['pad_up_z'][0], ZC + NK['pad_up_z'][1]),
        'ゴムパッド(-15°側)左': rect(-px1, -px0, HY - NK['lever_len'] * cosd(-15) - 3, HY - NK['lever_len'] * cosd(-15) + 3, ZC + NK['pad_dn_z'][0], ZC + NK['pad_dn_z'][1]),
        'ゴムパッド(-15°側)右': rect(px0, px1, HY - NK['lever_len'] * cosd(-15) - 3, HY - NK['lever_len'] * cosd(-15) + 3, ZC + NK['pad_dn_z'][0], ZC + NK['pad_dn_z'][1])}
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
def gap(P, Q):
    """凸多角形P,Qの最小距離(辺-点)。重なれば0。"""
    if pen(P, Q) > 0: return 0.0
    def pd(p, a, b):
        ax, ay = a; bx, by = b; px, py = p; dx, dy = bx - ax, by - ay; t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1))); return math.hypot(px - ax - t * dx, py - ay - t * dy)
    return min(min(pd(p, Q[i], Q[(i + 1) % len(Q)]) for i in range(len(Q))) for p in P) if False else min([min(pd(p, Q[i], Q[(i + 1) % len(Q)]) for i in range(len(Q))) for p in P] + [min(pd(q, P[i], P[(i + 1) % len(P)]) for i in range(len(P))) for q in Q])
worst = {}; tilts = [T0 + i * (T1 - T0) / 110 for i in range(111)]; STOP_HEAD = ('尾部レバー',); STOP_NECK = ('ゴムパッド',)
for hn, (hx0, hx1, hp) in HEAD.items():
    for nn, (nx0, nx1, np_) in NECK.items():
        if hx1 <= nx0 or nx1 <= hx0: continue
        for a in tilts:
            d = pen(rot(hp, a), np_)
            stop_pair = hn.startswith(STOP_HEAD) and nn.startswith(STOP_NECK)
            lim = (NK['pad_thick'] * 0.5 + 0.3) if stop_pair and (a <= T0 + 2.5 or a >= T1 - 2.5) else 0.05      # ストッパはゴムの圧縮代1.2mmまで(端のみ)
            if d > lim: worst[(hn, nn)] = max(worst.get((hn, nn), 0), d)
for (hn, nn), d in sorted(worst.items(), key=lambda kv: -kv[1])[:14]: print(f'[NG ] 掃引干渉 {hn} × {nn}: 最大貫入 {d:.1f}mm'); bad += 1
# ストッパが両端で必ず当たること(辺-点距離): 端(T0/T1)で貫入0〜パッド厚の50% または 距離≦0.3mm でなければ NG(ストッパが効かない)
for lab, a, nm in (('-15°端', T0, 'ゴムパッド(-15°側)右'), ('+40°端', T1, 'ゴムパッド(+40°側)右')):
    pin = rot(HEAD['尾部レバー右'][2], a); q = NECK[nm][2]; d = pen(pin, q); g_ = gap(pin, q); eff = (0 < d <= NK['pad_thick'] * 0.5) or g_ <= 0.3
    print(f'ストッパ{lab}: 貫入 {d:.2f}mm / 最小距離 {g_:.2f}mm [{"OK(当たる)" if eff else "NG(当たらない/食い込み過大)"}]'); bad += 0 if eff else 1
# 動的な挟み込み域: 頭部スラブ下縁と前後カバー上端の距離を全角度で計算(4〜25mmは指が挟まる危険域 EN 349 → 蛇腹ブーツ等の保護が必要。未設計=U53)
pinch = []
for a in tilts:
    for nn in ('前カバー', '後カバー'):
        g_ = gap(rot(HEAD['スラブ(前面ガラス+パネル+チン)'][2], a), NECK[nn][2]); pinch.append((g_, a, nn))
gmin = min(pinch); gmax = max(pinch); in_zone = sorted({round(a) for g_, a, nn in pinch if 4 <= g_ <= 25}); BT = NK['boot']; lo, hi = BT['length_range_mm']
ok_boot = lo <= gmin[0] and gmax[0] <= hi
print(f'スラブ下縁-カバー上端のすき間 {gmin[0]:.1f}〜{gmax[0]:.1f}mm(最小: チルト{gmin[1]:+.0f}° {gmin[2]})。4〜25mmの挟み込み域に入る角度 {len(in_zone)}段階 → 蛇腹ブーツ(伸縮{lo}〜{hi}mm, spec.neck.boot)で隙間を塞ぐ設計 [{"OK(範囲内)" if ok_boot else "NG(ブーツの伸縮範囲外)"}]。ブーツの実特性・耐久・指進入試験は UNVERIFIED(U53)')
if not ok_boot: bad += 1
# ブーツのせん断: 頭部側取付点(ヒンジブロック下面中央)とネック側の縁中央の水平ずれ(チルト全域)。ブーツの許容せん断以内であること
shear = max(abs(rot([(0.0, ZC)], a)[0][1] - ZC + 0.0 if False else (ZC + (0 - HY) * -math.sin(math.radians(a)) * -1 if False else 0)) for a in tilts) if False else max(abs((lambda dy: dy * math.sin(math.radians(a)))(0 - HY)) for a in tilts)
print(f'ブーツのせん断(上下取付面の水平ずれ) 最大 {shear:.1f}mm ≦ 許容 {BT["shear_mm"]}mm [{"OK" if shear <= BT["shear_mm"] else "NG"}]'); bad += 0 if shear <= BT['shear_mm'] else 1
if gmin[0] <= 0.05: print('[NG ] スラブ下縁がカバーに接触'); bad += 1
# バランサ下側部品(アンカー座・調整ねじ・ブリッジ)が基台に食い込まない: 最下点 ≥ 基台上面+2mm、かつ側板間に収まる
low = HY - BS; ok_low = low >= SYS - 1e-6     # アンカー=クレビス受け(耳R6)が基台上面に着座(ボルト固定)。調整ねじ等はばね端金物(balance_end_hw_mm)の内側
print(f'バランサ最下点(ばね座下面) y={low:.0f}mm / 基台上面 y={SYS:.0f}mm [{"OK" if ok_low else "NG(基台に干渉)"}]'); bad += 0 if ok_low else 1
# PE編組の長さ: 可動範囲での端間距離の最大 + 余長 ≦ 編組長(model/pe_braids.json)
PE = json.load(open(f'{R}/model/pe_braids.json'))
a_sw = 0.0; A0 = (NK['side_x'][1], 0.0); Bp = (0.0, -75.0)      # 水平面: ネック側(回転)端 r≈62、足側(固定)端 r≈75(背面側)。首振り±SWで端間距離が最大になる角度を探索
dmax_sw = max(math.hypot(62 * math.sin(math.radians(s_)) - 75 * math.sin(math.radians(sg)), 62 * math.cos(math.radians(s_)) - 75 * math.cos(math.radians(sg))) for s_ in (-SW, 0, SW) for sg in (0,)) + 0
pa = lambda a_: rot([(HY - 20, ZC - 20)], a_)[0]; pb = (HY - 10, ZC - 5)      # ヒンジ編組: 頭部側端(回転)/ネック側端(固定)の代表点
dmax_h = max(math.hypot(pa(a_)[0] - pb[0], pa(a_)[1] - pb[1]) for a_ in tilts)
for nm, dm, L in (('首振り編組', dmax_sw + 62 * 0.0, PE['swivel']['length_mm']), ('ヒンジ編組', dmax_h, PE['hinge']['length_mm'])):
    ok_ = L >= dm + PE['min_slack_mm']; print(f'{nm}: 最大端間距離 {dm:.0f}mm + 余長{PE["min_slack_mm"]}mm ≦ 編組長 {L}mm [{"OK" if ok_ else "NG"}]'); bad += 0 if ok_ else 1
if bad: print('総合: NG'); sys.exit(1)
ok = mn_foot >= need; print('総合:', 'OK(断面近似。実形状・指挟み保護・疲労は UNVERIFIED。挟み込みはWARN)' if ok else 'NG'); sys.exit(0 if ok else 1)
