"""配線・ホースの経路定義(単一情報源)。layout.json から座標を導き、model/cables.json を出力する。
座標: トレイ内座標(mm, ドーム内側の左下原点, z=スラブ背面からの高さ)。経路は折れ線(Blenderではベジェで滑らかに)。
各ケーブルの最小曲げ半径 mbr は暫定値(公式/規格の裏付け調査中: docs/research-notes.md)。"""
import json, math, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = {i['id']: i for i in json.load(open(f'{R}/model/layout.json'))['items']}
bx, by, bz = L['board']['pos']; gx, gy, gz = L['gpu']['pos']; px, py, pz = L['psu']['pos']; cx, cy, cz = L['ctrl_board']['pos']
rx, ry, rz = L['radiator']['pos']; cl = L['cooler']['pos']; cs = L['cooler']['size']; ax, ay, az = L['ac_inlet']['pos']
PJ = json.load(open(f'{R}/model/pump.json')); SX, SYA, SYB, STIP = PJ['stub_x'], PJ['stub_y'][0], PJ['stub_y'][1], PJ['stub']['z'][1]
HZ2 = 124.0      # H2は H1(HZ)の13mm下を通し、平面で交差しても干渉しない
HZ = 143.0      # ホース水平部の中心高さ(曲げ半径40mm仮置き+出口スタブ先端z81)
Z1 = bz + 1.6; pcx, pcy = cl[0] + 45.5, cl[1] + cs[1] / 2      # ポンプ円盤中心(筐体は+x側)
CAB = [
 dict(id='W1', name='ATX 24ピン(短尺カスタム長)', kind='cable', od=9.6, awg=18, mbr=12, frm='PSU modular(24p)', to='基板 ATX24', conn='24p (20+4)', ref_mm=0, mat='rubber',
      pts=[(px + 33, py - 2, 38), (px + 33, py - 12, 36), (px + 34, py - 24, 29)]),
 dict(id='W2', name='CPU EPS 8ピン(短尺)', kind='cable', od=5.6, awg=16, mbr=12, frm='PSU modular(EPS)', to='基板 CPU_12V(8p)', conn='EPS 4+4', ref_mm=0, mat='rubber',
      pts=[(px + 14, py - 2, 38), (px + 14, py - 18, 40), (50, py - 18, 42), (50, 60, 30), (66, 42, 25)]),
 dict(id='W3', name='GPU 12V-2x6(16AWG)', kind='cable', od=9.0, awg=16, mbr=20, frm='PSU modular(12V-2x6)', to='GPU 12V-2x6', conn='12V-2x6: コネクタ後方35mm直線', ref_mm=400, mat='rubber',
      pts=[(px + 90, py - 2, 38), (px + 98, py - 8, 40), (215, py - 8, 44), (250, 240, 62), (300, 280, 70), (gx + 110, gy + 225, gz + 47), (gx + 110, gy + 288, gz + 47)]),
 dict(id='W4', name='コントローラ基板 12V(短尺)', kind='cable', od=4.4, awg=20, mbr=6, frm='PSU modular(SATA/周辺)', to='ctrl_board DC入力', conn='SATA電源 or 2pin', ref_mm=0, mat='rubber',
      pts=[(px + 112, py - 2, 30), (px + 118, py - 8, 28), (cx - 5, cy + 5, 23), (cx - 1, cy + 8, 20)]),
 dict(id='W5', name='アンビリカル(eDP 30p/12V/USB)', kind='cable', od=6.0, awg=0, mbr=16, frm='ctrl_board eDP', to='パネル背面コネクタ', conn='eDP 30p + 12V + USB2 (全長380mm=整備余長100mm込み=整備余長込み)', ref_mm=380, mat='umb',
      pts=[(cx + 28, cy + 95, cz + 22), (cx + 28, cy + 105, cz + 26), (cx + 5, 340, 21), (150, 347, 16), (40, 349, 13), (14, 349, 10)]),
 dict(id='W6', name='AC電源(C14インレット→PSU C13)', kind='cable', od=7.2, awg=16, mbr=14, frm='C14インレット', to='SF1000 AC入力', conn='C13(内部延長600mm級: 市販品要確認 U40)', ref_mm=600, mat='rubber',
      pts=[(ax + 14, ay + 28, az + 8), (36, 62, 22), (36, 300, 24), (56, 336, 22), (100, 348, 22), (125, 340, 22), (px + 62, py + 102, pz + 14)]),
 dict(id='W7', name='内部映像ケーブル(GPU DisplayPort → コントローラ基板 入力, K10追加)', kind='cable', od=4.5, awg=30, mbr=16, frm='GPU DP出力(ブラケット側)', to='ctrl_board 映像入力(DP/HDMI, 型番未確定 U51)', conn='DP→(DP/HDMI)短尺 300〜400mm 市販 or 特注(HBR3/DP1.4)', ref_mm=450, mat='rubber',
      pts=[(gx + 12, gy - 34, 17), (gx - 14, gy - 34, 17), (gx - 14, gy + 14, 27), (gx - 14, cy - 18, 27), (gx - 14, cy + 14, 28)]),
 dict(id='H1', name='AIOホース(ポンプ出口A→ラジエーター口A, 上面垂直出口)', kind='hose', od=12.4, awg=0, mbr=40, frm='ポンプ出口A(上面スタブ)', to='ラジエーター口A', conn='ARCTIC 450mm/ID6.0(最小曲げ半径は未確認 U45: 40mm仮置き)', ref_mm=450, mat='hose',
      pts=[(pcx + SX, pcy + SYA, cl[2] + STIP), (pcx + SX, pcy + SYA, HZ), (300, pcy + SYA, HZ), (390, ry + 9, HZ), (rx + 60 - 12, ry + 9, HZ), (rx + 60 - 12, ry + 9, rz + 50)]),
 dict(id='H2', name='AIOホース(ポンプ出口B→ラジエーター口B, 上面垂直出口)', kind='hose', od=12.4, awg=0, mbr=40, frm='ポンプ出口B(上面スタブ)', to='ラジエーター口B', conn='ARCTIC 450mm/ID6.0(最小曲げ半径は未確認 U45: 40mm仮置き)', ref_mm=450, mat='hose',
      pts=[(pcx + SX, pcy + SYB, cl[2] + STIP), (pcx + SX, pcy + SYB, HZ), (340, pcy + SYB, HZ), (405, ry + 9 + 14, HZ), (rx + 60 + 12, ry + 9 + 14, HZ), (rx + 60 + 12, ry + 9, rz + 50)]),
]
def _unit(v): n = math.sqrt(sum(x * x for x in v)); return tuple(x / n for x in v)
def fillet(pts, r):
    """折れ線の各隅を半径rの円弧で丸める。区間が短くrが取れない隅は取れる最大半径に下げ、実際の最小半径を返す。"""
    out = [pts[0]]; rmin = 1e9
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        u1 = _unit(tuple(b[k] - a[k] for k in range(3))); u2 = _unit(tuple(c[k] - b[k] for k in range(3)))
        dot = max(-1, min(1, sum(u1[k] * u2[k] for k in range(3)))); th = math.acos(dot)     # 方向変化角
        if th < 0.02: out.append(b); continue
        l1, l2 = math.dist(a, b), math.dist(b, c)
        av1 = l1 * (1.0 if i == 1 else 0.5); av2 = l2 * (1.0 if i == len(pts) - 2 else 0.5)      # 端の区間は全長を使える
        rr = min(r, min(av1, av2) / math.tan(th / 2) if th < math.pi - 0.05 else 0.0)
        d = rr * math.tan(th / 2); rmin = min(rmin, rr)
        t1 = tuple(b[k] - u1[k] * d for k in range(3)); t2 = tuple(b[k] + u2[k] * d for k in range(3))
        n = max(4, int(th / 0.2))
        for s in range(n + 1):        # 2次ベジェで円弧近似(制御点=隅)
            u = s / n; out.append(tuple((1 - u) ** 2 * t1[k] + 2 * (1 - u) * u * b[k] + u * u * t2[k] for k in range(3)))
    out.append(pts[-1]); return out, rmin
for c in CAB:
    c['path'], c['min_r_actual'] = fillet(c['pts'], c['mbr'])
    c['path'] = [tuple(round(v, 2) for v in q) for q in c['path']]; c['min_r_actual'] = round(c['min_r_actual'], 1) if c['min_r_actual'] < 1e8 else None
def plen(p): return sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))
for c in CAB:
    c['len_mm'] = round(plen(c['path']) * (1.0 if c['kind'] == 'hose' else 1.15)); c['verdict'] = 'OK' if (c['ref_mm'] == 0 or c['len_mm'] <= c['ref_mm']) else '不足/長すぎ(要確認)'
if __name__ == '__main__':
    json.dump({'_doc': '配線・ホース定義(トレイ内座標)。tools/cablemodel.py が生成。長さ=折れ線長(ケーブルは×1.15の余長)。mbrは暫定最小曲げ半径(mm)', 'cables': CAB}, open(f'{R}/model/cables.json', 'w'), ensure_ascii=False, indent=1); print('cables.json', len(CAB))
