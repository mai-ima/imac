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
rho0, F0, ks, Rr = BC['rho0_mm'], BC['F0_total_N'], BC['k_spring_N_mm'], BC['roller_r_mm']; kt = 2 * ks; EXT = BC['cam_ext_deg']
angles = [T0 + i * (T1 - T0) / 22 for i in range(23)]
def Gj(a):                      # ∫0^a tg da [N·mm]  (a: rad)
    return mh * g * (dz * math.sin(a) + dy * (1 - math.cos(a)))
def rho(a):                     # ピッチ曲線: F0 x + kt/2 x² = G → x
    G = Gj(math.radians(a)); x = G / F0 if kt == 0 else (-F0 + math.sqrt(F0 * F0 + 2 * kt * G)) / kt
    return rho0 + x
# --- カム面: ピッチ曲線(ローラ中心の軌跡, 頭部座標)の法線オフセット(ローラ半径)。範囲は ±cam_ext 余長(ストッパ手前でローラが外れない) ---
def pitch_pt(a): r = rho(a); ar = math.radians(a); return (-r * math.sin(ar), -r * math.cos(ar))      # (zl, yl)
def cam_pts(n=400):
    out = []
    for i in range(n + 1):
        a = T0 - EXT + i * (T1 - T0 + 2 * EXT) / n; h = 1e-3
        p = pitch_pt(a); q1, q0 = pitch_pt(a + h), pitch_pt(a - h); tz, ty = q1[0] - q0[0], q1[1] - q0[1]; L = math.hypot(tz, ty); tz, ty = tz / L, ty / L
        nz, ny = -ty, tz
        if nz * (-p[0]) + ny * (-p[1]) < 0: nz, ny = -nz, -ny        # 原点側(カム内部)を向く法線
        out.append((a, p[0] + Rr * nz, p[1] + Rr * ny))
    return out
CAM = cam_pts()
def rho_sim(a):                 # 実カム面とローラ円の接触を数値で解いたローラ中心距離(独立検算: ピッチ曲線の式を使わない)
    ar = math.radians(a); c, s = math.cos(ar), math.sin(ar); yc = 1e9
    for _, zl, yl in CAM:
        z = zl * c - yl * s; y = zl * s + yl * c
        if abs(z) < Rr: yc = min(yc, y - math.sqrt(Rr * Rr - z * z))
    return -yc if yc < 1e8 else float('nan')
def Ug(a, dd=0.0): r = math.radians(a); return mh * g * (dz * math.sin(r) + (dy + dd) * (1 - math.cos(r)))   # 重力ポテンシャル [N·mm]
def Us(a, fs=1.0): x = rho_sim(a) - rho0; return fs * (F0 * x + kt / 2 * x * x)            # ばねポテンシャル(実接触から) [N·mm]
def resid(a, fs=1.0, dd=0.0, h=0.05):                  # 重力トルク(増加方向)-ばねの復元トルク [N·m] (エネルギー法, 符号規約に依存しない)
    d = lambda f: (f(a + h) - f(a - h)) / (2 * math.radians(h)) / 1000
    return d(lambda x: Ug(x, dd)) - fs * d(lambda x: Us(x))
