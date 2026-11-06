#!/usr/bin/env python3
"""仕様書一式の生成: docs/spec/*.md, drawings/parts/CP-*.svg, drawings/16_cable_clips.svg。
元データ: model/custom_parts.json, spec.json, parts.json, layout.json, cables.json。実行: python3 tools/gen_specs.py"""
import json, os, math
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda n: json.load(open(f'{R}/model/{n}.json'))
CP = J('custom_parts'); S = J('spec'); P = J('parts'); L = J('layout'); C = J('cables')['cables']
os.makedirs(f'{R}/docs/spec', exist_ok=True); os.makedirs(f'{R}/drawings/parts', exist_ok=True)
def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;')

# ---------- 部品シート(md) ----------
md = ['# 特注部品 仕様書 (自動生成: tools/gen_specs.py / 元データ model/custom_parts.json)', '', '数値は設計値(未承認)。試作→実測→改訂で確定。共通: ' + '; '.join(f'{k}={v}' for k, v in CP['general'].items()), '',
      '| ID | 部品 | 数量 | 材質 | 板厚 | 主な外形mm | 質量kg | 状態 |', '|---|---|---|---|---|---|---|---|']
for p in CP['parts']: md.append(f"| {p['id']} | {p['name']} | {p['qty']} | {p['material']} | {p['t'] or '-'} | {'×'.join(f'{v:g}' for v in p['size'] if v) or '-'} | {p['mass_kg']} | {p['status']} |")
for p in CP['parts']:
    md += ['', f"## {p['id']} {p['name']}", f"- 数量: {p['qty']} / 材質: {p['material']} / 板厚: {p['t'] or '-'} mm / 外形: {'×'.join(f'{v:g}' for v in p['size'] if v) or '-'} mm / 質量: {p['mass_kg']} kg",
           f"- 加工: {p['process']}", f"- 公差: {p['tolerance']} / 表面処理: {p['finish']}", '- 形状・加工要素:'] + [f'  - {f}' for f in p['features']] + ['- 相手部品(接合):'] + [f'  - {m}' for m in p['mates']] + [f"- 荷重/条件: {p['loads']}", f"- 寿命: {p['life']}", '- 試験: ' + ' / '.join(p['tests']), f"- 状態: {p['status']}", '- 未解決: ' + (' / '.join(p['open']) or 'なし')]
open(f'{R}/docs/spec/custom-parts.md', 'w').write('\n'.join(md) + '\n')

