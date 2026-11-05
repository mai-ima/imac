#!/usr/bin/env python3
"""実機 iMac(24") の部位・配置図 (公式画像・Apple修理資料・iFixit系報道に基づく)。
実線=確定(公式 or 独立5件以上一致) / 破線=未確定(推定)。"""
W,H,chin,bez=547,375,68,10
S=0.85
def f(v): return round(v*S,1)
o=[]
def R(x,y,w,h,fill="none",st="#444",sw=1,dash=False,rx=0):
    d=' stroke-dasharray="5 3"' if dash else ''
    o.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{fill}" stroke="{st}" stroke-width="{sw}"{d}/>')
def T(x,y,s,sz=11,a="middle",fill="#222",b=False):
    s=s.replace('&','&amp;')
    o.append(f'<text x="{f(x)}" y="{f(y)}" font-size="{sz}" text-anchor="{a}" fill="{fill}"{" font-weight=\"bold\"" if b else ""}>{s}</text>')
def N(x,y,n,conf):
    c="#1a7f37" if conf else "#d9730d"
    o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="9" fill="{c}"/><text x="{f(x)}" y="{f(y)+4}" font-size="11" text-anchor="middle" fill="#fff" font-weight="bold">{n}</text>')
o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 1170" font-family="Helvetica,Arial,sans-serif"><rect width="100%" height="100%" fill="#f6f7f9"/>')
T(750,32,"iMac 24インチ(M1〜M6系) 部位・配置図",20,b=True)
T(750,54,"●緑=確定(公式資料 or 独立5件以上一致) / ●橙・破線=未確定(推定)。内部配置はM1の分解記事が根拠(M4/M6の分解は未発見)",11)
# ---- 前面(内部透視) ----
ox,oy=60,100
T(ox+W/2,oy-14,"前面から見た内部配置(透視)",14,b=True)
R(ox,oy,W,H,"#e7e8eb","#555",1.4,rx=10)
R(ox+(W-520)/2,oy+bez,520,292.5,"#101114","#000")
T(ox+W/2,oy+bez+140,"ディスプレイ(4.5K 4480x2520 / 実測23.5型)",13,fill="#aaa")
# 上部ストリップ: ディスプレイ基板(△)
R(ox+20,oy+1.5,W-40,7,"#c8e6c9","#d9730d",1,True); 
o.append(f'<circle cx="{f(ox+W/2)}" cy="{f(oy+5)}" r="2.5" fill="#222"/>'); 
# 背面の大きな金属プレート2枚 (確定: 存在) 
R(ox+40,oy+60,200,200,"none","#1a7f37",1.5); R(ox+W-240,oy+60,200,200,"none","#1a7f37",1.5)
T(ox+140,oy+170,"金属プレート",12,fill="#7ec88b"); T(ox+W-140,oy+170,"金属プレート",12,fill="#7ec88b")
# チン内
cy=oy+H-chin
R(ox+8,cy+10,W-16,chin-20,"#d9ecff","#1a7f37",1.5)             # ロジックボード帯
R(ox+30,cy+14,50,chin-28,"#ffe3b3","#1a7f37",1.5); R(ox+W-80,cy+14,50,chin-28,"#ffe3b3","#1a7f37",1.5)  # ファン
R(ox+110,cy+16,60,chin-32,"#f3d1f4","#d9730d",1,True)          # スピーカー(推定)
R(ox+W-170,cy+16,60,chin-32,"#f3d1f4","#d9730d",1,True)
R(ox+W/2-60,cy+18,120,chin-36,"#bcd7f5","#1a7f37",1.2)          # SoC周辺
R(ox+W/2-120,cy+22,50,10,"#f2d7b6","#1a7f37",1.2)              # 銅ヒートパイプ
N(ox+W/2,oy+3,1,False); N(ox+W/2,oy+bez+12,2,True); N(ox+140,oy+80,3,True)
N(ox+W/2,cy+chin/2,4,True); N(ox+55,cy+chin/2,5,True); N(ox+140,cy+chin/2,6,False); N(ox+W-140,cy+chin-8,7,False)
N(ox+W/2-95,cy+8,8,True)
# スタンド
R(ox+W/2-65,oy+H,130,70,"#cfd2d6","#555",1.2); T(ox+W/2,oy+H+40,"スタンド(アルミ一枚板)",11)
# ---- 背面 ----
bx,by=640,100
T(bx+W/2,by-14,"背面",14,b=True)
R(bx,by,W,H,"#d2d3d5","#555",1.4,rx=10)
o.append(f'<path d="M{f(bx+W/2-17)} {f(by+130)} q17 -25 34 0 q-5 30 -17 33 q-12 -3 -17 -33z" fill="#e8e9eb" stroke="#999"/>')
for i in range(4): R(bx+55+i*16,by+H-45,4,12,"#222","#222",1,rx=2)
R(bx+W/2-65,by+H-170,130,170+70,"#bbbcbe","#555",1.2)
o.append(f'<ellipse cx="{f(bx+W/2)}" cy="{f(by+H-85)}" rx="{f(12)}" ry="{f(20)}" fill="#7a7a7e"/>')
R(bx+W/2-65,by+H-171,130,5,"#e0e1e3","#555",1)
N(bx+W/2,by+110,9,True); N(bx+107,by+H-64,10,True); N(bx+W/2,by+H-85,11,True); N(bx+W/2,by+H-171,12,True)
# ---- 側面 ----
sx,sy=1130,100
T(sx+150,sy-14,"側面(チルト可能)",14,b=True)
import math
ang=math.radians(8)
body=[(sx+110,sy),(sx+110+11.5,sy),(sx+110+11.5+H*math.sin(ang),sy+H*math.cos(ang)),(sx+110+H*math.sin(ang),sy+H*math.cos(ang))]
pts=" ".join(f"{f(x)},{f(y)}" for x,y in body)
o.append(f'<polygon points="{pts}" fill="#d2d3d5" stroke="#555" stroke-width="1.4"/>')
hx,hy=sx+110+60*math.sin(ang)-12,sy+0.75*H*math.cos(ang)-60
fx,fy=sx+60,sy+H*math.cos(ang)+30
o.append(f'<line x1="{f(hx)}" y1="{f(hy)}" x2="{f(fx+20)}" y2="{f(fy+90)}" stroke="#bbbcbe" stroke-width="{f(10)}" stroke-linecap="round"/>')
R(fx-30,fy+90,160,6,"#bbbcbe","#555",1)
o.append(f'<circle cx="{f(hx)}" cy="{f(hy)}" r="{f(10)}" fill="#e6e6e8" stroke="#555"/>')
o.append(f'<circle cx="{f(sx+110+H*math.sin(ang)-6)}" cy="{f(sy+H*math.cos(ang)-12)}" r="{f(3)}" fill="#222"/>')
N(hx,hy,13,True); N(sx+110+H*math.sin(ang)-6,sy+H*math.cos(ang)-34,14,True); N(sx+110+6,sy+10,15,True)
T(sx+150,sy+H*math.cos(ang)+58,"厚さ約11.5mm",11,fill="#c0392b")
# ---- 凡例 ----
items=[
(1,0,"ディスプレイ基板(上部の細いストリップ、カメラ/マイク周辺)","iFixit, Macworld, MacDailyNews, GadgetGuy の4件。公式修理項目に『カメラ&eDPフレックス』あり"),
(2,1,"12MPカメラ+上端に2マイク孔","Apple公式(カメラ/3マイク)。上端のマイク孔は公式画像で確認"),
(3,1,"大型の薄い金属プレート2枚(ディスプレイ背後)","6件一致で存在確定。用途(スピーカー室/放熱)は未確定"),
(4,1,"ロジックボード(小型, チン内)+EMIシールド","5件超一致+Apple修理項目(ロジックボードカバー)。メモリ/SSDは基板直付け"),
(5,1,"冷却ファン2基(基板の左右、ベースは1基)","6件+Apple公式ファンページ(左右2基・基板の下側)"),
(6,0,"スピーカー(基板の横, 6スピーカー)","Apple修理表『左USB-Cボード カウリング+スピーカークリップ』、9to5Mac。位置は推定"),
(7,0,"USB-Cボード(左右)+アダプタボード","Apple公式修理項目(左右USB-Cボード)。実際の配置は推定"),
(8,1,"銅ヒートパイプ+短いヒートシンク2枚","iFixit, Macworld, MacRumors, apfelpatient, Wccftech の5件(上位構成のみ)"),
(9,1,"Wi-Fi/Bluetoothアンテナ(Appleロゴ裏が電波の通り道)","MacRumors, apfelpatient, 9to5Mac, MacDailyNews, Engadget の5件"),
(10,1,"USB-Cポート(背面左下の縦スロット4つ)","Apple公式画像(2ポート版は2つ)"),
(11,1,"スタンド背面: マグネット式電源コネクタ凹み","Apple公式画像・仕様(マグネット式電源コネクタ)"),
(12,1,"スタンド上端のフランジ(本体背面と接合)","Apple公式画像/部品表(Flange, Stand)"),
(13,1,"ヒンジ(スタンド軸, 外から分解不可)","Apple公式画像。VESAは購入時選択(iFixit, Macworld, GadgetGuy)"),
(14,1,"3.5mmヘッドホンジャック(側面下部)","Apple公式画像・iFixit『薄すぎて背面に付けられず横向き』"),
(15,1,"一枚ガラス前面+接着構造(筐体はアルミ)","iFixit, MacRumors, apfelpatient, macandegg, 9to5Mac の5件"),
]
ly=600
o.append(f'<text x="60" y="{ly-24}" font-size="14" font-weight="bold" fill="#222">部位一覧と根拠(緑=確定 / 橙=未確定)</text>')
y=ly
for n,c,a_,b_ in items:
    col="#1a7f37" if c else "#d9730d"
    o.append(f'<circle cx="70" cy="{y-4}" r="9" fill="{col}"/><text x="70" y="{y}" font-size="11" text-anchor="middle" fill="#fff" font-weight="bold">{n}</text>')
    o.append(f'<text x="92" y="{y}" font-size="12" fill="#222" font-weight="bold">{a_.replace("&","&amp;")}</text>')
    o.append(f'<text x="92" y="{y+15}" font-size="10.5" fill="#555">{b_.replace("&","&amp;")}</text>')
    y+=36
o.append('</svg>'); open("concept/imac_anatomy.svg","w",encoding="utf-8").write("\n".join(o)); print("ok")
