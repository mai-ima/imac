// iMac(24インチ, M6, 2026) 風 一体型ゲーミングPC (v3)   単位: mm
// 寸法の根拠: Apple公式スペック(幅54.7cm/高さ46.1cm/スタンド奥行14.7cm/幅13cm)と公式画像の比率
// 座標: x=幅, y=高さ(本体下端=0), z=奥行(前面ガラス=0, 背面方向+)
// cutaway=true で背面カバーを外し内部配置を表示
cutaway = false;
flip = false;   // true: モデルを180°回して前面を明るく描画(プレビューの光源が固定のため)
color_scheme = "silver";   // silver / blue / purple / pink / orange / yellow / green (公式7色)

// --- 外形 (iMac 24") ---
W = 547;                    // 本体幅 (公式 54.7cm)
panel_w = 527; panel_h = 296.5;   // 23.8" 16:9 パネル有効領域 (iMacの表示領域は約520x292)
bezel = 10;  chin = 68;
H = panel_h + bezel + chin;       // ≈374.5
slab_t = 14;                // 前面スラブ厚 (iMacは11.5mm, 市販パネル+背面板で14mm)
corner = 10;
// --- 背面ポッド(市販部品を収める) ---
pod_w = 520; pod_h = 190; pod_t = 70;     // 総厚70mm
pod_x0 = (W-pod_w)/2;
// --- スタンド(iMac風一枚板アルミ) ---
stand_w = 130; stand_drop = 85;           // 公式: 本体下端から約85mm下がる(高さ46.1cm)
foot_d = 147;
cx = pod_x0;

// 色はApple公式画像(iMac 24" M6 ページ)から実測した値: [名前, 背面, スタンド, チン]
palette = [
 ["silver", "#D2D3D5", "#BBBCBE", "#D7D8DA"],
 ["blue",   "#5882B2", "#9EB2CD", "#BACEE9"],
 ["purple", "#8581B4", "#ACA3C0", "#C9C5E6"],
 ["pink",   "#E16280", "#E7A9B6", "#FFCFDB"],
 ["orange", "#E5734E", "#F0B498", "#FFCCAF"],
 ["yellow", "#EFD344", "#DCCB97", "#FDEEB7"],
 ["green",  "#41965F", "#A2BFAD", "#B9D8C6"] ];
pal = palette[search([color_scheme],palette)[0]];
body_c = pal[1]; stand_c = pal[2]; chin_c = pal[3];

module rrect(w,h,t,r){ linear_extrude(t) offset(r) offset(-r) square([w,h]); }
module box(p,s,c){ color(c) translate(p) cube(s); }

module slab(){
  color(body_c) rrect(W,H,slab_t,corner);
  color("#EDEEF0") translate([2,H-bezel-panel_h-4,-0.5]) rrect(W-4,panel_h+bezel+4-2,0.6,corner-2); // 前面ガラス(白縁)
  color("#0a0a0c") translate([(W-panel_w)/2,chin,-1]) cube([panel_w,panel_h,0.6]);                     // 表示領域
  color(chin_c)  translate([2,2,-1]) rrect(W-4,chin-2,0.6,corner-2);                                   // チン(淡色)
  color("#333") translate([W/2,H-5,-1.1]) cylinder(d=3,h=0.4,$fn=16);                                  // カメラ
}

module pod_cover(){
  difference(){
    color(body_c) translate([pod_x0,0,slab_t]) rrect(pod_w,pod_h,pod_t-slab_t,10);
    for(i=[0:28]) translate([pod_x0+25+i*(pod_w-50)/28, pod_h-12, slab_t+3]) cube([3,14,pod_t-slab_t-6]);  // 排気
    for(i=[0:28]) translate([pod_x0+25+i*(pod_w-50)/28, -2, slab_t+3]) cube([3,14,pod_t-slab_t-6]);        // 吸気
    if(cutaway) translate([pod_x0+3,3,slab_t+2.5]) cube([pod_w-6,pod_h-6,pod_t]);
  }
  // 背面I/O: iMac風の細スロットを左下に4つ
  if(!cutaway) for(i=[0:3]) color("#222") translate([pod_x0+30+i*14,18,pod_t-0.3]) rrect(4,12,0.4,2);
}

z0 = slab_t + 3;
module internals(){
  x = pod_x0;
  box([x+8,8,z0],[170,170,1.6],"#2a6a3a");                           // Mini-ITX 170x170
  box([x+60,60,z0+1.6],[66,66,35],"#b0b3b8");                         // 低背CPUクーラー
  color("#222") translate([x+93,93,z0+36.6]) cylinder(d=92,h=2,$fn=48);
  box([x+16,18,z0+1.6],[22,10,4],"#333");                             // M.2 SSD
  box([x+178,30,z0],[8,100,12],"#554");                               // PCIe ライザー
  box([x+188,20,z0],[200,125,40],"#202226");                          // GPU (ITX 2スロット)
  color("#888") translate([x+288,82,z0+40.1]) cylinder(d=70,h=0.5,$fn=40);
  box([x+188,148,z0],[150,34,22],"#334");                             // DC-ATX 電源基板
  box([x+396,35,z0],[120,120,25],"#111");                             // 排気ファン 120mm
  color("#555") translate([x+456,95,z0+25.1]) cylinder(d=100,h=0.5,$fn=48);
}

module stand(){
  color(stand_c) translate([W/2-stand_w/2,-stand_drop,(slab_t+pod_t)/2-4]) cube([stand_w,stand_drop+1,8]);        // アーム
  color(stand_c) translate([W/2-stand_w/2,-stand_drop-6,(slab_t+pod_t)/2-foot_d/2]) cube([stand_w,6,foot_d]);     // 足
}

translate([flip?W:0,0,0]) rotate([0,0,flip?180:0]) rotate([90,0,0]) { slab(); pod_cover(); stand(); if(cutaway) internals(); }
