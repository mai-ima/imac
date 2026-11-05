#!/usr/bin/env python3
"""設計図一式(基板配置・寸法入り配置図・断面・配線図・エアフロー・分解組立・BOM)を model/*.json から生成する。
出力: drawings/09〜15_*.svg, model/cables.json, docs/wiring.md, docs/bom-final.md
実行: python3 tools/gen_package.py   (既存の出力は archive 自動保存の対象: git commit 時)"""
import json, os, math
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f'{R}/drawings'
S = json.load(open(f'{R}/model/spec.json')); L = json.load(open(f'{R}/model/layout.json')); P = json.load(open(f'{R}/model/parts.json'))
BL = json.load(open(f'{R}/model/x870i_layout.json'))
D = S['dome']; PH = S['panels'][str(S['panel_size'])]['h']; W = S['body_w']; H = PH + S['bezel'] + S['chin']
IW = W - 2 * D['inset_left_right'] - 6; IH = H - D['inset_bottom'] - D['inset_top'] - 6
DEPTH = D['total_t'] - S['slab_t'] - 3
def dome_in(d): s = max(0, min(1, d / D['run'])); return D['edge_inner_depth'] + (DEPTH - D['edge_inner_depth']) * (s * s * (3 - 2 * s))
I = {i['id']: i for i in L['items']}
def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;')
def head(title, num, w=420, h=297, note=''):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif"><defs><marker id="ar" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#222"/></marker><marker id="ag" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#1a7f37"/></marker></defs><rect width="100%" height="100%" fill="#fff"/>',
            f'<rect x="4" y="4" width="{w-8}" height="{h-8}" fill="none" stroke="#000" stroke-width=".5"/>',
            f'<rect x="{w-170}" y="{h-30}" width="166" height="26" fill="none" stroke="#000" stroke-width=".4"/>',
            f'<text x="{w-166}" y="{h-21}" font-size="5">{esc(title)}</text><text x="{w-166}" y="{h-14}" font-size="3.2">図番 {num} / 単位 mm / 設計値(未承認) / 生成: tools/gen_package.py</text>',
            f'<text x="{w-166}" y="{h-9}" font-size="3">{esc(note)}</text>']
def T(x, y, s, sz=3.2, a='start', fill='#222', extra=''): return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" text-anchor="{a}" fill="{fill}" {extra}>{esc(s)}</text>'
def rect(x, y, w, h, fill='none', st='#333', sw=.3, op=1, rx=0): return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{st}" stroke-width="{sw}"/>'
def line(x1, y1, x2, y2, st='#222', sw=.3, dash='', mk=''): return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{st}" stroke-width="{sw}" {("stroke-dasharray=%s" % chr(34)+dash+chr(34)) if dash else ""} {mk}/>'
def dimh(x1, x2, y, label, off=6):   # 水平寸法線
    return [line(x1, y, x1, y + off, '#888', .2), line(x2, y, x2, y + off, '#888', .2), line(x1, y + off - 1.5, x2, y + off - 1.5, '#06c', .25, '', 'marker-start="url(#ar)" marker-end="url(#ar)"'), T((x1 + x2) / 2, y + off - 2.2, label, 2.6, 'middle', '#06c')]
def dimv(y1, y2, x, label, off=-6):
    return [line(x, y1, x + off, y1, '#888', .2), line(x, y2, x + off, y2, '#888', .2), line(x + off + 1.5, y1, x + off + 1.5, y2, '#06c', .25, '', 'marker-start="url(#ar)" marker-end="url(#ar)"'), T(x + off - .8, (y1 + y2) / 2, label, 2.6, 'middle', '#06c', f'transform="rotate(-90 {x+off-.8:.1f} {(y1+y2)/2:.1f})"')]
