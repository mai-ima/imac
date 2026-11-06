#!/usr/bin/env python3
"""チルト・バランサ(カム+ローラ従動子+圧縮ダイスプリング2本)の設計とゲート。 R9T-001対応で全面改訂(2026-11-06)。
旧方式(尾部レバー先端のピンを、下のアンカーとの間の圧縮ばねで押す)は、ピン間距離が|a|で伸びるほどばねが緩む=エネルギーが減るため
復元でなく**転倒方向のトルク**になる(圧縮ばねは A と B が軸の同じ側だと不安定)。エネルギー法で再計算して確認済み → 廃止。
新方式: 頭部のレバー先端をカム面とし、軸の真下の直線上を動くローラ(従動子)を圧縮ばねで押し上げる。
  ローラ中心のピッチ半径 ρ(a)(軸からの距離)を、重力ポテンシャルの増分を相殺するよう解く:  F0·(ρ-ρ0)+k_tot/2·(ρ-ρ0)² = G(a)
  ここで G(a)=∫tg da。トルクは エネルギー法 τ=-dU/da で独立に検算する(符号規約に依存しない)。
実行: python3 tools/balance_calc.py [--write](--write のときだけ model/balance.json を更新)。"""
import math, os, sys, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; g = 9.81; H_ = S['hinge']; BC = H_['balance_cam']
mh, cz, cy, _ = MM.head_cg(); hz, hy = H_['axis_z_from_glass'], H_['axis_y']; dz, dy = cz - hz, cy - hy
T0, T1 = H_['tilt_min_deg'], H_['tilt_max_deg']; FR = H_['friction_hold_Nm']; FTOL = H_['friction_tol_pct'] / 100; FPCT = H_['balance_force_tol_pct'] / 100; CGMM = H_['balance_cg_tol_mm']
rho0, F0, ks, Rr = BC['rho0_mm'], BC['F0_total_N'], BC['k_spring_N_mm'], BC['roller_r_mm']; kt = 2 * ks
angles = [T0 + i * (T1 - T0) / 22 for i in range(23)]
def Gj(a):                      # ∫0^a tg da [N·mm]  (a: rad)。tg=m g (dz cos a+dy sin a)/1000 [N·m]
    return mh * g * (dz * math.sin(a) + dy * (1 - math.cos(a)))
def rho(a):                     # F0 x + kt/2 x² = G → x
    G = Gj(math.radians(a)); x = G / F0 if kt == 0 else (-F0 + math.sqrt(F0 * F0 + 2 * kt * G)) / kt
    return rho0 + x
def Us(a, fs=1.0): x = rho(a) - rho0; return fs * (F0 * x + kt / 2 * x * x)         # ばねポテンシャル [N·mm]
def Ug(a, dd=0.0): r = math.radians(a); return mh * g * (dz * math.sin(r) + (dy + dd) * (1 - math.cos(r)))   # 重力ポテンシャル [N·mm]
# 符号: Ug は a の増加で増える(頭部を持ち上げる)。残差=重力トルク(増加方向)-ばねの復元トルク。
def resid(a, fs=1.0, dd=0.0, h=1e-3):
    d = lambda f: (f(a + h) - f(a - h)) / (2 * math.radians(h)) / 1000
    return d(lambda x: Ug(x, dd)) - fs * d(lambda x: Us(x))       # = 重力トルク(増加方向)-ばねの復元トルク [N·m]
