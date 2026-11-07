# システム仕様書 v7 (2026-11-05)
設計値。実測値は試作後に更新。出典の状態は model/parts.json の status を参照。

## 1. 目的・位置づけ
iMac(27型相当)の外観・体験を再現しつつ、内部をすべて市販の大手メーカー品で構成する一体型ゲーミングPC。外装(特注部品)のみ自作/外注。

## 2. 性能仕様(設計目標)
| 項目 | 仕様 | 根拠/状態 |
|---|---|---|
| CPU | AMD Ryzen 9 9950X3D(16C/32T, 128MB L3(V-Cache片CCD)+L2 16MB, TDP170W(PBP170/MTP230), PPT 230W想定, 5.7GHz) | レビュー引用値(公式PPT/Tjmaxは未取得 U44)。M6マルチを上回るため9800X3Dから変更 |
| GPU | **RTX 5070 Ti 16GB 小型2スロット(寸法基準 PNY Slim 290×150×40, TGP300W, 12V-2x6)** — 4Kで Cyberpunk/CoD/Cities SK2 を快適に(docs/spec/gaming-requirements.md) | 具体型番/入手性は未確定(U46) |
| メモリ | DDR5-6000 CL30 EXPO 32GB(2×16GB) | 型番未定(U12) |
| ストレージ | Samsung 990 PRO Heatsink 1TB(PCIe4.0 x4)+M.2_1(Gen5)空き | Samsung公式 |
| マザーボード | ASUS ROG STRIX X870-I GAMING WIFI(AM5, Mini-ITX, USB4×2, 2.5GbE, Wi-Fi 7) | ASUS公式 |
| 冷却 | ARCTIC Liquid Freezer III Pro 240(ラジエーターP12 Pro×2は外気直吸気)。ケースファン無し: ラジエーターファン2基が外気を吸い、全面格子・PSU・GPUファンから排気(再循環・正圧はU18=未実測) | 公式2D図面 |
| 電源 | Corsair SF1000(SFX 1000W, 80+Platinum) | 未確認(U47) |
| ディスプレイ | 27型4K(LG LM270WR3-SSC1 / BOE MV270QUM-N50)+保証付き制御基板 | 制御基板未確定(U13) |
| 消費電力 | ピーク DC約636W(CPU230+GPU300+基板等45+ファン16+パネル/制御45), AC入力約688W(PSU損失52W), PSU使用率64%(1000W): tools/power_budget.py が単一源 | fitcheck |
| 比較基準 | Apple M6 iMac: GPUは5070 Ti 16GBが上回る見込み、**CPUは9950X3Dでマルチ(GB6≈1.05倍, CB24≈1.7倍)は上回るが、単発は約0.6〜0.77倍でM6に及ばない**(docs/spec/performance-benchmark.md) | 報道/集計値ベース |

## 3. 外形・構造仕様
- 本体 620.0×415.3mm(パネル27型 596.7×335.7、ベゼル11.6、チン68)、スラブ厚25mm、背面ドーム最大総厚190mm(縁の内奥行6mm, 傾斜64mm)(縁は薄く中央へ傾斜)、スタンド: 腕幅150、足 幅360×奥行310(+鋼板ballast3.5kg)、ヒンジ軸 z=45/y=10。
- 構造: 前面: CP-01ガラスをスラブ枠(CP-02/03一体)へ直接接着、パネルは背板へM3 →CP-06サービストレイ(全内部部品)→CP-07ドーム。詳細: docs/spec/custom-parts.md, joint-matrix.md, drawings/01〜16, drawings/parts/。
- 色: 7色(spec.json palette)。外装はアルマイトII。
## 4. 機能仕様
- 取り外し: L1ドーム(工具T10), L2トレイ, L3パネル/スタンド(ガラスはスラブ枠に接着: 交換はスラブごと)(docs/service-manual.md)。
- チルト: **-15°〜+40°**、左右首振り **±60°**(v9)。バランサ=圧縮ダイスプリング2本+尾部レバー、保持=対称摩擦ヒンジ、首振り=クロスローラ軸受+摩擦リング(docs/tilt-swivel-design.md。型番U50/U51は未確認)。
- 冷却: ドームの六角穴(約32%開口)で吸排気、ラジエーター排気/GPU吸気/ケース排気の3経路。
- 接続: 背面左下(ドーム下側傾斜面)にI/O(USB4×2, USB 10Gbps×5, HDMI, 2.5GbE等)。電源ボタン/FlashBackは同所。
- 無線: Wi-Fi 7/BT5.4。アンテナは樹脂RF窓(CP-12)の裏。
- カメラ/マイク/スピーカー: 未選定(U14)。
## 5. 信頼性・耐久性仕様(目標)
| 項目 | 目標 | 試験 |
|---|---|---|
| ヒンジ | 25,000回チルト, ばね破断でも急降下しない | docs/tilt-swivel-design.md |
| 着脱 | ドーム500回, トレイ200回, 前面モジュール20回 | 繰返し試験 |
| 輸送 | 76cm落下(梱包)、衝撃30G | 落下試験 |
| 熱 | 負荷30分でCPU<90℃, GPU<83℃ | 負荷試験 |
| 騒音 | ≤38dBA(1m, 負荷時) | 音響測定 |
| 安全 | 保護接地≤0.1Ω, 表面温度≤48℃(外装) | 導通/温度測定 |
詳細: docs/failure-analysis.md(FMEA42項目)、docs/joint-analysis.md。
## 6. 未確定事項(購入/製作前に解消)
docs/unverified-tracker.md の全項目(U01〜U61。件数は台帳が正: 手書きしない)。特に: U13(パネル制御基板), U09(ライザー), U25/26(質量/ばね), U29/30(接合部品/ガスケット)。