COL = {'board': '#9ac8a6', 'cooler': '#e0b080', 'radiator': '#b0c4de', 'gpu': '#9aa0ad', 'riser': '#555', 'psu': '#c8c8c8', 'fan': '#d9c8a0', 'ctrl_board': '#a9c0d6', 'ssd': '#ccf0aa', 'ram': '#99ddee'}
def save(name, parts): open(f'{OUT}/{name}', 'w').write('\n'.join(parts) + '</svg>\n'); print('wrote', name)

# ================= 09 基板レイアウト(ASUS X870-I, 公式マニュアル図から実測) =================
sc = 1.2; ox, oy = 24, 38; B = 170
b = head('Mini-ITX基板 部品配置(ASUS ROG STRIX X870-I GAMING WIFI)', 'PKG-09', note='座標: 基板左下原点, x右/y上, I/O辺=下。出典 x870i_layout.json')
Y = lambda y: oy + (B - y) * sc; X = lambda x: ox + x * sc
b.append(rect(ox, oy, B * sc, B * sc, '#eaf3ea', '#000', .6))
feats = []
sx, sy = BL['socket_center']
feats += [('AM5ソケット(LGA1718, 40x40 IHS: AMD Ryzen 7 9800X3D)', sx - 30, sy - 30, 60, 60, '#cfd2d6'), ('CPU IHS 40x40', sx - 20, sy - 20, 40, 40, '#9da3ab')]
for i, (y0, y1) in enumerate(BL['dimm_slots']['y']): feats.append((f'DDR5 DIMMスロット{i+1} (x{BL["dimm_slots"]["x"][0]}-{BL["dimm_slots"]["x"][1]})', BL['dimm_slots']['x'][0], y0, BL['dimm_slots']['x'][1] - BL['dimm_slots']['x'][0], y1 - y0, '#9cd'))
a = BL['atx_pwr']; feats.append(('ATX 24ピン', a['x'][0], a['y'][0], a['x'][1] - a['x'][0], a['y'][1] - a['y'][0], '#fff'))
a = BL['cpu_12v']; feats.append(('CPU 8ピン(EPS)', a['x'][0], a['y'][0], a['x'][1] - a['x'][0], a['y'][1] - a['y'][0], '#fff'))
a = BL['pcie_x16']; feats.append(('PCIe 5.0 x16', a['x'][0], a['y'][0], a['x'][1] - a['x'][0], a['y'][1] - a['y'][0], '#555'))
a = BL['chipset']; feats.append(('チップセット(AMD X870)+ヒートシンク', a['x'][0], a['y'][0], a['x'][1] - a['x'][0], a['y'][1] - a['y'][0], '#bbb'))
feats.append(('M.2ドーターカード領域(M.2_1 Gen5 / M.2_2 Gen4)', 130, 79, 25, 59, '#d0e8c0'))
feats.append(('VRMヒートシンク+ファン(寸法は未確認・仮置き)', 8, 24, 98, 36, '#d8d8d8'))
for k, v in BL['io_x_ranges'].items(): feats.append((f'I/O {k}', v[0], -0.0, v[1] - v[0], 6, '#e8c0a0'))
for n, (lab, x, y, w, h, c) in enumerate(feats, 1):
    b.append(rect(X(x), Y(y + h), w * sc, h * sc, c, '#333', .3, .85)); b.append(T(X(x) + 1, Y(y + h) + 4, str(n), 3, 'start', '#900', 'font-weight="bold"'))
