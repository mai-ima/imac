#!/usr/bin/env python3
"""簡易強度ゲート(手計算級の概算。FEA・疲労・実材料データの代替ではない)。許容応力=降伏/安全率1.5。荷重ケース: バランサ最大ばね力、画面上端50N押し(ストッパ/首振りストッパ)、頭部重量。
材料降伏値は代表値(要データシート: U29)。1つでもNGなら終了コード1。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; N = S['neck']; sw = S['swivel']; BAL = json.load(open(f'{R}/model/balance.json')); g = 9.81
SF = 1.5; Y = {'SUS304': 205.0, 'A6063-T5': 145.0, 'A5052-H32': 193.0, 'SUS(ボルトA2-70)': 450.0}
mh = MM.head_cg()[0]; W_head = mh * g
F_spring_max = BAL['F0_longest_total'] * (1 + BAL['p']) / 2        # 1本あたり最大 [N]
push = 50.0; h_top = 0.41; M_push = push * h_top               # 画面上端を押す [N·m]
bad = 0
def chk(name, sigma, mat, note=''):
    global bad; allow = Y[mat] / SF; ok = sigma <= allow; bad += 0 if ok else 1
    print(f'[{"OK " if ok else "NG "}] {name}: 応力 {sigma:.0f} MPa ≤ 許容 {allow:.0f} MPa({mat}降伏{Y[mat]:.0f}/SF{SF}) {note}')
# 1) 尾部レバー(片持ち, 根元曲げ): 1本が受けるばね力×腕e
e = BAL['e']; Mlev = F_spring_max * e / 1000.0 * 1.0                # N·m(ばね力が軸直角成分でほぼ全部かかる保守側)
t, w = N['lever_t'], N['lever_w']; Z = t * w * w / 6.0
chk(f'尾部レバー曲げ(t{t:g}×幅{w:g})', Mlev * 1000 / Z, 'SUS304', f'M={Mlev:.1f}N·m/本')
# 2) 尾部レバー+軸: キー溝/軸Ø10の曲げ(レバー位置x=26から摩擦ヒンジx=45までの19mm)
d = 12.0; Zax = math.pi * d ** 3 / 32; Max = F_spring_max * 0.019
chk('ヒンジ軸Ø12 曲げ', Max * 1000 / Zax, 'SUS304', f'M={Max:.1f}N·m(ばね最大{F_spring_max:.0f}N/本)')
# 3) ストッパ(レバー先端): 画面上端50N押し → 軸まわりモーメントがレバー長で受けられる。片側のレバーが全部受ける最悪ケース
Fst = M_push / (N['lever_len'] / 1000.0); chk('レバー先端(ストッパ)曲げ', Fst * (N['lever_len'] / 1000.0) * 1000 / Z / 2.0, 'SUS304', f'50N押し→レバー先端力{Fst:.0f}N(2本で分担)')
# 4) ストッパ受け(前カバー t6): パッド位置を片持ちの高さで曲げ(有効幅40mm)
hc = (N['cover_top'] - (-S['stand']['drop'] + sw['stack_h'] + N['base_t'])); Fp = Fst / 2.0; bw, tc = 40.0, N['front_cover_z'][1] - N['front_cover_z'][0]
chk(f'前カバー t{tc:g}(ストッパ受け)', Fp * (hc * 0.5) / (bw * tc * tc / 6.0), 'A6063-T5', f'パッド荷重{Fp:.0f}N, 高さ{hc*0.5:.0f}mm片持ち')
tt = N['tie_z'][1] - N['tie_z'][0]; chk(f'タイプレート t{tt:g}(-15°ストッパ受け)', Fp * 10.0 / (bw * tt * tt / 6.0), 'A6063-T5', '両端支持(側板間)の保守側近似')
# 5) ネック基台M5×4: 転倒モーメント(静重力+押し)を、ボルト群の中心間距離で受ける
Mtot = (W_head * abs(MM.head_cg()[3][0][3] if False else 0.12) + M_push) ; zspan = 0.046; A_s = 14.2
sig_b = (Mtot / (2 * zspan)) / (2 * A_s)       # 2本×2列で引張を分担
chk('ネック基台M5×4 引張', sig_b, 'SUS(ボルトA2-70)', f'M≈{Mtot:.0f}N·m, ボルト間隔{zspan*1000:.0f}mm')
# 6) 首振りストッパ(ステータ上のポスト Ø8 鋼芯): 50N押しがポスト1本に掛かる(R=stop_r)
h_sw = (MM.H + S['stand']['drop'] - sw['stack_h']) / 1000.0      # 首振り軸から画面上端までの高さ(swivel_calc と同じ基準)
Fpost = push * h_sw / (sw['stop_r'] / 1000.0); Lp = 25.0
chk('首振りストッパポストØ10 曲げ', Fpost * Lp / (math.pi * 10 ** 3 / 32), 'SUS304', f'押し荷重{Fpost:.0f}N, 片持ち{Lp:g}mm')
# 7) 軸の曲げ+捩りの合成(Mises): 捩り=バランサの片側トルク(最大 nominal τg/2)、曲げは上記
Tq = 18.0 / 2; tau = Tq * 1000 / (math.pi * d ** 3 / 16); sig = Max * 1000 / Zax; chk('ヒンジ軸Ø12 曲げ+捩り合成(Mises)', math.sqrt(sig ** 2 + 3 * tau ** 2), 'SUS304', f'捩り{Tq:.1f}N·m/側(キー溝の応力集中・疲労は未評価)')
# 8) 単一故障: ばね1本折損 → 頭部が端へ落ちて停止ストッパへ衝突するエネルギー(摩擦は最小値)
def tg(a): a = math.radians(a); return mh * g * (MM.head_cg()[2] - S['hinge']['axis_y']) * math.sin(a) / 1000
s_, e_, F0, p_, lmax, stroke, sign = BAL['s'], BAL['e'], BAL['F0_longest_total'], BAL['p'], BAL['lmax'], BAL['stroke'], BAL['sign']
def sp(a, frac):
    ar = math.radians(a); Bz, By = -e_ * math.sin(ar), -e_ * math.cos(ar); vz, vy = Bz, By + s_; l = math.hypot(vz, vy); F = frac * F0 * (1 + p_ * (lmax - l) / stroke); return (Bz * (F * vy / l) - By * (F * vz / l)) / 1000
FRm = S['hinge']['friction_hold_Nm'] * (1 - S['hinge']['friction_tol_pct'] / 100); Ihead = mh * (MM.head_cg()[2] - S['hinge']['axis_y']) ** 2 / 1e6 + mh * (0.415 ** 2 + 0.15 ** 2) / 12
Emax = 0.0
for a0 in range(int(S['hinge']['tilt_min_deg']), int(S['hinge']['tilt_max_deg']) + 1, 5):
    for tgt in (S['hinge']['tilt_min_deg'], S['hinge']['tilt_max_deg']):
        n = 100; E = 0.0; d_ = 1 if tgt > a0 else -1
        for i in range(n):
            a = a0 + (tgt - a0) * (i + .5) / n; net = (tg(a) + sign * sp(a, 0.5)) * d_ - FRm; E += max(0.0, net) * math.radians(abs(tgt - a0)) / n
        Emax = max(Emax, E)
stroke_pad = N['pad_thick'] * 0.5 / 1000.0; Fimp = Emax / stroke_pad; Zl = N['lever_t'] * N['lever_w'] ** 2 / 6.0
chk('ばね1本折損→ストッパ衝突: レバー曲げ', Fimp / 2 * N['lever_len'] / Zl, 'SUS304', f'落下E={Emax:.2f}J(I={Ihead:.2f}kg·m², ω≈{math.sqrt(2*Emax/Ihead):.1f}rad/s)、パッド圧縮{N["pad_thick"]*0.5:g}mm→衝撃力{Fimp:.0f}N(2本分担)')
print('注: 概算(静的・ピーク)。疲労(25,000回)、ばねの応力集中、キー溝、ボルト予圧、ステータ/ロータ板の曲げは未評価=UNVERIFIED。')
sys.exit(1 if bad else 0)
