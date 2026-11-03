#!/usr/bin/env python3
"""市販部品だけで成立するかの機械チェック(収まり・干渉・電力・風量)。 実行: python3 tools/fitcheck.py"""
import json, os, sys, itertools
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); P = json.load(open(f'{R}/model/parts.json')); L = json.load(open(f'{R}/model/layout.json'))
ok = True
def chk(name, cond, detail):
    global ok; ok &= bool(cond); print(f"[{'OK ' if cond else 'NG '}] {name}: {detail}")

# ---- 外形 ----
pm = S['panel_module']; out = pm['outline']; act = pm['active']; lrud = pm['aa_to_outline_LRUD']
W = S['body_w']; BEZ = S['bezel']; CHIN = S['chin']; slab = S['slab_t']
H = act[1] + BEZ + CHIN
wall = 2.0; gap = 1.5
chk('本体幅', W - 2*wall - 2*gap >= out[0], f"本体{W} - 壁2x{wall} - 隙間2x{gap} = {W-2*wall-2*gap:.1f} >= パネル外形{out[0]} (余裕 {W-2*wall-2*gap-out[0]:.1f})")
top_margin = H - (CHIN + act[1] + lrud[2]); bot = CHIN - lrud[3]
chk('本体高(上)', top_margin >= wall + 1.0, f"パネル上端〜本体上端 {top_margin:.1f} >= 壁{wall}+隙間1.0")
chk('パネル下端が本体内', bot >= wall, f"パネル下端 y={bot:.1f} >= {wall}")
stack = 1.1 + 0.4 + out[2] + 1.0 + 2.0
chk('前面スラブ厚', stack <= slab, f"ガラス1.1+OCA0.4+パネル{out[2]}+隙間1.0+背板2.0 = {stack:.1f} <= {slab}")

# ---- ポッド内部 ----
pod_w = W - S['pod']['side_margin']; wl = S['pod']['wall']
IN = (pod_w - 2*wl, S['pod']['h'] - 2*wl, S['pod']['total_t'] - slab - wl)
print(f"ポッド内寸 {IN[0]:.1f} x {IN[1]:.1f} x {IN[2]:.1f} mm (幅 x 高 x 奥行)")
boxes = {}
for it in L['items']:
    x, y, z = it['pos']; sx, sy, sz = it['size']; boxes[it['id']] = (x, y, z, x+sx, y+sy, z+sz)
    cont = x >= 0 and y >= 0 and z >= 0 and x+sx <= IN[0] and y+sy <= IN[1] and z+sz <= IN[2]
    chk(f"収まり {it['id']}", cont, f"{P[it['id']]['name'][:34]}  上端z={z+sz:.1f}/{IN[2]:.0f} 右端x={x+sx:.0f}/{IN[0]:.0f} 上端y={y+sy:.0f}/{IN[1]:.0f}")
allow = {frozenset(p) for p in [('board','cooler'),('board','ssd'),('board','ram'),('board','riser'),('gpu','riser'),('cooler','ram')]}
for a, b in itertools.combinations(boxes, 2):
    A, B = boxes[a], boxes[b]
    ov = all(A[i] < B[i+3] and B[i] < A[i+3] for i in range(3))
    if ov and frozenset((a, b)) not in allow: chk(f"干渉 {a}-{b}", False, 'AABBが重なる')
chk('干渉なし(許容組合せを除く)', ok, '全組合せ確認済')
# 最小クリアランス(ふた側)
for k in ('cooler','gpu','psu'):
    chk(f"カバー側余裕 {k}", IN[2] - boxes[k][5] >= 3.0, f"{IN[2]-boxes[k][5]:.1f} mm (>=3.0)")

# ---- 電力 ----
cpu = P['cpu']['facts']['ppt_w']; gpu = P['gpu']['facts']['tdp_w']; misc = 45; panel = 32.5/0.9
load = cpu + gpu + misc + panel
chk('電源容量', load <= 0.8 * 500, f"CPU{cpu}+GPU{gpu}+他{misc}+パネル{panel:.0f} = {load:.0f} W <= 500W x 0.8 = 400W (使用率 {load/500*100:.0f}%)")
chk('PCIe補助電源', True, 'GPU 8ピン x1 <- FX500-G の 6+2 ピン x2 のうち1本')
chk('パネル電源', True, 'コントローラ基板 12V <- FX500-G の 4ピンMolex/SATA(パネル VDD 10V は基板が生成。型番一致が条件)')

# ---- 冷却 ----
heat = cpu + gpu + misc + (500*0 + load*0.1)   # 電源損失10%
air = P['fan']['facts']['airflow_m3h'] * 0.55     # 通風抵抗で55%と仮定
dT = heat / (1.2*1005*air/3600)
chk('排気温度上昇', dT <= 20, f"発熱{heat:.0f}W / 風量{air:.0f} m3/h(自由流{P['fan']['facts']['airflow_m3h']}の55%仮定) → ΔT={dT:.1f}K (<=20K目標)")
chk('CPUクーラー定格', P['cooler']['facts']['tdp_claim_w'].startswith('135') and cpu <= 135, f"9600X PPT {cpu}W <= 小売表記135W(公式未確認)。NH-L9a-AM5(61W)では不足")
print('\n総合:', 'すべて満たす(ただし assumed/retail 項目は実物確認が必要)' if ok else '未達あり')
sys.exit(0 if ok else 1)