# ITXの取付穴(規格値は未確認: U17)。仮に 6.35mm / 163.8mm 系の4点
for (hx, hy) in ((10.2, 6.4), (165.1, 6.4), (10.2, 163.8), (165.1, 163.8)): b += [f'<circle cx="{X(hx):.1f}" cy="{Y(hy):.1f}" r="{2.2*sc:.1f}" fill="none" stroke="#c0392b" stroke-width=".4"/>', T(X(hx) + 4, Y(hy) - 3, f'穴({hx},{hy})', 2.2, 'start', '#c0392b')]
b += dimh(ox, ox + B * sc, oy + B * sc, '170.0', 8) + dimv(oy, oy + B * sc, ox, '170.0', -8)
b.append(T(ox, oy - 6, 'I/O辺(下)は背面ドーム下側のI/O開口に向ける。後部I/Oブロックの並びは未確認(U03)。穴座標はMini-ITX規格値(U17: 規格書で要確認)。', 3))
tx = 24 + B * sc + 22
b.append(T(tx, 40, '番号', 3.6, 'start', '#000', 'font-weight="bold"')); b.append(T(tx + 12, 40, '部位(位置[x,y]・大きさ)', 3.6, 'start', '#000', 'font-weight="bold"'))
for n, (lab, x, y, w, h, c) in enumerate(feats, 1): b.append(T(tx, 40 + n * 6.2, str(n), 3)); b.append(T(tx + 12, 40 + n * 6.2, f'{lab} [{x:.1f},{y:.1f}] {w:.1f}x{h:.1f}', 2.5))
b.append(T(tx, 40 + (len(feats) + 2) * 6.2, '※ 出典: ASUSマニュアルp.14のlayout図を実測(2024年版,U16)。', 2.5, 'start', '#900'))
save('09_board_layout.svg', b)

# ================= 10 寸法入り配置図(トレイ平面) =================
sc = 0.46; ox, oy = 30, 44
b = head('部品配置図(寸法・座標・ドーム余裕つき)', 'PKG-10', note='座標: トレイ内寸の左下原点(ドーム内側)。z=トレイ面からの高さ')
b.append(rect(ox, oy, IW * sc, IH * sc, '#f7f8fa', '#000', .5, 1, 14))
for it in L['items']:
    x, y, z = it['pos']; w, h, d = it['size']; i = it['id']
    b.append(rect(ox + x * sc, oy + (IH - y - h) * sc, w * sc, h * sc, COL.get(i, '#ddd'), '#333', .3, .8))
    b.append(T(ox + (x + w / 2) * sc, oy + (IH - y - h / 2) * sc, f'{i}', 3.2, 'middle', '#000', 'font-weight="bold"'))
    dm = min(x, IW - (x + w), y, IH - (y + h)); lim = dome_in(dm); top = z + d
    b.append(T(ox + (x + w / 2) * sc, oy + (IH - y - h / 2) * sc + 4, f'{w:.0f}x{h:.0f}x{d:.0f} z{z:.0f}-{top:.0f}', 2.4, 'middle'))
# 寸法線(原点基準)
for i in ('board', 'gpu', 'radiator', 'psu', 'fan', 'ctrl_board'):
    it = I[i]; x, y, z = it['pos']; w, h, _ = it['size']; 
b += dimh(ox, ox + IW * sc, oy + IH * sc, f'{IW:.0f}', 9) + dimv(oy, oy + IH * sc, ox, f'{IH:.0f}', -9)
for i, dy in (('board', 0), ('gpu', 5), ('radiator', 10)):
    it = I[i]; x, y, z = it['pos']; w, h, _ = it['size']
    b += dimh(ox + x * sc, ox + (x + w) * sc, oy + IH * sc + 4 + dy, f'{i} x={x:.1f}..{x+w:.1f}', 4)
for i, dy in (('fan', 0), ('psu', 5), ('ctrl_board', 10)):
    it = I[i]; x, y, z = it['pos']; w, h, _ = it['size']
    b += dimh(ox + x * sc, ox + (x + w) * sc, oy - 22 + dy, f'{i} x={x:.1f}..{x+w:.1f}', 4)
tx = ox + IW * sc + 22
b.append(T(tx, 46, '部品  座標[x,y,z] / 外形 / 頂部z / ドーム許容z', 3, 'start', '#000', 'font-weight="bold"'))
for n, it in enumerate(L['items']):
    x, y, z = it['pos']; w, h, d = it['size']; dm = min(x, IW - (x + w), y, IH - (y + h)); lim = dome_in(max(dm, 0))
    ok = (z + d + 3) <= lim
    b.append(T(tx, 54 + n * 11, it['id'], 2.7, 'start', '#000', 'font-weight="bold"'))
    b.append(T(tx, 54 + n * 11 + 4.5, f'[{x:.1f},{y:.1f},{z:.1f}] [{w:.1f},{h:.1f},{d:.1f}] 頂{z+d:.1f} 許容{lim:.0f}(縁{max(dm,0):.0f}) {"OK" if ok else "要確認"}', 2.3, 'start', '#000' if ok else '#c0392b'))