# ---------- 部品図(2D外形+寸法+注記) ----------
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import drawlib as DL
def sheet(p):
    w, h = 297, 210; sx, sy = (p['size'] + [0, 0])[:2]
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" font-family="Helvetica,Arial,sans-serif"><defs><marker id="a" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto-start-reverse"><path d="M0,0 L5,2.5 L0,5 z" fill="#06c"/></marker></defs>']
    o += DL.frame(p['name'], f"{p['id']}", scale='NTS', material=p['material'][:58], finish=p['finish'][:58], note=f"状態: {p['status']}")
    o.append('<g transform="translate(22,18) scale(1.2)">')
    o.append(f'<text x="2" y="8" font-size="5" font-weight="bold">{esc(p["id"])} {esc(p["name"])}</text>')
    o.append(f'<text x="2" y="14" font-size="3">数量 {p["qty"]} / 板厚 {p["t"] or "-"} / 質量 {p["mass_kg"]}kg / 公差 {esc(p["tolerance"][:50])}</text>')
    if sx and sy:
        s = min(130 / sx, 90 / sy); ox, oy = 14, 30; rw, rh = sx * s, sy * s
        o.append(f'<rect x="{ox}" y="{oy}" width="{rw:.1f}" height="{rh:.1f}" rx="{min(8, rw/10):.1f}" fill="#eef2f6" stroke="#000" stroke-width=".5"/>')
        o.append(f'<line x1="{ox}" y1="{oy+rh+6}" x2="{ox+rw}" y2="{oy+rh+6}" stroke="#06c" stroke-width=".3" marker-start="url(#a)" marker-end="url(#a)"/><text x="{ox+rw/2}" y="{oy+rh+11}" font-size="3.4" text-anchor="middle" fill="#06c">{sx:g}</text>')
        o.append(f'<line x1="{ox-6}" y1="{oy}" x2="{ox-6}" y2="{oy+rh}" stroke="#06c" stroke-width=".3"/><text x="{ox-8}" y="{oy+rh/2}" font-size="3.4" text-anchor="middle" fill="#06c" transform="rotate(-90 {ox-8} {oy+rh/2})">{sy:g}</text>')
        if p['id'] == 'CP-06':
            k = rw / sx
            for it in L['items']: x, y, z = it['pos']; a, b, c = it['size']; o.append(f'<rect x="{ox+x*k:.1f}" y="{oy+rh-(y+b)*k:.1f}" width="{a*k:.1f}" height="{b*k:.1f}" fill="none" stroke="#999" stroke-width=".25" stroke-dasharray="2,1"/><text x="{ox+(x+a/2)*k:.1f}" y="{oy+rh-(y+b/2)*k:.1f}" font-size="2.6" text-anchor="middle" fill="#666">{it["id"]}</text>')
            for (x, y) in [tuple(k_) for k_ in json.load(open(f'{R}/model/layout.json'))['keyholes']]: o.append(f'<circle cx="{ox+x*k:.1f}" cy="{oy+rh-y*k:.1f}" r="{4.6*k:.1f}" fill="none" stroke="#c0392b" stroke-width=".4"/>')
    y = 30
    for t_ in ['加工: ' + p['process'], '表面処理: ' + p['finish'], '公差: ' + p['tolerance']] + ['要素: ' + f for f in p['features']] + ['接合: ' + m for m in p['mates']]:
        for i in range(0, len(t_), 56): o.append(f'<text x="156" y="{y}" font-size="2.6">{esc(t_[i:i+56])}</text>'); y += 4.2
        y += 1.0
        if y > 150: break
    o.append('</g></svg>')
    return '\n'.join(o)
for p in CP['parts']: open(f'{R}/drawings/parts/{p["id"]}.svg', 'w').write(sheet(p))

