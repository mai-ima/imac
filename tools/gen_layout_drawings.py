#!/usr/bin/env python3
"""配置図を実形状で生成: drawings/09_board_layout.svg(基板部品配置)と drawings/10_placement_dimensioned.svg(トレイ平面の部品配置)。
正規ソース: model/x870i_layout.json(基板), model/layout.json(配置), model/parts.json, model/pump.json, model/cables.json, model/spec.json。
実行: python3 tools/gen_layout_drawings.py     (tools/gen_package.py の 09/10 は本ツールへ移行済み)"""
import json, os, math, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f'{R}/drawings'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import drawlib as DL
J = lambda n: json.load(open(f'{R}/model/{n}.json', encoding='utf-8'))
S, L, BL, PJ, CB = J('spec'), J('layout'), J('x870i_layout'), J('pump'), J('cables')
D = S['dome']; PH = S['panels'][str(S['panel_size'])]['h']; W = S['body_w']; H = PH + S['bezel'] + S['chin']
IW = W - 2 * D['inset_left_right'] - 6; IH = H - D['inset_bottom'] - D['inset_top'] - 6
DEPTH = D['total_t'] - S['slab_t'] - 3
def dome_in(d): s = max(0, min(1, d / D['run'])); return D['edge_inner_depth'] + (DEPTH - D['edge_inner_depth']) * (s * s * (3 - 2 * s))
I = {i['id']: i for i in L['items']}
esc = DL.esc
def T(x, y, s, sz=2.6, a='start', fill='#222', w='normal', extra=''): return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{sz}" text-anchor="{a}" font-weight="{w}" fill="{fill}" {extra}>{esc(s)}</text>'
def rect(x, y, w, h, fill='none', st='#333', sw=.25, op=1, rx=0, dash=''): return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{st}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def circ(cx, cy, r, fill='none', st='#333', sw=.25, dash=''): return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="{st}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def line(x1, y1, x2, y2, st='#222', sw=.25, dash='', extra=''): return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{st}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + f' {extra}/>'
def poly(pts, fill='none', st='#333', sw=.25, op=1, dash=''): return f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in pts)}" fill="{fill}" fill-opacity="{op}" stroke="{st}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def head(title, num, scale, note=''):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" font-family="Helvetica,Arial,sans-serif"><defs><marker id="ar" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#06c"/></marker></defs>'
    return [svg] + DL.frame(title, num, scale=scale, note=note)
def dimh(x1, x2, y, label, off=7): return [line(x1, y, x1, y + off, '#888', .2), line(x2, y, x2, y + off, '#888', .2), line(x1, y + off - 1.5, x2, y + off - 1.5, '#06c', .25, '', 'marker-start="url(#ar)" marker-end="url(#ar)"'), T((x1 + x2) / 2, y + off - 2.3, label, 2.5, 'middle', '#06c')]
def dimv(y1, y2, x, label, off=-7): return [line(x, y1, x + off, y1, '#888', .2), line(x, y2, x + off, y2, '#888', .2), line(x + off + 1.5, y1, x + off + 1.5, y2, '#06c', .25, '', 'marker-start="url(#ar)" marker-end="url(#ar)"'), T(x + off - .8, (y1 + y2) / 2, label, 2.5, 'middle', '#06c', extra=f'transform="rotate(-90 {x+off-.8:.1f} {(y1+y2)/2:.1f})"')]
def save(name, parts): open(f'{OUT}/{name}', 'w', encoding='utf-8').write('\n'.join(parts) + '</svg>\n'); print('wrote', name)
def fan(cx, cy, d, n=9, hub=.3, fill='#ddd'):      # 軸流ファンの平面形(枠+羽根+ハブ)
    o = [rect(cx - d / 2, cy - d / 2, d, d, fill, '#222', .3, 1, d * .08), circ(cx, cy, d * .46, '#fff', '#555', .2), circ(cx, cy, d * hub / 2 + .3, '#444', '#222', .2)]
    for k in range(n):
        a = 2 * math.pi * k / n; r0, r1 = d * hub / 2, d * .45
        o.append(poly([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + (r0 + r1) / 2 * math.cos(a + .35) + 0, cy + (r0 + r1) / 2 * math.sin(a + .35)), (cx + r1 * math.cos(a + .75), cy + r1 * math.sin(a + .75))], 'none', '#555', .2))
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)): o.append(circ(cx + dx * d * .43, cy + dy * d * .43, d * .022, '#fff', '#222', .15))
    return o

