#!/usr/bin/env python3
"""自作する外装の製造図面を model/spec.json から生成する(DXF + 寸法入りSVG)。
実行: python tools/gen_mfg_drawings.py   (ezdxf が必要: uv pip install ezdxf)
注意: 寸法は設計値。板金/ガラスメーカーに渡す前に、最終BOM(部品確定)で再生成し、公差を協議すること。"""
import json, os, math
import ezdxf
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f'{R}/drawings'; os.makedirs(OUT, exist_ok=True)
S = json.load(open(f'{R}/model/spec.json'))
panel_w, panel_h = S['panels'][str(S['panel_size'])]['w'], S['panels'][str(S['panel_size'])]['h']
W, BEZ, CHIN, SLAB = S['body_w'], S['bezel'], S['chin'], S['slab_t']; H = panel_h + BEZ + CHIN
POD_T, POD_H, WALL = S['pod']['total_t'], S['pod']['h'], S['pod']['wall']; POD_W = W - S['pod']['side_margin']
ST_W, DROP, FOOT = S['stand']['w'], S['stand']['drop'], S['stand']['foot_depth']
CORNER = S['corner']; PO = S['panel_module']['outline']

import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import drawlib as DL
def svg_head(w, h, title, sheet, scale):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif">'] + DL.frame(title, sheet, scale=scale, material='A5052-H32 t2.0 / 強化ガラス t1.1 / A6063', finish='アルマイトII(硫酸) 10〜15um', note='注記: 図示の外形は設計値。展開図/曲げ線/穴径の詳細はCP部品図(drawings/parts)') + ['<g transform="translate(0,0)">']
def dim_h(x1, x2, y, label, off=10): return DL.dim_h(x1, x2, y, label, off)
def dim_v(x, y1, y2, label, off=10): return DL.dim_v(y1, y2, x + off, label, -off)
def rrect(x, y, w, h, r, **kw): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ' + ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items()) + '/>'

sc = 0.5   # 1/2 縮尺
def sheet(name, title, num, body, w=420, h=297):
    s = svg_head(w, h, title, num, '1:2') + body + ['</g></svg>']; open(f'{OUT}/{name}.svg', 'w', encoding='utf-8').write('\n'.join(s))

# ---------------- 01 前面ガラス ----------------
gx, gy = 40, 30; gw, gh = (W - .6) * sc, (H - .6) * sc
b = [rrect(gx, gy, gw, gh, CORNER * sc, fill='#eef0f3', stroke='#000', stroke_width=.5)]
b += [rrect(gx + (W - panel_w) / 2 * sc, gy + BEZ * sc, panel_w * sc, panel_h * sc, 0, fill='none', stroke='#555', stroke_width=.3, stroke_dasharray='2 1')]
b += [f'<text x="{gx+gw/2}" y="{gy+BEZ*sc+panel_h*sc/2}" font-size="5" text-anchor="middle" fill="#555">有効表示領域 {panel_w} x {panel_h}(印刷なし)</text>']
b += [f'<text x="{gx+gw/2}" y="{gy+gh-CHIN*sc/2}" font-size="4.4" text-anchor="middle" fill="#555">チン帯: 裏面印刷(Pantone指定、色は選択色)</text>']
b += [f'<circle cx="{gx+gw/2}" cy="{gy+4*sc+2}" r="{1.8*sc}" fill="none" stroke="#000" stroke-width=".3"/>', f'<text x="{gx+gw/2+6}" y="{gy+7}" font-size="3">カメラ窓 Ø4.0(要カメラモジュール確定)</text>']
b += dim_h(gx, gx + gw, gy + gh, f'{W-0.6:.1f}') + dim_v(gx + gw, gy, gy + gh, f'{H-0.6:.1f}')
b += [f'<text x="{gx}" y="{gy-6}" font-size="4">板厚 1.1 / 強化ガラス(化学強化) / 角R{CORNER} / 裏面印刷: ベゼル=白(#EDEEF0)、チン帯=パレット淡色(塗装でなくガラス裏面印刷)。AA外周の黒枠はパネルの遮光</text>']
sheet('01_front_glass', '前面ガラス(強化ガラス)', 'MFG-01', b)

