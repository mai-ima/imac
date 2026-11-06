#!/usr/bin/env python3
"""チルト・バランサ(圧縮ダイスプリング2本+ヒンジ尾部レバー)の寸法探索とゲート。
頭部重力トルク τg(a)=m·g·(dz·cos a+dy·sin a) を、スタンド内のばねが尾部レバー経由で相殺する。
幾何: 尾部レバー先端B(ヘッド側, 軸から下へ e, ヘッドと共に回転)とスタンド側アンカーA(軸から下へ s)の間にばね。
ばね特性: 力 F = F0·(1+p·u)。F0=最長側(圧縮最小)の荷重(2本合計)、u=圧縮率(0最長〜1最短)、p=荷重変化率(ばね定数 k=p·F0/ストローク)。
  全たわみ=ストローク·(1+1/p)、自由長=最長取付長+ストローク/p、たわみ率=全たわみ/自由長(JIS金型ばね軽荷重は≦40%を目安に採用)。
ゲート(満たさなければ終了コード1): たわみ率≦40% / 最悪残差(荷重±10%・重心±10mm)≦摩擦保持トルク(spec) / 摩擦保持から計算した操作力≦20N / ばね軸の最大揺れ角(情報)。
既定では model/balance.json を書き換えない(--write のときだけ上書き)。実行: python3 tools/balance_calc.py [--write]"""
import math, os, sys, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; g = 9.81
mh, cz, cy, _ = MM.head_cg(); hz, hy = S['hinge']['axis_z_from_glass'], S['hinge']['axis_y']
dz, dy = cz - hz, cy - hy
T0, T1 = S['hinge']['tilt_min_deg'], S['hinge']['tilt_max_deg']; H_ = S['hinge']; FR = H_['friction_hold_Nm']; FTOL = H_['friction_tol_pct'] / 100; FPCT = H_['balance_force_tol_pct'] / 100; CGMM = H_['balance_cg_tol_mm']
angles = [T0 + i * (T1 - T0) / 22 for i in range(23)]
def tg(a, ddy=0.0): a = math.radians(a); return mh * g * (dz * math.cos(a) + (dy + ddy) * math.sin(a)) / 1000
def geom(a, s, e):
    ar = math.radians(a); Bz, By = -e * math.sin(ar), -e * math.cos(ar); vz, vy = Bz, By + s; return Bz, By, vz, vy, math.hypot(vz, vy)
def spring_tau(a, s, e, F0, p, lmax, stroke, fscale=1.0):
    Bz, By, vz, vy, l = geom(a, s, e); u = (lmax - l) / stroke; F = fscale * F0 * (1 + p * u)
    return (Bz * (F * vy / l) - By * (F * vz / l)) / 1000
def resid(s, e, F0, p, sign, lmax, stroke, fscale=1.0, ddy=0.0):
    return [tg(a, ddy) + sign * spring_tau(a, s, e, F0, p, lmax, stroke, fscale) for a in angles]
best = None
for s in range(50, 68, 2):
    for e in range(20, 56, 5):
        if e > s - 15: continue
        L = [geom(a, s, e)[4] for a in angles]; lmin, lmax = min(L), max(L); stroke = lmax - lmin
        if stroke < 8 or stroke > 30: continue
        for p in (0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5):
            free = lmax + stroke / p; ratio = stroke * (1 + 1 / p) / free
            if ratio > 0.40: continue
            for F0 in range(200, 2001, 10):
                for sign in (1, -1):
                    r = resid(s, e, F0, p, sign, lmax, stroke); rr = max(abs(x) for x in r)
                    ww = max(abs(x) for fs in (1 - FPCT, 1 + FPCT) for dd in (-CGMM, CGMM) for x in resid(s, e, F0, p, sign, lmax, stroke, fs, dd))
                    key = ww + 0.5 * rr      # 保持(最悪残差)と操作(公称残差)の両方を小さくする
                    if best is None or key < best[0]: best = (key, s, e, F0, p, sign, stroke, lmin, lmax, ratio, free)
