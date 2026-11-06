#!/usr/bin/env python3
"""整備機構の図面(SVG)を model/spec.json と model/layout.json から生成する。
出力: drawings/06_service_tray_plan.svg(サービストレイ平面: 部品・固定・取り外し方向)
      drawings/07_dome_latch_section.svg(ドームの固定とトレイ吊り下げの断面)
      drawings/08_service_sequence.svg(取り外し順序の分解図)"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f'{R}/drawings'; os.makedirs(OUT, exist_ok=True)
S = json.load(open(f'{R}/model/spec.json')); L = json.load(open(f'{R}/model/layout.json')); P = json.load(open(f'{R}/model/parts.json'))
Dm = S['dome']; panel_h = S['panels'][str(S['panel_size'])]['h']; W = S['body_w']; H = panel_h + S['bezel'] + S['chin']
IW = W - 2*Dm['inset_left_right'] - 6; IH = H - Dm['inset_bottom'] - Dm['inset_top'] - 6
sc = 0.6
COL = {'board':'#9ac8a6','cooler':'#e0b080','radiator':'#b0c4de','gpu':'#9aa0ad','riser':'#444','psu':'#c8c8c8','fan':'#d9c8a0','ctrl_board':'#a9c0d6','ssd':'#cfa','ram':'#9cd'}
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import drawlib as DL
def head(w,h,title,num,scale='NTS'):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif"><defs><marker id="a" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#1a7f37"/></marker></defs>'
    return [svg] + DL.frame(title, num, scale=scale) + ['<g transform="translate(19,12) scale(0.93)">']
def T(x,y,s,sz=3.4,a='start',fill='#222'): return f'<text x="{x}" y="{y}" font-size="{sz}" text-anchor="{a}" fill="{fill}">{s}</text>'
# ---------- 06 トレイ平面 ----------
ox, oy = 30, 40; b = head(420, 297, 'サービストレイ平面(背面側から見た配置)', 'SVC-06')
b.append(f'<rect x="{ox}" y="{oy}" width="{IW*sc}" height="{IH*sc}" rx="20" fill="#f4f6f8" stroke="#000" stroke-width=".5"/>')
for it in L['items']:
    x,y,z=it['pos']; sx,sy,sz=it['size']; i=it['id']
    b.append(f'<rect x="{ox+x*sc}" y="{oy+(IH-y-sy)*sc}" width="{sx*sc}" height="{sy*sc}" fill="{COL.get(i,"#ddd")}" fill-opacity=".8" stroke="#333" stroke-width=".3"/>')
    b.append(T(ox+(x+sx/2)*sc, oy+(IH-y-sy/2)*sc, f"{i} ({P.get(i,{}).get('name','')[:22]})",2.6,'middle'))
# キーホール吊りピン(トレイをバックプレートに掛ける4点)とトレイ拘束ネジ
def free_point(tx, ty, margin=14):
    # 目標(tx,ty)に最も近い、どの部品とも margin 以上離れた点(吊りピンの頭が出るため部品の下には置けない)
    best=None
    for gx in range(20, int(IW)-20, 5):
        for gy in range(20, int(IH)-20, 5):
            if any(it['pos'][0]-margin < gx < it['pos'][0]+it['size'][0]+margin and it['pos'][1]-margin < gy < it['pos'][1]+it['size'][1]+margin for it in L['items']): continue
            d=(gx-tx)**2+(gy-ty)**2
            if best is None or d<best[0]: best=(d,gx,gy)
    return (best[1],best[2])
kh = [free_point(60,60), free_point(IW-60,60), free_point(60,IH-60), free_point(IW-60,IH-60)]
print('キーホール位置(トレイ内座標):', kh)
KH = kh
for (x,y) in kh: b += [f'<circle cx="{ox+x*sc}" cy="{oy+(IH-y)*sc}" r="3" fill="none" stroke="#c0392b" stroke-width=".4"/>', T(ox+x*sc+4, oy+(IH-y)*sc-3,'キーホール吊りピン',2.4,fill='#c0392b')]
for (x,y) in [(IW/2-60,14),(IW/2+60,14)]: b += [f'<circle cx="{ox+x*sc}" cy="{oy+(IH-y)*sc}" r="2.2" fill="#c0392b"/>', T(ox+x*sc, oy+(IH-y)*sc-5,'拘束ネジ(トレイ固定)',2.4,'middle','#c0392b')]
b.append(f'<line x1="{ox+IW*sc/2}" y1="{oy-6}" x2="{ox+IW*sc/2}" y2="{oy-18}" stroke="#1a7f37" stroke-width=".6" marker-end="url(#a)"/>')
b.append(T(ox+IW*sc/2+3, oy-9, '取り外し方向: 12mm持ち上げてキーホールを外し、背面(+z)へ引く',3,fill='#1a7f37'))
b.append(T(ox, oy+IH*sc+10, f'ドーム内寸 {IW:.0f} x {IH:.0f} / トレイ=A5052 t2.0。部品はスタンドオフで固定(M3)。GPUはクレードル(工具なしクランプ)で保持。', 3.4))
b.append(T(ox, oy+IH*sc+16, 'ケーブルはトレイ上のコームで束ね、ディスプレイ側は「アンビリカル」(eDP/12V/USB)でトレイ端のコネクタに分離。', 3.4))
b.append('</g></svg>'); open(f'{OUT}/06_service_tray_plan.svg','w',encoding='utf-8').write('\n'.join(b))
# ---------- 07 断面 ----------
k = 2.2; x0, y0 = 60, 50; b = head(420, 297, 'ドーム固定とトレイ吊り下げ(断面)', 'SVC-07')
slab = S['slab_t']; tot = Dm['total_t']
b += [f'<rect x="{x0}" y="{y0}" width="{slab*k}" height="150" fill="#cfd3d8" stroke="#000" stroke-width=".4"/>', T(x0+2, y0-4, '前面スラブ(ガラス+パネル+背板)')]
b += [f'<rect x="{x0+slab*k}" y="{y0+90}" width="{(tot-slab)*k*0.18}" height="60" fill="#e8c8c8" stroke="#000" stroke-width=".3"/>']
b.append(T(x0+slab*k+4, y0+86, 'キーホール吊りピン(M3・肩径Ø5 肩ねじ、背板M3にねじ込み)', 2.8))
tray_z = slab+3
b += [f'<rect x="{x0+(slab+8)*k}" y="{y0+20}" width="{2*k}" height="110" fill="#b9c4d0" stroke="#000" stroke-width=".4"/>', T(x0+(slab+8)*k+6, y0+30, 'サービストレイ A5052 t2.0(スタンドオフ 8mm)', 2.8)]
b += [f'<path d="M{x0+slab*k} {y0+170} L{x0+(tot-3)*k} {y0+170-Dm["run"]*k*0.6} L{x0+(tot-3)*k} {y0+20}" fill="none" stroke="#2a4a7a" stroke-width="1.6"/>']
b.append(T(x0+(tot)*k-30, y0+3, 'ドーム(A5052 t2.0) 傾斜 60mm', 2.8))
b += [f'<circle cx="{x0+(slab+4)*k}" cy="{y0+140}" r="3" fill="#c0392b"/>', T(x0+(slab+4)*k+6, y0+142, '下辺ラッチ(1/4回転, 下面の凹み内)。上辺は掛け爪フック', 2.8)]
b += [f'<rect x="{x0+(slab+1)*k}" y="{y0+120}" width="{2.2*k}" height="{2.2*k}" fill="#555"/>', T(x0+(slab+4)*k, y0+118, 'ネオジム磁石 8x3 ×12個(位置決め)', 2.8)]
b.append(T(x0, y0+195, '導電ガスケット(ファブリック・オーバー・フォーム 3mm)を縁に周回。ドーム縁と背板の隙間 0.5〜1.0mm。', 3.2))
b.append('</g></svg>'); open(f'{OUT}/07_dome_latch_section.svg','w',encoding='utf-8').write('\n'.join(b))
# ---------- 08 取り外し順序 ----------
b = head(420, 297, '取り外し順序(レベル別)', 'SVC-08')
steps = [('L1 ユーザー','①電源OFF・AC抜去(5分待つ) ②下面の凹みから下辺ラッチ6点(T10, 1/4回転) ③ドームを上へ3mmスライドして上辺フックを外し、後方へ外す','メモリ/SSD/ファン/ダストフィルタ/ケーブル確認'),
 ('L2 保守','④トレイ拘束ネジ2本 ⑤トレイを12mm持ち上げ背面へ約100mm引く(アンビリカル余長250mm) ⑥アンビリカルを外す(eDP, 12V, USB)・接地編組を外す ⑦トレイを取り出す','GPU/電源/AIO/基板の交換'),
 ('L2 保守','⑧GPUクレードルのクランプを開く→ライザーを抜く→GPUを外す ⑨SFX電源のM3×4を外す ⑩AIO: ラジエーターのスタンドオフ4本、ポンプのAM5ばね付きネジ4本','部品単位の交換'),
 ('L3 技術者','⑪背板のパネル固定M3×約18を外す(COF部を押さない) ⑫パネルを背面側へ取り出す(ガラスはスラブ枠に接着: 交換はスラブごと/加熱剥離)','パネル/前面ガラス交換'),
 ('スタンド','⑭ヒンジブロックの貫通M6×4を外す(裏当て鋼板に注意)','輸送/交換')]
y = 30
for lv, st, use in steps:
    b += [f'<rect x="20" y="{y}" width="380" height="40" rx="3" fill="#f3f6fb" stroke="#678" stroke-width=".4"/>', T(26, y+9, lv, 4.4), T(26, y+19, st[:78], 3.1), T(26, y+26, st[78:156], 3.1), T(26, y+33, '用途: '+use, 3.1, fill='#555')]
    y += 48
b.append(T(20, y+6, '工具: T10 トルクス(主), T6, 2.5mm六角, プラス#1。静電気対策(リストストラップ)。パネルのCOF部は押さない。', 3.4))
b.append('</g></svg>'); open(f'{OUT}/08_service_sequence.svg','w',encoding='utf-8').write('\n'.join(b))
print('ok: drawings/06..08')