# ================= 基板(ASUS ROG STRIX X870-I)を実形状で描く: ctx=(X,Y,sc) 基板座標→用紙座標 =================
USBA = {'usb_red': '#c8202b', 'usb2': '#15161a'}
def board_shapes(X, Y, sc, detail=True, label=None):
    """基板上の全部品を実形状(平面図)で返す。座標は基板左下原点・x右・y上(I/O辺=下)。"""
    o = []; fx = lambda x: X(x); fy = lambda y: Y(y)
    def R(x0, y0, x1, y1, fill='none', st='#333', sw=.25, rx=0, op=1, dash=''): return rect(fx(x0), fy(y1), (x1 - x0) * sc, (y1 - y0) * sc, fill, st, sw, op, rx * sc, dash)
    o.append(R(0, 0, 170, 170, '#16191d', '#000', .6, 3))      # PCB(黒基板)
    sx, sy = BL['socket_center']
    # --- VRMヒートシンク(+ファン)  ---
    o.append(R(8, 24, 106, 60, '#2b2d33', '#000', .3, 2.5)); o.append(R(8, 24, 106, 25.2, '#a8abb2', '#222', .2, 2.5, .9))
    for k in range(10): o.append(line(fx(10 + k * 9.6), fy(26), fx(10 + k * 9.6), fy(58), '#555', .15))      # フィン溝
    o += fan(fx(96), fy(42), 24 * sc, 7, .35, '#2b2d33')
    # --- チョーク/コンデンサ(個数は未確認・典型配置) ---
    for i in range(8): o.append(R(14 + i * 9.6, 62, 21 + i * 9.6, 69, '#3a3d44', '#111', .15, 1))
    for i in range(6): o.append(circ(fx(22 + i * 9.6), fy(74), 3.2 * sc, '#c0c4ca', '#222', .15))
    # --- AM5ソケット ---
    o.append(R(sx - 30, sy - 30, sx + 30, sy + 30, '#2a2c31', '#000', .35, 2)); o.append(R(sx - 24, sy - 24, sx + 24, sy + 24, '#4a4d55', '#111', .2, 1.5))
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)): o.append(circ(fx(sx + dx * 27), fy(sy + dy * 27), 2.4 * sc, '#9aa0a6', '#111', .2)); o.append(circ(fx(sx + dx * 27), fy(sy + dy * 27), 1.1 * sc, '#333', '#111', .1))
    o.append(R(sx - 20, sy - 20, sx + 20, sy + 20, '#b9bec6', '#222', .3, 1.2)); o.append(poly([(fx(sx - 20), fy(sy - 12)), (fx(sx - 12), fy(sy - 20)), (fx(sx - 20), fy(sy - 20))], '#666', '#222', .2))      # IHS+切欠
    o.append(line(fx(sx + 30), fy(sy + 22), fx(sx + 30), fy(sy - 22), '#aaa', .6))      # ロードレバー(位置はUNVERIFIED)
    # --- DIMM ×2: スロット+接点+ラッチ ---
    for i, (y0, y1) in enumerate(BL['dimm_slots']['y']):
        x0, x1 = BL['dimm_slots']['x']; o.append(R(x0, y0, x1, y1, '#e8e8ea', '#111', .3, .6))
        o.append(line(fx(x0 + 3), fy((y0 + y1) / 2), fx(x1 - 3), fy((y0 + y1) / 2), '#b8860b', .35))
        for k in range(int((x1 - x0 - 8) / 2.6)): o.append(line(fx(x0 + 4 + k * 2.6), fy(y0 + .7), fx(x0 + 4 + k * 2.6), fy(y1 - .7), '#999', .08))
        o.append(R(x0 - .2, y0, x0 + 3.2, y1, '#d0d0d4', '#111', .2, .5))      # ラッチ(片側, 位置はUNVERIFIED)
    # --- ATX 24ピン / EPS 8ピン(セル表現) ---
    a = BL['atx_pwr']; o.append(R(a['x'][0], a['y'][0], a['x'][1], a['y'][1], '#f2f2f2', '#111', .3, .5))
    for k in range(12):
        for j in range(2): o.append(R(a['x'][0] + 1 + k * 4.05, a['y'][0] + 1 + j * 4.2, a['x'][0] + 4.5 + k * 4.05 - .8, a['y'][0] + 4.8 + j * 4.2 - .6 + .6, '#d9d9d9', '#555', .1))
    a = BL['cpu_12v']; o.append(R(a['x'][0], a['y'][0], a['x'][1], a['y'][1], '#f2f2f2', '#111', .3, .5))
    for k in range(4):
        for j in range(2): o.append(R(a['x'][0] + 1.2 + j * 5.1, a['y'][0] + 1 + k * 4.2, a['x'][0] + 5.8 + j * 5.1 - .8, a['y'][0] + 4.7 + k * 4.2 - .4, '#d9d9d9', '#555', .1))
    # --- PCIe x16 / チップセット ---
    a = BL['pcie_x16']; o.append(R(a['x'][0], a['y'][0], a['x'][1], a['y'][1], '#1b1c20', '#000', .3, .6)); o.append(R(a['x'][0] + 3.2, a['y'][0] + 14, a['x'][0] + 5.4, a['y'][0] + 74, '#c9a227', '#6b5600', .1))
    for k in range(30): o.append(line(fx(a['x'][0] + 3.2), fy(a['y'][0] + 14 + k * 2), fx(a['x'][0] + 5.4), fy(a['y'][0] + 14 + k * 2), '#6b5600', .08))
    a = BL['chipset']; o.append(R(a['x'][0], a['y'][0], a['x'][1], a['y'][1], '#50545c', '#111', .3, 1))
    for k in range(7): o.append(line(fx(a['x'][0] + 2 + k * 2.8), fy(a['y'][0] + 1.5), fx(a['x'][0] + 2 + k * 2.8), fy(a['y'][1] - 1.5), '#8a8e96', .2))
    # --- M.2 ドーターカード(2枚)+BTOBコネクタ ---
    o.append(R(131, 77, 156, 138, '#1a3a2a', '#0b0', .25, 1.2, .95, '1.2 .8')); o.append(R(134, 104, 155, 108.5, '#2a2a2e', '#000', .2, .4))
    o.append(R(134.1, 118.5, 149.1, 122.5, '#2a2a2e', '#000', .2, .4))
    # --- 追加部品(components) ---
    for c in BL.get('components', []):
        col = {'white': '#f1efe6', 'dark': '#2a2c31', 'alu': '#b8bcc4', 'pcb_black': '#1a3a2a'}.get(c['color'], '#ddd')
        o.append(R(c['x'][0], c['y'][0], c['x'][1], c['y'][1], col, '#111', .2, .5))
        if c['kind'] == 'header':
            w_, d_ = c['x'][1] - c['x'][0], c['y'][1] - c['y'][0]; n = max(2, int(max(w_, d_) / 2.54))
            for k in range(n):
                px = c['x'][0] + (w_ / 2 if w_ < d_ else (k + .5) * w_ / n); py = c['y'][0] + ((k + .5) * d_ / n if w_ < d_ else d_ / 2)
                o.append(circ(fx(px), fy(py), .45 * sc, '#c9a227', '#6b5600', .08))
    o.append(circ(fx(143.5), fy(78), 2.6 * sc, '#9aa0a6', '#222', .2)); o.append(circ(fx(143.5), fy(134), 2.6 * sc, '#9aa0a6', '#222', .2))      # M.2固定ポスト(位置UNVERIFIED)
    # --- 背面I/O(下辺): シールドとポート ---
    iox = BL['io_x_ranges']; o.append(R(iox['HDMI_U10G34'][0] - 2, -2, iox['M2_WIFI'][1] + 2, 24, '#3a3d44', '#111', .3, .8, .55, '2 1'))
    ports = [('USB-A 10G', 24.5, 14.5, '#c8202b'), ('USB-A 10G', 24.5, 14.5, '#c8202b'), ('HDMI', 24.5, 15, '#222'), ('BTN', 44, 6.5, '#888'), ('BTN', 51, 6.5, '#888'), ('USB-A 10G', 47.5, 14.5, '#c8202b'), ('USB4-C', 47.5, 9, '#222'),
             ('USB2', 66, 14.5, '#15161a'), ('USB2', 66, 14.5, '#15161a'), ('USB2', 83.5, 14.5, '#15161a'), ('USB4-C', 83.5, 9, '#222'), ('RJ45', 101.5, 16, '#b8bcc4'), ('USB-A 10G', 101.5, 14.5, '#c8202b'), ('USB-C 10G', 101.5, 9, '#222')]
    seen = {}
    for nm, xc, w_, col in ports:
        k = seen.get(xc, 0); seen[xc] = k + 1
        if k == 0: o.append(R(xc - w_ / 2, -3.4, xc + w_ / 2, -1.6, col, '#111', .2, .3))      # 列ごとに最前面ポートの外形のみ(上下に積むため平面図では重なる)
    for k in range(2): o.append(circ(fx(117.5), fy(-4), 3.2 * sc, '#c9a227', '#6b5600', .2))      # SMA×2(縦積み)
    # --- 取付穴(ミニITX規格値はUNVERIFIED: U17) ---
    for (hx, hy) in ((10.2, 6.4), (165.1, 6.4), (10.2, 163.8), (165.1, 163.8)): o.append(circ(fx(hx), fy(hy), 2.2 * sc, '#fff', '#c0392b', .3)); o.append(circ(fx(hx), fy(hy), 1.0 * sc, '#16191d', '#c0392b', .2))
    return o

