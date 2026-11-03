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

def svg_head(w, h, title, sheet, scale):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif"><rect width="100%" height="100%" fill="#fff"/>',
            f'<rect x="4" y="4" width="{w-8}" height="{h-8}" fill="none" stroke="#000" stroke-width="0.5"/>',
            f'<rect x="{w-150}" y="{h-34}" width="146" height="30" fill="none" stroke="#000" stroke-width="0.4"/>',
            f'<text x="{w-146}" y="{h-24}" font-size="5">{title}</text><text x="{w-146}" y="{h-17}" font-size="3.4">図番 {sheet} / 縮尺 {scale} / 単位 mm / 第三角法</text>',
            f'<text x="{w-146}" y="{h-11}" font-size="3.4">普通公差 ±0.3(板金) / ±0.2(ガラス外形) / 表面 アルマイト</text>',
            f'<text x="{w-146}" y="{h-7}" font-size="3">設計値(未承認)。製造前に最終BOMで再生成すること。</text>']
def dim_h(x1, x2, y, label, off=10): return [f'<line x1="{x1}" y1="{y+off}" x2="{x2}" y2="{y+off}" stroke="#c0392b" stroke-width="0.3"/>', f'<line x1="{x1}" y1="{y}" x2="{x1}" y2="{y+off+2}" stroke="#c0392b" stroke-width="0.2"/>', f'<line x1="{x2}" y1="{y}" x2="{x2}" y2="{y+off+2}" stroke="#c0392b" stroke-width="0.2"/>', f'<text x="{(x1+x2)/2}" y="{y+off-1.5}" font-size="3.6" text-anchor="middle" fill="#c0392b">{label}</text>']
def dim_v(x, y1, y2, label, off=10): return [f'<line x1="{x+off}" y1="{y1}" x2="{x+off}" y2="{y2}" stroke="#c0392b" stroke-width="0.3"/>', f'<line x1="{x}" y1="{y1}" x2="{x+off+2}" y2="{y1}" stroke="#c0392b" stroke-width="0.2"/>', f'<line x1="{x}" y1="{y2}" x2="{x+off+2}" y2="{y2}" stroke="#c0392b" stroke-width="0.2"/>', f'<text x="{x+off-1.5}" y="{(y1+y2)/2}" font-size="3.6" text-anchor="middle" fill="#c0392b" transform="rotate(-90 {x+off-1.5} {(y1+y2)/2})">{label}</text>']
def rrect(x, y, w, h, r, **kw): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ' + ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items()) + '/>'

sc = 0.5   # 1/2 縮尺
def sheet(name, title, num, body, w=420, h=297):
    s = svg_head(w, h, title, num, '1:2') + body + ['</svg>']; open(f'{OUT}/{name}.svg', 'w', encoding='utf-8').write('\n'.join(s))

# ---------------- 01 前面ガラス ----------------
gx, gy = 40, 30; gw, gh = (W - .6) * sc, (H - .6) * sc
b = [rrect(gx, gy, gw, gh, CORNER * sc, fill='#eef0f3', stroke='#000', stroke_width=.5)]
b += [rrect(gx + (W - panel_w) / 2 * sc, gy + BEZ * sc, panel_w * sc, panel_h * sc, 0, fill='none', stroke='#555', stroke_width=.3, stroke_dasharray='2 1')]
b += [f'<text x="{gx+gw/2}" y="{gy+BEZ*sc+panel_h*sc/2}" font-size="5" text-anchor="middle" fill="#555">有効表示領域 {panel_w} x {panel_h}(印刷なし)</text>']
b += [f'<text x="{gx+gw/2}" y="{gy+gh-CHIN*sc/2}" font-size="4.4" text-anchor="middle" fill="#555">チン帯: 裏面印刷(Pantone指定、色は選択色)</text>']
b += [f'<circle cx="{gx+gw/2}" cy="{gy+4*sc+2}" r="{1.8*sc}" fill="none" stroke="#000" stroke-width=".3"/>', f'<text x="{gx+gw/2+6}" y="{gy+7}" font-size="3">カメラ窓 φ3.6(要カメラモジュール確定)</text>']
b += dim_h(gx, gx + gw, gy + gh, f'{W-0.6:.1f}') + dim_v(gx + gw, gy, gy + gh, f'{H-0.6:.1f}')
b += [f'<text x="{gx}" y="{gy-6}" font-size="4">板厚 1.1 / 強化ガラス(化学強化) / 角R{CORNER} / 裏面: 黒ベゼル印刷+白縁(#EDEEF0)+チン帯</text>']
sheet('01_front_glass', '前面ガラス(強化ガラス)', 'MFG-01', b)

# ---------------- 02 背面プレートとポッドの配置(背面図) ----------------
b = [rrect(gx, gy, W * sc, H * sc, CORNER * sc, fill='#d6d9de', stroke='#000', stroke_width=.5)]
px0 = gx + (W - POD_W) / 2 * sc; py0 = gy + (H - POD_H) * sc
b += [f'<rect x="{px0}" y="{py0}" width="{POD_W*sc}" height="{POD_H*sc}" rx="{4}" fill="#c4c8ce" stroke="#000" stroke-width=".4"/>']
b += dim_h(gx, gx + W * sc, gy + H * sc, f'{W}') + dim_v(gx + W * sc, gy, gy + H * sc, f'{H:.1f}', 12) + dim_h(px0, px0 + POD_W * sc, py0 + POD_H * sc, f'ポッド幅 {POD_W}', 22)
b += [f'<text x="{gx}" y="{gy-6}" font-size="4">背面図: A5052 t2.0 背面プレート + ポッド(別図 03)。スタンド取付位置は中央、ヒンジ中心 y={DROP-14}</text>']
sheet('02_back_plate_layout', '背面プレートとポッド配置', 'MFG-02', b)

