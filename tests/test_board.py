"""基板上の部品配置(model/x870i_layout.json)の幾何検査: 範囲内・相互非干渉。"""
import json, os, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = json.load(open(os.path.join(ROOT, 'model', 'x870i_layout.json'), encoding='utf-8'))
def ov(a, b, m=0.0): return a['x'][0] < b['x'][1] - m and b['x'][0] < a['x'][1] - m and a['y'][0] < b['y'][1] - m and b['y'][0] < a['y'][1] - m
def fixed():
    f = {'atx_pwr': BL['atx_pwr'], 'pcie_x16': BL['pcie_x16'], 'cpu_12v': BL['cpu_12v'], 'chipset': BL['chipset']}
    f['dimm_a'] = {'x': BL['dimm_slots']['x'], 'y': BL['dimm_slots']['y'][0]}; f['dimm_b'] = {'x': BL['dimm_slots']['x'], 'y': BL['dimm_slots']['y'][1]}
    sx, sy = BL['socket_center']; f['socket'] = {'x': [sx - 30, sx + 30], 'y': [sy - 30, sy + 30]}
    f['m2_daughter'] = {'x': [131, 156], 'y': [77, 138]}
    return f
class T(unittest.TestCase):
    def test_in_bounds(self):
        for c in BL['components']:
            self.assertTrue(0 <= c['x'][0] < c['x'][1] <= 170 and 0 <= c['y'][0] < c['y'][1] <= 170, c['id'])
    def test_no_mutual_overlap(self):
        C = BL['components']
        for i, a in enumerate(C):
            for b in C[i + 1:]: self.assertFalse(ov(a, b, 0.05), (a['id'], b['id']))
    def test_no_overlap_with_main_parts(self):
        F = fixed()
        for c in BL['components']:
            for k, f in F.items():
                if c['id'] == 'm2_pt2_conn' and k == 'm2_daughter': continue      # ドーターカード自身のコネクタ
                self.assertFalse(ov(c, f, 0.05), (c['id'], k))
    def test_height_declared(self):
        for c in BL['components']: self.assertGreater(c['h'], 0); self.assertIn('UNVERIFIED', c['h_source'])
if __name__ == '__main__': unittest.main()
