"""質量・重心モデル(単一情報源)。layout.json の位置から重心を導出する。質量は部品カタログ/推定(未実測, U25)。
座標: z=前面ガラスからの距離(背面+), y=本体下端からの高さ。"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); L = {i['id']: i for i in json.load(open(f'{R}/model/layout.json'))['items']}
D = S['dome']; slab = S['slab_t']; W = S['body_w']; H = S['panels'][str(S['panel_size'])]['h'] + S['bezel'] + S['chin']
rho = 2.68e-6; g = 9.81
def cg_item(k):
    x, y, z = L[k]['pos']; sx, sy, sz = L[k]['size']
    return slab + z + sz / 2, D['inset_bottom'] + S['dome']['inner_wall_offset_mm'] + y + sy / 2
def dome_integral(step=6.0):
    """ドーム殻(smoothstep曲面)の表面積と重心zを数値積分(傾斜による面積増を含む)。穿孔33%開口を質量に反映。"""
    import math
    dw, dh = W - 2 * D['inset_left_right'], H - D['inset_bottom'] - D['inset_top']; Rc = D['corner_r']; inner = D['total_t'] - slab - S['dome']['inner_wall_offset_mm']
    A = 0.0; Az = 0.0; nx, ny = int(dw / step), int(dh / step)
    for i in range(nx):
        for j in range(ny):
            x, y = (i + .5) * step, (j + .5) * step; dx, dy = min(x, dw - x), min(y, dh - y)
            d = max(0.0, Rc - math.hypot(Rc - dx, Rc - dy)) if (dx < Rc and dy < Rc) else min(dx, dy)
            t = min(1.0, d / D['run']); z = D['edge_inner_depth'] + (inner - D['edge_inner_depth']) * t * t * (3 - 2 * t)
            slope = (inner - D['edge_inner_depth']) * 6 * t * (1 - t) / D['run'] if t < 1 else 0.0
            a = step * step * math.sqrt(1 + slope * slope); A += a; Az += a * (slab + z)
    return A, Az / A
dome_area, dome_cg_z = dome_integral(); dome_area *= 0.67      # 穿孔(開口約33%)を除いた金属面積
def head():
    items = [('前面ガラス(1.1mm)', 620 * 415 * 1.1 * 2.5e-6, 0.5, H / 2, '計算'), ('パネル(27型4K)', 2.5, 12, H / 2, 'BOE N50 公式2450g(Panelook)'), ('背板(スラブ枠一体)A5052 t2.0+リム', 620 * 415 * 2.0 * rho + 1.0, slab - 1, H / 2, '計算+リム推定'),
             ('サービストレイ t2.0', 590 * 371 * 2.0 * rho * 0.9, slab + 1, D['inset_bottom'] + 3 + 371 / 2, '計算'), ('ドーム t2.0(曲面積分)', dome_area * 2.0 * rho, dome_cg_z, D['inset_bottom'] + (H - D['inset_bottom'] - D['inset_top']) / 2, '計算')]
    for k, m, src in (('board', 0.55, '推定(基板0.4+CPU+DIMM)'), ('cooler', 0.65, '推定(ポンプ側)'), ('radiator', 1.0, 'ARCTIC 1665g合計から推定'), ('gpu', 1.3, '推定(小型5070 Ti, 未確認)'), ('psu', 1.05, '推定(SF1000)'), ('ctrl_board', 0.25, '推定'), ('ssd', 0.05, '推定'), ('ac_inlet', 0.12, '推定')):
        z, y = cg_item(k); items.append((k, m, z, y, src))
    items.append(('ケーブル/金具/ガスケット/ラッチ等', 0.9, slab + 20, H / 2, '推定')); items.append(('断熱シート(CP-19)', 0.2, slab - 1, H / 2, '推定')); items.append(('ヒンジブロック一式(ばね/ヒンジ/ブロック)', 1.2, slab + 12, 12, '推定')); return items
def swivel_mass(): sw = S.get('swivel'); return (sw['mass_stator_kg'] + sw['mass_rotor_kg']) if sw else 0.0
def stand_mass(): return S['stand'].get('base_kg', 1.8) + S['stand'].get('ballast_kg', 0) + swivel_mass()      # 首振りユニット(軸受+板+摩擦リング)を含む
def head_cg():
    it = head(); m = sum(i[1] for i in it); return m, sum(i[1] * i[2] for i in it) / m, sum(i[1] * i[3] for i in it) / m, it