# ---------------- 02 背板(バックプレート)とドーム位置(背面図)  v7 ----------------
SHEET_T = S['dome'].get('sheet_t', 2.0)
Dm = S['dome']; DW = W - 2 * Dm['inset_left_right']; DH = H - Dm['inset_bottom'] - Dm['inset_top']; DEP = Dm['total_t'] - SLAB
b = [rrect(gx, gy, W * sc, H * sc, CORNER * sc, fill='#d6d9de', stroke='#000', stroke_width=.5)]
px0 = gx + Dm['inset_left_right'] * sc; py0 = gy + Dm['inset_top'] * sc
b += [f'<rect x="{px0}" y="{py0}" width="{DW*sc}" height="{DH*sc}" rx="{Dm["corner_r"]*sc}" fill="#c4c8ce" stroke="#000" stroke-width=".4"/>']
for (kx, ky) in [tuple(k) for k in json.load(open(os.path.join(R, 'model', 'layout.json')))['keyholes']]:   # キーホール吊りピン(トレイ座標→背板座標: トレイ原点=ドーム内寸の左下)
    b.append(f'<circle cx="{px0 + (3 + kx) * sc}" cy="{gy + (H - Dm["inset_bottom"] - 3 - ky) * sc}" r="{2.5*sc}" fill="#c0392b"/>')
b += dim_h(gx, gx + W * sc, gy + H * sc, f'{W}') + dim_v(gx + W * sc, gy, gy + H * sc, f'{H:.1f}', 12) + dim_h(px0, px0 + DW * sc, py0 + DH * sc, f'ドーム外形幅 {DW:.0f}', 22)
b += [f'<text x="{gx}" y="{gy-6}" font-size="4">背板 A5052 t2.0(CP-03) とドーム(CP-07)の位置。余白 左右{Dm["inset_left_right"]}/下{Dm["inset_bottom"]}/上{Dm["inset_top"]}、角R{Dm["corner_r"]}。赤=吊りピン(肩ねじ Ø5)</text>']
sheet('02_back_plate_layout', '背板とドーム配置', 'MFG-02', b)

# ---------------- 03 ドーム(平面+プロファイル)  v7 ----------------
LAY = json.load(open(f'{R}/model/layout.json'))['items']; LI = {i['id']: i for i in LAY}
b = [rrect(gx, gy, DW * sc, DH * sc, Dm['corner_r'] * sc, fill='#c4c8ce', stroke='#000', stroke_width=.5)]
ix0, iy0 = 3, 3   # ドーム内寸の左下(トレイ座標原点)
x_, y_, a_, b_ = 36, 36, 590 - 72, 371.3 - 72      # v8: 背面全面の均一パーフォレーション(Ø2.4×ピッチ4.0, 縁から36mm内側)
b.append(f'<rect x="{gx + (DW - ix0 - x_ - a_) * sc}" y="{gy + (DH - iy0 - y_ - b_) * sc}" width="{a_*sc}" height="{b_*sc}" fill="#fff" stroke="#000" stroke-width=".3" stroke-dasharray="2,1"/>')
b.append(f'<text x="{gx + DW/2*sc}" y="{gy + DH/2*sc}" font-size="3.4" text-anchor="middle">均一パーフォレーション領域 {a_:.0f}×{b_:.0f} (Ø2.4 千鳥 ピッチ4.0, 板厚2.0)</text>')
for (nm, x, w_, h_) in (('I/O スロット', LI['board']['pos'][0] + 12, 120, 22), ('GPU出力スロット', LI['gpu']['pos'][0] + 4, LI['gpu']['size'][0] - 8, 20), ('ACインレット', LI['ac_inlet']['pos'][0] - 2, 32, 26)):
    b.append(f'<rect x="{gx + (DW - ix0 - x - w_) * sc}" y="{gy + (DH - 6 - h_) * sc}" width="{w_*sc}" height="{h_*sc}" rx="2" fill="#fff" stroke="#c0392b" stroke-width=".4"/><text x="{gx + (DW - ix0 - x - w_/2) * sc}" y="{gy + (DH - 6 - h_/2) * sc}" font-size="2.4" text-anchor="middle" fill="#c0392b">{nm}</text>')