b.append(T(ox, oy + IH * sc + 32, f'ドーム内面: 許容z=12+{DEPTH-12:.0f}×smoothstep(d/{D["run"]}) (d=縁までの最短距離)、最大{DEPTH}。ssdはポンプ(z13.6〜)の下に潜る位置で干渉の可能性(U02/要試作)。', 2.8))
save('10_placement_dimensioned.svg', b)

# ================= 11 断面図(A-A: y=122 ソケット中心を通るx-z断面 / B-B: x=350 GPUを通る y-z断面) =================
def section(title, num, axis, cut, nm):
    s = 0.66; ox, oy = 24, 40; b = head(title, num, note='ドーム内面は設計値。斜線=トレイ(t2) / 部品は外形箱')
    span = IW if axis == 'x' else IH; zmax = DEPTH + 25
    base = oy + zmax * s + 4
    b.append(rect(ox, oy - 12, span * s, 12, '#d9dde2', '#000', .4)); b.append(T(ox + 3, oy - 3, f'前面スラブ(t18)・パネル', 3))
    pts = []
    for k in range(0, int(span) + 1, 4):
        # 断面上の位置kでの最短縁距離(他軸は中央付近=十分遠いとして切断線の値を使う)
        x_, y_ = (k, cut) if axis == 'x' else (cut, k)
        d = min(x_, IW - x_, y_, IH - y_); pts.append((ox + k * s, oy + dome_in(d) * s))
    b.append(f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px,py in pts)}" fill="none" stroke="#000" stroke-width=".7"/>')
    b.append(T(ox + span * s / 2, oy + DEPTH * s + 9, 'ドーム内面(外面は+3mm)', 3, 'middle', '#555'))
    b.append(rect(ox, oy, span * s, 2.0, '#8d9198', '#000', .3))
    for it in L['items']:
        x, y, z = it['pos']; w, h, d = it['size']
        lo, hi, c0, c1 = (x, x + w, y, y + h) if axis == 'x' else (y, y + h, x, x + w)
        if not (c0 <= cut <= c1): continue
        b.append(rect(ox + lo * s, oy + z * s, (hi - lo) * s, d * s, COL.get(it['id'], '#ddd'), '#333', .3, .85)); b.append(T(ox + (lo + hi) / 2 * s, oy + (z + d / 2) * s + 1, it['id'], 3, 'middle'))
    b += dimv(oy, oy + DEPTH * s, ox + span * s, f'ドーム最大内奥行 {DEPTH}', 10)
    b.append(T(ox, oy + zmax * s + 14, f'断面{nm}: {"y" if axis=="x" else "x"}={cut} の{"x-z" if axis=="x" else "y-z"}面。上=スラブ側(z=0)、下=背面方向。', 3.2))
    return b
save('11a_section_AA.svg', section('断面 A-A (y=122: CPU/ポンプ/ライザー/GPU/ラジエーター)', 'PKG-11A', 'x', 122, 'A-A'))
save('11b_section_BB.svg', section('断面 B-B (x=350: GPU/ラジエーター)', 'PKG-11B', 'y', 350, 'B-B') if False else section('断面 B-B (x=350: GPU)', 'PKG-11B', 'y', 350, 'B-B'))