# ---------- 接合マトリクス ----------
JM = [
 ('J01', '前面ガラス↔スラブ枠(CP-01↔CP-02/03)', '構造用シリコーン接着 厚1.0mm全周(OCA無し・パネルとはエアギャップ0.9)', '接着', '交換=加熱剥離(スラブ全体, L3)', 'ガラス割れ/剥離 FMEA'),
 ('J02', '(廃止) 前面枠↔背板 M3×16', 'v7で廃止: 前面モジュール固定ネジなし(P1)', '-', '-', 'C-3対応'),
 ('J03', 'パネル↔背板', 'M3×約18(BOE Fig.6穴, TSOA, 背板後面から)', '0.3〜0.4N·m(要データシート)', '可(L3: トレイ取り出し後)', 'COF部は押さない'),
 ('J04', '背板↔トレイ(吊り)', '肩ねじ M3×肩径Ø5 h8×3.0(CP-04)×4 + SUSブッシュ(CP-05)', '0.8N·m+ネジロック', '可(L2)', '30G: せん断50MPa/支圧65MPa'),
 ('J05', 'トレイ拘束', 'M3 T10 拘束ねじ ×2(トレイ下辺)', '0.6N·m', '可(L2)', '外れ止め'),
 ('J06', '背板↔ドーム(位置決め)', 'Ø4 H7ピン×2(非対称配置)', '-', '-', 'ポカヨケ'),
 ('J07', '背板↔ドーム(保持)', '上辺: 掛け爪フック×6(ネジ無し) + 下辺: 1/4回転ラッチ×6(下面の凹み, T10) + 位置決め磁石×12 + EMIガスケット', 'ラッチ60N以上/点×6', '可(L1: 下面から)', '閉合力≤約340N(U30)'),
 ('J08', '背板↔ヒンジブロック/スタンド', 'M6貫通ボルト×4 + 裏当て鋼板(SPCC t3) + 局所補強板(A5052 t4)', '6N·m+ネジロック', '可(L3)', '2mm板へのタップ不可(雌ねじ強度)'),
 ('J09', 'ヒンジブロック↔スタンド腕', 'Ø10軸+摩擦ヒンジ+バランスばね+ストッパ(-5°/+25°)', '-', '可(L3)', 'ばね金属保持'),
 ('J10', 'トレイ↔基板', 'Mini-ITXスタンドオフ M3×4(高さ6.35, PEM TSOA)', '0.5N·m', '可(L2)', '穴座標 U17, AM5バックプレート逃げ'),
 ('J11', 'トレイ↔PSU', 'M3×4(SFX規格穴, 高さ3.0)', '0.5N·m', '可(L2)', '穴座標 U17'),
 ('J12', 'トレイ↔ラジエーター', 'M3×4(ARCTIC公式穴, 高さ3.0)', '0.4N·m', '可(L2)', ''),
 ('J13', 'トレイ↔GPU', 'クレードル(CP-14: 下端支持)+ライザー+PCIe', '工具なしクランプ', '可(L2)', '縦置きの自重は下端で支持'),
 ('J14', 'CPU↔ポンプ', 'AM5バックプレート+ばね付きM4×4(対角締め)', '付属ドライバ', '可(L2)', '初回グリス'),
 ('J15', 'トレイ↔ファン', 'ゴムピン4点(クイック)+ファンハブ', '-', '可(L1)', ''),
 ('J16', 'ドーム↔RF窓', '格子裏の樹脂板をドーム内側へ両面テープ', '-', '不可', ''),
 ('J17', 'ドーム↔メッシュフィルタ', '磁石12点で内側に保持(全面1枚)', '-', '可(L1)', ''),
 ('J18', 'ctrl基板↔パネル', 'アンビリカル(eDP/12V/USB, ロック, 250mm)', '-', '可(L2)', 'U19'),
 ('J19', 'PE(保護接地)系統', 'C14 PE→M4リング端子→トレイ接地スタッド→編組×2→背板→編組×2→ドーム/ヒンジ', '導通≤0.1Ω', '可(L2)', 'CP-18, docs/spec/grounding-spec.md'),
]
m = ['# 接合マトリクス (自動生成: tools/gen_specs.py)', '', '| ID | 接合 | 方式/締結 | 締付/強度 | 脱着(レベル) | 備考 |', '|---|---|---|---|---|---|'] + [f'| {" | ".join(r)} |' for r in JM]
open(f'{R}/docs/spec/joint-matrix.md', 'w').write('\n'.join(m) + '\n')

# ---------- 配線仕様+クリップ座標 ----------
def sample(pts, step=60):
    out = [pts[0]]; acc = 0
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        n = int(d // step)
        for k in range(1, n + 1): t = k * step / d; out.append(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))
    out.append(pts[-1]); return out
clips = {}
for c in C: clips[c['id']] = [tuple(round(v, 1) for v in q) for q in sample(c['pts'])]
w = ['# 内部配線仕様 (自動生成: tools/gen_specs.py / 元データ model/cables.json)', '', '座標はトレイ内座標(mm, 左下原点, z=トレイ面からの高さ)。クリップは約60mmピッチ(CP-16)。', '',
     '## ケーブル', '| ID | 名称 | 区間 | AWG | コネクタ | 設計長mm | 最小曲げ半径 | 判定 |', '|---|---|---|---|---|---|---|---|']
