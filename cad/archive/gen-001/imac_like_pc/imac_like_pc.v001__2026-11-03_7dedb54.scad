// iMac風 一体型ゲーミングPC 外観パラメトリックモデル (単位: mm)
// 注意: OpenSCAD未実行の初稿。寸法は docs/design.md の設計値に対応。
panel_w = 596.7;  panel_h = 335.7;   // 27" 16:9 有効表示領域
bezel   = 12;                         // 左右上ベゼル
chin    = 42;                         // 下部チン(iMac風)
body_t  = 14;                         // 前面スラブ厚(パネル+背面プレート)
pod_h   = 200; pod_t = 46;            // 背面下部サーマルポッド(深さ合計=pod_t)
corner  = 12;

W = panel_w + 2*bezel;
H = panel_h + bezel + chin;

module rrect(w,h,t,r){ linear_extrude(t) offset(r) offset(-r) square([w,h],center=false); }

module slab(){ // 前面スラブ(アルミ背面+ガラス前面)
  color("#d9dbde") rrect(W,H,body_t,corner);
  // ガラス/パネル面
  color("#0b0b0d") translate([bezel,chin,-0.01]) cube([panel_w,panel_h,0.5]);
}

module pod(){ // 背面サーマルポッド(下部): 吸気=下面スリット, 排気=上面スリット
  color("#c9ccd0") translate([30,0,body_t]) rrect(W-60,pod_h,pod_t-body_t,10);
  // 排気スリット
  for(i=[0:24]) color("#222") translate([60+i*(W-120)/24, pod_h-2, body_t+(pod_t-body_t)/2]) cube([2,4,(pod_t-body_t)/2],center=false);
}

module stand(){ // iMac 24風 一枚アーム
  color("#d9dbde") translate([W/2-30, -150, body_t+2]) cube([60,160,10]);
  color("#d9dbde") translate([W/2-110, -160, 0]) cube([220,10,150]);
}

slab(); pod(); stand();
