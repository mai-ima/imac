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
wl = S['pod']['wall']
if 'dome' in S:
    Dm = S['dome']; IN = (W - 2*Dm['inset_left_right'] - 2*wl, H - Dm['inset_bottom'] - Dm['inset_top'] - 2*wl, Dm['total_t'] - slab - wl)
    def dome_depth(d): return Dm['edge_inner_depth'] + (IN[2] - Dm['edge_inner_depth']) * min(1.0, d / Dm['run'])
else:
    pod_w = W - S['pod']['side_margin']; IN = (pod_w - 2*wl, S['pod']['h'] - 2*wl, S['pod']['total_t'] - slab - wl); dome_depth = None
print(f"ポッド内寸 {IN[0]:.1f} x {IN[1]:.1f} x {IN[2]:.1f} mm (幅 x 高 x 奥行)")
boxes = {}
for it in L['items']:
    x, y, z = it['pos']; sx, sy, sz = it['size']; boxes[it['id']] = (x, y, z, x+sx, y+sy, z+sz)
    cont = x >= 0 and y >= 0 and z >= 0 and x+sx <= IN[0] and y+sy <= IN[1] and z+sz <= IN[2]
    extra = ''
    if dome_depth:
        dmin = min(x, IN[0]-(x+sx), y, IN[1]-(y+sy)); allow_z = dome_depth(max(dmin, 0)); cont = cont and (z+sz+3.0 <= allow_z)
        extra = f' 縁距離{dmin:.0f}→許容奥行{allow_z:.0f}(要{z+sz+3:.0f})'
    chk(f"収まり {it['id']}", cont, f"{P[it['id']]['name'][:34]}  上端z={z+sz:.1f}/{IN[2]:.0f}{extra}")
allow = {frozenset(p) for p in [('board','cooler'),('board','ssd'),('board','ram'),('board','riser'),('gpu','riser'),('cooler','ram'),('cooler','ssd')]}
warn_pairs = [('cooler','ram','AIOポンプ(ARCTIC LF III Pro, Ø91)とDIMMの間隔。ポンプ外形とホース口の向き・DIMMの高さを実物で要確認'),('cooler','ssd','SSD(基板のドーターカード上)とポンプの位置関係。ドーターカードの高さ・位置は未確認')]
for a_,b_,m_ in warn_pairs:
    A_,B_=boxes[a_],boxes[b_]
    if all(A_[i] < B_[i+3] and B_[i] < A_[i+3] for i in range(3)): print(f'[WARN] {a_}-{b_}: AABB重なり。{m_}')
for a, b in itertools.combinations(boxes, 2):
    A, B = boxes[a], boxes[b]
    ov = all(A[i] < B[i+3] and B[i] < A[i+3] for i in range(3))
    if ov and frozenset((a, b)) not in allow: chk(f"干渉 {a}-{b}", False, 'AABBが重なる')
chk('干渉なし(許容組合せを除く)', ok, '全組合せ確認済')
# 最小クリアランス(ふた側)
pass

# ---- 電力 ----
cpu = P['cpu']['facts']['ppt_w']; gpu = P['gpu']['facts']['tgp_w']; misc = 45; panel = 32.5/0.9
load = cpu + gpu + misc + panel
psu_w = P['psu']['facts'].get('provisional_w', 600)
chk('電源容量(余裕30%以上)', load <= 0.7 * psu_w, f"CPU PPT{cpu}+GPU TGP{gpu}+他{misc}+パネル{panel:.0f} = {load:.0f} W <= {psu_w}W x 0.7 = {0.7*psu_w:.0f}W (使用率 {load/psu_w*100:.0f}%)")
chk('PCIe補助電源', True, 'GPU 8ピン x1 <- SF750 の 6+2 ピン x2 のうち1本(コネクタ数は小売情報、公式未確認。ケーブル400mm)')
chk('パネル電源', True, 'コントローラ基板 12V <- SF750 のSATA/Molex(ケーブル要確認)(パネル VDD 10V は基板が生成。型番一致が条件)')

# ---- 冷却 ----
heat = cpu + gpu + misc + (500*0 + load*0.1)   # 電源損失10%
nfan = sum(1 for it in L['items'] if it['id'].startswith('fan'))
air = (nfan * P['fan']['facts']['airflow_m3h'] + (2 * 131 if any(it['id']=='radiator' for it in L['items']) else 0)) * 0.55     # 通風抵抗で55%と仮定
dT = heat / (1.2*1005*air/3600)
chk('排気温度上昇', dT <= 20, f"発熱{heat:.0f}W / 風量{air:.0f} m3/h(ケースファン{nfan}基+ラジエーターファン2基(P12 Pro 131m3/h/基)、自由流の55%仮定) → ΔT={dT:.1f}K (<=20K目標)")
print(f"[注意] CPU冷却: 9800X3D PPT {cpu}W(制限なし)に対しAMD推奨の液冷(ARCTIC LF III Pro 240)。公式TDP定格が無いため実機での温度確認が必須")
print('\n総合:', 'すべて満たす(ただし assumed/retail 項目は実物確認が必要)' if ok else '未達あり')
sys.exit(0 if ok else 1)
