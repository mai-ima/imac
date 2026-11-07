# 部品表 BOM(自動生成: tools/gen_estimate.py / 元データ model/parts.json + model/procurement.json + model/custom_parts.json)

購入品は parts.json の全エントリ(radiator は cooler と同一製品で数量0=二重計上しない。rad_duct は特注 CP-25)。状態: official=メーカー公式資料で確認 / retail=小売・報道の一致 / assumed=未確認 / CANDIDATE=未採用候補。

## 1. 購入品

| ID | 名称/型番 | メーカー | 数量 | 外形mm | 状態 | 発注可否 | 主な根拠(出典) |
|---|---|---|---|---|---|---|---|
| panel | LG Display LM270WR3-SSC1(第一候補) / BOE MV270QUM-N50(代替) | LG Display / BOE | 1 | 609.4x355.6x13.3 | official | 型番は2候補(第一候補のデータシートは第三者掲載)。購入前に1つへ確定 | https://www.panelook.com/upload/202310/MV270QUM-N50_Ver.0_20210111_202310319200.pdf |
| ctrl_board | 型番未確定(4K eDPコントローラ基板) | 未定 | 1 | 55x110x15 | assumed | NO(型番未確定) | - |
| board | ROG STRIX X870-I GAMING WIFI | ASUS | 1 | 170x170x1.6 | official | YES(型番確定) | https://rog.asus.com/motherboards/rog-strix/rog-strix-x870-i-gaming-wifi/spec/ |
| cpu | Ryzen 9 9950X3D(BOX, クーラー無し) | AMD | 1 | 40x40x5 | retail | YES(型番確定) | https://www.notebookcheck.net/AMD-Ryzen-9-9950X3D-Review-Ryzen-7-9800X3D-levels-of-gaming-performance-and-power-efficiency-for-50-markup-over-the-Ryzen-9-9950X.976049.0.html |
| cooler | Liquid Freezer III Pro 240 (ACFRE00178A, 非RGB) | ARCTIC | 1 | 108.47x91x68.5 | official | YES(型番確定。ただし公式シートはA-RGB版 U33) | https://www.arctic.de/media/8d/19/d2/1744191002/Spec_Sheet_Liquid_Freezer_III_Pro_240_A-RGB_EN.pdf |
| gpu | RTX 5070 Ti 16GB 小型2スロット(PNY Slim 290x150x40 を寸法基準。具体型番は未確定 U46) | PNY(寸法基準) | 1 | 290x150x40 | assumed | NO(具体型番・国内入手性が未確定 U46) | https://hothardware.com/news/pny-slim-2-slot-rtx-5080-5070-ti-5070-gpus-sff-gaming-pcs |
| riser | AVA5 PCIe 5.0 x16 ライザー AG-P5-33SS-020BK-v2(直線)または右角(SR)品 | LINKUP | 1 | 200x89x6 | assumed | PARTIAL(直線/右角の選択が未確定) | https://preisvergleich.heise.de/linkup-ava5-v2-riser-kabel-ag-p5-33ss-020bk-v2-a3400918.html |
| psu | SF1000 (SFX 1000W 80+ Platinum) | Corsair | 1 | 125x100x63.5 | assumed | YES(型番確定。公式仕様は未取得) | https://www.corsair.com/us/en/p/psu/cp-9020284-na/sf-series-sf750-fully-modular-80-plus-platinum-sfx-power-supply-cp-9020284-na |
| ssd | 990 PRO with Heatsink 1TB (MZ-V9P1T0CW) | Samsung | 1 | 80.15x25x8.88 | official | YES(型番確定) | https://download.semiconductor.samsung.com/resources/data-sheet/Samsung_NVMe_SSD_990_PRO_with_Heatsink_Datasheet_Rev_2.0_10129695053410.pdf |
| ram | DDR5-6000 CL30 EXPO 32GB(2x16GB)キット(型番未定) | Corsair/G.Skill/Kingston 等 | 1 | 133.35x8x44 | assumed | NO(型番未定) | - |
| camera_audio | Webカメラ/マイク/スピーカー(未選定) | 未選定 | 1 | 0x0x0 | assumed | NO(未選定) | - |
| radiator | (cooler と同一製品 ACFRE00178A に含まれる。P12 Pro ×2 同梱) | ARCTIC | 0 | 277x120x63 | official | cooler に含む | https://www.arctic.de/media/8d/19/d2/1744191002/Spec_Sheet_Liquid_Freezer_III_Pro_240_A-RGB_EN.pdf |
| ac_inlet | IEC C14 インレット(型番未選定 U40) | Schurter/Qualtek等 | 1 | 28x26x20 | assumed | NO(型番未選定) | - |
| rad_duct | (特注 CP-25 として custom_parts.json に登録) | 特注 | 0 | 228x120x43 | CANDIDATE | 特注品(CP-25) | - |

基板上部品: 基板上部品19点(docs/board-components.md, model/x870i_layout.json components)は X870-I 基板に実装済みの部品(ヘッダ/コネクタ/M.2 WiFi等)で、別途購入する部品ではない。BOMには計上しない(基板1枚に含む)。高さは典型値=UNVERIFIED。

## 2. 特注部品(要見積。詳細は docs/spec/custom-parts.md、見積条件は handoff/00_見積依頼書.md)

