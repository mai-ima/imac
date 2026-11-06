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
d = 10.0; Zax = math.pi * d ** 3 / 32; Max = F_spring_max * 0.019
chk('ヒンジ軸Ø10 曲げ', Max * 1000 / Zax, 'SUS304', f'M={Max:.1f}N·m(ばね最大{F_spring_max:.0f}N/本)')
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
Fpost = push * h_top / (sw['stop_r'] / 1000.0); Lp = 25.0
chk('首振りストッパポストØ10 曲げ', Fpost * Lp / (math.pi * 10 ** 3 / 32), 'SUS304', f'押し荷重{Fpost:.0f}N, 片持ち{Lp:g}mm')
print('注: 概算(静的・ピーク)。疲労(25,000回)、ばねの応力集中、キー溝、ボルト予圧、ステータ/ロータ板の曲げは未評価=UNVERIFIED。')
sys.exit(1 if bad else 0)