# ================= 配線(ケーブル定義と長さ) =================
bx, by, bz = I['board']['pos']; gx, gy, gz = I['gpu']['pos']; px, py, pz = I['psu']['pos']; cx, cy, cz = I['ctrl_board']['pos']; Z1 = bz + 1.6
CAB = [
 dict(id='W1', name='ATX 24ピン', frm='PSU modular(24p)', to='基板 ATX24', awg=18, conn='24p (20+4)', ref_mm=300, pts=[(px+20, py-6, pz+25), (px+8, py-20, pz+30), (bx+36, by+176, Z1+20), (bx+38, by+164, Z1+12)]),
 dict(id='W2', name='CPU EPS 8ピン', frm='PSU modular(EPS)', to='基板 CPU_12V(8p)', awg=16, conn='EPS 4+4', ref_mm=400, pts=[(px+38, py-6, pz+25), (px+30, py-16, 30), (bx-6, 190, 26), (bx-6, by+40, 18), (bx+6, by+12, Z1+8)]),
 dict(id='W3', name='GPU PCIe 6+2ピン', frm='PSU modular(PCIe)', to='GPU 8ピン', awg=16, conn='PCIe 6+2', ref_mm=400, pts=[(px+76, py-6, pz+25), (px+100, py-20, 40), (300, 198, 58), (gx+102, gy+205, 58), (gx+102, gy+212, gz+42)]),
 dict(id='W4', name='コントローラ基板 12V', frm='PSU modular(SATA/周辺)', to='ctrl_board DC入力', awg=20, conn='SATA電源 or 2pin', ref_mm=0, pts=[(px+100, py+100, pz+20), (cx+20, cy-4, 14), (cx+20, cy+6, cz+4)]),
 dict(id='W5', name='アンビリカル(eDP 30p/12V/USB)', frm='ctrl_board eDP', to='パネル背面コネクタ', awg=0, conn='eDP 30p + 12V + USB2', ref_mm=0, pts=[(cx+146, cy+28, cz+5), (cx+146, cy+50, 10), (cx+120, IH-8, 6), (cx+120, IH+2, 1)]),
]
def plen(p): return sum(math.dist(p[i], p[i+1]) for i in range(len(p)-1))
for c in CAB: c['len_mm'] = round(plen(c['pts']) * 1.15); c['verdict'] = ('OK' if (c['ref_mm'] == 0 or c['len_mm'] <= c['ref_mm']) else '不足(延長/別ケーブル要)')
json.dump({'_doc': '配線定義(トレイ内座標)。長さ=経路折れ線長×1.15(余長)。ref_mm=PSU付属ケーブル長(小売記載、公式未確認)', 'cables': CAB}, open(f'{R}/model/cables.json', 'w'), ensure_ascii=False, indent=1)

# ================= 12 配線図 =================
b = head('配線図(電源・信号・冷却)', 'PKG-12', note='ケーブル長は経路折れ線長×1.15。PSU付属長は小売記載(未確認)')
def box(x, y, w, h, t, c='#eef', s=3.2): return [rect(x, y, w, h, c, '#333', .4, 1, 2), T(x + w / 2, y + h / 2 + 1, t, s, 'middle')]
b += [rect(20, 120, 40, 20, '#fde', '#333', .4, 1, 2)]; b.append(T(40, 128, 'AC100V', 3, 'middle')); b.append(T(40, 134, 'C14インレット', 3, 'middle'))
b += [rect(80, 115, 50, 30, '#ddd', '#333', .4, 1, 2)]; b.append(T(105, 126, 'Corsair SF750', 3.4, 'middle')); b.append(T(105, 133, 'SFX 750W 80+Plat', 2.8, 'middle')); b.append(T(105, 139, 'ATX3.1 / 12V-2x6対応', 2.6, 'middle'))
b.append(line(60, 130, 80, 130, '#c00', .6, '', 'marker-end="url(#ar)"')); b.append(T(70, 128, 'C13(AC)', 2.6, 'middle'))
tg = [('ASUS X870-I(ATX24+EPS)', 40, 'W1,W2'), ('ASUS Dual RTX 5060 Ti(8pin)', 75, 'W3'), ('4K eDPコントローラ(12V)', 110, 'W4'), ('Noctua NF-A12x25(基板FAN_HDR)', 145, '基板'), ('ARCTIC AIO ポンプ/P12 Pro×2(基板)', 180, '基板')]
for (nm, y, cid) in tg:
    b += box(190, y, 80, 22, nm, '#eef', 3)
    b.append(line(130, 130, 190, y + 11, '#06c' if cid.startswith('W') else '#888', .5, '' if cid.startswith('W') else '2,1', 'marker-end="url(#ar)"')); b.append(T(160, (130 + y + 11) / 2 - 2, cid, 2.8, 'middle', '#06c'))
