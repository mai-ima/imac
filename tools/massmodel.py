"""質量・重心モデル(単一情報源)。layout.json の位置から重心を導出する。質量は部品カタログ/推定(未実測, U25)。
座標: z=前面ガラスからの距離(背面+), y=本体下端からの高さ。"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); L = {i['id']: i for i in json.load(open(f'{R}/model/layout.json'))['items']}
D = S['dome']; slab = S['slab_t']; W = S['body_w']; H = S['panels'][str(S['panel_size'])]['h'] + S['bezel'] + S['chin']
rho = 2.68e-6; g = 9.81
def cg_item(k):
    x, y, z = L[k]['pos']; sx, sy, sz = L[k]['size']
    return slab + z + sz / 2, D['inset_bottom'] + S['pod']['wall'] + y + sy / 2
dome_area = (W - 2 * D['inset_left_right']) * (H - D['inset_bottom'] - D['inset_top']) * 1.25
def head():
    items = [('前面ガラス(1.1mm)', 620 * 415 * 1.1 * 2.5e-6, 0.5, H / 2, '計算'), ('パネル(27型4K)', 2.5, 12, H / 2, 'BOE N50 公式2450g(Panelook)'), ('背板(スラブ枠一体)A5052 t2.0+リム', 620 * 415 * 2.0 * rho + 1.0, slab - 1, H / 2, '計算+リム推定'),
             ('サービストレイ t2.0', 590 * 371 * 2.0 * rho * 0.9, slab + 1, D['inset_bottom'] + 3 + 371 / 2, '計算'), ('ドーム t2.0', dome_area * 2.0 * rho, slab + 55, D['inset_bottom'] + (H - D['inset_bottom'] - D['inset_top']) / 2, '計算')]
    for k, m, src in (('board', 0.55, '推定(基板0.4+CPU+DIMM)'), ('cooler', 0.65, '推定(ポンプ側)'), ('radiator', 1.0, 'ARCTIC 1665g合計から推定'), ('gpu', 0.95, '推定(公式未確認)'), ('psu', 0.96, '小売'), ('fan', 0.16, '小売'), ('ctrl_board', 0.25, '推定'), ('ssd', 0.05, '推定'), ('ac_inlet', 0.12, '推定')):
        z, y = cg_item(k); items.append((k, m, z, y, src))
    items.append(('ケーブル/金具/ガスケット/ラッチ等', 0.9, slab + 20, H / 2, '推定')); return items
def stand_mass(): return 1.8 + S['stand'].get('ballast_kg', 0)
def head_cg():
    it = head(); m = sum(i[1] for i in it); return m, sum(i[1] * i[2] for i in it) / m, sum(i[1] * i[3] for i in it) / m, it
