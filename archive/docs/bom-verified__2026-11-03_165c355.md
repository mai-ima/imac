# 市販部品BOMと実現性の検証 (外装のみ特注)

方針: 内部は**すべて市販品**。外装(アルミ板金・前面ガラス・スタンド)のみ特注。各部品は「公式資料で確認」「小売・報道で一致」「未確認」に分けて記録する(`model/parts.json`)。寸法の根拠はリンク先。

## 1. BOM
| 区分 | 製品 | 寸法 (mm) | 確認状況 | 根拠 |
|---|---|---|---|---|
| ディスプレイ | BOE **MV270QUM-N50** 27型4K IPS (eDP 4lane/30pin) | 外形 609.4×355.6×13.3 / 有効 596.736×335.664 / 2.45kg | **公式データシート確認** (取付穴・コネクタ位置を図面から読取) | [BOE仕様書(Panelook)](https://www.panelook.com/upload/202310/MV270QUM-N50_Ver.0_20210111_202310319200.pdf) |
| (代替) | LG **LM270WR3-SSC1** | 608.8×355.3×12.8 / 有効 596.74×335.66 | 小売(Data-Modul掲載値) | [Data-Modul](https://data-modul.com/en/products/product-finder/find-your-tft-display/lm270wr3-ssc1) |
| パネル制御 | 4K eDP コントローラ基板 (LM270WR3-SSA3/SSB1/SSC1/SSC2 対応をうたうキット) | 未確認(縦55×150×15の空間を確保) | **未確認** | [Amazon出品](https://www.amazon.com/HDMI-Compatible-LM270WR3-SSA3-LM270WR3-SSB1-LM270WR3-SSC1-LM270WR3-SSC2/dp/B0F5VVQQCD) |
| マザーボード | GIGABYTE **B650I AX** (Mini-ITX) | 170×170 | 外形・I/Oは公式 | [GIGABYTE](https://www.gigabyte.com/Motherboard/B650I-AX-rev-12/sp) |
| CPU | AMD **Ryzen 5 9600X** | TDP 65W / PPT 88W | 小売一致 | [TechPowerUp](https://techpowerup.com/cpu-specs/ryzen-5-9600x.c3652) |
| CPUクーラー | Thermalright **AXP90-X47** | 95×94.5×47(CPU上面基準) | 小売一致(TDP定格は公式未確認) | [Guru3D](https://www.guru3d.com/news-story/thermalright-releases-4-versions-of-ultra-low-profile-cpu-cooler-axp90.html) |
| GPU | MSI **RTX 5060 8G INSPIRE ITX OC** | 145×120×45 / 8ピン×1 / 145W | 複数媒体で一致 | [Tom's Hardware](https://www.tomshardware.com/pc-components/gpus/msi-unveils-one-of-the-tiniest-rtx-5060-gpus-yet-single-fan-inspire-rtx-model-measures-just-145-x-120-x-45mm) / [TechPowerUp](https://techpowerup.com/337599/msi-readies-compact-geforce-rtx-5060-8-gb-inspire-itx-gpu) |
| ライザー | LINKUP **AVA5** PCIe 5.0 x16 20cm | 幅・厚み未確認 | **未確認** | [Heise](https://preisvergleich.heise.de/linkup-ava5-v2-riser-kabel-ag-p5-33ss-020bk-v2-a3400918.html) |
| 電源 | SilverStone **FX500-G** (Flex ATX 500W) | 150×81.5×40.5 / PCIe 6+2×2 / EPS 8 | 小売一致 | [Performance-PCs](https://www.performance-pcs.com/products/silverstone-80-plus-gold-500w-flex-atx-power-supply) |
| ケースファン | Noctua **NF-A12x15 PWM** | 120×120×15 / 94.2m³/h | **公式** | [Noctua](https://noctua.at/en/products/fan/nf-a12x15-pwm/specification) |
| SSD | Samsung **990 EVO Plus** 1TB | 80.15×22.15×2.38 | 小売一致 | [dq-solutions](https://www.dq-solutions.ch/en/samsung-1-tb-ssd-990-evo-plus-nvme-m-2-ssd-m-2-hs1010?m=6293) |
| メモリ | DDR5-5600 UDIMM 16GB | JEDEC 133.35×31.25 | 型番未選定 | — |
| カメラ/音 | USBカメラ・小型スピーカー | — | **未選定** | — |
| **外装(特注)** | アルミ板金A5052+アルマイト、前面強化ガラス、一枚板スタンド | — | 見積もり未取得 | — |

## 2. 実現性チェック結果 (`python3 tools/fitcheck.py`, 全文は `fitcheck-report.txt`)
- 本体幅: 620 − 壁2×2.0 − 隙間2×1.5 = 613.0 ≥ パネル外形609.4 (**余裕3.6mm。薄壁の板金で成立するが精度が必要**)
- 前面スラブ: ガラス1.1+OCA0.4+パネル13.3+隙間1.0+背板2.0 = 17.8 ≤ 18mm
- ポッド内寸 587×184×63mm(総厚84mm)。全部品が収まり、AABB干渉なし。カバー側余裕: CPUクーラー5.9mm / GPU 11mm / 電源15.5mm
- 電力: CPU 88 + GPU 145 + 他45 + パネル36 ≒ 314W(500Wの63%)。GPU 8ピンはFX500-Gの6+2から供給可
- 冷却: 発熱約309W、NF-A12x15の自由流94.2m³/hの55%(52m³/h)でΔT≒17.8K(目標20K以下)
- 注意: この冷却見積もりは単純な熱収支。CPU/GPUの個別温度は実機または熱流体解析が必要

## 3. 実現できない/不確実な点 (正直な一覧)
1. **パネル制御基板**: 市販キットはあるが、基板寸法・バックライト駆動・パネルとの適合が出品者情報のみ。BOE N50は8ch×42V×70mAのバックライト、10V入力で、**適合する基板を現物で確認するまで未確定**。
2. **基板上の部品位置**: GIGABYTEの基板レイアウト(CADや寸法図)は入手できず、ソケット・DIMM・M.2位置は典型例。**実物の寸法を測ってから、クーラーや配線の干渉を再確認**。
3. **CPUクーラーの高さ基準**: 47mmをCPU上面基準と仮定(+約5.5mm)。小売の定格TDP(135W)は公式未確認。
4. **iMacほど薄くはならない**: 前面スラブ18mm、ポッド込み総厚84mm(iMacは約11.5mm)。
5. **ライザーケーブル**: 幅・曲げ半径が未確認。基板のx16スロットとGPUの位置関係(約20cm)は机上のみ。
6. **電源の供給**: FX500-GのAC入力(IEC C14)を下壁から出す加工、ファン騒音(40mm)は未検討。
7. **MSI INSPIRE ITXは一部小売で販売終了**。ZOTAC RTX 5060 SOLO(約164.5×111.2×36.4)で代替する場合はレイアウト再確認。
8. **カメラ・マイク・スピーカー・Wi-Fiアンテナ位置**: 未選定。
9. 板金筐体の公差(幅余裕3.6mm)・ガラス貼り合わせ・放熱の実測は試作が必要。

## 4. 購入前チェックリスト
- [ ] パネルと制御基板の型番一致をメーカー/出品者に確認(バックライト電流・10V電源)
- [ ] GIGABYTE B650I AXの実物でソケット/DIMM/M.2位置を採寸→ `model/layout.json` を更新→ `fitcheck.py`
- [ ] AXP90-X47の高さ基準とAM5搭載時の実高さを確認
- [ ] ライザーの寸法と曲げ半径を確認
- [ ] 板金・ガラスの見積もり