b += box(300, 110, 60, 22, 'パネル 4K LM270WR3', '#fed', 3); b.append(line(270, 121, 300, 121, '#a50', .5, '', 'marker-end="url(#ar)"')); b.append(T(285, 118, 'W5 アンビリカル', 2.8, 'middle', '#a50'))
b.append(T(20, 215, 'ケーブル表', 4, 'start', '#000', 'font-weight="bold"'))
b.append(T(20, 222, 'ID', 3, 'start', '#000', 'font-weight="bold"')); 
for c0, tx_ in (('名称', 32), ('PSU側→機器側', 90), ('線径AWG', 170), ('設計長mm', 190), ('PSU付属mm', 212), ('判定', 240)): b.append(T(tx_, 222, c0, 3, 'start', '#000', 'font-weight="bold"'))
for n, c in enumerate(CAB):
    y = 229 + n * 6; b.append(T(20, y, c['id'], 3)); b.append(T(32, y, c['name'], 2.9)); b.append(T(90, y, f"{c['frm']} → {c['to']}", 2.7)); b.append(T(170, y, str(c['awg'] or '-'), 3)); b.append(T(190, y, str(c['len_mm']), 3)); b.append(T(212, y, str(c['ref_mm'] or '-'), 3)); b.append(T(240, y, c['verdict'], 3, 'start', '#000' if c['verdict'] == 'OK' else '#c0392b'))
b.append(T(20, 266, '電力: 12V系 CPU162W+GPU180W+その他≒60W ⇒ ピーク約400W / 750W = 53%(余裕47%)。補助電源はEPS×1, PCIe 8pin×1のみ使用(予備: EPS×1, PCIe×1, 12V-2x6×1)。', 3))
b.append(T(20, 272, '接地: AC保護アース→PSU筐体→トレイ(M3スタンドオフ接触)→ドーム(ガスケット)→背板の順で導通。ファンはPWM 4pin。', 3))
save('12_wiring_diagram.svg', b)

# ================= 13 エアフロー・熱 =================
sc = .46; ox, oy = 30, 44
b = head('エアフロー・熱設計(平面)', 'PKG-13', note='熱量は仕様値。風量は公称値の和(実機測定が必要)')
b.append(rect(ox, oy, IW * sc, IH * sc, '#f7f8fa', '#000', .5, 1, 14))
for it in L['items']:
    x, y, z = it['pos']; w, h, d = it['size']; b.append(rect(ox + x * sc, oy + (IH - y - h) * sc, w * sc, h * sc, COL.get(it['id'], '#ddd'), '#333', .2, .55)); b.append(T(ox + (x + w / 2) * sc, oy + (IH - y - h / 2) * sc, it['id'], 3, 'middle'))
