#!/usr/bin/env python3
"""ドーム傾斜制約付きの配置探索。部品の長方形(x,y)を乱択+局所探索で配置し、制約を満たす案を出力する。
制約: ポッド内寸内、ドーム縁からの最小距離dminに対し z_top+margin <= depth(dmin)、重なり無し(許容ペア除く)、
GPUはライザー整合(基板PCIeスロットの右側に隣接、y指紋整列±tol)、基板I/O辺(下)はdepth>=I/O高、CPUポンプは基板上のソケット位置に固定。
実行: python3 tools/layout_search.py  → model/layout_dome.json を更新"""
import json, os, random, math
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); D = S['dome']
W = S['body_w'] - 2*D['inset_left_right'] - 6; H = (S['panels'][str(S['panel_size'])]['h'] + S['bezel'] + S['chin']) - D['inset_bottom'] - D['inset_top'] - 6
run, d0 = D['run'], D['edge_inner_depth']; DEPTH = D['total_t'] - S['slab_t'] - 3
def depth(d): s = max(0.0, min(1.0, d / run)); return d0 + (DEPTH - d0) * s * s * (3 - 2 * s)   # smoothstep(Blender/図面と同一)
def ok_z(x0, y0, x1, y1, ztop, margin=3.0):
    dmin = min(x0, W - x1, y0, H - y1); return dmin >= 0 and ztop + margin <= depth(dmin)
# 部品: id: (xsize, ysize, ztop, rot可)
I = {'board': (170, 170, 8.0, False), 'gpu': (120, 229, 53.0, False), 'radiator': (277, 120, 66.0, True),
     'psu': (125, 100, 66.5, True), 'fan': (120, 120, 28.0, False), 'ctrl': (55, 150, 18.0, True)}
PUMP = (108.47, 91.0, 4.6 + 9 + 68.5)   # ソケット中心の周り
SOCKET = (71.4, 89.1)                    # 基板座標(回転後)
IO_H = 49.0
best = None
rnd = random.Random(7)
def rect(it, x, y, rot):
    w, h, z, _ = I[it]; return (x, y, x + (h if rot else w), y + (w if rot else h), z)
def overlap(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
for trial in range(2000000):
    rrot = rnd.random() < .5
    rw, rh = (120, 277) if rrot else (277, 120)
    rx = rnd.uniform(0, W - rw); ry = rnd.uniform(0, H - rh); rad = (rx, ry, rx + rw, ry + rh, 66.0)
    if not ok_z(*rad): continue
    bx = rnd.uniform(0, W - 170); by = rnd.uniform(0, H - 170)
    if not ok_z(bx, by, bx + 170, by + 170, 8.0): continue
    if depth(by) < IO_H: continue                               # I/Oが出る下辺の深さ
    px, py = bx + SOCKET[0], by + SOCKET[1]
    pump = (px - PUMP[1] / 2, py - PUMP[0] / 2, px + PUMP[1] / 2, py + PUMP[0] / 2, PUMP[2])
    if not ok_z(*pump): continue
    # GPU: 基板右側(PCIeスロットx=bx+158..166)から20〜30mm右
    gx = bx + 170 + rnd.uniform(18, 30); gy = by + 43 + 16 - 16 + rnd.uniform(-6, 6) - 20   # 指紋y≈スロットy
    g = (gx, gy, gx + 120, gy + 229, 53.0)
    if not ok_z(*g) or overlap(g, (bx, by, bx + 170, by + 170)): continue
    if overlap(rad, (bx, by, bx + 170, by + 170)) or overlap(rad, g): continue
    placed = {'board': (bx, by, bx + 170, by + 170, 8.0), 'pump': pump, 'gpu': g, 'radiator': rad}
    # 残り部品を貪欲に配置
    fail = False
    for it in ('psu', 'fan', 'ctrl'):
        ok = False
        for _ in range(3000):
            rot = rnd.random() < .5 if I[it][3] else False
            w, h = (I[it][1], I[it][0]) if rot else (I[it][0], I[it][1])
            x = rnd.uniform(0, W - w); y = rnd.uniform(0, H - h); r = (x, y, x + w, y + h, I[it][2])
            if not ok_z(*r): continue
            # 他部品と重ならない(基板とポンプは別: 基板は低背だが重ならないよう扱う)
            if any(overlap(r, p) for k, p in placed.items() if not (k == 'board' and it in ())): continue
            placed[it] = r; ok = True; break
        if not ok: fail = True; break
    if fail: continue
    free = sum(1 for _ in range(0))  # 将来: 余白評価
    best = (trial, placed); break
if not best: print('配置が見つかりませんでした(ドーム寸法の拡大が必要)'); raise SystemExit(1)
print('配置成功 試行', best[0]); out = {}
for k, r in best[1].items(): print(f"  {k:9s} x {r[0]:6.1f}..{r[2]:6.1f}  y {r[1]:6.1f}..{r[3]:6.1f}  z_top {r[4]:5.1f}")
json.dump({k: {'x0': round(r[0], 1), 'y0': round(r[1], 1), 'x1': round(r[2], 1), 'y1': round(r[3], 1), 'z_top': r[4]} for k, r in best[1].items()}, open(f'{R}/model/layout_dome.json', 'w'), indent=1)
print(f'ドーム内寸 {W:.0f} x {H:.0f}, 最大深さ {DEPTH}, 傾斜 {run}')