b.append(f'<rect x="{gx + (DW/2 - 40) * sc}" y="{gy + 60 * sc}" width="{80*sc}" height="{30*sc}" fill="none" stroke="#06c" stroke-width=".4" stroke-dasharray="1.5,1"/><text x="{gx + DW/2*sc}" y="{gy + 76 * sc}" font-size="2.4" text-anchor="middle" fill="#06c">RF窓ゾーン(平板 60×30, 格子裏)</text>')
b += dim_h(gx, gx + DW * sc, gy + DH * sc, f'{DW:.0f}') + dim_v(gx + DW * sc, gy, gy + DH * sc, f'{DH:.1f}')
# プロファイル(縁→中央): 内面深さ=12+75*smoothstep(d/run)
pts = []
for k_ in range(0, 61, 3):
    s_ = k_ / Dm['run']; dep = Dm['edge_inner_depth'] + (DEP - 3 - Dm['edge_inner_depth']) * s_ * s_ * (3 - 2 * s_); pts.append((gx + DW * sc + 25 + k_ * 0.6, gy + 10 + dep * 0.6))
b.append('<polyline fill="none" stroke="#000" stroke-width=".6" points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '"/>')
b.append(f'<text x="{gx+DW*sc+10}" y="{gy+4}" font-size="2.8">縁→内側プロファイル(内奥行 {Dm["edge_inner_depth"]}→{DEP-3}mm)</text>')
b += [f'<text x="{gx}" y="{gy-6}" font-size="4">ドーム CP-07(背面から見た図: x反転): A5052 t{SHEET_T} / 均一パーフォレーション Ø2.4×ピッチ4.0 千鳥 / 下辺ラッチ6+上辺フック6 / 位置決めピン穴Ø4×2 / EMIガスケット溝 3.0×1.5 / アルマイトII</text>']
sheet('03_pod_cover', 'ドーム(背面カバー)', 'MFG-03', b)

# ---------------- 04 断面(厚み構成) v7 ----------------
x0, y0 = 60, 40; k = 1.6
b = []
stack = [(1.1, '前面ガラス', '#bcd'), (0.9, 'エアギャップ(OCA無し)', '#fff'), (PO[2], f'液晶モジュール {PO[2]}', '#9c9'), (4.0, '空気層', '#fff'), (3.0, '断熱シート', '#cb9'), (2.0, '背板 A5052', '#ccd')]
x = x0
for t_, n, c in stack:
    b.append(f'<rect x="{x}" y="{y0}" width="{t_*k}" height="90" fill="{c}" stroke="#000" stroke-width=".3"/>'); b.append(f'<text x="{x+t_*k/2}" y="{y0-3}" font-size="2.8" text-anchor="middle" transform="rotate(-30 {x+t_*k/2} {y0-3})">{n}</text>'); x += t_ * k
b.append(f'<rect x="{x}" y="{y0+90*0.52}" width="{(Dm["total_t"]-SLAB)*k}" height="{90*0.48}" fill="#dde" stroke="#000" stroke-width=".3"/>')
b += dim_h(x0, x0 + SLAB * k, y0 + 90, f'スラブ {SLAB}', 8) + dim_h(x0, x0 + Dm['total_t'] * k, y0 + 90, f'総厚 {Dm["total_t"]}', 20)
b += [f'<text x="{x0}" y="{y0+135}" font-size="4">厚み構成(拡大 x1.6 の概略図)。ドーム板厚 t{SHEET_T}(外面最大厚 {Dm["total_t"]})。内部有効奥行 最大 {Dm["total_t"]-SLAB-WALL}mm</text>']
sheet('04_section_stack', '厚み構成(断面)', 'MFG-04', b)

# ---------------- 05 スタンド(v9: 足300×290 + 首振りユニット + ネック + チルトバランサ) ----------------
SWv = S['swivel']; STv = S['stand']; HYv = S['hinge']['axis_y']; BALv = json.load(open(f'{R}/model/balance.json'))
b = []; s5 = 0.5
# 平面図(上から) 原点 (40,50)。上=背面側 / 下=前面側
ox, oy = 40, 50; fw5, fd5 = STv['foot_w'], STv['foot_depth']; cx5, cy5 = ox + fw5 * s5 / 2, oy + STv['foot_back'] * s5      # 首振り軸(足の中心線, 前100/後190)
b.append(rrect(ox, oy, fw5 * s5, fd5 * s5, 3, fill='#e3e5e8', stroke='#000', stroke_width=.5))
b.append(f'<circle cx="{cx5}" cy="{cy5}" r="{SWv["bearing_od"]/2*s5}" fill="#c8cbd0" stroke="#000" stroke-width=".4"/><circle cx="{cx5}" cy="{cy5}" r="{SWv["bearing_id"]/2*s5}" fill="#fff" stroke="#000" stroke-width=".3"/><circle cx="{cx5}" cy="{cy5}" r="{55*s5}" fill="none" stroke="#000" stroke-width=".3" stroke-dasharray="2 1"/>')
for sg_ in (-1, 1):
    ang = math.radians(90 + sg_ * (SWv['range_deg'] + 8.6)); b.append(f'<circle cx="{cx5 + 60*s5*math.cos(ang):.1f}" cy="{cy5 + 60*s5*math.sin(ang):.1f}" r="{4*s5}" fill="#333"/>')
for k_ in range(6):
    for (r_, lab) in ((SWv['pcd_inner']/2, 'i'), (SWv['pcd_outer']/2, 'o')):
        an = math.radians(k_ * 60 + (30 if lab == 'i' else 0)); b.append(f'<circle cx="{cx5 + r_*s5*math.cos(an):.1f}" cy="{cy5 + r_*s5*math.sin(an):.1f}" r="1.2" fill="none" stroke="#000" stroke-width=".25"/>')
for sx_ in (-1, 1):
    for sy_ in (-1, 1): b.append(f'<circle cx="{ox + fw5*s5/2 + sx_*(fw5/2-24)*s5}" cy="{oy + fd5*s5/2 + sy_*(fd5/2-24)*s5}" r="{10*s5}" fill="#444"/>')
b += dim_h(ox, ox + fw5 * s5, oy + fd5 * s5 + 6, f'幅 {fw5}', 8) + dim_v(ox + fw5 * s5 + 6, oy, oy + fd5 * s5, f'奥行 {fd5} (軸から前{STv["foot_front"]}/後{STv["foot_back"]})', 8)
b += dim_v(ox - 6, oy, cy5, f'後 {STv["foot_back"]}', 6) + dim_v(ox - 14, cy5, oy + fd5 * s5, f'前 {STv["foot_front"]}', 6)
b.append(f'<text x="{ox}" y="{oy-8}" font-size="4">平面図(上=背面) 首振りユニット Ø{SWv["bearing_od"]:g}軸受 / ストッパポスト r60 ±{SWv["range_deg"]+8.6:.1f}° / 軸受ボルト 内輪PCD{SWv["pcd_inner"]:g}×6・外輪PCD{SWv["pcd_outer"]:g}×6 / ゴム足Ø20×4</text>')
# 側面断面(右へ): 縦は y=0 を地面。横=z(前面が左)
sx0, sy0 = 250, 150; s6 = 0.9
def Y(y): return sy0 - (y + DROP + 12) * s6         # y(設計)→図の縦(上が+)
b.append(rrect(sx0, Y(-DROP), fd5 * s6 * 0.5, 12 * s6, 1, fill='#e3e5e8', stroke='#000', stroke_width=.4))      # 足(縮尺注: 側面図は奥行を0.5倍に圧縮表示)
zc6 = sx0 + STv['foot_front'] * s6 * 0.5
for i_, (lab, h_, col) in enumerate((('ステータ板 t6', 6, '#c8cbd0'), ('クロスローラ軸受 12', 12, '#aeb3ba'), ('ロータ板 t6 (+1内輪ボス)', 7, '#c8cbd0'))):
    y0_ = -DROP + sum(h for h in (6, 12, 7)[:i_]); b.append(rrect(zc6 - 55 * s6 / 2 * 1.0, Y(y0_ + h_), 55 * s6, h_ * s6, .5, fill=col, stroke='#000', stroke_width=.3)); b.append(f'<text x="{zc6+34*s6}" y="{Y(y0_+h_/2)+1}" font-size="2.4">{lab}</text>')
b.append(rrect(zc6 - 14 * s6, Y(HYv + 11), 28 * s6, (HYv + 11 - (-DROP + SWv['stack_h'])) * s6, 0.5, fill='#d7dadf', stroke='#000', stroke_width=.4))         # ネック側板(幅28)
b.append(f'<circle cx="{zc6}" cy="{Y(HYv)}" r="{11*s6}" fill="#bfc3c9" stroke="#000" stroke-width=".4"/><circle cx="{zc6}" cy="{Y(HYv)}" r="{5*s6}" fill="#555"/>')          # 摩擦ヒンジ+軸
e_, s_ = BALv['e'], BALv['s']
b.append(f'<line x1="{zc6}" y1="{Y(HYv)}" x2="{zc6}" y2="{Y(HYv-e_)}" stroke="#a00" stroke-width="1.4"/><line x1="{zc6}" y1="{Y(HYv-e_)}" x2="{zc6}" y2="{Y(HYv-s_)}" stroke="#06a" stroke-width="2.2"/>')
b.append(f'<text x="{zc6+10}" y="{Y(HYv-e_)+1}" font-size="2.4" fill="#a00">尾部レバー e={e_}</text><text x="{zc6+10}" y="{Y(HYv-(e_+s_)/2)+1}" font-size="2.4" fill="#06a">ダイスプリング(取付長{BALv["lmin"]:.0f}〜{BALv["lmax"]:.0f}) アンカー s={s_}</text>')
b += dim_v(zc6 + 45, Y(-DROP), Y(HYv), f'足上面〜ヒンジ軸 {DROP+HYv}', 8) + dim_v(zc6 - 40, Y(-DROP + SWv['stack_h']), Y(-DROP), f'首振りユニット {SWv["stack_h"]:g}', 8)
b.append(f'<text x="{sx0-60}" y="{sy0-125}" font-size="4">側面断面(奥行は0.5倍に圧縮)</text><text x="{sx0-60}" y="{sy0-119}" font-size="2.8">足t12+ballast / 首振り積層25 / ネック側板 / ヒンジ軸Ø10+摩擦ヒンジ / バランサ</text>')
b.append(f'<text x="40" y="{oy+fd5*s5+40}" font-size="3">注記: チルト {S["hinge"]["tilt_min_deg"]:+g}°〜{S["hinge"]["tilt_max_deg"]:+g}°(ゴムストッパ)、首振り ±{SWv["range_deg"]:g}°(ゴムポスト)。ballast鋼板 {STv["ballast_kg"]}kg。部品: CP-10/20/21/22/23。型番は U26/U50/U51。図面はPRELIMINARY(設計値)。</text>')
sheet('05_stand', 'スタンド(足・首振り・ネック・バランサ)', 'MFG-05', b)

# ---------------- DXF (v8: 現行形状。レイヤ別・実寸 mm・単位mm。背板/トレイ/ドームは前面視の座標(x右/y上)) ----------------
doc = ezdxf.new('R2010'); doc.units = 4; msp = doc.modelspace()
for ly, col in (('GLASS_OUTLINE', 7), ('GLASS_HOLES', 1), ('BACKPLATE_OUTLINE', 7), ('BACKPLATE_HOLES', 1), ('TRAY_OUTLINE', 7), ('TRAY_KEYHOLE', 1), ('TRAY_STANDOFF_HOLES', 3), ('DOME_OUTLINE', 7), ('DOME_PERF_ZONE', 5), ('DOME_PERF_HOLES', 2), ('DOME_SLOTS', 1), ('DOME_LATCH_HOOK_PIN', 3), ('DOME_MAGNET', 4), ('TEXT_NOTE', 7)): doc.layers.add(ly, color=col)
def dxf_rrect(x, y, w, h, r, layer):
    for (a, b_, c, d) in [(x + r, y, x + w - r, y), (x + w, y + r, x + w, y + h - r), (x + w - r, y + h, x + r, y + h), (x, y + h - r, x, y + r)]: msp.add_line((a, b_), (c, d), dxfattribs={'layer': layer})
    for (cx, cy, a0) in [(x + w - r, y + r, 270), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)]: msp.add_arc((cx, cy), r, a0, a0 + 90, dxfattribs={'layer': layer})
