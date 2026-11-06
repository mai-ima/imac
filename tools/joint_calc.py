#!/usr/bin/env python3
"""接合部・ヒンジ・熱膨張などの強度/トルク概算(v6質量見積り)。出力: docs/joint-analysis.md
質量は部品カタログ値または推定(未実測)。式と前提を併記し、実測後に更新する。実行: python3 tools/joint_calc.py"""
import json, math, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); g = 9.81
D = S['dome']; W = S['body_w']; PH = S['panels'][str(S['panel_size'])]['h']; H = PH + S['bezel'] + S['chin']
rho_al = 2.68e-6   # kg/mm3 (A5052)
# ---- 質量(kg): (名前, 質量, 根拠, 重心z[前面ガラス=0, 背面+], 重心y[本体下端=0]) ----
import sys; sys.path.insert(0, f'{R}/tools'); import massmodel as MM
M = [(n, m, s, z, y) for (n, m, z, y, s) in MM.head()] + [('スタンド A6063(ヒンジ軸より下)', MM.stand_mass(), '推定', 60, -40)]
tot = sum(m for _, m, *_ in M); head_ = [m for m in M if not m[0].startswith('スタンド')]
mh = sum(m[1] for m in head_); cz = sum(m[1] * m[3] for m in head_) / mh; cy = sum(m[1] * m[4] for m in head_) / mh
hinge_y = S['hinge']['axis_y']; hinge_z = S['hinge']['axis_z_from_glass']   # spec.json hinge(v7: 軸を重心の背面側へ)
out = ['# 接合部・ヒンジ・強度の概算 (自動生成: tools/joint_calc.py)', '', '質量・重心は推定(未実測)。実測後に tools/joint_calc.py の表を更新して再生成する。', '',
       '## 1. 質量見積り(v6)', '| 部品 | 質量kg | 根拠 |', '|---|---|---|']
for n, m, s, z, y in M: out.append(f'| {n} | {m:.2f} | {s} |')
out += [f'| **合計(ヒンジより上: ディスプレイ部)** | **{mh:.1f}** | 重心 z={cz:.0f}mm(前面から), y={cy:.0f}mm(下端から) |', f'| 合計(スタンド含む) | {tot:.1f} | |', '']
# ---- ヒンジ必要トルク ----
dz = cz - hinge_z; dy = cy - hinge_y
out += ['## 2. ヒンジ保持トルク(チルト角 a で本体を保持するのに必要)', f'式: τ(a) = m·g·(dz·cos a + dy·sin a)。m={mh:.1f}kg, 重心オフセット dz={dz:.0f}mm(軸より背面側が+), 軸から重心の高さ dy={dy:.0f}mm。', '', '| チルト a | 必要トルク N·m | 備考 |', '|---|---|---|']
tau = {}
for a in (-5, 0, 10, 20, 25):
    t = mh * g * (dz * math.cos(math.radians(a)) + dy * math.sin(math.radians(a))) / 1000; tau[a] = t
    out.append(f'| {a:+d}° | {t:.1f} | {"前方へ倒れる向き" if t<0 else "後方(上向き)へ倒れる向き"} |')
tmax = max(abs(v) for v in tau.values())
out += ['', f'**問題**: 最大 {tmax:.1f} N·m を摩擦だけで保持する定トルクヒンジは、ユーザーが指で傾ける力(上端で約{tmax/0.415:.0f} N)になり**実用的でない**(市販の定トルク/フリクションヒンジは数N·m級が主流: 要調査, docs/research-notes.md)。', '',
        '### 対策(v9 採用)', '- **採用**: ヒンジ軸 z=40mm・y=10mm、チルト -15°〜+40°(spec.json)。重力トルクをダイスプリング2本+尾部レバーで相殺し(tools/balance_calc.py)、残差を対称摩擦ヒンジで保持。詳細は docs/tilt-swivel-design.md。',
        f'- **A. カウンターバランス**: ダイスプリング+レバー(旧案の定荷重ばね/ガススプリングは不採用)で重力モーメントを相殺し、残りを小トルクの摩擦で保持(Apple Studio Display / iMac式)。相殺トルクの目標: ±{0.15*tmax:.1f}N·m 程度の残差。',
        f'- **B. 回転軸を重心の高さに近づける**: dyを減らす(軸を本体中央付近へ)。ただし軸のアームがトレイ/ドームを貫通せず背板に取り付く構造が必要(スタンド腕を背板直付け→ドーム下端の切り欠き)。dy を {dy:.0f}→100mm にすると最大トルクは約 {mh*g*(dz*math.cos(math.radians(25))+100*math.sin(math.radians(25)))/1000:.1f} N·m。',
        '- **C. チルトを固定段階(ラチェット)にする**: 段数を減らす代わりに摩擦を不要にする。',
        '', '## 3. トレイ吊りピン(キーホール)の強度',]
