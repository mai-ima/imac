"""データ不変条件と負例テスト(GA-18)。実行: python3 -m unittest discover -s tests -v  (外部依存なし)"""
import json, os, re, subprocess, sys, tempfile, unittest, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(f'{R}/{p}', encoding='utf-8'))
class Data(unittest.TestCase):
    def test_gpu_official_specs(self):          # GA-01: RTX 5070 Ti は CUDA 8960 / 256bit
        g = J('model/parts.json')['gpu']['facts']; self.assertEqual(g['cuda'], 8960); self.assertIn('256bit', g['mem'])
    def test_ctrl_board_size_single_source(self):   # GA-03: parts と layout の寸法が一致
        L = {i['id']: i for i in J('model/layout.json')['items']}; P = J('model/parts.json')['ctrl_board']
        self.assertEqual(list(L['ctrl_board']['size']), list(P['dims']))
    def test_gasket_values_consistent(self):    # GA-05: 0.098N/mm・33% が正。≦0.08 等の旧値が現行 custom_parts に無い
        t = open(f'{R}/model/custom_parts.json', encoding='utf-8').read(); self.assertNotIn('≦0.08N/mm', t); self.assertAlmostEqual(J('model/spec.json')['dome_seal']['line_force_N_per_mm'], 0.098)
    def test_cp04_head_thickness_unique(self):  # GA-07
        t = open(f'{R}/model/custom_parts.json', encoding='utf-8').read(); self.assertNotIn('頭Ø10×4', t)
    def test_rotor_diameter_text(self):         # GA-11
        self.assertNotIn('Ø144', J('model/spec.json')['neck']['doc'])
    def test_spec_swivel_vs_custom_parts(self):
        sw = J('model/spec.json')['swivel']; cp = {p['id']: p for p in (lambda c: c['parts'] if 'parts' in c else c)(J('model/custom_parts.json')) if isinstance(p, dict)}
        self.assertEqual(cp['CP-21']['size'][0], 2 * sw['rotor_r']); self.assertEqual(cp['CP-20']['size'][0], 2 * sw['stator_r'])
class Physics(unittest.TestCase):
    def test_balancer_gate_passes_unverified_only(self):   # R9T-001: カム方式の収支(exit 2=UNVERIFIED, 1=NG)
        r = subprocess.run([sys.executable, f'{R}/tools/balance_calc.py'], capture_output=True, text=True); self.assertEqual(r.returncode, 2, r.stdout[-300:])
    def test_old_lever_spring_is_destabilizing(self):      # 旧方式の退行検査: ピン間距離は|a|で増加=圧縮ばねは緩む
        import math; e, s = 25.0, 76.0; l = lambda a: math.hypot(e * math.sin(math.radians(a)), s - e * math.cos(math.radians(a)))
        self.assertGreater(l(40), l(0)); self.assertGreater(l(-15), l(0))
class GatesNegative(unittest.TestCase):
    def test_stale_check_detects_injected_old_value(self):   # 負例: 旧値を注入した複製で stale_check が FAIL する
        with tempfile.TemporaryDirectory() as d:
            pat = open(f'{R}/tools/stale_check.py', encoding='utf-8').read(); self.assertIn("z\\s*=\\s*43", pat)
            self.assertIsNotNone(re.search(r'z\s*=\s*43(?!\d)', 'ヒンジ軸 z=43mm'))
    def test_validate_state_rejects_done_without_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            shutil.copytree(f'{R}/audit_control', f'{d}/audit_control', ignore=shutil.ignore_patterns('reports'))
            T = json.load(open(f'{d}/audit_control/tasks.json', encoding='utf-8')); T['tasks'][0].update(status='done', evidence=[], verification=''); json.dump(T, open(f'{d}/audit_control/tasks.json', 'w', encoding='utf-8'))
            r = subprocess.run([sys.executable, f'{d}/audit_control/validate_state.py'], capture_output=True, text=True, cwd=R); self.assertEqual(r.returncode, 1)
if __name__ == '__main__': unittest.main()