def dRho(a, h=0.05): return (rho_sim(a + h) - rho_sim(a - h)) / (2 * math.radians(h))      # mm/rad
rr = [resid(a) for a in angles]; rnom = max(abs(x) for x in rr)
worst = max(abs(resid(a, fs, dd)) for a in angles for fs in (1 - FPCT, 1 + FPCT) for dd in (-CGMM, CGMM))
worst_raw = max(abs(resid(a, fs, dd)) for a in angles for fs in (0.9, 1.1) for dd in (-10, 10))
rhos = [rho_sim(a) for a in angles]; xs = [r - rho0 for r in rhos]
Fmax = (F0 + kt * max(xs)) / 2; Fmin = F0 / 2                                   # 1本あたり [N]
dmin, dmax = Fmin / ks, Fmax / ks                                              # ばね たわみ [mm]
phi = max(math.degrees(math.atan(abs(dRho(a)) / rho_sim(a))) for a in angles)       # 圧力角(従動子が軸を通る直線上: tanφ=(dρ/da)/ρ)
cam_r = [math.hypot(zl, yl) for _, zl, yl in CAM]                              # 実カム面の軸からの距離
fr_min, fr_max = FR * (1 - FTOL), FR * (1 + FTOL); fr_aged = fr_min * (1 - H_['friction_aging_loss'])
op_force = (fr_max + worst) / 0.41
print(f"頭部 m={mh:.1f}kg dz={dz:.0f} dy={dy:.0f}mm, チルト{T0:+.0f}〜{T1:+.0f}° / 方式: カム+ローラ従動子+圧縮ダイスプリング2本(x=±{BC['spring_x_mm']:g})")
print(f"ピッチ半径 ρ0={rho0:g}mm → 最大{max(rhos):.1f}mm / カム面半径 {min(cam_r):.1f}〜{max(cam_r):.1f}mm(レバー長{S['neck']['lever_len']:g}) / 圧力角 最大{phi:.1f}°(目標≦30°)")
print('角度: 重力τg / 残差(エネルギー法) [N·m]')
for a, rv in list(zip(angles, rr))[::2]: print(f'{a:+6.1f}°: {MM.S and mh*g*(dz*math.cos(math.radians(a))+dy*math.sin(math.radians(a)))/1000:+7.2f} / {rv:+6.2f}')
print(f'公称最大残差 {rnom:.2f}N·m / 調整後の最悪残差(荷重±{FPCT*100:.0f}%・重心±{CGMM:.0f}mm) {worst:.2f}N·m / 未調整の最悪残差(±10%・±10mm) {worst_raw:.2f}N·m')
print(f'摩擦保持 公称{FR:.1f}N·m(公差±{FTOL*100:.0f}% → {fr_min:.2f}〜{fr_max:.2f}) / 保持条件: 経年後の最小摩擦{fr_aged:.2f} ≧ 最悪残差 / 操作力(上端0.41m)=(最大摩擦+最悪残差)/0.41 = {op_force:.1f}N(目標≦{H_["op_target_N"]:g}N)')
# --- ばね(コイルばね OD×線径, SWOSC-V想定)の成立性: 有効巻数・密着高さ・せん断応力・自由長 ---
G_S = 79e3; Dw = BC['spring_wire_mm']; Dm = BC['spring_od_mm'] - Dw; Nact = G_S * Dw ** 4 / (8 * Dm ** 3 * ks)
solid = (Nact + 2) * Dw; tau = 1.2 * 8 * Fmax * Dm / (math.pi * Dw ** 3)           # Wahl係数≒1.2
free = max(dmax / 0.40, solid + dmax + 1.5); Lmax, Lmin = free - dmin, free - dmax        # 自由長(たわみ率≦40% かつ 最大荷重でも密着+1.5mm以上)
slen = Lmax / Dm
# --- カム接触: ヘルツ線接触(焼入れ鋼 SUS440C HRC58 / SUJ2) と 案内ロッドの横力 ---
Rc = min(cam_r[:23]) if False else sum(math.hypot(zl, yl) for _, zl, yl in CAM) / len(CAM); Rstar = 1 / (1 / Rr + 1 / Rc); Ep = 2.3e5; Lc = BC['cam_t_mm'] - 1.0
Fn = Fmax / math.cos(math.radians(phi)); p0 = math.sqrt(Fn * Ep / (math.pi * Lc * Rstar))
Flat = Fmax * math.tan(math.radians(phi)); Lg = 42.0; dg = BC['guide_rod_d_mm']; sig_rod = (Flat / 2 * Lg) / (math.pi * dg ** 3 / 32)     # 2本で分担, 片持ち長42mm
print(f"ばね: OD{BC['spring_od_mm']:g}×線径{Dw:g} 有効巻数{Nact:.1f} 密着高さ{solid:.1f}mm / 自由長≧{free:.1f}mm・取付長{Lmin:.1f}〜{Lmax:.1f}mm / せん断応力{tau:.0f}MPa(目安≦900) / 取付長÷平均径={slen:.1f}(案内ロッドで拘束)")
print(f"ヘルツ接触応力 {p0:.0f}MPa(目安≦1600: 焼入れ鋼HRC58)、カム横力{Flat:.0f}N/本 → 案内ロッド2本Ø{dg:g}の曲げ{sig_rod:.0f}MPa(許容667: SUS630 H1025/SF1.5)")
# --- 収まり(R10M-001): ローラ中心→キャリア下面→ばね座上面の間にばねが入るか(0°とカム最大位置) ---
space0 = BC['base_seat_depth_mm'] - BC['seat_t_mm'] - (rho0 + Rr + BC['carrier_h_mm']); space1 = space0 - max(xs)
print(f'収まり: ばね座上面〜キャリア下面 {space0:.1f}mm(0°)/{space1:.1f}mm(最大圧縮) ≧ ばね取付長 {Lmax:.1f}/{Lmin:.1f}mm')
fails = []
if space0 < Lmax - 0.01 or space1 < Lmin - 0.01: fails.append(f'ばねが収まらない(空間{space0:.1f}/{space1:.1f} < 取付長{Lmax:.1f}/{Lmin:.1f})')
if abs(space0 - Lmax) > 0.05: fails.append(f'ばね座の深さ(spec base_seat_depth_mm)が取付長と不一致: 0°の空間{space0:.2f}mm ≠ 取付長{Lmax:.2f}mm → base_seat_depth_mm を {Lmax + BC["seat_t_mm"] + rho0 + Rr + BC["carrier_h_mm"]:.2f} にする(MDD-001: 隙間があると予圧が不足する)')
if tau > 900: fails.append(f'ばねせん断応力{tau:.0f}>900MPa')
if free > 62: fails.append(f'ばね自由長{free:.0f}>62mm(収まらない)')
if p0 > 1600: fails.append(f'ヘルツ応力{p0:.0f}>1600MPa')
if sig_rod > 667: fails.append(f'案内ロッド曲げ{sig_rod:.0f}>667MPa')
if abs(rho_sim(T0) - rho(T0)) > 0.3 or abs(rho_sim(T1) - rho(T1)) > 0.3: fails.append('実カム接触とピッチ曲線のずれ>0.3mm(カム面の作り方が不正)')
def old_sign_check():      # 旧方式(圧縮ばね+下アンカー): ピン間距離が|a|で増加=ばねが緩む=転倒方向 の退行検査
    e, s = 25.0, 76.0; l = lambda a: math.hypot(e * math.sin(math.radians(a)), s - e * math.cos(math.radians(a))); return l(40) > l(0)
