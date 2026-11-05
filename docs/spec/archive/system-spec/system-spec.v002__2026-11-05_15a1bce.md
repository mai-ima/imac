# システム仕様書 v7 (2026-11-05)
設計値。実測値は試作後に更新。出典の状態は model/parts.json の status を参照。

## 1. 目的・位置づけ
iMac(27型相当)の外観・体験を再現しつつ、内部をすべて市販の大手メーカー品で構成する一体型ゲーミングPC。外装(特注部品)のみ自作/外注。

## 2. 性能仕様(設計目標)
| 項目 | 仕様 | 根拠/状態 |
|---|---|---|
| CPU | AMD Ryzen 7 9800X3D(8C/16T, L3 96MB, TDP120W, Tjmax95℃, PPT162W) | AMD公式(TDP/Tjmax)/PPTは第三者 |
| GPU | ASUS Dual RTX 5060 Ti 16GB(4608 CUDA, GDDR7 28Gbps 128bit, TGP180W, 8ピン1本) | ASUS公式 |
| メモリ | DDR5-6000 CL30 EXPO 32GB(2×16GB) | 型番未定(U12) |
| ストレージ | Samsung 990 PRO Heatsink 1TB(PCIe4.0 x4)+M.2_1(Gen5)空き | Samsung公式 |
| マザーボード | ASUS ROG STRIX X870-I GAMING WIFI(AM5, Mini-ITX, USB4×2, 2.5GbE, Wi-Fi 7) | ASUS公式 |
| 冷却 | ARCTIC Liquid Freezer III Pro 240 + Noctua NF-A12x25 ×1(ケース排気) | 公式/小売 |
| 電源 | Corsair SF750(SFX 750W, 80+Platinum, 12V-2x6) | 小売(公式未確認) |
| ディスプレイ | 27型4K(LG LM270WR3-SSC1 / BOE MV270QUM-N50)+保証付き制御基板 | 制御基板未確定(U13) |
| 消費電力 | ピーク約423W(CPU162+GPU180+他45+パネル36), PSU使用率56% | fitcheck |
| 比較基準 | Apple最新iMac(M系)以上のCPU/GPU性能 | 公開ベンチ値は未確認 |

## 3. 外形・構造仕様
- 本体 620.0×415.3mm(パネル27型 596.7×335.7、ベゼル11.6、チン68)、スラブ厚19mm、背面ドーム最大総厚113mm(縁は薄く中央へ傾斜)、スタンド: 腕幅150、足 幅260×奥行245、ヒンジ軸 z=43/y=10。
- 構造: 前面: CP-01ガラスをスラブ枠(CP-02/03一体)へ直接接着、パネルは背板へM3 →CP-06サービストレイ(全内部部品)→CP-07ドーム。詳細: docs/spec/custom-parts.md, joint-matrix.md, drawings/01〜16, drawings/parts/。
- 色: 7色(spec.json palette)。外装はアルマイトII。
## 4. 機能仕様
- 取り外し: L1ドーム(工具T10), L2トレイ, L3パネル/スタンド(ガラスはスラブ枠に接着: 交換はスラブごと)(docs/service-manual.md)。
- チルト: -5°〜+25°(要確認)、カウンターバランス+対称摩擦ヒンジ(docs/hinge-design.md)。
- 冷却: ドームの六角穴(約32%開口)で吸排気、ラジエーター排気/GPU吸気/ケース排気の3経路。
- 接続: 背面左下(ドーム下側傾斜面)にI/O(USB4×2, USB 10Gbps×5, HDMI, 2.5GbE等)。電源ボタン/FlashBackは同所。
- 無線: Wi-Fi 7/BT5.4。アンテナは樹脂RF窓(CP-12)の裏。
- カメラ/マイク/スピーカー: 未選定(U14)。
## 5. 信頼性・耐久性仕様(目標)
| 項目 | 目標 | 試験 |
|---|---|---|
| ヒンジ | 25,000回チルト, ばね破断でも急降下しない | docs/hinge-design.md |
| 着脱 | ドーム500回, トレイ200回, 前面モジュール20回 | 繰返し試験 |
| 輸送 | 76cm落下(梱包)、衝撃30G | 落下試験 |
| 熱 | 負荷30分でCPU<90℃, GPU<83℃ | 負荷試験 |
| 騒音 | ≤38dBA(1m, 負荷時) | 音響測定 |
| 安全 | 保護接地≤0.1Ω, 表面温度≤48℃(外装) | 導通/温度測定 |
詳細: docs/failure-analysis.md(FMEA42項目)、docs/joint-analysis.md。
## 6. 未確定事項(購入/製作前に解消)
docs/unverified-tracker.md の U01〜U30。特に: U13(パネル制御基板), U09(ライザー), U25/26(質量/ばね), U29/30(接合部品/ガスケット)。
