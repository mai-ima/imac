#!/usr/bin/env python3
"""首振り軸受の要求仕様(静荷重+操作荷重+衝撃)と操作力・ストッパ荷重の概算。軸受の実定格(spec.swivel.bearing_moment_rating_Nm)が未設定なら UNVERIFIED。
出力: 要求モーメント定格/軸力、操作力、ストッパ衝撃。"""
import math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; sw = S['swivel']; g = 9.81
hm, cz, cy, _ = MM.head_cg(); hz, hy = S['hinge']['axis_z_from_glass'], S['hinge']['axis_y']
T1 = S['hinge']['tilt_max_deg']; drop = S['stand']['drop']
dy = cy - hy
r_cg = abs(dy * math.sin(math.radians(T1)))/1000.0          # 頭部重心の水平オフセット(最大チルト) [m]
h_cg = (cy + drop - sw['stack_h']) / 1000.0                   # 軸受面から頭部重心までの高さ [m]
h_top = (MM.H + drop - sw['stack_h']) / 1000.0                # 軸受面から画面上端まで [m]
Fa = hm * g                                                  # 軸力(頭部のみ) [N]
M_static = hm * g * r_cg                                     # 静荷重モーメント [N·m]
push = 50.0                                                  # 画面上端を押す操作荷重 [N](ユーザーが強く押す想定)
M_push = push * h_top
M_shock = 2.0 * M_static + M_push * 0.0   # 運搬・衝撃の簡易(2G)
M_req = max(M_static + M_push, M_shock) * 1.5                            # 安全率1.5
print(f'頭部 {hm:.1f}kg / 最大チルト{T1:+.0f}°での重心水平オフセット {r_cg*1000:.0f}mm / 軸受面から画面上端 {h_top*1000:.0f}mm')
print(f'軸力 {Fa:.0f}N / 静モーメント {M_static:.1f}N·m / 操作押し荷重{push:.0f}N→{M_push:.1f}N·m / 衝撃(2G) {M_shock:.1f}N·m')
print(f'要求: 軸受の許容モーメント ≧ {M_req:.0f}N·m(安全率1.5, 静+操作), 許容軸力 ≧ {Fa*3:.0f}N(3倍), ストッパ衝撃 etc.')
tau = sw['holding_torque_Nm']; print(f'首振り操作力(画面端 0.31m): {tau/0.31:.1f}N(目標≦20N) → [{"OK" if tau/0.31<=20 else "NG"}]')
w = 0.25   # 首振り速度 rad/s(ゆっくり押す) → 運動エネルギーはストッパで受ける
I = hm * (0.31 ** 2 + 0.1 ** 2) / 3.0   # 板状の慣性モーメント概算 [kg·m²]
E = 0.5 * I * w ** 2; print(f'ストッパ衝突エネルギー(0.25rad/s): {E*1000:.1f}mJ(ゴムポストで十分小さい想定。実測U52)')
rt = sw.get('bearing_moment_rating_Nm')
if rt is None: print('軸受定格: 未設定 → UNVERIFIED(型番選定U50: 許容モーメント≧要求を満たす市販クロスローラ/スリューリングを選ぶこと)'); sys.exit(2)
ok = rt >= M_req; print(f'軸受定格 {rt}N·m ≥ 要求 {M_req:.0f}N·m: {"OK" if ok else "NG"}'); sys.exit(0 if ok else 1)
