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
bad = 0
for c in CM.CAB:
    r = c['od'] / 2; pts = dense(c['pts']); n = len(pts)
    issues = []
    for i, p in enumerate(pts):
        if i < 7 or i > n - 8: continue            # 端点付近(≈20mm)
        for it in L:
            x, y, z = it['pos']; sx, sy, sz = it['size']
            if x - r < p[0] < x + sx + r and y - r < p[1] < y + sy + r and z - r < p[2] < z + sz + r:
                issues.append(f"{it['id']}と干渉 @({p[0]:.0f},{p[1]:.0f},z{p[2]:.0f})"); break
        # ドーム内面
        dmin = min(p[0], 590 - p[0], p[1], 371.3 - p[1]); s_ = max(0, min(1, dmin / Dm['run'])); lim = Dm['edge_inner_depth'] + (S['dome']['total_t'] - S['slab_t'] - 3 - Dm['edge_inner_depth']) * s_ * s_ * (3 - 2 * s_)
        if p[2] + r + 2 > lim: issues.append(f'ドーム内面に接触 @({p[0]:.0f},{p[1]:.0f},z{p[2]:.0f}) 許容{lim:.0f}')
    # 曲げ半径(元の制御点列で評価。ベジェ化で緩むので折れ線の外接円は保守的)
    p0 = c['pts']
    for i in range(1, len(p0) - 1):
        d1, d2 = math.dist(p0[i-1], p0[i]), math.dist(p0[i], p0[i+1]); m = min(d1, d2) / 2
        a = tuple(p0[i][k] + (p0[i-1][k] - p0[i][k]) * min(1, m / d1) for k in range(3)); b2 = tuple(p0[i][k] + (p0[i+1][k] - p0[i][k]) * min(1, m / d2) for k in range(3))
        rr = circ_r(a, p0[i], b2) if False else None
        # 折れ角 θ から、隣接区間の半分で内接する円弧半径 = m·tan(θ/2)...(θ=2つの方向ベクトルの内角)
        v1 = [p0[i][k] - p0[i-1][k] for k in range(3)]; v2 = [p0[i+1][k] - p0[i][k] for k in range(3)]
        dot = sum(v1[k] * v2[k] for k in range(3)) / (math.hypot(*v1) * math.hypot(*v2)); th = math.acos(max(-1, min(1, dot)))   # 方向変化角
        if th > 0.05:
            rad = m / math.tan(th / 2) if th < math.pi - 0.01 else 0
            if rad < c['mbr']: issues.append(f"折れ点{i}: 方向変化{math.degrees(th):.0f}° → 半径≈{rad:.0f}mm < 最小{c['mbr']}mm")
    if c['len_mm'] > c['ref_mm'] and c['ref_mm']: issues.append(f"長さ {c['len_mm']}mm > 公称 {c['ref_mm']}mm")
    print(('[NG ]' if issues else '[OK ]'), c['id'], c['name'], f"len={c['len_mm']}mm od={c['od']}")
    for s in issues[:6]: print('      ', s)
    bad += bool(issues)
# ケーブル同士の最小間隔
for i, a in enumerate(CM.CAB):
    for b in CM.CAB[i + 1:]:
        da, db = dense(a['pts']), dense(b['pts']); need = (a['od'] + b['od']) / 2 + 0.5; md = min(math.dist(p, q) for p in da[7:-7] for q in db[7:-7]) if len(da) > 14 and len(db) > 14 else 99
        if md < need: print('[NG ] 近接', a['id'], b['id'], f'最小間隔 {md:.1f}mm < 必要 {need:.1f}mm'); bad += 1
print('総合:', '問題なし' if not bad else f'{bad}件の問題')