def gen_09():
    sc = 1.1; ox, oy = 34, 38; B = 170
    X = lambda x: ox + x * sc; Y = lambda y: oy + (B - y) * sc
    b = head('基板 部品配置図(ROG STRIX X870-I)', 'PKG-09', '1.1 : 1(拡大)', note='座標: 基板左下原点, x右/y上, I/O辺=下。位置の出典: ASUS マニュアルp.14 配置図の読み取り(±2mm)。高さは典型値=UNVERIFIED')
    b += board_shapes(X, Y, sc)
    items = [('1', 'AM5 ソケット(LGA1718)+IHS 40x40', '', ''), ('2', 'DDR5 DIMM ×2(スロット長144, ピッチ9.2)', '', ''), ('3', 'ATX 24ピン(50.1x10)', '', ''), ('4', 'CPU 8ピン(EPS 11.8x18.1)', '', ''), ('5', 'PCIe 5.0 x16(8.6x89)', '', ''),
             ('6', 'チップセット+ヒートシンク(21x19)', '', ''), ('7', 'M.2 ドーターカード ×2(位置のみ。高さ・向きUNVERIFIED U56)', '', ''), ('8', 'VRM ヒートシンク+ファン(寸法は仮置きUNVERIFIED)', '', ''), ('9', 'チョーク8/コンデンサ6(個数・位置UNVERIFIED)', '', ''), ('10', '背面I/O(USB-A 10G×4/USB4-C×2/USB2×3/HDMI/RJ45/USB-C 10G/SMA×2)', '', '')]
    for (n, x, y) in (('1', BL['socket_center'][0] - 22, BL['socket_center'][1] + 33), ('2', 90, 157), ('3', 38, 171.5), ('4', 3, 24), ('5', 161, 38), ('6', 138, 70), ('7', 143, 140), ('8', 30, 21), ('9', 56, 77), ('10', 60, -9)):
        b += [circ(X(x), Y(y), 2.6, '#fff', '#900', .35), T(X(x), Y(y) + 1.0, n, 2.8, 'middle', '#900', 'bold')]
    b += dimh(ox, ox + B * sc, oy + B * sc, '170.0', 8) + dimv(oy, oy + B * sc, ox, '170.0', -8)
    tx = ox + B * sc + 16; ty = 38
    b.append(T(tx, ty, '凡例(主要部品)', 3.4, 'start', '#000', 'bold'))
    for k, (n, lab, _, _) in enumerate(items): b += [circ(tx + 2.4, ty + 6.5 + k * 6.4 - 1.0, 2.2, '#fff', '#900', .3), T(tx + 2.4, ty + 6.5 + k * 6.4, n, 2.2, 'middle', '#900', 'bold'), T(tx + 7, ty + 6.5 + k * 6.4, lab, 2.3)]
    ty2 = ty + 6.5 + len(items) * 6.4 + 4
    b.append(T(tx, ty2, f'追加部品(components {len(BL["components"])}点: x[mm] / y[mm] / 高さ)', 3.0, 'start', '#000', 'bold'))
    for k, c in enumerate(BL['components']):
        b.append(T(tx, ty2 + 5.2 + k * 4.35, f'{c["name"]}  x{c["x"][0]:g}–{c["x"][1]:g}  y{c["y"][0]:g}–{c["y"][1]:g}  h{c["h"]:g}', 2.0))
    b.append(T(tx, ty2 + 5.2 + len(BL['components']) * 4.35 + 3, '※ 取付穴(赤)はMini-ITX規格値の転記(U17: 規格書で要確認)。部品高さは典型値で公式資料に無い(UNVERIFIED)。', 2.1, 'start', '#900'))
    save('09_board_layout.svg', b)

