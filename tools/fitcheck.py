#!/usr/bin/env python3
"""市販部品だけで成立するかの機械チェック(収まり・干渉・電力・風量)。 実行: python3 tools/fitcheck.py"""
import json, os, sys, itertools
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); P = json.load(open(f'{R}/model/parts.json')); L = json.load(open(f'{R}/model/layout.json'))
ok = True
unverified = []
def unv(name, detail):
    """実物/公式未確認の項目。PASSにせず UNVERIFIED として数える(偽PASS防止, K23)。"""
    unverified.append(name); print(f"[UNV] {name}: {detail}")

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
stack = 1.1 + 0.9 + out[2] + 1.0 + 2.0
chk('前面スラブ厚', stack <= slab, f"ガラス1.1+エアギャップ0.9(OCA無し)+パネル{out[2]}+隙間1.0+背板2.0 = {stack:.1f} <= {slab} (余裕{slab-stack:.1f})")

# ---- ポッド内部 ----
wl = S['pod']['wall']
if 'dome' in S:
    Dm = S['dome']; IN = (W - 2*Dm['inset_left_right'] - 2*wl, H - Dm['inset_bottom'] - Dm['inset_top'] - 2*wl, Dm['total_t'] - slab - wl)
    def dome_depth(d): return Dm['edge_inner_depth'] + (IN[2] - Dm['edge_inner_depth']) * (lambda s: s*s*(3-2*s))(max(0.0, min(1.0, d / Dm['run'])))   # smoothstep: Blenderモデル/図面と同一
else:
    pod_w = W - S['pod']['side_margin']; IN = (pod_w - 2*wl, S['pod']['h'] - 2*wl, S['pod']['total_t'] - slab - wl); dome_depth = None
print(f"ポッド内寸 {IN[0]:.1f} x {IN[1]:.1f} x {IN[2]:.1f} mm (幅 x 高 x 奥行)")
import math
def rr_dist(x0, y0, x1, y1, step=5.0):
    """矩形(部品外形)から角丸矩形(ドーム内寸, 角R=corner_r-壁)の境界までの最短距離(角Rを考慮)。"""
    Rr = Dm['corner_r'] - wl; hx, hy = IN[0]/2, IN[1]/2; best = 1e9
    xs = [x0 + (x1-x0)*i/max(1,int((x1-x0)/step)) for i in range(max(1,int((x1-x0)/step))+1)]; ys = [y0 + (y1-y0)*i/max(1,int((y1-y0)/step)) for i in range(max(1,int((y1-y0)/step))+1)]
    for (px, py) in [(a, b) for a in xs for b in (y0, y1)] + [(a, b) for a in (x0, x1) for b in ys]:
        qx, qy = abs(px-hx) - (hx-Rr), abs(py-hy) - (hy-Rr)
        sdf = math.hypot(max(qx,0), max(qy,0)) + min(max(qx,qy),0) - Rr; best = min(best, -sdf)
    return best
boxes = {}
for it in L['items']:
    x, y, z = it['pos']; sx, sy, sz = it['size']; boxes[it['id']] = (x, y, z, x+sx, y+sy, z+sz)
    cont = x >= 0 and y >= 0 and z >= 0 and x+sx <= IN[0] and y+sy <= IN[1] and z+sz <= IN[2]
    extra = ''
    if dome_depth and it['id']!='ac_inlet':      # ac_inletはドーム下辺の開口を貫通するため傾斜壁の判定対象外
        dmin = rr_dist(x, y, x+sx, y+sy); allow_z = dome_depth(max(dmin, 0)); cont = cont and (z+sz+3.0 <= allow_z)
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
    if ov and frozenset((a, b)) in allow: print(f'[EXPECTED_OVERLAP] {a}-{b}: AABB重なりを許容(基板上取付/重なりは実形状未確認=UNVERIFIED。例外許可リスト allow の項目)')
chk('干渉なし(許容組合せを除く)', ok, '全組合せ確認済')
# 最小クリアランス(ふた側)
pass

# ---- 基板上の最大高さ・プラグ空間(v10追加: 従来は基板を1.6mmの板として扱い、I/Oスタックやポート前のプラグ空間を見ていなかった) ----
def edge_dist(x, y, Wd, Hd, Rc):
    dx, dy = min(x, Wd - x), min(y, Hd - y)
    return max(0.0, Rc - math.hypot(Rc - dx, Rc - dy)) if (dx < Rc and dy < Rc) else min(dx, dy)