LAYJ = json.load(open(f'{R}/model/layout.json')); LI2 = {i_['id']: i_ for i_ in LAYJ['items']}
def note(x, y, s, h=6): msp.add_text(s, dxfattribs={'layer': 'TEXT_NOTE', 'height': h, 'insert': (x, y)})
# (1) 前面ガラス t1.1: 外形 + カメラ窓Ø4.0 + マイク穴Ø1.0×2
OX = 0; dxf_rrect(OX, 0, W, H, CORNER, 'GLASS_OUTLINE'); msp.add_circle((OX + W / 2, H - 5), 2.0, dxfattribs={'layer': 'GLASS_HOLES'})
for sx_ in (-70, 70): msp.add_circle((OX + W / 2 + sx_, H - 5), 0.5, dxfattribs={'layer': 'GLASS_HOLES'})
note(OX, -12, 'GLASS t1.1 chemically tempered / AR+AFC / camera hole D4.0, mic holes D1.0 x2 (center y = H-5)')
# (2) 背板 A5052 t2.0: 外形 + 吊りピン座(M3下穴 Ø2.5) + ヒンジブロックM6貫通(Ø6.6) + 接地スタッド(M4 Ø3.3)
OX = 800; dxf_rrect(OX, 0, W, H, CORNER, 'BACKPLATE_OUTLINE')
ix0 = Dm['inset_left_right'] + WALL; iy0 = Dm['inset_bottom'] + WALL      # トレイ内座標の原点(背板座標)
for (kx, ky) in LAYJ['keyholes']: msp.add_circle((OX + ix0 + kx, iy0 + ky + 12), 1.25, dxfattribs={'layer': 'BACKPLATE_HOLES'})       # 吊りピン M3下穴(掛け位置=細溝の上端)
for sx_ in (-55, 55):
    for yy_ in (5, 17): msp.add_circle((OX + W / 2 + sx_, yy_), 3.3, dxfattribs={'layer': 'BACKPLATE_HOLES'})                            # ヒンジブロックM6貫通
