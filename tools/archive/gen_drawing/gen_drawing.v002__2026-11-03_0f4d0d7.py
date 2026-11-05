#!/usr/bin/env python3
"""cad/imac_like_pc.scad と同じ寸法から 設計図SVG を生成する (単位 mm)。"""
W,panel_w,panel_h,bezel,chin=547,527,296.5,10,68
H=panel_h+bezel+chin
slab_t,pod_w,pod_h,pod_t=14,W-27,190,70
stand_w,drop,foot_d=130,85,147
pod_x0=(W-pod_w)/2
S=0.9  # px/mm
def f(v): return round(v*S,1)
out=[]
def R(x,y,w,h,fill="none",stroke="#333",sw=1,rx=0,extra=""):
    out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def T(x,y,s,size=11,anchor="middle",fill="#222",extra=""):
    out.append(f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" {extra}>{s}</text>')
def Ln(x1,y1,x2,y2,stroke="#c0392b",sw=1):
    out.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" stroke-width="{sw}"/>')
def dim_h(x1,x2,y,label):
    Ln(x1,y,x2,y); Ln(x1,y-4,x1,y+4); Ln(x2,y-4,x2,y+4); T((x1+x2)/2,y-4,label,10,fill="#c0392b")
def dim_v(x,y1,y2,label):
    Ln(x,y1,x,y2); Ln(x-4,y1,x+4,y1); Ln(x-4,y2,x+4,y2)
    out.append(f'<text x="{f(x)-4}" y="{f((y1+y2)/2)}" font-size="10" fill="#c0392b" text-anchor="middle" transform="rotate(-90 {f(x)-4} {f((y1+y2)/2)})">{label}</text>')
total_w=1500; total_h=1000
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" font-family="Helvetica,Arial,sans-serif">')
out.append('<rect width="100%" height="100%" fill="#f6f7f9"/>')
T(750,34,"iMac(24\", M6)風 一体型ゲーミングPC — 設計図 (単位: mm)",20)
# ---------- 正面図 ----------
ox,oy=70,90
T(ox+W/2,oy-42,"正面図",14)
R(ox,oy,W,H,"#d9dbde","#555",1.2,10)
R(ox+(W-panel_w)/2,oy+bezel,panel_w,panel_h,"#0b0b0d","#000")
R(ox+2,oy+bezel+panel_h+4,W-4,chin-6,"#e8e9ec","#bbb",0.5,8)
out.append(f'<circle cx="{f(ox+W/2)}" cy="{f(oy+5)}" r="2" fill="#333"/>')
R(ox+W/2-stand_w/2,oy+H,stand_w,drop-6,"#b9bcc1","#555")
R(ox+W/2-stand_w/2-10,oy+H+drop-6,stand_w+20,6,"#a0a3a8","#555")
dim_h(ox,ox+W,oy+H+drop+30,f"本体幅 {W}")
dim_v(ox-22,oy,oy+H,f"本体高 {H:.1f}")
dim_v(ox+W+22,oy+bezel,oy+bezel+panel_h,f"表示 {panel_h}")
dim_h(ox+(W-panel_w)/2,ox+(W+panel_w)/2,oy+bezel/2+ -22,f"表示 {panel_w}")
dim_v(ox+W+44,oy+H-chin,oy+H,f"チン {chin}")
dim_h(ox+W/2-stand_w/2,ox+W/2+stand_w/2,oy+H+drop/2,f"スタンド幅 {stand_w}")
# ---------- 側面図 ----------
sx,sy=760,90
T(sx+60,sy-18,"側面図",14)
zc=(slab_t+pod_t)/2; fz0=zc-foot_d/2
x0=sx+ (-fz0)*S + 20   # z=0 の位置
R(x0,sy,slab_t,H,"#d9dbde","#555",1.2,3)
R(x0+slab_t,sy+H-pod_h,pod_t-slab_t,pod_h,"#c5c8cc","#555",1.2,6)
R(x0+zc-4,sy+H,8,drop-6,"#b9bcc1","#555")
R(x0+fz0,sy+H+drop-6,foot_d,6,"#a0a3a8","#555")
dim_h(x0,x0+slab_t,sy-6,f"{slab_t}")
dim_h(x0,x0+pod_t,sy+H+drop+30,f"総厚 {pod_t}")
dim_h(x0+fz0,x0+fz0+foot_d,sy+H+drop+55,f"足の奥行 {foot_d}")
dim_v(x0+pod_t+22,sy+H-pod_h,sy+H,f"ポッド高 {pod_h}")
T(x0-40,sy+H-pod_h/2,"吸気↑",10); T(x0+pod_t/2,sy+H-pod_h-8,"排気↑",10)
# ---------- 背面図 (内部配置) ----------
bx,by=70,640
T(bx+pod_w*S/2,by-18,"背面ポッド内部配置 (背面カバーを外した状態)",14)
R(bx,by,pod_w,pod_h,"#c5c8cc","#555",1.2,10)
def part(x,y,w,h,fill,label):
    R(bx+x,by+pod_h-y-h,w,h,fill,"#333",1); T(bx+x+w/2,by+pod_h-y-h/2+4,label,10)
part(8,8,170,170,"#9ac8a6","Mini-ITX 170x170")
part(188,20,165,115,"#9aa0ad","GPU 165x115x40(例:RTX5060 SOLO)")
part(188,148,150,34,"#a9a9d6","DC-ATX 電源基板")
part(pod_w-124,35,120,120,"#d9c8a0","120mm 排気ファン")
part(178,30,8,100,"#bba","ライザー")
part(360,40,28,100,"#ddd","予備")
T(bx+pod_w/2,by+pod_h+24,"I/O: 背面左下スリット(USB-C x4 + HDMI/DP, 2.5GbE)  ※基板I/Oを延長ブラケットで引き出し",10)
dim_h(bx,bx+pod_w,by+pod_h+46,f"ポッド幅 {pod_w}")
# ---------- 注記 ----------
notes=["根拠: Apple公式 iMac(24インチ,M6) 仕様 — 幅54.7cm / 高さ46.1cm / 足の奥行14.7cm / 足の幅13cm /","表示領域4,480x2,520(16:9, 実測23.5型) / 重量4.42kg。本機は23.8型4K IPS市販パネル(有効527x296.5)で代替。","iMac本体の厚さ約11.5mm(過去モデル公称)に対し、本機は前面スラブ14mm + 背面ポッドで総厚70mm。"]
for i,n in enumerate(notes): T(bx+pod_w*S+60,by+i*20+20,n,11,"start")
out.append('</svg>')
open("concept/blueprint.svg","w",encoding="utf-8").write("\n".join(out))
print("ok",H)
