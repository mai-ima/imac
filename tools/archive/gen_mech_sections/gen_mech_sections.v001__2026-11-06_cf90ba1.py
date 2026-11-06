#!/usr/bin/env python3
"""機構の内部構造・断面図(ハッチング、バルーン、部品表、動作注記)。cadquery で実形状を組み、切断面をハッチして描く。
D03 チルト摩擦ヒンジ+尾部レバー / D04 ダイスプリング式バランサ / D05 首振りクロスローラ軸受 / D06 ストッパ・ドームラッチ。
実行: /tmp/bl/.venv/bin/python tools/gen_mech_sections.py
注意: 市販品(摩擦ヒンジ/軸受/ばね)は『代表的な内部構造と代表寸法』を図示する。型番確定まで内部寸法はUNVERIFIED(U26/U27/U50)。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import cadquery as cq, cadviews as CV, drawlib as DL
S = json.load(open(f'{R}/model/spec.json')); OUT = f'{R}/drawings/v10'; os.makedirs(OUT, exist_ok=True)
HATCH = {'h_st': (45, 1.3, .22), 'h_st2': (135, 1.3, .22), 'h_al': (45, 2.4, .22), 'h_al2': (135, 2.4, .22), 'h_br': (135, .8, .22), 'h_ru': (45, .7, .3), 'h_ss': (45, 1.9, .22), 'h_cu': (0, 1.0, .22)}
def sheet(path, title, num, body, scale, material, finish, note=''):
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="Helvetica,Arial,sans-serif">', CV.hatch_defs(HATCH)] + DL.frame(title, num, scale=scale, material=material, finish=finish, note=note) + body + ['</svg>']
    open(path, 'w', encoding='utf-8').write('\n'.join(o)); print('wrote', os.path.relpath(path, R))
# ---------- 作図ヘルパ ----------
def cylX(d, x0, x1): return cq.Workplane('YZ').workplane(offset=x0).circle(d / 2).extrude(x1 - x0)
def ringX(ro, ri, x0, x1): return cylX(2 * ro, x0, x1).cut(cylX(2 * ri, x0 - 1, x1 + 1))
def boxs(x0, x1, y0, y1, z0, z1): return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
def revX(pts): return cq.Workplane('XY').polyline(pts).close().revolve(360, (0, 0, 0), (1, 0, 0))   # pts=(x, 半径)
def dflat(solid, x0, x1, w=11.0): return solid.cut(boxs(x0, x1, -20, 20, w / 2, 20)).cut(boxs(x0, x1, -20, 20, -20, -w / 2))      # Dカット(平面はz=±w/2)
def balloon(x, y, tx, ty, n):
    return [DL.ln(x, y, tx, ty, .25), f'<circle cx="{tx:.2f}" cy="{ty:.2f}" r="3.4" fill="#fff" stroke="#000" stroke-width=".35"/>', DL.txt(tx, ty + 1.2, str(n), 3.4, 'middle', 'bold'), f'<circle cx="{x:.2f}" cy="{y:.2f}" r=".7" fill="#000"/>']
def partlist(x, y, rows, w=170, title='部品表 / PARTS LIST'):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{6 + 4.6 * len(rows)}" fill="#fff" stroke="#000" stroke-width=".4"/>', DL.ln(x, y + 6, x + w, y + 6, .3), DL.txt(x + 2, y + 4.2, title, 2.6, w='bold')]
    cols = [x + 2, x + 10, x + 70, x + 84, x + 115]; heads = ['No', '名称 / Name', '数量', '材質 / Material', '備考 / Remarks']
    # 列見出しは1行目に統合(行高4.6)
    for i, (n, name, q, mat, rem) in enumerate(rows):
        yy = y + 6 + 4.6 * (i + 1) - 1.3
        o += [DL.ln(x, y + 6 + 4.6 * (i + 1), x + w, y + 6 + 4.6 * (i + 1), .12), DL.txt(cols[0], yy, n, 2.3), DL.txt(cols[1], yy, name, 2.3), DL.txt(cols[2], yy, q, 2.3), DL.txt(cols[3], yy, mat, 2.1), DL.txt(cols[4], yy, rem, 2.1)]
    return o
# ---------- D03 チルト摩擦ヒンジ(右側ユニット x=29〜66)+尾部レバー ----------
def hinge_parts():
    P = {}
    axle = cylX(12, 20, 66).cut(ringX(7, 4.8, 63.1, 64.1))                       # E止め輪溝(Ø9.6)
    P['1'] = ('ヒンジ軸 Ø12 (h6), Dカット幅11', dflat(axle, 38, 62), 'h_ss')
    ear = boxs(24, 29, -34, 0, -7, 7).union(cylX(24, 24, 29)).union(cylX(22, 29, 55.5))      # 耳板(尾部レバー一体)+ハウジング管
    ear = ear.cut(cylX(16, 34, 53.5)).cut(cylX(14.2, 53.5, 56)).cut(cylX(14, 23, 34))                  # 内孔(摩擦パック室Ø16, 端壁Ø14.2, 軸受孔Ø14)
    ear = ear.cut(boxs(41, 51, -1.7, 1.7, 7.9, 8.8)).cut(boxs(41, 51, -1.7, 1.7, -8.8, -7.9))
    ear = ear.cut(cq.Workplane('XZ').workplane(offset=-12).center(36.5, 0).circle(1.5).extrude(6))      # 止めねじ穴(上方向, 肉厚部)
    P['2'] = ('ヒンジ本体(耳板・尾部レバー一体, 外径Ø22)', ear, 'h_al')
    P['3'] = ('焼結含油ブッシュ A (Ø12/Ø14×10)', ringX(7, 6, 24, 34), 'h_br')
    P['4'] = ('フランジ付ブッシュ B (Ø12/Ø14, 鍔Ø15.8)', ringX(7, 6, 53.5, 55.5).union(ringX(7.9, 6, 51.5, 53.5)), 'h_br')
    pl = None
    for k in range(4):
        x0 = 41.5 + 2.5 * k * 1.0 * (1.0) if False else 41.5 + k * 2.5
        p_ = ringX(8, 6.3, x0, x0 + 1.0).union(boxs(x0, x0 + 1.0, -1.5, 1.5, 7.5, 8.6)).union(boxs(x0, x0 + 1.0, -1.5, 1.5, -8.6, -7.5)); pl = p_ if pl is None else pl.union(p_)
    P['5'] = ('摩擦板(外径キー2か所, t1.0)×4', pl, 'h_st')
    ds = None
    for k in range(3):
        x0 = 42.5 + k * 2.5
        d_ = dflat(cylX(14.8, x0, x0 + 1.5), x0 - .1, x0 + 1.6, 11).cut(cylX(12, x0 - 1, x0 + 2)).union(boxs(x0, x0 + 1.5, -1, 1, 5.5, 7.3).union(boxs(x0, x0 + 1.5, -1, 1, -7.3, -5.5)))
        d_ = cylX(14.8, x0, x0 + 1.5).cut(dflat(cylX(12, x0 - 1, x0 + 2.5), x0 - 2, x0 + 3, 11)); ds = d_ if ds is None else ds.union(d_)
    P['6'] = ('摩擦ディスク(Dボア, 焼結青銅 t1.5)×3', ds, 'h_br')
    bv = None
    for k in range(3):
        x0 = 39 + k * .7
        b_ = revX([(x0, 6.1), (x0 + .7, 6.1), (x0 + 1.1, 7.9), (x0 + .4, 7.9)]); bv = b_ if bv is None else bv.union(b_)
    P['7'] = ('皿ばね Ø15.8/Ø12.2 t0.7 ×3(並列)', bv, 'h_st2')
    cap = ringX(8, 6.3, 34, 39).cut(cq.Workplane('XZ').workplane(offset=-8).center(35.2, 0).circle(1.0).extrude(2.5)).cut(cq.Workplane('XZ').workplane(offset=5.6).center(35.2, 0).circle(1.0).extrude(2.5))
    P['8'] = ('調整キャップ M16×1(ピンスパナ穴Ø2×2)', cap, 'h_st2')
    P['9'] = ('止めねじ M3×4 (ロックタイト)', cq.Workplane('XZ').workplane(offset=-10.8).center(36.5, 0).circle(1.5).extrude(3.2), 'h_ss')
    P['10'] = ('スラストワッシャ t1.5', ringX(7.9, 6.3, 50, 51.5), 'h_st2')
    plate = boxs(56, 62, -30, 0, -4, 4).union(cylX(22, 56, 62)).cut(cylX(12, 55, 63))
    P['11'] = ('ネック側板 ボス部(Dボア圧入)', plate, 'h_al2')
    P['12'] = ('平ワッシャ Ø12.5/Ø18 t1', ringX(9, 6.3, 62, 63), 'h_st')
    P['13'] = ('E止め輪 軸Ø12用 (JIS B2804)', ringX(7.6, 4.8, 63.1, 64.1), 'h_ss')
    return P
def sec_view(P, origin, normal, xdir, ox, oy, s, label, lx, ly, only=None, vis_w=.18):
    """P={id:(名称,solid,hatch)}: 平面で半割りして外形(見える線)+切断面ハッチを描く。"""
    sel = {k: v for k, v in P.items() if (only is None or k in only)}
    full = None
    for k, (nm, sol, h) in sel.items(): full = sol if full is None else full.union(sol)
    half, _, (xd, yd) = CV.cut_half(full, origin, normal, xdir); Pr = CV.project(half, tuple(normal), tuple(xdir))
    o = [CV.place(Pr, ox, oy, s, hidden=False, vis_w=vis_w)]
    for k, (nm, sol, h) in sel.items():
        _, polys, _ = CV.cut_half(sol, origin, normal, xdir); o.append(CV.place_section(polys, ox, oy, s, h, .45))
    o.append(DL.txt(lx, ly, label, 3.4, 'middle', 'bold')); return o, Pr
def balloons_row(items, ox, oy, s, y_row, x_from, x_to):
    """items=[(n, モデルx, モデルy)] を x 昇順に y_row の行へ等間隔配置し、斜め引出線で結ぶ。"""
    items = sorted(items, key=lambda i: i[1]); n = len(items); step = (x_to - x_from) / max(1, n - 1); o = []
    for k, (num, px, py) in enumerate(items): o += balloon(ox + s * px, oy - s * py, x_from + k * step, y_row, num)
    return o
def sheet_hinge():
    P = hinge_parts(); body = []; s = 3.2; ox = 28 - s * 20; oy = 104
    o, Pa = sec_view(P, (0, 0, 0), (0, 0, 1), (1, 0, 0), ox, oy, s, '断面 A-A (z=0 軸を含む面)', ox + s * 43, oy - s * 11 - 28); body += o
    body.append(DL.ln(ox + s * 18, oy, ox + s * 68, oy, .18, '9 1.5 1.5 1.5'))
    body += DL.dim_v(oy - s * 11, oy + s * 11, ox + s * 66, 'Ø22', 8)
    body += DL.dim_h(ox + s * 29, ox + s * 55.5, oy + s * 11, '本体管 L26.5(x=29〜55.5)', 18)
    body += DL.dim_h(ox + s * 41.5, ox + s * 50, oy + s * 11, '摩擦パック 8.5', 30)
    body += DL.dim_h(ox + s * 20, ox + s * 66, oy + s * 11, '軸 L46', 42)
    body += balloons_row([(3, 28, 6.5), (8, 36.5, 7.2), (9, 36.5, 10), (7, 40, 7.4), (5, 41.9, 7), (6, 44.5, 6.8), (10, 50.7, 7), (4, 54.5, 6.5), (11, 59, 9), (12, 62.5, 7.5), (13, 63.6, 6.2)], ox, oy, s, oy - s * 11 - 14, ox + s * 21, ox + s * 66 + 22)
    body += balloon(ox + s * 22, oy + s * 3, ox + s * 22, oy + s * 11 + 10, 1)
    body += balloon(ox + s * 26.5, oy + s * 20, ox + s * 38, oy + s * 20 + 6, 2)
    body.append(DL.txt(ox + s * 20, oy + s * 36, '↓ 尾部レバー(x=24〜29, 幅14, 長34)。バランサのばねが先端を押す(D04)', 2.3))
    # 側板は下方を省略
    body.append(DL.txt(ox + s * 59, oy + s * 30 + 6, '側板(下方省略)', 2.1, 'middle'))
    # B-B 断面(摩擦ディスク位置 x=45.7)
    o, Pb = sec_view(P, (45.7, 0, 0), (1, 0, 0), (0, 0, -1), 322, 78, 4.0, '断面 B-B (x=45.7 摩擦ディスク位置, +X側から見る)', 322, 40, vis_w=.2); body += o
    body += DL.dim_h(322 - 4 * 11, 322 + 4 * 11, 78 + 4 * 11, 'Ø22', 6)
    body.append(DL.txt(322, 78 + 4 * 11 + 16, '軸のDカット幅11(z=±5.5)に摩擦ディスク(6)のDボアが噛み、', 2.2, 'middle'))
    body.append(DL.txt(322, 78 + 4 * 11 + 20, '摩擦板(5)の外径キーがハウジング内面の溝に噛む。', 2.2, 'middle'))
    rows = [(k, v[0], {'5': '4', '6': '3', '7': '3', '11': '1'}.get(k, '1'), {'1': 'SUS303(研削)', '2': 'S45C+無電解Ni', '3': '焼結含油青銅', '4': '焼結含油青銅', '5': 'SUS304 t1', '6': '焼結青銅', '7': 'SUP10', '8': 'S45C', '9': 'SUS', '10': 'SUS304', '11': 'A6063-T5', '12': 'SUS304', '13': 'SUS304'}[k],
             {'1': 'CP-20', '2': 'CP-23(特注)', '11': 'CP-10', '5': '摩擦ヒンジ内部', '6': '摩擦ヒンジ内部', '7': '摩擦ヒンジ内部', '8': '摩擦ヒンジ内部'}.get(k, '市販')) for k, v in P.items()]
    body += partlist(186, 150, rows, 224)
    notes = ['動作: ヒンジ本体(2)は頭部側に固定、ヒンジ軸(1)はネック側板(11)にDカット圧入で固定(回らない)。頭部のチルトで(2)が軸まわりに回り、ハウジング内の',
             '  摩擦板(5; 外径キーでハウジングと一体)と摩擦ディスク(6; Dボアで軸と一体)の間に滑りが生じて保持トルクを発生する。',
             '調整: 調整キャップ(8)を頭部内側(トレイ取外し後)からピンスパナで回し、皿ばね(7)の押し付けを増減。止めねじ(9)で固定。',
             '保持トルク: 公称5.8N·m(2個合計)±8%・経年-30%を見込む。ばね荷重/μ/皿ばね特性は実測で確定(U27)。操作力目標≦25N(要ユーザー確認)。',
             '市販摩擦ヒンジ(5〜8)は代表的な内部構造を図示。型番確定(U27)までは寸法・材質は代表値でUNVERIFIED。(2)の耳板・尾部レバーは特注(CP-23)。',
             'ハウジング外径Ø22は軸y=10に対し底面y=-1。ブーツ内空間に1mm突出する(干渉なし)。寿命目標25,000往復で保持低下≦30%(U51)。']
    for i, t_ in enumerate(notes): body.append(DL.txt(186, 224 + i * 3.6, t_, 2.0))
    return body, P

# ---------- D04 チルトバランサ(ダイスプリング+尾部レバー+アンカー) 座標: 軸中心を原点, y'=軸からの上下(下が負), x=左右, z=奥行き ----------
def spring_solid(xc, y_bot, length, n=10, wire=3.0, od=16.0):
    rm = (od - wire) / 2.0; pitch = length / n
    helix = cq.Wire.makeHelix(pitch, length - wire * 0.0, rm)
    prof = cq.Workplane('XZ').center(rm, 0).circle(wire / 2)
    sp = prof.sweep(cq.Workplane(obj=helix), isFrenet=True)
    return sp.rotate((0, 0, 0), (1, 0, 0), -90).translate((xc, y_bot, 0))
def balancer_parts():
    N_ = S['neck']; PD = N_['lever_pin_d']; BAL = json.load(open(f'{R}/model/balance.json')); E_, S_ = -BAL['e'], -BAL['s']; hw2 = S['hinge']['balance_end_hw_mm'] / 2   # E_=-25(上ピン), S_=-76(下ピン)
    P = {}
    lev = None
    for sx in (-1, 1):
        l_ = boxs(sx * 26.5 - 2.5, sx * 26.5 + 2.5, -N_['lever_len'], 0, -7, 7).union(cq.Workplane('YZ').workplane(offset=sx * 26.5 - 2.5).circle(12).extrude(5))
        l_ = l_.cut(cq.Workplane('YZ').workplane(offset=sx * 26.5 - 3).center(E_, 0).circle(PD / 2).extrude(6)).cut(cq.Workplane('YZ').workplane(offset=sx * 26.5 - 3).circle(7).extrude(6))
        lev = l_ if lev is None else lev.union(l_)
    P['1'] = ('尾部レバー(ヒンジ本体の耳板, 左右)', lev, 'h_al')
    P['2'] = ('ヒンジ軸 Ø12(部分)', cylX(12, -34, 34), 'h_ss')
    P['3'] = (f'レバー先端 横ピン Ø{PD:g} (SUS630 H1025)', cq.Workplane('YZ').workplane(offset=-32).center(E_, 0).circle(PD / 2).extrude(64), 'h_st')
    up = None
    for sx in (-1, 1):
        xc = sx * 14
        b = cq.Workplane('YZ').workplane(offset=xc - 5).center(E_, 0).circle(6).extrude(10).cut(cq.Workplane('YZ').workplane(offset=xc - 6).center(E_, 0).circle(PD / 2).extrude(12))
        yt = E_ - hw2
        d = cq.Workplane('XZ').workplane(offset=-(yt + 2)).center(xc, 0).circle(8).extrude(2)           # 座円盤(上): y'=yt..yt+2 ←XZ法線は-Y: offset=-y
        bs = cq.Workplane('XZ').workplane(offset=-yt).center(xc, 0).circle(3.8).extrude(4)                 # 位置決めボス: yt-4..yt
        w = b.union(d).union(bs); up = w if up is None else up.union(w)
    P['4'] = ('ロッドエンド(上, 左右) ばね座+位置決めボスØ7.6', up, 'h_st2')
    sp = None
    yt = E_ - hw2; yb = S_ + hw2 + 1.0                                       # 下端: 座円盤1+ピールシム1.0 を除いたばね下端
    for sx in (-1, 1):
        w = spring_solid(sx * 14, yb, yt - yb); sp = w if sp is None else sp.union(w)
    P['5'] = ('ダイスプリング Ø16×Ø8 (JIS金型用, 線径3.0, 自由長≧' + f"{BAL['free_length_min']:.0f}mm)", sp, 'h_cu')
    lo = None; sh = None
    for sx in (-1, 1):
        xc = sx * 14
        b = cq.Workplane('YZ').workplane(offset=xc - 5).center(S_, 0).circle(6).extrude(10).cut(cq.Workplane('YZ').workplane(offset=xc - 6).center(S_, 0).circle(PD / 2).extrude(12))
        d = cq.Workplane('XZ').workplane(offset=-(S_ + 6)).center(xc, 0).circle(8).extrude(1.0)        # 座円盤(下) y'=S_+6..S_+7
        bs = cq.Workplane('XZ').workplane(offset=-(S_ + hw2)).center(xc, 0).circle(3.8).extrude(4)
        w = b.union(d); lo = w if lo is None else lo.union(w)
        s_ = ringXY(8, 4.2, xc, S_ + hw2 - 1.0, S_ + hw2); sh = s_ if sh is None else sh.union(s_)
    P['6'] = ('トラニオン(下, 左右) ばね座', lo, 'h_st2')
    P['7'] = ('ピールシム 0.25mm×8枚(公称4枚=1.0mm)', sh, 'h_br')
    P['8'] = (f'アンカーピン Ø{PD:g}', cq.Workplane('YZ').workplane(offset=-24).center(S_, 0).circle(PD / 2).extrude(48), 'h_st')
    br = boxs(-30, 30, S_ - 6, S_ - 3, -9, 9)
    for xs in (-23, -9, 5, 19):
        br = br.union(boxs(xs, xs + 4, S_ - 6, S_, -9, 9)).union(cq.Workplane('YZ').workplane(offset=xs).center(S_, 0).circle(6).extrude(4))
    br = br.cut(cq.Workplane('YZ').workplane(offset=-30).center(S_, 0).circle(PD / 2).extrude(60))
    for xb in (-27, 27): br = br.cut(cq.Workplane('XZ').workplane(offset=-(S_ - 3)).center(xb, 0).circle(2.7).extrude(3.2))
    P['9'] = ('アンカーブリッジ(A5052 t3+耳4枚)', br, 'h_al2')
    P['10'] = ('M5皿ボルト×4 (SUS, 基台へ)', cq.Workplane('XZ').workplane(offset=-(S_ - 3)).center(27, 0).circle(2.5).extrude(14).union(cq.Workplane('XZ').workplane(offset=-(S_ - 3)).center(-27, 0).circle(2.5).extrude(14)), 'h_ss')
    P['11'] = ('ネック基台 t8(CP-21)', boxs(-34, 34, S_ - 6 - 8, S_ - 6, -30, 30), 'h_al')
    return P
def ringXY(ro, ri, xc, y0, y1): return cq.Workplane('XZ').workplane(offset=-y1).center(xc, 0).circle(ro).circle(ri).extrude(y1 - y0)
def wrap_notes(body, x, y0, notes, width=84, step=3.7, size=2.1):
    y = y0
    for t_ in notes:
        for k in range(0, len(t_), width): body.append(DL.txt(x + (0 if k == 0 else 3), y, t_[k:k + width], size)); y += step
        y += 1.2
    return y
def sheet_balancer():
    P = balancer_parts(); body = []; s = 2.0; ox = 112; oy = 62
    o, Pa = sec_view(P, (0, 0, 0), (0, 0, 1), (1, 0, 0), ox, oy, s, '断面 A-A (z=0: 両ばね軸・両レバー・ピンを含む面, チルト0°)', ox, 30); body += o
    for xx in (-14, 14): body.append(DL.ln(ox + s * xx, oy - s * 8, ox + s * xx, oy + s * 92, .18, '9 1.5 1.5 1.5'))
    body.append(DL.ln(ox - s * 34, oy, ox + s * 34, oy, .18, '9 1.5 1.5 1.5'))
    BAL = json.load(open(f'{R}/model/balance.json')); e, sA = BAL['e'], BAL['s']; hw = S['hinge']['balance_end_hw_mm']
    xl = ox - s * 34
    body += DL.dim_v(oy + s * e, oy + s * sA, xl, f"ピン間 {sA - e:g}(0°)", -10)
    body += DL.dim_v(oy + s * (e + hw / 2), oy + s * (sA - hw / 2), xl, f"ばね長 {sA - e - hw:g}", -22)
    body += DL.dim_v(oy, oy + s * e, xl, f"e={e}", -34)
    body += DL.dim_v(oy, oy + s * sA, xl, f"s={sA}", -46)
    body += DL.dim_h(ox - s * 30, ox + s * 30, oy + s * 90.5, 'アンカーブリッジ L60', 6)
    body += DL.dim_h(ox, ox + s * 14, oy - s * 8, 'ばね中心 14', -4)
    items = [(1, 26.5, -30), (3, 31, -25), (4, 18, -31), (5, 20, -50), (7, 20, -68.4), (6, 18, -70.5), (8, 22, -76), (9, 7, -80), (10, 27, -84), (11, 30, -88), (2, 33, -3)]
    items.sort(key=lambda i: -i[2] if False else i[2], reverse=True)
    lx = ox + s * 34 + 22; ylast = -1e9
    for n, px, py in items:
        yb = max(oy - s * py, ylast + 9); ylast = yb; body += balloon(ox + s * px, oy - s * py, lx, yb, n)
    rows = [(k, v[0], {'1': '2', '4': '2', '5': '2', '6': '2', '7': '2', '10': '4'}.get(k, '1'), {'1': 'SUS304 t5', '2': 'SUS303', '3': 'SUS630-H1025', '4': 'S45C', '5': 'SWOSC-V(クロムシリコン)', '6': 'S45C', '7': 'SUS304 t0.25', '8': 'SUS630-H1025', '9': 'A5052-H32', '10': 'SUS', '11': 'A6063-T5'}[k],
             {'1': 'CP-23', '2': 'CP-20', '3': 'CP-23', '4': 'CP-23', '5': '市販(型番未選定U26)', '6': 'CP-23', '7': '市販ピールシム', '8': 'CP-23', '9': 'CP-23', '10': '市販', '11': 'CP-21'}[k]) for k, v in P.items()]
    body += partlist(226, 28, rows, 184)
    notes = ['原理: 頭部の重力モーメントはチルト角で増える。ばね(5)が尾部レバー(1)先端のピン(3)を押し、ばね力×てこ腕が角度の正弦にほぼ比例して変わることで重力モーメントを相殺する。',
             '構造: ばねは上端のロッドエンド(4)と下端のトラニオン(6)で両端を揺動ピン(3)(8)支持する。座の位置決めボス(Ø7.6)がばね内径(Ø8)に嵌まる。案内ロッドなし(取付長/平均径<4で座屈しにくい)。',
             '調整(荷重): ばね下座とトラニオンの間のピールシム(7; 0.25mm×8)を増減し、ばね荷重を±約27N/本(±7%)調整。組立時に頭部の実測重量へ合わせ、トルクペイントで封印(整備者L3のみ再調整)。',
             f'幾何: 上ピンは軸から下へ{e}mm、下ピン(アンカー)は{sA}mm。端金物の長さ計{hw:g}mm(ピン中心→ばね座面が片側{hw/2:g}mm)。ばね長=ピン間-{hw:g}mm。',
             'ばね軸はチルトで-16〜+7°揺動する。ばね1本折損時は残り1本+摩擦ヒンジ(D03)+ゴムストッパで減速・保持(tools/strength_check.py)。',
             '座標: 縦=ヒンジ軸からの距離(下が負)、横=左右。図は0°の姿勢。軸・ヒンジ本体はD03、ストッパ/ネックは docs/mechanisms/03。',
             '市販ばね(5)・ピールシム(7)の型番は未確定(U26/U51)。寸法は代表値でUNVERIFIED。ばね疲労(25,000回)は未評価。']
    wrap_notes(body, 226, 104, notes)
    return body, P
E_0 = 0

if __name__ == '__main__':
    b, P = sheet_balancer(); sheet(f'{OUT}/D04_balancer_section.svg', 'チルトバランサ 内部構造・断面', 'D04', b, '2:1', 'SUS/S45C/SWOSC-V/A5052', '-', '')
    b, P = sheet_hinge(); sheet(f'{OUT}/D03_tilt_hinge_section.svg', 'チルト摩擦ヒンジ 内部構造・断面', 'D03', b, 'A-A 3.2:1 / B-B 4:1', 'SUS303/S45C/焼結青銅/A6063', '-', '')