msp.add_circle((OX + W / 2 + 100, 10), 1.65, dxfattribs={'layer': 'BACKPLATE_HOLES'})                                                # 接地スタッドM4
note(OX, -12, 'BACKPLATE A5052-H32 t2.0 / hang-pin M3 tapped (PEM TSOA) x4 at keyhole pin positions / hinge block M6 clearance D6.6 x4 / PE stud M4')
# (3) トレイ A5052 t2.0 590x371.3 R44: キーホール(丸Ø9.2 + 細溝W5.1×12) + スタンドオフ穴(Ø4.0 PEM圧入: 規格値 U17/U29)
OX = 1600; dxf_rrect(OX, 0, 590, 371.3, 44, 'TRAY_OUTLINE')
for (kx, ky) in LAYJ['keyholes']:
    msp.add_circle((OX + kx, ky), 4.6, dxfattribs={'layer': 'TRAY_KEYHOLE'}); msp.add_line((OX + kx - 2.55, ky), (OX + kx - 2.55, ky + 12), dxfattribs={'layer': 'TRAY_KEYHOLE'}); msp.add_line((OX + kx + 2.55, ky), (OX + kx + 2.55, ky + 12), dxfattribs={'layer': 'TRAY_KEYHOLE'}); msp.add_arc((OX + kx, ky + 12), 2.55, 0, 180, dxfattribs={'layer': 'TRAY_KEYHOLE'})
