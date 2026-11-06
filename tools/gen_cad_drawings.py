#!/usr/bin/env python3
"""実形状(cadquery)から正投影(第三角法)の図面を生成する: 外部設計図(ARCTIC 2D図面/ASUSマニュアル図)と同水準=多面図+寸法+部品表+題名欄。
出力: drawings/v10/*.svg。実行: /tmp/bl/.venv/bin/python tools/gen_cad_drawings.py。現状の対象: ポンプ(公式図と照合), スタンド一式。順次拡大。
注意: 形状はモデル値(PRELIMINARY)。ポンプの外形/高さは公式図の読み取り値(±数mm)で、図中に出典を明記する。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import cadquery as cq, cadviews as CV, drawlib as DL
S = json.load(open(f'{R}/model/spec.json')); OUT = f'{R}/drawings/v10'; os.makedirs(OUT, exist_ok=True)
def sheet(path, title, num, body, scale='1:1', material='-', finish='-', note=''):
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="Helvetica,Arial,sans-serif">'] + DL.frame(title, num, scale=scale, material=material, finish=finish, note=note) + body + ['</svg>']
    open(path, 'w', encoding='utf-8').write('\n'.join(o)); print('wrote', os.path.relpath(path, R))
def view(shape, vdir, xdir, ox, oy, s, label, hidden=True):
    P = CV.project(shape, vdir, xdir); x0, y0, x1, y1 = P['bbox']
    return P, [CV.place(P, ox, oy, s, hidden), DL.txt(ox + s * (x0 + x1) / 2, oy - s * y0 + 8, label, 3.2, 'middle', 'bold')]
def dimh(P, ox, oy, s, label, off=8, y_edge='bottom'):
    x0, y0, x1, y1 = P['bbox']; return DL.dim_h(ox + s * x0, ox + s * x1, oy - s * y0 + 2, label, off)
def dimv(P, ox, oy, s, label, off=-8, x_edge='left'):
    x0, y0, x1, y1 = P['bbox']; return DL.dim_v(oy - s * y1, oy - s * y0, ox + s * (x0 if x_edge == 'left' else x1), label, off)

# ---------------- ポンプ(ARCTIC Liquid Freezer III Pro 240。公式2D図面 ACFRE00178A〜189A共通 p.1 を直接確認した寸法・構造に基づく) ----------------
def pump():
    P = json.load(open(f'{R}/model/pump.json'))
    def cyl(d, z0, z1, cx=0, cy=0): return cq.Workplane('XY').workplane(offset=z0).center(cx, cy).circle(d / 2).extrude(z1 - z0)
    def box(x, y, z): return cq.Workplane('XY').box(x[1] - x[0], y[1] - y[0], z[1] - z[0], centered=False).translate((x[0], y[0], z[0]))
    cpl = P['coldplate']; sh = box(cpl['x'], cpl['y'], cpl['z']).union(box((-24, 24), (-24, 24), P['base']['z']))
    for k in range(P['cage']['ribs']):                                             # VRMファンを囲むアーチ状リブ(開放ケージ)
        a = math.radians(k * 360 / P['cage']['ribs']); z0, z1 = P['cage']['z']; sh = sh.union(box((P['cage']['r'] * math.cos(a) - 2, P['cage']['r'] * math.cos(a) + 2), (P['cage']['r'] * math.sin(a) - 2, P['cage']['r'] * math.sin(a) + 2), (z0, z1)))
    sh = sh.union(cyl(P['cap_lip']['d'], *P['cap_lip']['z'])).union(cyl(P['cap_top']['d'], *P['cap_top']['z']))
    sh = sh.union(box(P['housing_body']['x'], P['housing_body']['y'], P['housing_body']['z'])).union(box(P['elbow']['x'], P['elbow']['y'], P['elbow']['z']))
    for sy in P['stub_y']: sh = sh.union(cyl(P['nut']['d'], *P['nut']['z'], P['stub_x'], sy)).union(cyl(P['stub']['d'], *P['stub']['z'], P['stub_x'], sy))
    return sh.union(cyl(P['vrm_fan']['d'], *P['vrm_fan']['z']))
def sheet_pump():
    shp = pump(); s = 0.8; body = []
    TX, TY = 100, 62          # 上面図の中心(=ポンプ円盤中心)
    FX, FY = 100, 190         # 正面図の原点(円盤中心, コールドプレート底面)
    SX, BX_ = 230, 335        # 側面・背面の原点x
    Pt, g = view(shp, (0, 0, 1), (1, 0, 0), TX, TY, s, '上面 TOP', False); body += g
    Pf, g = view(shp, (0, -1, 0), (1, 0, 0), FX, FY, s, '正面 FRONT'); body += g
    Ps, g = view(shp, (1, 0, 0), (0, 1, 0), SX, FY, s, '側面 SIDE'); body += g
    Pb, g = view(shp, (0, 1, 0), (-1, 0, 0), BX_, FY, s, '背面 BACK'); body += g
    Pu, g = view(shp, (0, 0, -1), (1, 0, 0), SX + 20, TY, s, '下面 BOTTOM', False); body += g
    # 寸法: 公式図と同じ 3 寸法(Ø91.0 / 108.47 / 68.5)+ 追加(キャップ上面55, スタブ先端81)
    x0, y0, x1, y1 = Pf['bbox']; body += DL.dim_h(FX + s * (-45.5), FX + s * 45.5, FY + 2, 'Ø91.0', 14)
    x0, y0, x1, y1 = Pt['bbox']; body += DL.dim_h(TX + s * (-45.5), TX + s * x1, TY - s * y0 + 2, f'{(x1+45.5):.2f} 全長(公式 108.47)', 10)
    xs0, ys0, xs1, ys1 = Ps['bbox']; body += DL.dim_v(FY - s * 68.5, FY, SX + s * xs0, '68.5', -10) + DL.dim_v(FY - s * 55, FY, SX + s * xs0, '55', -20) + DL.dim_v(FY - s * ys1, FY, SX + s * xs1, f'{ys1:.1f}', 12)
    body += [DL.txt(25, 226, '出典: ARCTIC LF III Pro 240/280/360/420 A-RGB 2D Drawing(P/N ACFRE00178A〜189A, Rev 9/7/2025)。', 2.4), DL.txt(25, 230, 'Ø91.0・全長108.47・高さ68.5(ナット上端)は公式値。68.5は基板側(コールドプレート底面)基準。', 2.4),
             DL.txt(25, 234, 'ケージ/VRMファン/コールドプレート/スタブ径は図面からの読み取り(±3mm)。未確認: U57(ホース曲げ), U58(VRMファン径)。', 2.4), DL.txt(25, 238, 'ホース口は上面から垂直(公式図)。ホース: φ12.4/ID6.0/450mm。', 2.4)]
    sheet(f'{OUT}/D01_pump_LF3Pro.svg', 'CPUクーラー ポンプ(ARCTIC Liquid Freezer III Pro)', 'D01', body, '1:1.25', 'ARCTIC 市販品(参考図)', '-', '市販品の参考図。公式2D図面と同じ構成(上面/正面/側面/背面/下面)')

# ---------------- スタンド一式(足・首振り・ネック・ヒンジ・バランサ)。座標: x右, y上(本体下端=0), z=前面ガラス0・背面が負 ----------------
def stand_solids():
    S_ = S; st, sw, nk, H_ = S_['stand'], S_['swivel'], S_['neck'], S_['hinge']; DROP = st['drop']; ZC = -H_['axis_z_from_glass']; HY = H_['axis_y']; BAL = json.load(open(f'{R}/model/balance.json'))
    def box(x0, x1, y0, y1, z0, z1): return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    def cylY(d, y0, y1, cx=0, cz=ZC): return cq.Workplane('XZ').workplane(offset=-y1).center(cx, cz).circle(d / 2).extrude(y1 - y0)       # Y軸方向の円柱(XZ平面は法線-Y)
    def cylX(d, x0, x1, cy, cz): return cq.Workplane('YZ').workplane(offset=x0).center(cy, cz).circle(d / 2).extrude(x1 - x0)
    P = {}
    P['足'] = box(-st['foot_w'] / 2, st['foot_w'] / 2, -DROP - 12, -DROP, ZC - st['foot_back'], ZC + st['foot_front'])
    P['ステータ板'] = cylY(2 * sw['stator_r'], -DROP, -DROP + 6); P['クロスローラ軸受'] = cylY(sw['bearing_od'], -DROP + 6, -DROP + 18); P['ロータ板'] = cylY(2 * sw['rotor_r'], -DROP + 19, -DROP + 25)
    SY = -DROP + sw['stack_h']; SYS = SY + nk['base_t']; bz0, bz1 = nk['base_z']
    P['ネック基台'] = box(-nk['base_half_x'], nk['base_half_x'], SY, SYS, ZC + bz0, ZC + bz1)
    side = None
    for sx0, sx1 in ((-nk['side_x'][1], -nk['side_x'][0]), (nk['side_x'][0], nk['side_x'][1])):
        body = box(sx0, sx1, SYS, nk['body_top'], ZC + nk['side_z'][0], ZC + nk['side_z'][1]).union(box(sx0, sx1, nk['body_top'], HY, ZC - nk['strip_w'] / 2, ZC + nk['strip_w'] / 2)).union(cylX(2 * nk['boss_r'], sx0, sx1, HY, ZC))
        side = body if side is None else side.union(body)
    P['ネック側板'] = side
    P['タイプレート/前後カバー/タブ'] = box(-nk['side_x'][0], nk['side_x'][0], nk['tie_y'][0], nk['tie_y'][1], ZC + nk['tie_z'][0], ZC + nk['tie_z'][1]).union(box(-60, 60, SYS, nk['cover_top'], ZC + nk['front_cover_z'][0], ZC + nk['front_cover_z'][1])).union(box(-60, 60, SYS, nk['cover_top'], ZC + nk['back_cover_z'][0], ZC + nk['back_cover_z'][1])).union(box(nk['tab_x'][0], nk['tab_x'][1], nk['cover_top'], nk['tab_y_top'], ZC + nk['front_cover_z'][0], ZC + nk['front_cover_z'][1]))
    P['ヒンジ軸Ø12'] = cylX(12, -75, 75, HY, ZC)
    lev = None
    for sx in (-1, 1):
        l_ = box(sx * 26.5 - nk['lever_t'] / 2, sx * 26.5 + nk['lever_t'] / 2, HY - nk['lever_len'], HY, ZC - nk['lever_w'] / 2, ZC + nk['lever_w'] / 2)
        sp = cylY(16, HY - BAL['s'], HY - BAL['e'], sx * 14, ZC); lev = l_.union(sp) if lev is None else lev.union(l_).union(sp)
    P['尾部レバー+ダイスプリング'] = lev
    for sx in (-1, 1): P['摩擦ヒンジ'] = cylX(22, sx * 45 - 11, sx * 45 + 11, HY, ZC) if '摩擦ヒンジ' not in P else P['摩擦ヒンジ'].union(cylX(22, sx * 45 - 11, sx * 45 + 11, HY, ZC))
    # 頭部(下部のみ表示): スラブ下端の80mm+ヒンジブロック
    P['頭部(下部80mm・幅は切断表示)'] = box(-110, 110, 0, 80, -S_['slab_t'], 0).union(box(-75, 75, 0, 22, -61, -25))
    return P
def sheet_stand():
    P = stand_solids(); allp = None
    for v in P.values(): allp = v if allp is None else allp.union(v)
    st, sw, nk, H_ = S['stand'], S['swivel'], S['neck'], S['hinge']; DROP = st['drop']; ZC = -H_['axis_z_from_glass']; HY = H_['axis_y']; s = 0.42; body = []
    FX, FY = 100, 78; SXo, SYo = 270, 78; TXo, TYo = 105, 215       # 正面(左上) / 側面(右上)
    Pf, g = view(allp, (0, 0, 1), (1, 0, 0), FX, FY, s, '正面 FRONT', False); body += g
    Ps, g = view(allp, (1, 0, 0), (0, 0, -1), SXo, FY, s, '側面 SIDE(前面ガラス=左)', False); body += g
    half = allp.intersect(cq.Workplane('XY').box(400, 800, 800, centered=False).translate((-400, -400, -400)))      # x<=0 の半断面
    Pa, g = view(half, (1, 0, 0), (0, 0, -1), 150, 188, s, '断面 A-A(x=0 半割り)', False); body += g
    # 寸法
    x0, y0, x1, y1 = Pf['bbox']
    body += DL.dim_h(FX + s * (-st['foot_w'] / 2), FX + s * (st['foot_w'] / 2), FY - s * (-DROP - 12) + 2, f"足 幅 {st['foot_w']}", 10)
    body += DL.dim_v(FY - s * HY, FY - s * (-DROP - 12), FX + s * (-st['foot_w'] / 2), f"ヒンジ軸〜足底 {DROP+12+HY}", -12)
    body += DL.dim_v(FY - s * (-DROP + sw['stack_h']), FY - s * (-DROP), FX + s * (st['foot_w'] / 2), f"首振りユニット {sw['stack_h']:g}", 12)
    sx0, sy0, sx1, sy1 = Ps['bbox']; body += DL.dim_h(SXo + s * sx0, SXo + s * sx1, FY - s * (-DROP - 12) + 2, f"足 奥行 {st['foot_depth']}(軸から前{st['foot_front']}/後{st['foot_back']})", 10)
    body += [DL.txt(255, 205, f"チルト {H_['tilt_min_deg']:+g}〜{H_['tilt_max_deg']:+g}° / 首振り ±{sw['range_deg']:g}° / バランサ: ダイスプリング2本(s={json.load(open(f'{R}/model/balance.json'))['s']}, e={json.load(open(f'{R}/model/balance.json'))['e']}) + 尾部レバー t{nk['lever_t']:g}×幅{nk['lever_w']:g}×長{nk['lever_len']:g}。", 2.4),
             DL.txt(255, 210, f"ネック基台 t{nk['base_t']:g}(M5×4でロータ板Ø{2*sw['rotor_r']:g}へ)、側板 t6、前後カバー、タイプレート。ストッパ=尾部レバー側縁がゴムパッド(厚{nk['pad_thick']:g})へ。詳細: docs/mechanisms/。", 2.4),
             DL.txt(255, 215, '形状はモデル値(PRELIMINARY)。製造用の部品図は drawings/parts/CP-10, 20〜24。', 2.4)]
    sheet(f'{OUT}/D02_stand_assembly.svg', 'スタンド一式(足・首振り・ネック・バランサ)', 'D02', body, '1:2.4', 'A6063/A5052/SUS304', 'アルマイトII', '多面図(正面/側面/断面A-A)。断面は半割りの外形線(ハッチングは未実装)')
if __name__ == '__main__': sheet_pump(); sheet_stand()