_, s, e, F0, p, sign, stroke, lmin, lmax, ratio, free = best
rr = max(abs(x) for x in resid(s, e, F0, p, sign, lmax, stroke))
worst = max(abs(x) for fs in (1 - FPCT, 1 + FPCT) for dd in (-CGMM, CGMM) for x in resid(s, e, F0, p, sign, lmax, stroke, fs, dd))
worst_raw = max(abs(x) for fs in (0.9, 1.1) for dd in (-10, 10) for x in resid(s, e, F0, p, sign, lmax, stroke, fs, dd))
tilt_ax = [math.degrees(math.atan2(geom(a, s, e)[2], geom(a, s, e)[3])) for a in angles]; swing = (min(tilt_ax), max(tilt_ax))
k_rate = p * F0 / stroke / 2; fmax = F0 * (1 + p) / 2
print(f'頭部 m={mh:.1f}kg dz={dz:.0f} dy={dy:.0f}mm, チルト{T0:+.0f}〜{T1:+.0f}°')
print(f'採用(2本合計): s={s}mm e={e}mm / 最長側荷重 F0={F0}N(1本{F0/2:.0f}N, 最大 {fmax:.0f}N/本) / 荷重変化率 p={p} → ばね定数 {k_rate:.1f}N/mm/本 / ストローク{stroke:.1f}mm(取付長 {lmin:.0f}〜{lmax:.0f}mm)')
print(f'ばね自由長 ≧{free:.0f}mm、全たわみ{stroke*(1+1/p):.1f}mm、たわみ率 {ratio*100:.0f}%(許容≦40%)、ばね軸の揺れ角 {swing[0]:+.0f}〜{swing[1]:+.0f}°(両端揺動ピン必須)')
print('角度: 重力τg / 公称残差 [N·m]')
for a, rv in list(zip(angles, resid(s, e, F0, p, sign, lmax, stroke)))[::2]: print(f'{a:+6.1f}°: {tg(a):+7.2f} / {rv:+6.2f}')
fr_min, fr_max = FR * (1 - FTOL), FR * (1 + FTOL)
op_force = (fr_max + rr) / 0.41           # 動かす力 = 摩擦(最大)+公称残差(ばね/重力の不釣合い)。上端0.41mで評価
print(f'公称最大残差 {rr:.2f}N·m / 調整後の最悪残差(荷重±{FPCT*100:.0f}%・重心±{CGMM:.0f}mm) {worst:.2f}N·m / 未調整の最悪残差(±10%・±10mm) {worst_raw:.2f}N·m')
print(f'摩擦保持 公称{FR:.1f}N·m(公差±{FTOL*100:.0f}% → {fr_min:.2f}〜{fr_max:.2f}) / 保持条件: 最小摩擦 ≧ 最悪残差 / 操作力(上端0.41m)=(最大摩擦+公称残差)/0.41 = {op_force:.1f}N(目標≦20N)')
fails = []
if ratio > 0.40: fails.append('ばねたわみ率>40%')
if worst > fr_min: fails.append(f'最悪残差{worst:.2f} > 最小摩擦保持{fr_min:.2f}')
if op_force > 20: fails.append(f'操作力{op_force:.1f}N > 20N')
print('総合:', 'OK(ばね型番・実特性・重心はUNVERIFIED)' if not fails else 'NG ' + ' / '.join(fails))
if '--write' in sys.argv:
    json.dump(dict(s=s, p_offset=0, e=e, F0_longest_total=F0, p=p, stroke=stroke, lmin=lmin, lmax=lmax, free_length_min=free, resid_nominal=rr, resid_worst=worst, sign=sign), open(f'{R}/model/balance.json', 'w'), ensure_ascii=False, indent=1)
sys.exit(1 if fails else 0)