mt = sum(m[1] for m in M if m[0] in ('サービストレイ t2.0', 'board', 'cooler', 'radiator', 'gpu', 'psu', 'fan', 'ctrl_board', 'ssd', 'ac_inlet', 'ケーブル/金具/ガスケット/ラッチ等'))
sh_d = 5.0; A = math.pi / 4 * sh_d ** 2; t_plate = 3.0;      # v7: 肩径Ø5(CP-04)、SUSブッシュで実効板厚3.0(CP-05)
sy = 193.0; su = 228.0     # A5052-H32 降伏/引張(代表値, 要データシート)
for label_, G in (('静荷重(1G)', 1), ('輸送衝撃 30G', 30), ('衝撃 50G', 50)):
    F = mt * g * G / 2     # 上側2点で支持する最悪ケース
    out.append(f'- {label_}: トレイ総質量 {mt:.1f}kg → 1点あたり {F:.0f} N。ピン肩径{sh_d}mmのせん断応力 {F/A:.1f} MPa(SUS304 降伏≈200MPa, せん断≈115MPa)、A5052+SUSブッシュ(実効t{t_plate})の支圧応力 {F/(sh_d*t_plate):.0f} MPa(降伏{sy:.0f}MPa) → {"OK" if F/(sh_d*t_plate) < sy*0.6 else "要補強(ブッシュ/板厚増/ピン径増)"}')
out += ['', '→ 輸送衝撃はキーホール縁の局所変形が支配的。キーホール周囲に硬質ブッシュ(SUS)またはt3.0へ増厚を推奨。トレイ法線方向の衝撃(GPU/AIOのスタンドオフ荷重)は §5。', '']
# ---- ドーム固定 ----
perim = 2 * ((W - 2 * D['inset_left_right']) + (H - D['inset_bottom'] - D['inset_top']))
out += ['## 4. ドーム固定(磁石・ガスケット)', f'- ドーム外周長 ≈ {perim:.0f} mm。', '- **磁石の相手は鉄系が必要**: アルミは非磁性のため、背板側に鋼板(SPCC/SUS430)のストライクプレートが要る。磁石単体の吸着は鋼板接触で約2〜2.5kgf(N52 φ8×3, メーカー値要確認)、ガスケット圧縮後の実隙間1mmで低下(定性的に1/3程度)。',
        f'- 12個の磁石の合計保持力(隙間1mm想定): 約 {12*7:.0f} N(1個7Nと仮定: 未検証)。']
for fN in (0.05, 0.175, 0.5):
    out.append(f'- EMIガスケット閉合力 {fN} N/mm × {perim:.0f}mm = {fN*perim:.0f} N。')
out += [f'- **結論**: Parker SOFT-SHIELD 3500の公称閉合力は<1lb/inch(≈0.175N/mm, docs/research-notes.md)→ 最大 {0.175*perim:.0f}N に対し磁石12個は約84N(未検証)で不足。**ガスケットを低圧縮で使う(圧縮率を30%程度に抑える)うえで、4分の1回転ラッチ(または拘束ねじ)を上側にも増設して計6点以上にする**。実測で調整(U21)。', '']
# ---- 5. トレイ法線方向(衝撃) ----
out += ['## 5. 輸送衝撃(トレイ法線方向)']
for nm, m_ in (('GPU(ブラケット+クレードル+ライザー)', 0.95), ('AIOラジエーター+ファン(4点ねじ)', 1.2), ('PSU(SFX 4点)', 0.96)):
    F = m_ * g * 30
    out.append(f'- {nm}: {m_}kg × 30G = {F:.0f} N。M3×4点なら1点 {F/4:.0f} N(PEM SO系スタンドオフの押抜き/引抜き強度≈1000N級は要データシート確認 U21)→ ネジ自体より、GPUはPCIe端子とライザーの保持(クレードル両端支持)が支配的。')
out += ['', '## 6. 熱膨張差(ΔT=40K)']
for nm, a_, L in (('アルミ(背板/ドーム) 23.6e-6/K', 23.6e-6, 620), ('化学強化ガラス 9e-6/K', 9e-6, 620), ('ステンレスSUS304 17.3e-6/K', 17.3e-6, 620)):
    out.append(f'- {nm} × {L}mm × 40K = {a_*L*40:.2f} mm')
out += [f'- ガラス枠とアルミの差 ≈ {(23.6e-6-9e-6)*620*40:.2f} mm → 枠への構造用シリコーン接着(厚≥1.0mm, せん断追従)または周囲クリアランス ≥0.5mm が必要。ガラスを硬いエポキシで全面接着してはならない。', '',
        '## 7. その他の接合部リスク(要試験)', '- アルマイト層は絶縁(Type II 約10〜25µm)。接地導通が必要な箇所(ドーム縁, トレイ-スタンドオフ, 背板)はマスキングまたは導電(アロジン/化成)処理。', '- ステンレス締結具×アルミ: 乾燥環境では実用上問題が小さいが、結露時のガルバニック腐食に対しアルマイト+グリース/シーラント。',
        '- ホース(EPDM系,ARCTIC): 透過による冷却液減少(数年)と、ポンプ上方の気泡溜まり(ディスプレイ縦置き)。ラジエーターを高所、ポンプを低所に置く(本設計: ラジエーター上端がポンプより高い → 気泡はラジエーター上部のタンクに集まる)。',
        '- GPU縦置き: 長軸が鉛直。重量を支えるのは下端ブラケット/クレードル。ライザーのPCIeコネクタ(横向き)に曲げモーメントを与えないこと。', '- ファン軸受(スリーブ/FDB)の姿勢依存: ファン軸が水平(ディスプレイ縦置き)でも寿命が低下しにくい軸受(FDB/SSO)を使う。Noctua NF-A12x25はSSO2、ARCTIC P12 ProはFDB(仕様は要確認)。']
open(f'{R}/docs/joint-analysis.md', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out[:30]))