HOLES = []      # (部品, x, y)
bx_, by_, _bz = LI2['board']['pos']
for k, (hx, hy) in enumerate(((10.2, 6.4), (165.1, 6.4), (10.2, 163.8), (165.1, 163.8))): HOLES.append(('board(ITX規格値 U17)', bx_ + hx, by_ + hy))
px_, py_, _ = LI2['psu']['pos']; psw, psh, _ = LI2['psu']['size']
for (dx, dy) in ((8, 8), (psw - 8, 8), (8, psh - 8), (psw - 8, psh - 8)): HOLES.append(('psu(SFX: 仮の角穴 U17)', px_ + dx, py_ + dy))
rx_, ry_, _ = LI2['radiator']['pos']
for (dx, dy) in ((10, 10), (110, 10), (10, 267), (110, 267)): HOLES.append(('radiator(ARCTIC図面で要確認)', rx_ + dx, ry_ + dy))
cx_, cy_, _ = LI2['ctrl_board']['pos']
for (dx, dy) in ((4, 4), (51, 4), (4, 146), (51, 146)): HOLES.append(('ctrl_board(仮)', cx_ + dx, cy_ + dy))
gx_, gy_, _ = LI2['gpu']['pos']
for (dx, dy) in ((20, 12), (130, 12)): HOLES.append(('gpu cradle', gx_ + dx, gy_ + dy))
HOLES += [('tray拘束ネジ(M3 T10)', 295 - 60, 14), ('tray拘束ネジ(M3 T10)', 295 + 60, 14), ('PEスタッド M4', 40, 40)]
for (nm, x_, y_) in HOLES: msp.add_circle((OX + x_, y_), 2.0 if 'M4' not in nm else 2.1, dxfattribs={'layer': 'TRAY_STANDOFF_HOLES'})
note(OX, -12, 'TRAY A5052-H32 t2.0 590x371.3 R44 / keyhole D9.2 + slot W5.1x12 (up) / PEM TSOA-M3 holes D4.0 (values pending U17/U29)')
# (4) ドーム A5052 t2.0: 外形 596x377.3 R50、均一パーフォレーション Ø2.4 ピッチ4.0 千鳥、下辺スロット、ラッチ/フック/ピン/磁石位置
OX = 2400; DWd, DHd = W - 2 * Dm['inset_left_right'], H - Dm['inset_bottom'] - Dm['inset_top']
dxf_rrect(OX, 0, DWd, DHd, Dm['corner_r'], 'DOME_OUTLINE')
zx0, zy0, zx1, zy1 = WALL + 36, WALL + 36, DWd - WALL - 36, DHd - WALL - 36
msp.add_lwpolyline([(OX + zx0, zy0), (OX + zx1, zy0), (OX + zx1, zy1), (OX + zx0, zy1)], close=True, dxfattribs={'layer': 'DOME_PERF_ZONE'})
row = 0; yy = zy0
while yy <= zy1:
    xx = zx0 + (2.0 if row % 2 else 0)
    while xx <= zx1: msp.add_circle((OX + xx, yy), 1.2, dxfattribs={'layer': 'DOME_PERF_HOLES'}); xx += 4.0
    yy += 4.0 * .866; row += 1