def arrow(x1, y1, x2, y2, c): return line(ox + x1 * sc, oy + (IH - y1) * sc, ox + x2 * sc, oy + (IH - y2) * sc, c, .9, '', 'marker-end="url(#ar)"')
rx, ry, _ = I['radiator']['pos']; fx, fy, _ = I['fan']['pos']
for k in range(3): b.append(arrow(gx + 30 + k * 30, gy + 20, gx + 30 + k * 30, gy + 70, '#1a7f37'))   # GPU吸気(ドーム穴→GPUファン)
b.append(T(ox + (gx + 60) * sc, oy + (IH - gy - 85) * sc, 'GPU: ドーム穴から吸気→ヒートシンク→トレイ面沿いに排気', 2.2, 'middle', '#1a7f37'))
for k in range(3): b.append(arrow(rx + 25 + k * 35, ry + 200, rx + 25 + k * 35, ry + 250, '#06c'))
b.append(T(ox + (rx + 60) * sc, oy + (IH - ry - 270) * sc, 'ラジエーター: P12 Pro×2で吸気→ドーム穴へ排気', 2.2, 'middle', '#06c'))
for k in range(2): b.append(arrow(fx + 40 + k * 40, fy + 40, fx + 40 + k * 40, fy + 100, '#c0392b'))
b.append(T(ox + (fx + 60) * sc, oy + (IH - fy - 130) * sc, 'NF-A12x25: ケース内の熱気をドームの穴から排気', 2.6, 'middle', '#c0392b'))
tx = ox + IW * sc + 20
b.append(T(tx, 44, '熱収支(ピーク)', 4, 'start', '#000', 'font-weight="bold"'))
heat = [('CPU Ryzen 7 9800X3D PPT', 162), ('GPU RTX 5060 Ti TGP', 180), ('基板/SSD/RAM/ファン', 40), ('PSU損失(効率92%)', 35), ('コントローラ/パネル', 30)]
tot = sum(v for _, v in heat)
for n, (k, v) in enumerate(heat): b.append(T(tx, 52 + n * 6, f'{k}: {v} W', 3))
b.append(T(tx, 52 + len(heat) * 6 + 3, f'合計 約{tot} W', 3.4, 'start', '#000', 'font-weight="bold"'))
b.append(T(tx, 52 + len(heat) * 6 + 12, '冷却能力(公称): ARCTIC LF III Pro 240 → CPU PPT162Wに対し一般に余裕あり(AMD推奨は液冷)。', 2.8))
b.append(T(tx, 52 + len(heat) * 6 + 18, 'ΔT計算は tools/fitcheck.py。実機は①CPU/GPU温度②ファン回転数③表面温度の実測が必須(未測定)。', 2.8))
b.append(T(tx, 52 + len(heat) * 6 + 24, '懸念: ドームの穴開口率・吸気経路の圧損、ポンプ下のSSD/VRM冷却(VRMファン60mm付き)。', 2.8, 'start', '#c0392b'))
save('13_airflow_thermal.svg', b)

# ================= 14 分解組立図(側面の積層) =================
b = head('分解組立図(側面)と組立順', 'PKG-14', note='番号=組立順。外装(自作)=①④⑤、他は市販品')
layers = [('①前面ガラス+アルミ枠(自作/外注)', 'glass', 6), ('②パネル 27型4K (LG LM270WR3 / BOE N50)', 'panel', 14), ('③背板(A5052 t2.0)+吊りピン×4+スタンド取付', 'back', 3), ('④サービストレイ(A5052 t2.0)', 'tray', 3), ('⑤部品: 基板/GPU/PSU/ラジエーター/ファン/ctrl', 'parts', 60), ('⑥ドーム(A5052 t2.0, 外装)', 'dome', 3)]
y = 40; ox = 40
for i, (t, k, h) in enumerate(layers):
    hh = max(h, 5) * 1.6; b.append(rect(ox, y, 160, hh, ['#dfe9f5', '#222', '#bbb', '#8d9198', '#9ac8a6', '#d9dde2'][i], '#000', .4)); b.append(T(ox + 165, y + hh / 2 + 1, t, 3.4))
    if i < len(layers) - 1: b.append(line(ox + 80, y + hh, ox + 80, y + hh + 10, '#1a7f37', .6, '', 'marker-end="url(#ag)"'))
    y += hh + 12
