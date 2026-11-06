> **【更新 2026-11-05】** 本書の「確定または有力」表のうち SilverStone FX600 と Noctua NH-L12S は v6 で不採用。現行: 電源=Corsair SF750、冷却=ARCTIC LF III Pro 240、ケースファン=NF-A12x25 **1基**(旧記載の排気ファン2基は廃止。ΔTは docs/thermal-analysis.md と fitcheck を参照)。

# 部品選定 v5 (大手・最新規格・高性能・拡張性) — 途中経過

要件: 大手の信頼できる部品、最新規格、高性能、拡張性、機械同士の相性。確認は公式資料を優先し、取得できない項目は「未確認」。**サブエージェントの調査は多くの公式サイトが403/429/503で取得できず、確認できた項目が限られた**。公式資料を直接取得できたものは「公式確認」と記す。

## 確定または有力
| 区分 | 選定 | 確認状況 | 根拠 |
|---|---|---|---|
| GPU | **ASUS Dual GeForce RTX 5060 Ti 16GB OC** | **公式確認**: 229×120×50mm、2.5スロット、補助電源 8ピン×1、推奨電源550W、出力 HDMI 2.1b×1 + DP 2.1b×3、CUDA 4608、GDDR7 28Gbps/128bit。TGP180W・PCIe 5.0はNVIDIA公式(サブエージェント) | [ASUS公式](https://www.asus.com/motherboards-components/graphics-cards/dual/dual-rtx5060ti-o16g/techspec/) |
| SSD | **Samsung 990 PRO with Heatsink** 1TB/2TB | **公式確認**: 最大 80.15×25×8.88mm、M.2 2280、PCIe 4.0 x4 / NVMe 2.0、Samsung自社コントローラ、1GB/2GB LPDDR4 | [Samsung公式データシート](https://download.semiconductor.samsung.com/resources/data-sheet/Samsung_NVMe_SSD_990_PRO_with_Heatsink_Datasheet_Rev_2.0_10129695053410.pdf) |
| 電源 | SilverStone **FX600 Platinum** (Flex ATX 600W) | 寸法150×81.5×40.5は複数小売一致。コネクタ構成(PCIe 6+2×2、12V-2x6の有無、固定/モジュラー)は**未確認** | [SFF.net](https://smallformfactor.net/articles/first-look-silverstone-fx600-platinum-flex-atx-power-supply/) |
| ファン | Noctua **NF-A12x25 PWM** (または NF-A12x15) | 120×120×25、102m³/h、2.34mmH2O(TechPowerUp、公式は429で取得不可) | [TechPowerUp](https://techpowerup.com/review/noctua-nf-a12x25-pwm/single-page.html) |
| 基板 | **ASUS ROG STRIX X870-I GAMING WIFI** | **公式確認(寸法170×170、レイアウト図p.14を実測)**。USB4×2、USB 10Gbps×5、2.5GbE、Wi-Fi 7、PCIe 5.0 x16、DDR5×2(EXPO)、M.2×2(ドーターカード方式)。Ryzen 9000の出荷時BIOS対応は未確認(FlashBackあり)。VRMはファン付きヒートシンクで高さ未確認。マニュアルは第三者ホスト版(2024年版) | [ASUS仕様](https://rog.asus.com/motherboards/rog-strix/rog-strix-x870-i-gaming-wifi/spec/) |
| CPU | **AMD Ryzen 7 9800X3D** | TDP120W/PPT162W/Tjmax95℃/8C16T/L3 96MB(第三者一致、AMD公式は取得不可) | [BuildCores](https://www.buildcores.com/products/CPU/7xjqsomhr/AMD-Ryzen-7-9800X3D) |
| CPUクーラー | **Noctua NH-L12S** | 128×146×70mm、390g(ファン無)。軸の割当と基準面は未確認(小売一致) | [Galaxus](https://galaxus.de/en/s1/product/noctua-nh-l12s-70-mm-cpu-coolers-6817433) |

## 決定 v6 (最新。ケース拡張の許可・性能無制限の方針)
- **CPU冷却**: AMD公式が液冷推奨のため **ARCTIC Liquid Freezer III Pro 240**(ラジエーター277×120×38+ファン25=63mm、ポンプ108.47×Ø91×68.5mm、保証6年、AM5対応、すべて公式仕様書/2D図面で確認)。NH-L12Sは不採用。
- **電源**: **Corsair SF750 (SFX 750W)**(ATX 3.1/12V-2x6、125×63.5×100mm、保証7年。公式は403で、値は小売情報)。GX-750(ATX, 保証10年, 150×85×140mm)は高さ85mmがドーム最大深さ87mmに入らず不採用。
- **ポッド → 背面ドーム**: ほぼ背面全面(ドーム外形 596×約377mm、最大総厚108mm、縁の傾斜60mm)。配置は `tools/layout_search.py` の探索解(`model/layout.json`)。
- **fitcheck(傾斜考慮)**: 全部品が成立(総合OK)。ΔT 6.4K(ラジエーターファン含む)、電力使用率56%(性能無制限)。警告は2件(ポンプとDIMM/SSDの位置関係)。

## (旧) 決定 v5
- 高性能案(案B)を採用: **9800X3D + NH-L12S**、ポッド総厚 **108mm**、ポッド高 **256mm**(GPU長229mmのため)。薄型案(案A)は代替。
- **性能は制限しない**(ユーザー方針)。電源は最悪ケース(CPU PPT162W+GPU TGP180W+他≒423W)に対し余裕30%以上 → 750W級へ変更(調査中)。CPU冷却はAMD公式の『液冷推奨』に従い240mm AIOを調査中(NH-L12Sは不採用方向)。
- **ポッド排気ファンを2基(NF-A12x25)**に変更(1基だと排気ΔT 22.8Kで基準超過、2基で10.2K)。
- fitcheck結果: 収まり・干渉・電力・風量はOK。**警告2件**: (1)NH-L12SとDIMMのクリアランス未確認、(2)SSD(ドーターカード)とクーラーの高さ関係未確認。

## 判断が必要な論点(根拠つき)
1. **CPUと冷却の組合せ(ポッドの厚みを決める)**
   - 案A(薄型): Ryzen 7 9700X (PPT 88W) + Noctua NH-L9a-AM5 (全高37mm)。内寸63mmに収まるが、定格が61〜75W(出典で食い違い)でPPT 88Wには余裕が薄い。
   - 案B(高性能): Ryzen 7 9800X3D + Noctua NH-L12S (全高70mm)。基板面基準で約79mmの内寸が必要 → **ポッド総厚 約100〜104mm**。ゲーム用途の実負荷は50〜80W程度でゲームには成立する見込みだが、定量データは未確認。
   - 現時点の暫定: **案Bを推奨**(要件の「高性能」)、案Aを薄型の代替として併記。
2. **電源容量**: 9800X3D(約160W PPT)+ RTX 5060 Ti(180W)+他60W ≒ 400W。FX600の600Wなら使用率約67%(余裕33%)。
3. **GPUの入手性**: 5060 Ti 16GBはGDDR7高騰で終息との報道(NVIDIA公式ではない)。代替は NVIDIA RTX 5070 FE(242×112mm、250W)。
4. **ディスプレイ**: 保証付きの「パネル+制御基板」を単体で売る大手の公式キットは確認できなかった。
   - LG LM270WR3-SSC1: Data-Modul掲載の外形 608.8×355.3×12.8mm、有効596.74×335.66、eDP、10bit(8bit+FRC)。**リフレッシュレートは60Hz級と思われるが未確認**。制御基板キットの有無は未確認。
   - 市販モニタ分解流用(例: LG 27UK850/27UL850)は薄いが、純正保証は失効。
   - AccuView OFU270Uは684mm幅で本体に入らず不採用。
   - **要 Data-Modul への直接問い合わせ**(外形図、最大厚み、対応コントローラ基板、保証)。120Hz以上/5Kの候補は未確認。
5. **PCIeライザー**: LINKUPのPCIe 5.0 x16ライザーの寸法・曲げ半径は未確認(公式サイト取得不可)。GPU(5060 Ti)は物理x8の可能性があり、ライザー互換は実機確認が必要。
6. **メモリ**: DDR5-6000 CL30 EXPO 32GB(Corsair Vengeance / G.Skill / Kingston Fury等)。ヒートスプレッダ込みの高さ・ラベル仕様は未確認。

## 次の作業
- 基板の選定結果を反映 → `model/parts.json`・`layout.json` を更新 → `tools/fitcheck.py` → Blenderモデルの更新。
- 自作外装の図面を新寸法で再生成(`tools/gen_mfg_drawings.py`)。