# ---------------- 03 ポッドカバー(吸排気穴パターン) ----------------
b = [rrect(gx, gy, POD_W * sc, POD_H * sc, 4, fill='#c4c8ce', stroke='#000', stroke_width=.5)]
for (cx, cy, rr) in [(WALL + 196 + 60, WALL + 18 + 72, 48), (WALL + 405 + 60, WALL + 20 + 60, 56)]:
    step = 7.0; row = 0; yy = -rr
    while yy <= rr:
        xx = -rr
        while xx <= rr:
            x = xx + (step / 2 if row % 2 else 0)
            if math.hypot(x, yy) < rr - 3: b.append(f'<circle cx="{gx+(cx+x)*sc}" cy="{gy+(POD_H-(cy+yy))*sc}" r="{2.1*sc}" fill="#fff" stroke="#000" stroke-width=".15"/>')
            xx += step
        yy += step * .87; row += 1
b += dim_h(gx, gx + POD_W * sc, gy + POD_H * sc, f'{POD_W}') + dim_v(gx + POD_W * sc, gy, gy + POD_H * sc, f'{POD_H}')
b += [f'<text x="{gx}" y="{gy-6}" font-size="4">ポッド背面カバー A5052 t{WALL} / 吸気穴 φ4.2 ピッチ7.0 千鳥(2領域) / 外周R10相当 / アルマイト</text>']
sheet('03_pod_cover', 'ポッド背面カバー', 'MFG-03', b)

# ---------------- 04 断面(厚み構成) ----------------
x0, y0 = 60, 40; k = 1.6
b = []
stack = [(1.1, '前面ガラス', '#bcd'), (0.4, 'OCA/接着', '#fe9'), (PO[2], f'液晶モジュール {PO[2]}', '#9c9'), (1.0, '隙間', '#fff'), (2.0, '背面プレート A5052', '#ccd')]
x = x0
for t, n, c in stack:
    b.append(f'<rect x="{x}" y="{y0}" width="{t*k}" height="90" fill="{c}" stroke="#000" stroke-width=".3"/>'); b.append(f'<text x="{x+t*k/2}" y="{y0-3}" font-size="2.8" text-anchor="middle" transform="rotate(-30 {x+t*k/2} {y0-3})">{n}</text>'); x += t * k
b.append(f'<rect x="{x}" y="{y0+90*0.52}" width="{(POD_T-SLAB)*k}" height="{90*0.48}" fill="#dde" stroke="#000" stroke-width=".3"/>')
b += dim_h(x0, x0 + SLAB * k, y0 + 90, f'スラブ {SLAB}', 8) + dim_h(x0, x0 + POD_T * k, y0 + 90, f'総厚 {POD_T}', 20)
b += [f'<text x="{x0}" y="{y0+135}" font-size="4">厚み構成(縮尺 1.6倍)。ポッド壁 t{WALL}。内部有効奥行 {POD_T-SLAB-WALL}mm</text>']
sheet('04_section_stack', '厚み構成(断面)', 'MFG-04', b)

# ---------------- 05 スタンド ----------------
b = [rrect(gx, gy, ST_W * sc, (DROP) * sc, 3, fill='#c8cbd0', stroke='#000', stroke_width=.5), rrect(gx - 10, gy + DROP * sc, (ST_W + 20) * sc, 6 * sc, 2, fill='#c8cbd0', stroke='#000', stroke_width=.5)]
b += dim_h(gx, gx + ST_W * sc, gy + DROP * sc + 4, f'幅 {ST_W}', 10) + dim_v(gx + ST_W * sc, gy, gy + DROP * sc, f'{DROP}', 6)
b += [f'<text x="{gx}" y="{gy-6}" font-size="4">スタンド(一枚板) A6063/A5052 t8 アルマイト。足 奥行{FOOT}。ヒンジ: 市販トルクヒンジ(型番はBOM確定後)</text>']
sheet('05_stand', 'スタンド', 'MFG-05', b)

# ---------------- DXF ----------------
doc = ezdxf.new('R2010'); doc.units = 4; msp = doc.modelspace()
def dxf_rrect(x, y, w, h, r, layer):
    for (a, b_, c, d) in [(x + r, y, x + w - r, y), (x + w, y + r, x + w, y + h - r), (x + w - r, y + h, x + r, y + h), (x, y + h - r, x, y + r)]: msp.add_line((a, b_), (c, d), dxfattribs={'layer': layer})
    for (cx, cy, a0) in [(x + w - r, y + r, 270), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)]: msp.add_arc((cx, cy), r, a0, a0 + 90, dxfattribs={'layer': layer})
dxf_rrect(0, 0, W - .6, H - .6, CORNER, 'GLASS_OUTLINE'); msp.add_circle(((W - .6) / 2, H - 5), 1.8, dxfattribs={'layer': 'GLASS_CAMERA'})
dxf_rrect(1000, 0, POD_W, POD_H, 4, 'POD_COVER')
for (cx, cy, rr) in [(WALL + 196 + 60, WALL + 18 + 72, 48), (WALL + 405 + 60, WALL + 20 + 60, 56)]:
    step = 7.0; row = 0; yy = -rr
    while yy <= rr:
        xx = -rr
        while xx <= rr:
            x = xx + (step / 2 if row % 2 else 0)
            if math.hypot(x, yy) < rr - 3: msp.add_circle((1000 + cx + x, cy + yy), 2.1, dxfattribs={'layer': 'POD_COVER_VENT'})
            xx += step
        yy += step * .87; row += 1
doc.saveas(f'{OUT}/outlines.dxf'); print('ok: drawings/*.svg, outlines.dxf')
