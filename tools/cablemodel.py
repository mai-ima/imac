"""配線・ホースの経路定義(単一情報源)。layout.json から座標を導き、model/cables.json を出力する。
座標: トレイ内座標(mm, ドーム内側の左下原点, z=スラブ背面からの高さ)。経路は折れ線(Blenderではベジェで滑らかに)。
各ケーブルの最小曲げ半径 mbr は暫定値(公式/規格の裏付け調査中: docs/research-cables.md)。"""
import json, math, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = {i['id']: i for i in json.load(open(f'{R}/model/layout.json'))['items']}
bx, by, bz = L['board']['pos']; gx, gy, gz = L['gpu']['pos']; px, py, pz = L['psu']['pos']; cx, cy, cz = L['ctrl_board']['pos']
rx, ry, rz = L['radiator']['pos']; cl = L['cooler']['pos']; cs = L['cooler']['size']; ax, ay, az = L['ac_inlet']['pos']; fx, fy, fz = L['fan']['pos']
Z1 = bz + 1.6; pcx, pcy = cl[0] + cs[0] / 2, cl[1] + cs[1] / 2
CAB = [
 dict(id='W1', name='ATX 24ピン', kind='cable', od=9.6, awg=18, mbr=30, frm='PSU modular(24p)', to='基板 ATX24', conn='24p (20+4)', ref_mm=300, mat='rubber',
      pts=[(px + 14, py - 2, pz + 25), (px - 2, py - 3, pz + 22), (bx + 38, by + 168, Z1 + 20), (bx + 38, by + 164, Z1 + 14)]),
 dict(id='W2', name='CPU EPS 8ピン', kind='cable', od=5.6, awg=16, mbr=20, frm='PSU modular(EPS)', to='基板 CPU_12V(8p)', conn='EPS 4+4', ref_mm=400, mat='rubber',
      pts=[(px + 33, py - 2, pz + 25), (px + 33, py - 8, 46), (px - 70, py - 4, 46), (88, 196, 44), (88, 60, 26), (99, 46, 22)]),
 dict(id='W3', name='GPU PCIe 6+2ピン', kind='cable', od=6.4, awg=16, mbr=20, frm='PSU modular(PCIe)', to='GPU 8ピン', conn='PCIe 6+2', ref_mm=400, mat='rubber',
      pts=[(px + 71, py - 2, pz + 25), (px + 80, py - 10, 56), (300, 200, 63), (385, 255, 63), (391, 262, 57), (391, gy + 213, gz + 47)]),
 dict(id='W4', name='コントローラ基板 12V', kind='cable', od=4.4, awg=20, mbr=15, frm='PSU modular(SATA/周辺)', to='ctrl_board DC入力', conn='SATA電源 or 2pin', ref_mm=0, mat='rubber',
      pts=[(px + 52, py - 2, pz + 25), (px + 52, py - 8, 56), (110, 196, 56), (75, 190, 56), (70, 160, 30), (cx + 48, cy + 112, cz + 12)]),
 dict(id='W5', name='アンビリカル(eDP 30p/12V/USB)', kind='cable', od=6.0, awg=0, mbr=25, frm='ctrl_board eDP', to='パネル背面コネクタ', conn='eDP 30p + 12V + USB2 (全長250mm=整備余長込み)', ref_mm=250, mat='umb',
      pts=[(cx + 28, cy + 146, cz + 12), (cx + 20, cy + 165, 12), (8, 180, 8), (-2, 180, 2)]),
 dict(id='W6', name='AC電源(C14インレット→PSU C13)', kind='cable', od=7.2, awg=16, mbr=25, frm='C14インレット', to='SF750 AC入力', conn='C13(内部延長600mm級: 市販品要確認 U40)', ref_mm=600, mat='rubber',
      pts=[(ax + 14, ay + 20, az + 9), (ax + 14, ay + 26, 24), (281, 50, 24), (281, 310, 24), (px + 62, 314, 22), (px + 62, py + 102, 16)]),
 dict(id='H1', name='AIOホース(上段)', kind='hose', od=12.4, awg=0, mbr=60, frm='ポンプ出口A', to='ラジエーター入口', conn='ARCTIC 450mm/ID6.0', ref_mm=450, mat='hose',
      pts=[(pcx + 40, pcy - 36, cl[2] + 17), (pcx + 70, pcy - 38, 40), (262, 76, 44), (272, 58, 40), (290, 46, 38), (350, 46, 38), (440, 46, 34), (rx + 40, ry + 4, rz + 19)]),
 dict(id='H2', name='AIOホース(下段)', kind='hose', od=12.4, awg=0, mbr=60, frm='ポンプ出口B', to='ラジエーター出口', conn='ARCTIC 450mm/ID6.0', ref_mm=450, mat='hose',
      pts=[(pcx - 40, pcy - 36, cl[2] + 17), (pcx - 30, 66, 42), (200, 66, 44), (262, 62, 46), (276, 44, 42), (290, 32, 36), (350, 32, 36), (470, 32, 36), (rx + 80, ry + 4, rz + 19)]),
]
def plen(p): return sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))
for c in CAB:
    c['len_mm'] = round(plen(c['pts']) * (1.0 if c['kind'] == 'hose' else 1.15)); c['verdict'] = 'OK' if (c['ref_mm'] == 0 or c['len_mm'] <= c['ref_mm']) else '不足/長すぎ(要確認)'
if __name__ == '__main__':
    json.dump({'_doc': '配線・ホース定義(トレイ内座標)。tools/cablemodel.py が生成。長さ=折れ線長(ケーブルは×1.15の余長)。mbrは暫定最小曲げ半径(mm)', 'cables': CAB}, open(f'{R}/model/cables.json', 'w'), ensure_ascii=False, indent=1); print('cables.json', len(CAB))
