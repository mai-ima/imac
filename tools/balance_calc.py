#!/usr/bin/env python3
"""チルト・バランサ設計(ガススプリング+ヒンジ尾部レバー)の寸法探索。
頭部重力トルク τg(a)=m·g·(dz·cos a+dy·sin a) を、スタンド内のガススプリング2本が尾部レバー経由で相殺する。
ばね力は圧縮で F=F0·(1+k·(ストローク使用率)) とする(進行率k: ダイスプリングの荷重変化率を保守的に35%と置く)。
結果: 最小残差トルクを与える (s,e,F0) と、残差を保持する摩擦ヒンジ必要トルク。出力は標準出力(docs/tilt-swivel-design.md が引用)。"""
import math, os, sys, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; g = 9.81
mh, cz, cy, _ = MM.head_cg(); hz, hy = S['hinge']['axis_z_from_glass'], S['hinge']['axis_y']
dz, dy = cz - hz, cy - hy
T0, T1 = S['hinge']['tilt_min_deg'], S['hinge']['tilt_max_deg']
angles = [T0 + i * (T1 - T0) / 11 for i in range(12)]
def tg(a): a = math.radians(a); return mh * g * (dz * math.cos(a) + dy * math.sin(a)) / 1000       # N·m(+=後ろへ倒れる向き)
def spring_torque(a, s, e, F0, stroke_max, l_ref, pre=0.0):
    """ステム側アンカーA=(スタンド, 軸から下へ s mm)、ヘッド側アンカーB=(尾部レバー先端, 軸から下へ e mm, ヘッドと共に回転)。
    a>0(上端が後ろへ)でBは前(−z)へ動く向き。トルク=F·(AB方向に対するBの腕の長さ)。圧縮ガススプリングはAとBを引き離す向きに押す。"""
    ar = math.radians(a)
    Bz, By = -e * math.sin(ar) * -1, -e * math.cos(ar)       # Bの軸基準座標(下向きeを a だけ回転; 上端後ろ=負のx回転 → Bは前へ(-z))
    Bz = -e * math.sin(ar)
    Az, Ay = 0.0, -s
    dzv, dyv = Bz - Az, By - Ay; l = math.hypot(dzv, dyv)
    comp = max(0.0, l_ref - l) if False else (l - (s - e))   # 初期長 s-e からの伸び
    F = F0 * (1 + 0.35 * max(0.0, (stroke_max - (l - (s - e) if l >= s - e else 0)) / max(stroke_max, 1e-6)) * 0)  # 簡易: 力一定+進行率を下で付与
    # 圧縮量は l が短いほど大。l が最短(a=T0付近)で最大力。ストローク使用率 u=(l_max-l)/(l_max-l_min)
    return Bz, By, dzv, dyv, l
best = None
# ステム側アンカーAは軸から下へ s、後方(+)へ p だけずらせる(ガススプリングの取付全長を確保するため)。
for s in range(40, 66, 5):
  for p in (0,):
    for e in range(20, 56, 5):
        if e > s - 15: continue
        pts = []
        for a in angles:
            ar = math.radians(a); Bz, By = -e * math.sin(ar), -e * math.cos(ar)
            vz, vy = Bz - p, By - (-s); pts.append((a, Bz, By, vz, vy, math.hypot(vz, vy)))
        lmin, lmax = min(q[5] for q in pts), max(q[5] for q in pts); stroke = lmax - lmin
        if stroke < 8 or stroke > 30: continue   # ダイスプリング(JIS金型用コイルばね+ガイドロッド)は取付全長が短くても可(ガススプリングと違い最小全長制約が緩い)
        for F0 in range(200, 2001, 20):
            res = []
            for (a, Bz, By, vz, vy, l) in pts:
                F = F0 * (1 + 0.35 * (lmax - l) / stroke)                       # 圧縮が深いほど力が増える(進行率35%)
                fz, fy = F * vz / l, F * vy / l
                res.append((Bz * fy - By * fz) / 1000)
            for sign in (1, -1):
                r = [tg(a) + sign * t for a, t in zip(angles, res)]; rr = max(abs(x) for x in r)
                if best is None or rr < best[0]: best = (rr, s, e, F0, sign, stroke, lmin, lmax, r, p)
rr, s, e, F0, sign, stroke, lmin, lmax, r, pA = best
print(f'頭部 m={mh:.1f}kg dz={dz:.0f} dy={dy:.0f}mm, チルト{T0:+.0f}〜{T1:+.0f}°')
print(f'最適(2本合計): ステム側アンカー s={s}mm(後方オフセット p={pA}mm) / 尾部レバー e={e}mm / 合計初期力 F0={F0}N (1本{F0/2:.0f}N) / ストローク使用 {stroke:.1f}mm (長さ {lmin:.0f}〜{lmax:.0f}mm) / 向き符号 {sign}')
print('角度: 重力τg / 残差(保持が必要) [N·m]')
for a, rv in zip(angles, r): print(f'{a:+6.1f}°: {tg(a):+7.2f} / {rv:+6.2f}')
print(f'最大残差 {rr:.2f} N·m → 摩擦ヒンジ保持トルク ≥ {rr*1.5:.1f} N·m(安全率1.5, 温度±10K での力変化±3.5%分を別途加味)')
json.dump(dict(s=s, p=pA, e=e, F0_total=F0, stroke=stroke, lmin=lmin, lmax=lmax, resid_max=rr, sign=sign), open(f'{R}/model/balance.json', 'w'), ensure_ascii=False, indent=1)