MBR = {'W1': 30, 'W2': 20, 'W3': 20, 'W4': 15, 'W5': 25, 'W6': 25}
for c in C: w.append(f"| {c['id']} | {c['name']} | {c['frm']} → {c['to']} | {c['awg'] or '-'} | {c['conn']} | {c['len_mm']} | {MBR.get(c['id'], 20)} mm(外径の約6倍) | {c['verdict']} |")
w += ['', '## 固定点(クリップ位置)']
for c in C: w += [f"### {c['id']} {c['name']}"] + [f'- P{i+1}: ({q[0]}, {q[1]}, z{q[2]})' for i, q in enumerate(clips[c['id']])]
w += ['', '## 主要コネクタのピン割当(規格の一般仕様。部品の実物で要確認)',
 '- ATX 24ピン: 3.3V×3, 5V×4, 12V×2, GND×9ほか(ATX12V 3.1 標準)。PS_ON#(16番)は基板が制御。',
 '- EPS 8ピン(4+4): 12V×4 / GND×4。CPU 12V は9800X3Dの162W PPT(約14A)に対し十分。',
 '- PCIe 6+2: 12V×3 / GND×5(8ピン)。GPU TGP 180W+PCIeスロット75W上限。',
 '- ファン 4ピン PWM: GND / +12V / TACH / PWM(25kHz)。ポンプ(AIO)も基板AIO_PUMP/CPU_FANヘッダ、VRMファンはポンプ付属ケーブル。',
 '- eDP(30ピン): 差動ペア×(最大4レーン)+AUX+HPD+VDD+LCD_VDD+BL制御(PWM/EN)+LED電源。パネルBOE N50の公式ピン表と一致させる(U19)。',
 '- USB2.0 内部ヘッダ(9ピン): カメラ/マイク用。', '', '## 配線ルール',
 '- 電源線は信号線(eDP/USB/PWM)と平行に長距離並走させない(最小離隔10mm、交差は直角)。', '- 鋭角折れ禁止: 最小曲げ半径は上表。クリップ間でたるみ最大10mm。', '- ホース(ARCTIC 450mm, OD12.4): 最小曲げ半径は公式未確認(U)。キンク防止クリップを曲がりごとに設置。',
 '- 配線はドームとの隙間2mm以上確保(ドームの傾斜内側と干渉しない)。', '- すべてのケーブルに番号タグ(W1〜W5)。']
open(f'{R}/docs/spec/wiring-spec.md', 'w').write('\n'.join(w) + '\n')
# 図: クリップ位置
sc = 0.46; ox, oy = 30, 40; IW = 590; IH = 371.3
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" font-family="Helvetica,Arial,sans-serif"><rect width="100%" height="100%" fill="#fff"/><rect x="4" y="4" width="412" height="289" fill="none" stroke="#000" stroke-width=".5"/>',
     f'<rect x="{ox}" y="{oy}" width="{IW*sc}" height="{IH*sc}" rx="10" fill="#f7f8fa" stroke="#000" stroke-width=".4"/>']
for it in L['items']: x, y, z = it['pos']; a, b, c = it['size']; o.append(f'<rect x="{ox+x*sc:.1f}" y="{oy+(IH-y-b)*sc:.1f}" width="{a*sc:.1f}" height="{b*sc:.1f}" fill="#dde3ea" stroke="#888" stroke-width=".2"/><text x="{ox+(x+a/2)*sc:.1f}" y="{oy+(IH-y-b/2)*sc:.1f}" font-size="3" text-anchor="middle" fill="#555">{it["id"]}</text>')
cols = ['#c0392b', '#06c', '#1a7f37', '#a50', '#707', '#087']
for k, c in enumerate(C):
    pts = c['pts']; o.append(f'<polyline fill="none" stroke="{cols[k]}" stroke-width=".7" points="' + ' '.join(f'{ox+p[0]*sc:.1f},{oy+(IH-p[1])*sc:.1f}' for p in pts) + '"/>')
    for q in clips[c['id']]: o.append(f'<circle cx="{ox+q[0]*sc:.1f}" cy="{oy+(IH-q[1])*sc:.1f}" r="1.1" fill="{cols[k]}"/>')
    o.append(f'<text x="{ox+pts[0][0]*sc+2:.1f}" y="{oy+(IH-pts[0][1])*sc-2:.1f}" font-size="3.4" fill="{cols[k]}">{c["id"]}</text>')
o.append('<rect x="250" y="267" width="166" height="26" fill="none" stroke="#000" stroke-width=".4"/><text x="254" y="276" font-size="5">ケーブル経路とクリップ位置</text><text x="254" y="283" font-size="3.2">図番 PKG-16 / 単位 mm / 設計値(未承認) / docs/spec/wiring-spec.md</text></svg>')
open(f'{R}/drawings/16_cable_clips.svg', 'w').write('\n'.join(o))
print('specs done', len(CP['parts']), 'parts')