for (nm, x_, w_, h_) in (('IO', LI2['board']['pos'][0] + 12, 120, 22), ('GPU', LI2['gpu']['pos'][0] + 4, LI2['gpu']['size'][0] - 8, 20), ('AC', LI2['ac_inlet']['pos'][0] - 2, 32, 26)):
    xx0 = WALL + x_; msp.add_lwpolyline([(OX + xx0, 0), (OX + xx0 + w_, 0), (OX + xx0 + w_, h_ + 6), (OX + xx0, h_ + 6)], close=True, dxfattribs={'layer': 'DOME_SLOTS'})
for k, xd in enumerate((-250, -150, -50, 50, 150, 250)):
    msp.add_circle((OX + DWd / 2 + xd, 5.5), 4.1, dxfattribs={'layer': 'DOME_LATCH_HOOK_PIN'})                               # 下辺ラッチ穴 Ø8.2
    msp.add_lwpolyline([(OX + DWd / 2 + xd - 7, DHd - 7), (OX + DWd / 2 + xd + 7, DHd - 7), (OX + DWd / 2 + xd + 7, DHd), (OX + DWd / 2 + xd - 7, DHd)], close=True, dxfattribs={'layer': 'DOME_LATCH_HOOK_PIN'})   # 上辺フック爪 14x7