def dRho(a, h=1e-3): return (rho(a + h) - rho(a - h)) / (2 * math.radians(h))      # mm/rad
rr = [resid(a) for a in angles]; rnom = max(abs(x) for x in rr)
worst = max(abs(resid(a, fs, dd)) for a in angles for fs in (1 - FPCT, 1 + FPCT) for dd in (-CGMM, CGMM))
worst_raw = max(abs(resid(a, fs, dd)) for a in angles for fs in (0.9, 1.1) for dd in (-10, 10))
rhos = [rho(a) for a in angles]; xs = [r - rho0 for r in rhos]
Fmax = (F0 + kt * max(xs)) / 2; Fmin = F0 / 2                                   # 1本あたり [N]
dmin, dmax = Fmin / ks, Fmax / ks                                              # ばね たわみ [mm]
free = dmax / 0.40                                                              # たわみ率≦40% に必要な自由長
Lmax, Lmin = free - dmin, free - dmax                                           # 取付長 [mm]
phi = max(math.degrees(math.atan(abs(dRho(a)) / rho(a))) for a in angles)       # 圧力角(従動子が軸を通る直線上: tanφ=(dρ/da)/ρ)
cam_r = [r - Rr for r in rhos]                                                  # カム面の軸からの距離(ローラ半径分内側)
fr_min, fr_max = FR * (1 - FTOL), FR * (1 + FTOL); fr_aged = fr_min * (1 - H_['friction_aging_loss'])
op_force = (fr_max + worst) / 0.41
D_MEAN = 13.0; slen = Lmax / D_MEAN
print(f"頭部 m={mh:.1f}kg dz={dz:.0f} dy={dy:.0f}mm, チルト{T0:+.0f}〜{T1:+.0f}° / 方式: カム+ローラ従動子+圧縮ダイスプリング2本(x=±{BC['spring_x_mm']:g})")
print(f"ピッチ半径 ρ0={rho0:g}mm → 最大{max(rhos):.1f}mm / カム面半径 {min(cam_r):.1f}〜{max(cam_r):.1f}mm(レバー長{S['neck']['lever_len']:g}) / 圧力角 最大{phi:.1f}°(目標≦30°)")
print(f"ばね(1本): 初期荷重{F0/2:.0f}N(0°)・最大{Fmax:.0f}N / ばね定数{ks:g}N/mm / たわみ{dmin:.1f}〜{dmax:.1f}mm / 自由長≧{free:.0f}mm(たわみ率40%) / 取付長{Lmin:.1f}〜{Lmax:.1f}mm / 取付長÷平均径={slen:.1f}(案内ロッドで拘束)")
print('角度: 重力τg / 残差(エネルギー法) [N·m]')
for a, rv in list(zip(angles, rr))[::2]: print(f'{a:+6.1f}°: {MM.S and mh*g*(dz*math.cos(math.radians(a))+dy*math.sin(math.radians(a)))/1000:+7.2f} / {rv:+6.2f}')
print(f'公称最大残差 {rnom:.2f}N·m / 調整後の最悪残差(荷重±{FPCT*100:.0f}%・重心±{CGMM:.0f}mm) {worst:.2f}N·m / 未調整の最悪残差(±10%・±10mm) {worst_raw:.2f}N·m')
print(f'摩擦保持 公称{FR:.1f}N·m(公差±{FTOL*100:.0f}% → {fr_min:.2f}〜{fr_max:.2f}) / 保持条件: 経年後の最小摩擦{fr_aged:.2f} ≧ 最悪残差 / 操作力(上端0.41m)=(最大摩擦+最悪残差)/0.41 = {op_force:.1f}N(目標≦{H_["op_target_N"]:g}N)')
# 独立検算: 旧方式(圧縮ばね+下アンカー, エネルギー法)が転倒方向であることの再現(退行防止)
def old_sign_check():
    e, s, FF = 25.0, 76.0, 365.0; l = lambda a: math.hypot(e * math.sin(math.radians(a)), s - e * math.cos(math.radians(a)))
    return (l(40) > l(0))      # ピン間距離が増える=圧縮ばねは緩む=エネルギー減少=駆動側
fails = []
if not old_sign_check(): fails.append('退行検査: 旧方式の幾何前提が変わった')
if rnom > 0.3: fails.append(f'公称残差{rnom:.2f}N·m(解析解のはずが大きい)')
if free and dmax / free > 0.4001: fails.append('たわみ率>40%')
if phi > 30: fails.append(f'圧力角{phi:.1f}°>30°')
if max(cam_r) > S['neck']['lever_len']: fails.append('カム面がレバー長を超える')
if worst > fr_aged: fails.append(f'最悪残差{worst:.2f} > 経年後の最小摩擦保持{fr_aged:.2f}')
if op_force > H_['op_target_N']: fails.append(f"操作力{op_force:.1f}N > {H_['op_target_N']:g}N")
if slen >= 4.0 and not BC.get('guide_rod'): fails.append(f'ばね細長比{slen:.1f}≧4(案内が必要)')
print('総合:', 'OK(ばね型番・実特性・重心・カム加工精度はUNVERIFIED)' if not fails else 'NG ' + ' / '.join(fails))
if '--write' in sys.argv:
    prof = [[round(a, 2), round(rho(a), 3)] for a in [T0 + i * (T1 - T0) / 55 for i in range(56)]]
    json.dump(dict(model='cam_roller', rho0=rho0, roller_r=Rr, spring_x=BC['spring_x_mm'], k_spring=ks, F0_total=F0, F0_longest_total=F0, p=(F0 + kt * max(xs)) / F0 - 1, s=BC['base_seat_depth_mm'], e=round(max(cam_r), 2), p_offset=0,
                   stroke=round(max(xs), 3), lmin=round(Lmin, 2), lmax=round(Lmax, 2), free_length_min=round(free, 1), F_spring_max=round(Fmax, 1), pressure_angle_deg=round(phi, 1), resid_nominal=round(rnom, 3), resid_worst=round(worst, 3), sign=1, cam_profile_pitch_radius=prof),
              open(f'{R}/model/balance.json', 'w'), ensure_ascii=False, indent=1)
sys.exit(1 if fails else 2)      # ばね型番/実特性/重心が未確定=UNVERIFIED
