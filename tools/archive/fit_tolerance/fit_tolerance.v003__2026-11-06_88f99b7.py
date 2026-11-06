#!/usr/bin/env python3
"""機構の「ゆるゆる/硬すぎ」ゲート: 各インタフェースの公差(IT級・摩擦係数・ばね荷重・圧縮量)を最悪ケースで振り、遊び/操作力/保持力が許容窓に入るかを判定する。
窓の外側が『緩すぎ(ガタ・滑り・保持不足)』または『硬すぎ(閉まらない・動かない・操作力超過)』。NGは終了コード1。数値は model/spec.json(dome_seal, fits, hinge, swivel, neck)と balance.json。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = json.load(open(f'{R}/model/spec.json')); BAL = json.load(open(f'{R}/model/balance.json'))
F, DS, H, SW = S['fits'], S['dome_seal'], S['hinge'], S['swivel']; bad = 0; warn = 0; rows = []
def row(name, lo, hi, wlo, whi, unit, note='', margin_warn=0.05):
    """lo/hi=最悪ケースの範囲、wlo/whi=許容窓。窓の幅に対し端からの余裕が margin_warn 未満なら WARN。"""
    global bad, warn
    ok = (wlo is None or lo >= wlo) and (whi is None or hi <= whi); width = (whi - wlo) if (wlo is not None and whi is not None) else None
    tight = ok and ((width and (min(lo - wlo, whi - hi) < margin_warn * width)) or (wlo is None and whi is not None and unit == 'N' and hi > 0.9 * whi) or (wlo is not None and whi is None and lo < wlo * 1.05) or (unit in ('N·m',) and wlo is not None and whi is not None and lo < wlo + 0.05 * (whi - wlo)))
    if not ok: bad += 1
    if tight: warn += 1
    tag = 'NG' if not ok else ('WARN(余裕小)' if tight else 'OK')
    rows.append((name, lo, hi, wlo, whi, unit, tag, note)); print(f"[{tag:<12}] {name}: {lo:.3g}〜{hi:.3g}{unit} / 窓 {('-' if wlo is None else format(wlo,'.3g'))}〜{('-' if whi is None else format(whi,'.3g'))}{unit} {note}")
# 1) ドーム閉合: ガスケット反力(圧縮量±)とラッチ容量
L = DS['perimeter_mm']; Fn = DS['line_force_N_per_mm'] * L; cmin = DS['comp_nom'] - DS['comp_tol_stack'] - DS['comp_flat'] - DS['comp_set']; cmax = DS['comp_nom'] + DS['comp_tol_stack'] + DS['comp_flat']      # 最小=積層+平面度+永久歪み(寿命末期), 最大=積層+平面度
Fg = lambda c: Fn * (c / DS['comp_nom']) ** 1.5
row(f'ガスケット反力(圧縮{cmin*100:.1f}〜{cmax*100:.1f}%)', Fg(cmin), Fg(cmax), DS['min_line_N_per_mm'] * L, None, 'N', '下限=EMI接触に必要な最低線荷重(0.04N/mm: 根拠はメーカー確認 U61)、最小圧縮は永久歪み・平面度込み', 0)
cap = DS['latch_n'] * DS['latch_hold_N'] + DS['side_hooks'] * DS['side_hook_hold_N']; row('ラッチ+側辺フック容量 ≧ 最大反力×安全率', Fg(cmax) * DS['safety'], Fg(cmax) * DS['safety'], None, cap, 'N', f"(下辺ラッチ{DS['latch_n']}×{DS['latch_hold_N']}N+側辺フック{DS['side_hooks']}×{DS['side_hook_hold_N']}N={cap}N。硬すぎ=閉まらない/緩すぎ=保持不足)")
Tl = lambda Fl: Fl / DS['latch_n'] * DS['latch_turn_lead_mm'] / 1000 / (math.pi / 2) / DS['latch_eff']      # 回すのは下辺ラッチ6点のみ(側辺フックは掛けるだけ)
row('ラッチ回転トルク(T10, 最大反力時)', Tl(Fg(cmin)), Tl(Fg(cmax)), 0.05, 0.5, 'N·m', '手で回せる窓 0.05〜0.5N·m')
# 2) トレイ吊りピン(肩Ø5 h8)とキーホール溝W5.1(+0.05/0): 隙間
c_lo = F['keyhole_slot_w'] + F['keyhole_slot_tol'][0] - (F['pin_shoulder_d'] + F['pin_tol'][1]); c_hi = F['keyhole_slot_w'] + F['keyhole_slot_tol'][1] - (F['pin_shoulder_d'] + F['pin_tol'][0])
row('キーホール溝-吊りピン肩の隙間(4点の位置公差±%.1f積み上げ後)' % F['keyhole_pos_stack'], c_lo - F['keyhole_pos_stack'], c_hi, 0.05, F['keyhole_rattle_max'], 'mm', '最小=溝-ピンの最小隙間-位置公差積み上げ(トレイ側±0.1+背板側±0.1)。トレイの位置決めは別の位置決めピンが担うため、吊りの隙間は0.6まで許容')
# 3) 位置決めピンØ4(g6) と ピン穴Ø4 H7
d_lo = F['dowel_d'] + F['dowel_hole_tol'][0] - (F['dowel_d'] + F['dowel_shaft_tol'][1]); d_hi = F['dowel_d'] + F['dowel_hole_tol'][1] - (F['dowel_d'] + F['dowel_shaft_tol'][0])
row('位置決めピン Ø4 g6/H7 の隙間', d_lo, d_hi, 0.0, 0.03, 'mm', F['dowel_note'], 0)
# 4) ヒンジ軸Ø10 h7相当 と軸ボス穴 H7相当
a_lo = F['axle_bore_tol'][0] - F['axle_tol'][1]; a_hi = F['axle_bore_tol'][1] - F['axle_tol'][0]
row('ヒンジ軸Ø12-ボス穴の隙間', a_lo, a_hi, 0.0, 0.02, 'mm', '緩い=軸ガタ→画面のカタつき(上端で隙間×0.41/0.02倍に拡大)', 0)
# 5) 首振り摩擦: T=μ·F·r (μ, 予圧の公差) と 操作力/保持
Fp = F['swivel_preload_N']; pt = F['swivel_preload_tol']; r = F['swivel_r_mm'] / 1000
Tlo = F['swivel_mu'][0] * Fp * (1 - pt) * r; Thi = F['swivel_mu'][1] * Fp * (1 + pt) * r; w0, w1 = F['swivel_hold_window_Nm']
row('首振り摩擦トルク', Tlo, Thi, w0, w1, 'N·m', f"緩すぎ<{w0}(画面を触ると回る) / 硬すぎ>{w1}(操作力超過)", 0.0)
row('首振り操作力(画面端0.31m)', Tlo / 0.31, Thi / 0.31, None, 20.0, 'N', '目標≦20N')
# 6) チルト: 保持(最小摩擦≧最悪残差) と 操作力(最大摩擦+公称残差)/0.41 ≦ 20N
FR = H['friction_hold_Nm']; ft = H['friction_tol_pct'] / 100; resid_nom = BAL['resid_nominal']; resid_w = BAL['resid_worst']
AG = H['friction_aging_loss']; row('チルト保持(経年-%d%%後): 最小摩擦 ≧ 最悪残差' % (AG * 100), FR * (1 - ft) * (1 - AG), FR * (1 - ft) * (1 - AG), resid_w, None, 'N·m', f'最悪残差{resid_w:.2f}N·m(調整後公差)。経年・摩耗で摩擦が{AG*100:.0f}%低下した後でも保持', 0.0)
row('チルト操作力(上端0.41m, 最悪=最大摩擦+調整後の最悪残差)', (FR * (1 - ft) - resid_w) / 0.41 if FR * (1 - ft) > resid_w else 0.0, (FR * (1 + ft) + resid_w) / 0.41, None, H['op_target_N'], 'N', f"保持と同じ最悪残差で評価。目標≦{H['op_target_N']:g}N(旧20Nから変更: 経年余裕のためのトレードオフ。要ユーザー確認)", 0.0)
# 7) 首振り: 軸受のガタ(予圧)→ 画面端のカタつき
play = 0.02; edge = play / (S['swivel']['bearing_od'] / 2) * 495.0
row('軸受ガタ起因の画面端の動き', 0.0, edge, None, 0.3, 'mm', '軸受の予圧指定(ラジアル遊び≦0.02mm)が必要(U50)', 0)
print(f'\n総合: {"NG" if bad else "OK"}(NG {bad}件 / WARN {warn}件)。実測(摩擦μ・ばね荷重・ガスケット線荷重)は未実施=UNVERIFIED')
sys.exit(1 if bad else 0)