| CP | 名称 | 数量/台 | 材質 | 状態 |
|---|---|---|---|---|
| CP-01 | 前面ガラス | 1 | 化学強化ガラス(アルミノシリケート) | 設計(試作要) |
| CP-02 | スラブ枠(背板の曲げ縁・ガラス受け) | 1 | A5052-H32 t2.0(背板CP-03と一体の曲げ縁) または A6063押出枠+背板 | 設計(試作要) |
| CP-03 | 背板(バックプレート) | 1 | A5052-H32 | 設計(試作要) |
| CP-04 | キーホール吊りピン(肩ねじ) | 4 | SUS304 肩ねじ(Misumi/McMaster相当) M4ねじ, 肩径Ø6 h8×6.0(支圧部=トレイ+ブッシュ3.0), 頭Ø10×t3 | 規格品選定(U29: 品番確定) |
| CP-05 | キーホール補強ブッシュ | 4 | SUS304 t1.0 プレート(16×28 長丸) | 設計 |
| CP-06 | サービストレイ | 1 | A5052-H32 | 設計(試作要) |
| CP-07 | 背面ドーム(カバー) | 1 | A5052-H32 または A5052-O絞り | 設計(試作要) |
| CP-08 | EMIガスケット | 1 | 導電ファブリックオーバーフォーム(候補: Parker SOFT-SHIELD 3500 / Laird FoF) | 候補選定(U30) |
| CP-09 | ドームラッチ(下面・隠し)+上辺フック | 6 | SUS303 カム+樹脂ノブ または 規格品(Southco/Misumi 1/4回転) | 規格品選定中(U29) |
| CP-10 | スタンド足(ballast内蔵) | 1 | A6063-T5(足本体)+SPCC鋼板ballast+A5052底カバー t1.5 | 設計(試作要) |
| CP-11 | チルト機構(ヒンジ+カウンターバランス) | 1 | 対称摩擦ヒンジ(Reell PHL/PHC級)×2(合計保持3.0N·m) + カム式バランサ(CP-23: カム板+ローラ+ダイスプリング2本, 型番未選定) | 方式決定・部品未選定(U26/U27) |
| CP-12 | RF窓(格子裏の樹脂板) | 1 | PC樹脂(UL94 V-0, 非導電, 厚2.0) | 設計(未実装:Blender/図面未反映) |
| CP-13 | 黒メッシュフィルタ(ドーム内面追従の殻) | 1 | A5052 t1.0 枠+SUSメッシュ(#100) | 設計 |
| CP-14 | GPU低背ステー(下端支持, z5〜14) | 1 | A5052 t2.0 板金+POM当て(3mm) | 設計(U18: 実物ブラケット寸法) |
| CP-16 | ケーブルクリップ/コーム | 24 | POM/ナイロン(UL94 V-2以上) | 規格品 |
| CP-17 | アンビリカルハーネス(eDP/12V/USB, 全長380mm=経路約270+整備余長100) | 1 | 市販ケーブル+ロックコネクタ(型番U19) | 未選定(U19) |
| CP-18 | 保護接地(PE)系統 | 1 | AWG16 緑/黄ケーブル+M4リング端子+歯付座金+編組ストラップ6mm² | 設計(U41: 試験は有資格者) |
| CP-19 | 断熱シート/断熱スペーサ(トレイ-背板, パネル熱遮断) | 1 | 断熱シート t3 (エアロゲル/フェノールフォーム, k≤0.04W/mK) + PEEKブッシュ | 設計(U48) |
| CP-20 | 首振りステータ板 | 1 | A5052-H32 | PROPOSED(v9, 未試作) |
| CP-21 | 首振りロータ板 | 1 | A5052-H32 | PROPOSED(v9, 未試作) |
| CP-22 | ネック(基台+側板+タイプレート+前後カバー) | 1 | A6063-T5 | PROPOSED(v9, 未試作) |
| CP-23 | チルトバランサ(カム板+ローラ従動子+ダイスプリング2本+ストッパ用尾部レバー) | 1 | カム板 SUS440C HRC58 t10 / ローラ SUJ2 Ø12×12+ニードル軸受 / 案内ロッド Ø8×2 SUS630 H1025 / ばね座 SUS304 t2.7 / コイルばね OD20×線径4 k=80N/mm(市販品で実在するか未確認) / 尾部レバー SUS304 t5×幅14×長34 | PROPOSED(v9, 未試作) |
| CP-24 | ACコード引張逃がしクランプ(インレット背面) | 1 | PA66-GF30(難燃UL94 V-0)+SUSばね | PROPOSED(v9, 未試作) |
| CP-25 | ラジエーター吸気ダクト(外気のみをファンへ導く四方壁) | 1 | A5052-H32 t1.0(材質は仮置き。parts.json rad_duct は板厚のみ規定) | CANDIDATE(未採用。熱効果は未実証 R10E-001) |
| CP-26 | 首振りスカート(足固定の円筒外皮, 軸受を隠す) | 1 | A6063-T5 または A5052-H32 t2.0(板厚・材質は仮置き。同色アルマイト) | PROPOSED(v11, 形状のみ。CAD未登録=SHAPE-01) |
| CP-27 | ネックカラー(ネックと一緒に回る円筒カラー, ロータ上面を隠す) | 1 | A6063-T5 または A5052-H32 t2.0(仮置き。同色アルマイト) | PROPOSED(v11, 形状のみ。CAD未登録=SHAPE-01) |
| CP-28 | ネック外皮(ネック機構を覆う角丸の外皮) | 1 | A6063-T5 または A5052-H32 t2.0(仮置き。同色アルマイト) | PROPOSED(v11, 形状のみ。CAD未登録=SHAPE-01) |

## 3. 小物・締結(3D描画分 model/hardware_list.json。区分は procurement.json hw_class)

| 区分 | 行数 | 数量計 |
|---|---|---|
| 規格品(購入) | 12 | 70 |
| CP部品の構成要素(CP側で見積) | 16 | 47 |
| 特注・加工品でCP番号なし(要登録検討) | 6 | 20 |
| 購入品に付属 | 1 | 1 |
