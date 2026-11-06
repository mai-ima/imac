#!/usr/bin/env python3
"""ネックのストッパ幾何を導出して model/spec.json の neck に書き戻す(--write)。入力: lever_len/lever_w/lever_t/pad_thick と チルト端、出力: パッド・タイプレート・前カバー・基台の z 範囲(ZC基準の相対値)。
レバー側縁の角が、-15°端と+40°端で、パッドにそれぞれ comp だけ食い込む位置にパッド近面を置く。パッドは厚み pad_thick(ウレタン緩衝, 衝撃時は厚みの50%まで圧縮可)。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = json.load(open(f'{R}/model/spec.json')); N = S['neck']; H = S['hinge']
L, w, T = N['lever_len'], N['lever_w'], N['pad_thick']; comp_dn, comp_up = 0.5, 1.0
a0, a1 = math.radians(abs(H['tilt_min_deg'])), math.radians(H['tilt_max_deg'])
c_dn = L * math.sin(a0) + (w / 2) * math.cos(a0); c_up = L * math.sin(a1) + (w / 2) * math.cos(a1)        # レバー側縁の角のz(軸から前後方向の距離)
n_dn, n_up = c_dn - comp_dn, c_up - comp_up                                                                  # パッド近面
N['pad_dn_z'] = [-(n_dn + T), -n_dn]; N['tie_z'] = [-(n_dn + T + 6.0), -(n_dn + T)]
N['pad_up_z'] = [n_up, n_up + T]; N['front_cover_z'] = [n_up + T, n_up + T + 6.0]
N['base_z'] = [N['tie_z'][0] - 1.0, N['front_cover_z'][1]]; N['side_z'] = [N['tie_z'][0], N['front_cover_z'][1]]
N['pad_comp_mm'] = {'dn': comp_dn, 'up': comp_up}
print(f"レバー角 z: -15°側 {c_dn:.1f} / +40°側 {c_up:.1f} → パッド -[{n_dn:.1f}..{n_dn+T:.1f}] / +[{n_up:.1f}..{n_up+T:.1f}]、前カバー外面 z={N['front_cover_z'][1]:.1f}(軸基準) = 絶対 z={N['front_cover_z'][1]-H['axis_z_from_glass']:.1f}(前面ガラス=0。負=ガラスより後ろ)")
ok = N['front_cover_z'][1] - H['axis_z_from_glass'] <= -1.0
print('前面ガラス面より後ろに収まる:', 'OK' if ok else 'NG(前方へはみ出す)')
if '--write' in sys.argv: json.dump(S, open(f'{R}/model/spec.json', 'w'), ensure_ascii=False, indent=1)
sys.exit(0 if ok else 1)