b.append(T(20, 190, '組立順', 4, 'start', '#000', 'font-weight="bold"'))
steps = ['A. パネル/前面ガラス: ガラス+枠を接着(U22)し、背板へM3×16(リム)。トリムリング磁石で隠す。', 'B. 背板: 吊りピン×4(M3.5肩ネジ)、スタンドM6×4、ヒンジ。', 'C. トレイ(机上): スタンドオフ→基板(ITX4点)→CPU→ポンプ(AM5バックプレート)→DIMM→SSD。', 'D. トレイ: ラジエーター(M3×4)→PSU(SFX M3×4)→GPU(クレードル)→ライザー→ファン→ctrl基板。', 'E. 配線(W1〜W5)をコーム/タグで固定。通電前にBIOS確認(FlashBack)。', 'F. トレイを吊りピンに掛け、拘束ネジ×2。アンビリカル接続後、ドームを磁石+拘束ネジで固定。']
for n, s in enumerate(steps): b.append(T(20, 198 + n * 7, s, 3.2))
save('14_exploded_assembly.svg', b)

# ================= 15 BOM =================
rows = []
for k in ('panel', 'ctrl_board', 'board', 'cpu', 'cooler', 'radiator', 'gpu', 'riser', 'psu', 'fan', 'ssd', 'ram', 'camera_audio'):
    p = P[k]; rows.append((k, p['name'], p['maker'], 'x'.join(f'{v:g}' for v in p['dims']), p['status'], (p.get('sources') or [''])[0]))
b = head('部品表(BOM) 市販品一覧', 'PKG-15', note='status: official=公式確認 / retail=小売一致 / assumed=未確認')
b.append(T(10, 20, 'ID', 3.4, 'start', '#000', 'font-weight="bold"')); 
for h_, x_ in (('名称', 40), ('メーカー', 190), ('外形mm', 235), ('状態', 280)): b.append(T(x_, 20, h_, 3.4, 'start', '#000', 'font-weight="bold"'))
for n, r in enumerate(rows):
    yy = 28 + n * 8; b.append(T(10, yy, r[0], 3)); b.append(T(40, yy, r[1][:62], 2.8)); b.append(T(190, yy, r[2][:22], 2.8)); b.append(T(235, yy, r[3], 2.8)); b.append(T(280, yy, r[4][:40], 2.6, 'start', '#c0392b' if r[4].startswith(('assumed', '未')) else '#000'))
b.append(T(10, 28 + len(rows) * 8 + 8, '自作部品(外装): 前面ガラス+アルミ枠 / 背板 / サービストレイ / ドーム / スタンド+ヒンジ(定トルク) / トリムリング → 製造図面 MFG-01〜05, SVC-06〜08。', 3))
save('15_bom_sheet.svg', b)

# ================= docs =================
w = ['# 配線表(自動生成: tools/gen_package.py)', '', '長さは経路折れ線長×1.15(余長)。PSU付属ケーブル長は小売記載で公式未確認(U08)。', '', '| ID | 名称 | 接続 | AWG | コネクタ | 設計長mm | PSU付属mm | 判定 |', '|---|---|---|---|---|---|---|---|']
for c in CAB: w.append(f"| {c['id']} | {c['name']} | {c['frm']} → {c['to']} | {c['awg'] or '-'} | {c['conn']} | {c['len_mm']} | {c['ref_mm'] or '-'} | {c['verdict']} |")
w += ['', '## 配線ルール', '- 電源線は番号タグ+色。最小曲げ半径: 24p/EPS/PCIe は線外径の6倍以上(約30mm)。', '- ホース(ARCTIC, 450mm, OD12.4): 最小曲げ半径は公式未確認(U)。クリップで固定し90°折れを避ける。', '- アンビリカルはトレイ上端のコネクタ。取り外し時は保護キャップ。', '- ファンはPWM 4pinを基板FAN_HDRへ(ファンハブ使用時はハブ→基板CPU_FAN)。']
open(f'{R}/docs/wiring.md', 'w').write('\n'.join(w) + '\n')
bm = ['# 部品表 BOM(自動生成: tools/gen_package.py / 元データ model/parts.json)', '', '| ID | 名称 | メーカー | 外形mm | 状態 | 主な根拠 |', '|---|---|---|---|---|---|'] + [f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |' for r in rows]
open(f'{R}/docs/bom-final.md', 'w').write('\n'.join(bm) + '\n')
print('docs written')