_bx, _by, _bz = [i for i in L['items'] if i['id'] == 'board'][0]['pos'][:3]; _g = [i for i in L['items'] if i['id'] == 'gpu'][0]
_Wd, _Hd, _Rc = IN[0], IN[1], Dm['corner_r'] - wl if 'dome' in S else 47
IO_TOP = (_bz + 1.6) + 44.45 + 0.0       # I/Oシールド(ATX標準44.45mm)の上端z。窓の外側は傾斜面より低い必要がある
IO_WIN_END = _by - 18 + 22               # cover_io_cutter の y 終端(build と同じ)
dd = dome_depth(edge_dist(_bx + 70, IO_WIN_END, _Wd, _Hd, _Rc))
chk('I/Oスタック上端と傾斜面(窓の終端)', dd >= IO_TOP + 3, f"I/O上端z={IO_TOP:.1f} + 隙間3 <= 窓終端 y={IO_WIN_END:.0f} での内面深さ {dd:.1f}mm")
GPLUG = _g['pos'][1] - 30
dd2 = dome_depth(edge_dist(_g['pos'][0] + 60, GPLUG, _Wd, _Hd, _Rc))
chk('GPU出力プラグ空間(30mm)と傾斜面', dd2 >= 28 + 3, f"プラグ先端 y={GPLUG:.0f} での内面深さ {dd2:.1f}mm >= プラグ上端z28+3(窓: cover_gpu_cutter)")
_r = [i for i in L['items'] if i['id'] == 'radiator'][0]
dd3 = dome_depth(edge_dist(_r['pos'][0] + _r['size'][0], _r['pos'][1] + _r['size'][1] / 2, _Wd, _Hd, _Rc))
chk('I/O・GPU窓がドーム縁まで連続(プラグを外から挿せる)', S['windows']['io_y0'] <= -2 and S['windows']['gpu_y0'] <= -2, f"io窓 y0={S['windows']['io_y0']}, GPU窓 y0={S['windows']['gpu_y0']} (<=-2 で縁を貫通)")
chk('ホース上空経路とドーム/フィルタの隙間', S['dome']['total_t'] - S['slab_t'] - S['pod']['wall'] - 3 - (143.0 + 6.2) >= 5.0, f"内奥行{S['dome']['total_t']-S['slab_t']-S['pod']['wall']}-フィルタ3 - ホース上端149.2 >= 5mm")
chk('ラジエーター右端と傾斜面', dd3 >= _r['pos'][2] + _r['size'][2] + 3, f"右端での内面深さ {dd3:.1f}mm >= ラジエーター上端 {_r['pos'][2]+_r['size'][2]:.0f}+3")
# ---- 電力 ----
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import power_budget as PB
_b = PB.budget('最大(CPU PPT+GPU TGP同時)'); cpu = _b['cpu']; gpu = _b['gpu']; misc = _b['board'] + _b['fans']; panel = _b['panel']
load = cpu + gpu + misc + panel
psu_w = P['psu']['facts'].get('provisional_w', 600)
chk('電源容量(余裕30%以上)', load <= 0.7 * psu_w, f"CPU PPT{cpu}+GPU TGP{gpu}+他{misc}+パネル{panel:.0f} = {load:.0f} W <= {psu_w}W x 0.7 = {0.7*psu_w:.0f}W (使用率 {load/psu_w*100:.0f}%)")
unv('GPU電源コネクタ(12V-2x6)', 'PSU(SF1000)の12V-2x6ケーブル有無・長さは公式未確認(U34)。W3の経路長はcable_checkで検査済みだが、コネクタ形状はUNVERIFIED')
unv('パネル/コントローラ12V給電', 'コントローラ基板型番未選定(U37)のため給電仕様・コネクタ互換は未検証')

# ---- 冷却 ----
heat = cpu + gpu + misc + (500*0 + load*0.1)   # 電源損失10%
nfan = sum(1 for it in L['items'] if it['id'].startswith('fan'))
air = (nfan * (P['fan']['facts']['airflow_m3h'] if 'fan' in P else 0) + (2 * 131 if any(it['id']=='radiator' for it in L['items']) else 0)) * 0.55     # 通風抵抗で55%と仮定
dT = heat / (1.2*1005*air/3600)
chk('排気温度上昇', dT <= 20, f"発熱{heat:.0f}W / 風量{air:.0f} m3/h(ケースファン{nfan}基+ラジエーターファン2基(P12 Pro 131m3/h/基)、自由流の55%仮定) → ΔT={dT:.1f}K (<=20K目標)")
print(f"[注意] CPU冷却: {P['cpu']['name']} PPT {cpu}W(制限なし)に対し240mm AIO(AMD推奨は240/280mm級, 実測はUNVERIFIED)。実機での温度確認が必須")
print(f'\nUNVERIFIED {len(unverified)} 件: ' + ', '.join(unverified))
print('\n総合:', ('計算可能な項目はすべて満たす(UNVERIFIED項目は合格扱いではない)') if ok else '未達あり')
sys.exit(0 if ok else 1)