if not old_sign_check(): fails.append('退行検査: 旧方式の幾何前提が変わった')
if rnom > 0.3: fails.append(f'公称残差{rnom:.2f}N·m(解析解のはずが大きい)')
if dmax / free > 0.4001: fails.append('たわみ率>40%')
if phi > 30: fails.append(f'圧力角{phi:.1f}°>30°')
if max(cam_r) > S['neck']['lever_len']: fails.append('カム面がレバー長を超える')
if worst > fr_aged: fails.append(f'最悪残差{worst:.2f} > 経年後の最小摩擦保持{fr_aged:.2f}')
if op_force > H_['op_target_N']: fails.append(f"操作力{op_force:.1f}N > {H_['op_target_N']:g}N")
print('総合:', 'OK(ばね型番・実特性・重心・カム加工精度はUNVERIFIED)' if not fails else 'NG ' + ' / '.join(fails))
if '--write' in sys.argv:
    prof = [[round(a, 2), round(rho(a), 3)] for a in [T0 - EXT + i * (T1 - T0 + 2 * EXT) / 63 for i in range(64)]]
    surf = [[round(a, 2), round(zl, 3), round(yl, 3)] for a, zl, yl in CAM[::6]]
    json.dump(dict(model='cam_roller', rho0=rho0, roller_r=Rr, spring_x=BC['spring_x_mm'], k_spring=ks, F0_total=F0, F0_longest_total=F0, p=(F0 + kt * max(xs)) / F0 - 1, s=BC['base_seat_depth_mm'], e=round(max(cam_r), 2), p_offset=0,
                   stroke=round(max(xs), 3), lmin=round(Lmin, 2), lmax=round(Lmax, 2), free_length_min=round(free, 1), F_spring_max=round(Fmax, 1), pressure_angle_deg=round(phi, 1), hertz_MPa=round(p0), spring_shear_MPa=round(tau), spring_solid_mm=round(solid, 1),
                   resid_nominal=round(rnom, 3), resid_worst=round(worst, 3), sign=1, cam_profile_pitch_radius=prof, cam_surface_head_frame=surf), open(f'{R}/model/balance.json', 'w'), ensure_ascii=False, indent=1)
sys.exit(1 if fails else 2)      # ばね型番/実特性/重心/カム加工が未確定=UNVERIFIED