def gen_10():
    sc = 0.46; ox, oy = 36, 40
    X = lambda x: ox + x * sc; Y = lambda y: oy + (IH - y) * sc
    b = head('部品配置図(トレイ平面)', 'PKG-10', f'1:{1/sc:.2f} (≈0.46倍)', note='座標: トレイ内寸(ドーム内側)の左下原点。z=トレイ面からの高さ。ドーム内面の許容zは縁からの距離で変化(smoothstep)')
    b.append(rect(ox, oy, IW * sc, IH * sc, '#f7f8fa', '#000', .5, 1, 50 * sc))
    for r_ in (D['run'],): b.append(rect(ox + r_ * sc, oy + r_ * sc, (IW - 2 * r_) * sc, (IH - 2 * r_) * sc, 'none', '#888', .2, 1, max(50 - r_, 6) * sc, '2 1.5'))      # ドーム傾斜の終端(最大深さ域)
    # 基板
    bp = I['board']['pos']; b += board_shapes(lambda x: X(bp[0] + x), lambda y: Y(bp[1] + y), sc, detail=False)
    # ポンプ/ヘッド(円盤Ø91+筐体+エルボ) 平面
    cl = I['cooler']['pos']; cs = I['cooler']['size']; pcx, pcy = cl[0] + 45.5, cl[1] + cs[1] / 2
    b += [circ(X(pcx), Y(pcy), PJ['disc_d'] / 2 * sc, '#2b2d33', '#000', .4), circ(X(pcx), Y(pcy), 42 * sc, '#3a3d44', '#111', .2), circ(X(pcx), Y(pcy), 28 * sc, '#1a1b1f', '#111', .2)]
    for k in range(12): a = 2 * math.pi * k / 12; b.append(line(X(pcx + 30 * math.cos(a)), Y(pcy + 30 * math.sin(a)), X(pcx + 42 * math.cos(a)), Y(pcy + 42 * math.sin(a)), '#777', .2))
    hx0, hx1 = PJ['housing_body']['x']; hy0, hy1 = PJ['housing_body']['y']
    b += [rect(X(pcx + hx0), Y(pcy + hy1), (hx1 - hx0) * sc, (hy1 - hy0) * sc, '#2b2d33', '#000', .3, 1, 2 * sc), rect(X(pcx + PJ['elbow']['x'][0]), Y(pcy + PJ['elbow']['y'][1]), (PJ['elbow']['x'][1] - PJ['elbow']['x'][0]) * sc, (PJ['elbow']['y'][1] - PJ['elbow']['y'][0]) * sc, '#3a3d44', '#000', .3, 1, 2 * sc)]
    # ラジエーター(コア+タンク+ファン×2)
    rp = I['radiator']['pos']; rs = I['radiator']['size']
    b += [rect(X(rp[0]), Y(rp[1] + rs[1]), rs[0] * sc, rs[1] * sc, '#a9afb8', '#111', .4, 1, 1.5 * sc)]
    for k in range(int(rs[1] / 4)): b.append(line(X(rp[0] + 2), Y(rp[1] + 12 + k * 4), X(rp[0] + rs[0] - 2), Y(rp[1] + 12 + k * 4), '#7d838d', .12))      # フィン
    for yy in (rp[1], rp[1] + rs[1] - 12): b.append(rect(X(rp[0]), Y(yy + 12), rs[0] * sc, 12 * sc, '#2b2d33', '#000', .3, 1, 1 * sc))
    for k in range(2): b += fan(X(rp[0] + 60), Y(rp[1] + 18.5 + 60 + k * 120), 120 * sc, 11, .4, '#9aa0a8')
    # GPU(基板PCB+ヒートシンク+シュラウド+ファン×2) / ライザー
    gp = I['gpu']['pos']; gs = I['gpu']['size']
    b += [rect(X(gp[0]), Y(gp[1] + gs[1]), gs[0] * sc, gs[1] * sc, '#c8ccd2', '#111', .4, 1, 3 * sc), rect(X(gp[0] + 5), Y(gp[1] + gs[1] - 12), (gs[0] - 10) * sc, (gs[1] - 20) * sc, 'none', '#555', .2, 1, 0, '2 1.5')]
    for k in range(2): b += fan(X(gp[0] + gs[0] / 2), Y(gp[1] + gs[1] / 2 + (-70 if k == 0 else 70)), 110 * sc, 11, .36, '#3a3d44')
    b.append(line(X(gp[0] + 2), Y(gp[1] + gs[1] / 2), X(gp[0] + gs[0] - 2), Y(gp[1] + gs[1] / 2), '#fff', .6))
    rz = I['riser']; b += [rect(X(rz['pos'][0]), Y(rz['pos'][1] + rz['size'][1]), rz['size'][0] * sc, rz['size'][1] * sc, '#555', '#111', .3, 1)]
    for k in range(6): b.append(line(X(rz['pos'][0] + 2 + k * 3.7), Y(rz['pos'][1]), X(rz['pos'][0] + 2 + k * 3.7), Y(rz['pos'][1] + rz['size'][1]), '#999', .15))
    # PSU(SFX-L: ケース+92mmファン+グリル+ケーブル出口)
    ps = I['psu']; pp, pz = ps['pos'], ps['size']
    b += [rect(X(pp[0]), Y(pp[1] + pz[1]), pz[0] * sc, pz[1] * sc, '#d6d8dc', '#111', .4, 1, 2 * sc)] + fan(X(pp[0] + 62), Y(pp[1] + 50), 92 * sc, 9, .34, '#c9ccd2')
    for k in range(8): b.append(line(X(pp[0] + 6), Y(pp[1] + 6 + k * 3), X(pp[0] + 119), Y(pp[1] + 6 + k * 3), '#aaa', .1))
    # コントローラ基板/RAM/SSD/ACインレット
    for k, c_, lab in (('ctrl_board', '#a9c0d6', 'ctrl'), ('ssd', '#2a2a2e', 'SSD')):
        it = I[k]; p_, s_ = it['pos'], it['size']; b += [rect(X(p_[0]), Y(p_[1] + s_[1]), s_[0] * sc, s_[1] * sc, c_, '#111', .3, .9, 1 * sc)]
    ac = I['ac_inlet']; b += [rect(X(ac['pos'][0]), Y(ac['pos'][1] + ac['size'][1]), ac['size'][0] * sc, ac['size'][1] * sc, '#e0e0e0', '#111', .3, 1, 1 * sc), rect(X(ac['pos'][0] + 4), Y(ac['pos'][1] + ac['size'][1] - 5), (ac['size'][0] - 8) * sc, (ac['size'][1] - 10) * sc, '#222', '#000', .2)]
    # ホース/ケーブル(cables.json の経路を平面投影)
    CC = {'H': ('#0d0e10', 1.5), 'W': ('#c0392b', .5)}
    for c in CB['cables']:
        pts = [(X(p[0]), Y(p[1])) for p in c['pts']]; col, wd = CC['H' if c['id'].startswith('H') else 'W']
        b.append(poly(pts, 'none', col, wd * (1 if c['id'].startswith('H') else 1), .9))
    # 番号+凡例
    lab = {'board': '基板', 'cooler': 'ポンプ(CPU)', 'radiator': 'ラジエーター+ファン×2', 'gpu': 'GPU', 'riser': 'ライザー', 'psu': 'PSU', 'ctrl_board': 'コントローラ基板', 'ssd': 'SSD', 'ram': 'RAM', 'ac_inlet': 'ACインレット'}
    for n, k in enumerate(L['items'], 1):
        x, y, z = k['pos']; w_, h_, d_ = k['size']; cx_, cy_ = x + w_ / 2, y + h_ / 2
        if k['id'] in ('ram', 'board'): cx_, cy_ = (x + 8, y + h_ - 8) if k['id'] == 'ram' else (x + 8, y + 8)
        b += [circ(X(cx_), Y(cy_), 2.6, '#fff', '#900', .35), T(X(cx_), Y(cy_) + 1.0, str(n), 2.8, 'middle', '#900', 'bold')]
    b += dimh(ox, ox + IW * sc, oy + IH * sc, f'{IW:.0f}', 9) + dimv(oy, oy + IH * sc, ox, f'{IH:.0f}', -9)
    for i, dy in (('board', 0), ('gpu', 5), ('radiator', 10)):
        p_, s_ = I[i]['pos'], I[i]['size']; b += dimh(ox + p_[0] * sc, ox + (p_[0] + s_[0]) * sc, oy + IH * sc + 4 + dy, f'{i} x={p_[0]:.0f}..{p_[0]+s_[0]:.0f}', 4)
    tx = ox + IW * sc + 14
    b.append(T(tx, 44, '部品一覧(座標[x,y,z] / 外形 / 頂部z / ドーム許容z)', 3.0, 'start', '#000', 'bold'))
    for n, it in enumerate(L['items'], 1):
        x, y, z = it['pos']; w_, h_, d_ = it['size']; dm = max(min(x, IW - (x + w_), y, IH - (y + h_)), 0); lim = dome_in(dm); ok = (z + d_ + 3) <= lim
        b += [circ(tx + 2.2, 50 + n * 12.5 - 1.0, 2.1, '#fff', '#900', .3), T(tx + 2.2, 50 + n * 12.5, str(n), 2.1, 'middle', '#900', 'bold'), T(tx + 7, 50 + n * 12.5, f'{lab.get(it["id"], it["id"])} ({it["id"]})', 2.6, 'start', '#000', 'bold'),
              T(tx + 7, 50 + n * 12.5 + 4.2, f'[{x:.1f}, {y:.1f}, {z:.1f}]  {w_:.0f}x{h_:.0f}x{d_:.0f}  頂{z+d_:.1f}  許容{lim:.0f}  {"OK" if ok else "要確認"}', 2.2, 'start', '#222' if ok else '#c0392b')]
    b.append(T(tx, 50 + (len(L['items']) + 1) * 12.5, '黒太線=AIOホース / 赤細線=電源・信号ケーブル(cables.json)', 2.3))
    b.append(T(tx, 50 + (len(L['items']) + 1) * 12.5 + 5, f'ドーム内面の許容z = {D["edge_inner_depth"]} + {DEPTH-D["edge_inner_depth"]:.0f}×smoothstep(d/{D["run"]}) (d=縁までの最短距離)。最大{DEPTH}。', 2.3))
    b.append(T(tx, 50 + (len(L['items']) + 1) * 12.5 + 10, 'ファン羽根・GPU/PSU内部は概形(UNVERIFIED)。寸法正=layout.json', 2.3, 'start', '#900'))
    save('10_placement_dimensioned.svg', b)

if __name__ == '__main__':
    gen_09(); gen_10()