for (dxp, dyp) in ((-180, DHd - 20), (140, DHd - 20)): msp.add_circle((OX + DWd / 2 + dxp, dyp), 2.0, dxfattribs={'layer': 'DOME_LATCH_HOOK_PIN'})
mags = [(-200, DHd - 10), (0, DHd - 10), (200, DHd - 10), (-200, 10), (0, 10), (200, 10)] + [(-DWd / 2 + 10 + DWd / 2, DHd * f) for f in (.25, .5, .75)] + [(DWd - 10, DHd * f) for f in (.25, .5, .75)]
for k, (mx, my) in enumerate(mags): msp.add_circle((OX + (DWd / 2 + mx if k < 6 else mx), my), 4.05, dxfattribs={'layer': 'DOME_MAGNET'})
note(OX, -12, 'DOME A5052 t2.0 596x377.3 R50 (flat pattern pending: forming/drawing vendor) / perforation D2.4 pitch 4.0 staggered / latch holes D8.2 x6, hook tabs x6, dowel D4 x2, magnet pockets D8.1 x12')
doc.saveas(f'{OUT}/outlines.dxf')
# 穴座標表(単一情報源: layout.json + 規格値)
tbl = ['# 穴・開口の座標表 (自動生成: tools/gen_mfg_drawings.py)', '', '座標: トレイ内寸の左下原点(mm)。**規格値/仮値(U17/U29)を含む**: 基板=Mini-ITX規格穴、PSU=SFXの仮の角穴、ラジエーター=ARCTIC公式図で要確認。実部品の穴図が確定したら更新。', '', '## トレイ(CP-06) スタンドオフ/ネジ穴 Ø4.0', '| # | 部品 | x | y |', '|---|---|---|---|']
for n, (nm, x_, y_) in enumerate(HOLES, 1): tbl.append(f'| {n} | {nm} | {x_:.1f} | {y_:.1f} |')
tbl += ['', '## キーホール(トレイ丸穴中心 / 背板ピン位置=y+12)', '| # | トレイ丸穴 x,y | 背板M3(ピン) x,y |', '|---|---|---|'] + [f'| {n} | ({kx}, {ky}) | ({kx}, {ky + 12}) |' for n, (kx, ky) in enumerate(LAYJ['keyholes'], 1)]
tbl += ['', '## ドーム(CP-07) 加工位置(ドーム外形の左下原点)', '- 下辺ラッチ穴 Ø8.2 ×6: x = 298 + {-250,-150,-50,50,150,250}, y = 5.5', '- 上辺フック爪 14×7 ×6: 同x, y = 370.3〜377.3', '- 位置決めピン穴 Ø4.0 ×2: x = 298-180, 298+140, y = 357.3', '- 磁石ポケット Ø8.1 ×12 / パーフォレーション領域 ' + f'{zx1-zx0:.0f}×{zy1-zy0:.0f} (縁から{WALL+36}mm内側), Ø2.4 ピッチ4.0 千鳥', '- 下辺スロット: I/O 120×28 / GPU出力 ' + f'{LI2["gpu"]["size"][0]-8:.0f}×26 / AC 32×32 (幅×高さ, 下端開放)']
open(f'{R}/docs/spec/hole-table.md', 'w', encoding='utf-8').write('\n'.join(tbl) + '\n')
print('ok: drawings/*.svg, outlines.dxf, docs/spec/hole-table.md')
