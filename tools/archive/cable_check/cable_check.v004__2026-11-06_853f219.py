#!/usr/bin/env python3
"""配線の干渉・曲げ半径・長さの検査。部品(layout AABB)との貫通、ケーブル同士の近接、折れ角の曲げ半径(外接円)を判定する。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import cablemodel as CM
L = json.load(open(f'{R}/model/layout.json'))['items']
S = json.load(open(f'{R}/model/spec.json')); Dm = S['dome']
def dense(pts, step=3.0):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for k in range(n): out.append(tuple(a[i] + (b[i] - a[i]) * k / n for i in range(3)))
    out.append(pts[-1]); return out
def circ_r(a, b, c):
    ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
    cr = [(b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]), (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]), (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])]
    area2 = math.sqrt(sum(v * v for v in cr))
    return float('inf') if area2 < 1e-9 else ab * bc * ca / (2 * area2)
# 各ケーブルが「始点/終点の機器」と接するのは許容: 端点から 20mm 以内は無視
# 小物障害物(AABB): 吊りピン頭, PEスタッド, GPU低背ステー, 基板スタンドオフ等
OBST = []
for (kx, ky) in json.load(open(f'{R}/model/layout.json'))['keyholes']: OBST.append(('吊りピン', kx - 5, ky + 7, 5.5, kx + 5, ky + 17, 9.5))
OBST.append(('PEスタッド', 22, 116, 5, 30, 124, 14)); gx_, gy_ = [i for i in L if i['id'] == 'gpu'][0]['pos'][:2]; gw_ = [i for i in L if i['id'] == 'gpu'][0]['size'][0]
OBST.append(('GPUステー', gx_ - 2, gy_ - 14, 5, gx_ + gw_ + 2, gy_ - 4, 14))
def edge_dist(x, y, W_=590.0, H_=371.3, Rc=47.0):
    """ドーム内面外周(角丸矩形 角R=corner_r-壁)までの内側距離。角では円弧距離(矩形距離より小さくなる)。"""
    dx, dy = min(x, W_ - x), min(y, H_ - y)
    if dx < Rc and dy < Rc: return max(0.0, Rc - math.hypot(Rc - dx, Rc - dy))
    return min(dx, dy)
# GPU出力プラグ(HDMI/DP オーバーモールド≈30mm)の占有空間
OBST.append(('GPU出力プラグ空間', gx_ + 2, gy_ - 30, 10, gx_ + 122, gy_, 28))
bad = 0
for c in CM.CAB:
    r = c['od'] / 2; pts = dense(c['path']); n = len(pts)
    issues = []
    for i, p in enumerate(pts):
        sk = 9 if c['kind'] == 'hose' else 2      # ホースは両端のスタブ/ポートに被さるため約27mm除外、ケーブルは約6mm
        if i < sk or i > n - 1 - sk: continue
        for it in L:
            x, y, z = it['pos']; sx, sy, sz = it['size']
            if it['id'] == 'cooler':      # ポンプ: 円盤キャップ(Ø91×z0〜55)+VRMケージ+側方筐体(+x側17.5mm張出, z8〜46)。ホース口スタブ(z55〜81)は被さる部分なので除外
                ccx, ccy = x + 45.5, y + sy / 2; hit = (math.hypot(p[0] - ccx, p[1] - ccy) < 45.5 + r and z - r < p[2] < z + 55 + r) or (ccx + 35 - r < p[0] < ccx + 63 + r and abs(p[1] - ccy) < 23 + r and z + 8 - r < p[2] < z + 46 + r)
            else: hit = x - r < p[0] < x + sx + r and y - r < p[1] < y + sy + r and z - r < p[2] < z + sz + r
            if hit:
                issues.append(f"{it['id']}と干渉 @({p[0]:.0f},{p[1]:.0f},z{p[2]:.0f})"); break
        for (nm, x0, y0, z0, x1, y1, z1) in OBST:
            if x0 - r < p[0] < x1 + r and y0 - r < p[1] < y1 + r and z0 - r < p[2] < z1 + r: issues.append(f'{nm}と干渉 @({p[0]:.0f},{p[1]:.0f},z{p[2]:.0f})'); break
        # ドーム内面
        dmin = edge_dist(p[0], p[1]); s_ = max(0, min(1, dmin / Dm['run'])); lim = Dm['edge_inner_depth'] + (S['dome']['total_t'] - S['slab_t'] - 3 - Dm['edge_inner_depth']) * s_ * s_ * (3 - 2 * s_)
        if p[2] + r + 2 > lim: issues.append(f'ドーム内面に接触 @({p[0]:.0f},{p[1]:.0f},z{p[2]:.0f}) 許容{lim:.0f}')
    # 曲げ半径: 各隅を半径mbrの円弧で丸める(区間が短く取れない隅は実半径が低下) → 実半径が規定未満なら不合格
    if c['min_r_actual'] is not None and c['min_r_actual'] < c['mbr'] - 0.5: issues.append(f"区間が短く規定半径を確保できない隅あり: 実半径≈{c['min_r_actual']:.0f}mm < 規定{c['mbr']}mm")
    if c['len_mm'] > c['ref_mm'] and c['ref_mm']: issues.append(f"長さ {c['len_mm']}mm > 公称 {c['ref_mm']}mm")
    print(('[NG ]' if issues else '[OK ]'), c['id'], c['name'], f"len={c['len_mm']}mm od={c['od']}")
    for s in issues[:6]: print('      ', s)
    bad += bool(issues)
# ケーブル同士の最小間隔
for i, a in enumerate(CM.CAB):
    for b in CM.CAB[i + 1:]:
        da, db = dense(a['path']), dense(b['path']); need = (a['od'] + b['od']) / 2 + 0.5; md = min(math.dist(p, q) for p in da[7:-7] for q in db[7:-7]) if len(da) > 14 and len(db) > 14 else 99
        if md < need: print('[NG ] 近接', a['id'], b['id'], f'最小間隔 {md:.1f}mm < 必要 {need:.1f}mm'); bad += 1
print('総合:', '問題なし' if not bad else f'{bad}件の問題')
