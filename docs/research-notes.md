# 調査ノート(統合版)

旧 research-hinge / research-joints / research-cables / research の4文書を統合した。元ファイルは各ディレクトリの archive/ に版付きで保存済み(削除していない)。出典の確度は各節のとおり(多くは UNVERIFIED。docs/unverified-tracker.md が台帳)。

## 1. ヒンジ・スタンド(旧 research-hinge.md)

## 保持トルク(調査側の計算, m=19kg, CG: 軸の背面側31mm/高さ190mm)
d(25°)=31cos25+190sin25=108.4mm → T=19×9.81×0.1084≈**20.2N·m**(0°:5.8、-5°:2.7、約-9°で符号反転 → **双方向(対称)の保持が必要**)。当方の概算(docs/joint-analysis.md, m=13.3kg, 軸をドーム中央z=63に置いた場合)は最大±7.5N·m。**差の原因: 質量(19 vs 13.3kg: 実測が必要)と軸位置(CGに対する前後オフセット)**。安全側として設計目標は 20N·m級を想定し、実測質量で確定する。

### 候補(全て単体では不足 → 並列または カウンターバランス併用)
| 候補 | トルク | 寿命 | 必要数(20.2N·m) | 状態 |
|---|---|---|---|---|
| Reell PHT-2.0/4.0/6.0(一方向) | 2/4/6 N·m | 20,000回(目標25,000に不足) | 4個(6N·m品) | https://reell.com/products/friction-hinges/pht |
| Reell PH35(一方向) | 5.65〜11.3 N·m | UNVERIFIED | 2個 | プレスリリースのみ(型番詳細UNVERIFIED) |
| Reell PHC / PHL(対称) | 0〜2.79 / 0.9〜3.4 N·m | 50,000回 | 6〜8個 | 補助摩擦として有望 https://reell.com/product-listings/phl |
| Sugatsune HG-T70S30(2軸) | チルト7N·m(±20%) | UNVERIFIED | 4個(公差考慮) | PDF https://www.sugatsune.com/content/site-assets/501_PDF/HG-T30S15_HG-T70S30.pdf |
| Southco ST-10E-440FJ-33 | 順4.97/逆2.93N·m(非対称) | UNVERIFIED | 5個以上 | monroeengineering掲載 |
| Misumi トルクヒンジ | 最大約5.9N·m | 2万回以上 | 不足 | https://th.misumi-ec.com/en/vona2/detail/221000129063 |
| Ergotron LX HD | UNVERIFIED | | 15kg耐荷重の確認不可 | 本体質量に不適合の可能性 |
Torqmaster/Humanscale/Hanwha/Mitsubishi、ガススプリング、定荷重ばね: UNVERIFIED(要追加調査)。

### Apple iMac(参考)
Apple公式(Late 2012 27")は奥行8in・21lb。チルトのみ(高さ/ピボット無し: HotHardware)。iFixit(EMC 2639)はヒンジが**ばね式**で、ばね保持の**樹脂キャップが劣化すると画面が落下**する(M5金属ワッシャで代替修理)。2012-2014の27インチでヒンジ不具合の事例。 → **教訓: ばね保持部品は金属製にし、寿命試験を行う**。 https://www.ifixit.com/Guide/iMac+Intel+27-Inch+EMC+2639+Hinge+spring+caps+Replacement/134707

## 2. 接合部・材料(旧 research-joints.md)

出典URLは各行。UNVERIFIED=未確認。設計への反映は docs/joint-analysis.md / docs/failure-analysis.md。

### 1. 締結部品
- PEM TSO/TSOA/TSOS(アルミ用TSOA)スタンドオフ: 板厚0.63mm〜対応、母材硬度上限HRB50/HB82(A5052-H32≈60HBで適合見込み)。t2.0は最小板厚を十分上回る。TSOA-M3-400/800/1200の存在確認。押抜き/トルクアウト値(t2.0)は UNVERIFIED(PEM技術部へ問合せ)。側荷重でクリンチ部破損の注意。 [PEM Standoff Tech Sheet](https://www.pemnet.com/wp-content/uploads/sites/2/2022/06/Standoff_Tech_Sheet.pdf), [TSOA-M3-800](https://devaws.pemnet.com/de/products/product-finder/tsoa-m3-800/)
- M3 Torx拘束ねじ: Essentra(303/316SUS, 10/16/40mm, ねじ掛かり2.0mm表記品あり, Eクリップ記載なし) [Essentra](https://www.essentracomponents.com/en-gb/p/captive-screws-button-head)、Accu(Torxノブ型) [Accu](https://accu-components.com/us/shop/precision-components/precision-screws/captive-panel-screws/metric-torx-knob-captive-panel-screws)。Southco ATCAはPhillipsでTorxではない。T10+Eクリップ品の品番とトルク上限は UNVERIFIED → **拘束ねじは「皿頭+ねじ山抜け止め(Eクリップ)」ではなく、板に圧入するキャプティブ品(Essentra等)へ設計変更を検討**。
### 2. 磁石
- N52 φ8×3の吸着力データは UNVERIFIED。参考: RS Eclipse 8×3(N35)=1.32kgf。K&JのN52 φ9.52×1.59は鋼板1枚2.62lb/両面鋼板10.65lbと試験条件で約4倍違う → 仕様は条件付きで確認。 [RS](https://uk.rs-online.com/web/p/neodymium-magnets/8734966), [K&J](https://www.kjmagnetics.com/d61-n52-neodymium-disc-magnet)
### 3. EMIガスケット(ファブリックオーバーフォーム)
- Parker Chomerics SOFT-SHIELD 3500: >100dB、**閉合力 <1 lb/inch(≈0.175 N/mm)**、圧縮永久歪み15%。 [Parker 3500](https://ph.parker.com/us/en/soft-shield-3500-plated-fabric-wrapped-foam)
- SOFT-SHIELD 3700(シリコーンフォーム): >100dB(100MHz–3GHz)、永久歪み<10%。 [Parker 3700](https://ph.parker.com/gb/en/37-131-1025-09600)
- SOFT-SHIELD 4800: 平均95dB(20MHz–10GHz)。 [4800](https://marianinc.com/wp-content/uploads/2025/08/Chomerics-SOFT-SHIELD-4800.pdf)
- Laird FoF: 1GHzで113dB、表面抵抗<0.07Ω/sq、圧縮30〜75%、永久歪み<20%。 [Mouser](https://www.mouser.jp/laird-fof-emi-shield-gaskets)
- Kitagawa/Tatsuta: UNVERIFIED。**→ 実在値「<1 lb/in ≈ 0.175N/mm」を joint_calc の閉合力計算に採用(外周約1900mmで最大約330N)。磁石12個では不足 → ラッチ増設が必要**。
### 4. ショルダーねじ
- Misumi: 軸径4〜20mm、公差g6/h7/e9。M3.5/M4の具体品番とせん断強度は UNVERIFIED。流通品の例: 肩径5mm M4で公差0/-0.025mm(Zoro)、McMaster M3ねじ肩径5mm頭径9mm頭高4mm。 [Misumi](https://pt.misumi-ec.com/vona2/detail/110300249320/?CAD=01), [McMaster](https://mcmaster.com/products/made-to-order-shoulder-screws)
- → 設計案の「M3.5肩ネジ・肩径4」は規格品に無い可能性。**M3ねじ・肩径5mm(McMaster系)またはMisumi肩径4/5mm品へ見直し**(キーホールの寸法を図面で更新)。
### 5. A5052-H32と陽極酸化
- 降伏≈193MPa(典型。規格最小は130MPa → 設計は最小値)、引張≈228–230MPa、疲労≈117–120MPa(5×10^8回)、伸び≈12%、硬度≈60HB。 [Aerospace Metals](https://www.aerospacemetals.com/wp-content/uploads/2023/06/Aluminum-5052-H32.pdf), [MakeItFrom](https://makeitfrom.com/material-properties/5052-H32-Aluminum)
- 陽極酸化皮膜は絶縁。接地部はマスクまたは導電処理(MIL-DTL-5541 Class 3相当)。ねじ穴内の皮膜でクリアランスが減る事例あり。 [anodizing.org](https://www.anodizing.org/page/military-spec-anodic-coatings), [finishing.com](https://finishing.com/599/69.shtml)
### 6. ガルバニック
- アノード指数: SUS18-8≈0.5–0.6V、Al≈0.9V(差0.3–0.4V、裸金属値)。許容差の目安0.15〜0.25V。接地のため皮膜を除去した箇所は裸Al×SUSとなり湿度で腐食の可能性(一般論)。 [Fastener Superstore](https://fastenersuperstore.com/blog/understanding-preventing-galvanic-corrosion), [Carr Lane](https://www.carrlane.com/engineering-resources/technical-information/galvanic-corrosion/design-considerations-for-galvanic-corrosion)

### 要確定(追加調査リスト → docs/unverified-tracker.md U25〜)
PEMクリンチ部押抜/トルク値(t2.0)、N52 8×3吸着力、拘束ねじ品番とトルク、ショルダーねじ品番・せん断強度、Kitagawa/Tatsuta、皮膜厚と接触抵抗。

## 3. ケーブル(旧 research-cables.md)

## 結論
公式の最小曲げ半径が取得できたのは少数(RG178/RG316同軸、12V-2x6のコネクタ直後)。他(ATX/EPS/PCIe、ライザー、AIOホース、eDP同軸、FFC)は**UNVERIFIED**で、設計では暫定値(docs/spec/wiring-spec.md, tools/cablemodel.py の mbr)を使い、**実物で確認するまで未確定**とする。
### 確認できた値
| 対象 | 値 | 出典 |
|---|---|---|
| 12V-2x6/12VHPWR(参考: 本機は8ピン使用) | コネクタから約35mm(Corsairは言語版で30〜40mm)は曲げない。装着後は左右方向に曲げない | CableMod/Seasonic/Corsair(wccftech, TechPowerUp) |
| RG178(SMA延長) | 外径約1.8mm: 静的10mm、反復18mm(50回)、動的27mm(Huber+Suhner)。Lapp: 固定6×OD、頻繁10×OD | Huber+Suhner/Lapp/L-com |
| RG316 | 約13〜15mm(L-com) | L-com |
| 同軸の一般則 | 外径の10倍以上(AS50881)、6倍の記載もあり | Lectromec |
| 多対銅ケーブル | 10×OD / 遮蔽付き鉱山ケーブル 6×OD(Wesco) | Lectromec/Wesco |
| FFC/FPC(基板の目安) | 静的: 厚みの約10倍、動的: 100〜200倍(IPC-2223引用、個別品は要データシート) | FLIR/PCBONLINE/JLCPCB |
| eDP極細同軸(I-PEX CABLINE-CA II) | AWG38, 45Ω。最小曲げ半径は公式UNVERIFIED | distyparts datasheet |
| ARCTIC LF III Pro 240ホース | 外径12.4/内径6.0/450mm(小売転載)。**曲げ半径UNVERIFIED** → 外径の6〜10倍=約75〜125mmを暫定採用(推定) | teqex/c2g |
| LINKUP AVA5(AG-P5-33SS-020BK-v2, 直線20cm) | 幅/厚/曲げ半径 UNVERIFIED。レビューで急な曲げは遮蔽に応力痕(60cm品)。**緩いS字まで**を前提 | heise/desertcart/GraphicsCardHub |
| SF750付属 ATX24/EPS/PCIe | 長さ300/400/400mm(Corsair SFキット表記)。AWG/剛性/半径 UNVERIFIED | Corsair CP-8920202 |
### 設計ルール(暫定=推定を含む)
1. 電源ケーブル(スリーブ16〜18AWG)はコネクタ後方に**直線15〜20mm**を確保し、曲げ半径は外径の3〜4倍(ATX24=30mm, EPS/PCIe=20mm)以上(**暫定**)。
2. AIOホースは半径**75mm以上**(6×OD, 暫定)。90°を超える折れ・S字の連続は避け、ポンプ/ラジエーターのコネクタ根元に曲げ荷重をかけない。
3. ライザーは緩いS字まで(半径は問合せ)。ツイスト禁止。
4. 同軸(SMAアンテナ延長 RG178)は静的10mm以上、整備で動かす箇所は27mm以上。
5. eDPアンビリカルは外径の6〜10倍以上、ロックコネクタ根元にストレインリリーフ。
6. すべて「曲げ半径の実物確認」を購入前チェックリストへ(U45)。
### 追加調査(未確認)
LINKUP AVA5実寸と曲げ半径、ARCTICホース曲げ半径、I-PEX/Hirose/JAE公式の最小曲げ半径と挿抜寿命、UL 758/IPC-WHMA-A-620原文、SF750ケーブルの実仕様(フラット/スリーブ/AWG)。

## 4. 実在iMacの調査(旧 research.md)

調査日: 2026-11-03。**公式を主、非公式は補助**。非公式情報は「独立した5件以上で一致」したものだけを確定扱いにした。

### A. 公式情報 (Apple)
| 項目 | 内容 | 出典 |
|---|---|---|
| 発表/発売 | 2026-10-27発表, 予約10-28(日本は10-29), 発売11-06 | Apple Newsroom(米) / Apple予約ページ |
| 価格 | 米: $1,499(10コア) / $1,699(12コア)。日本(税込, 報道): 249,800円 / 289,800円 | Apple Newsroom(米のみ記載) / ITmedia, ケータイWatch |
| チップ | M6。10C CPU+10C GPU / 12C+12C。Neural Engine 16コア×2、帯域170GB/s | apple.com/jp/imac/specs |
| ディスプレイ | 24"(実測23.5") 4480x2520 218ppi 500nit P3 True Tone。Nano-textureは12コアのみ | 同上 |
| ポート | 10コア: TB/USB4×2 / 12コア: TB4×4。3.5mm。2.5GbEは12コア標準 | 同上 / Newsroom |
| 無線 | Wi-Fi 7 / Bluetooth 6 / Thread(N1) | 同上 |
| 寸法 | 幅54.7cm 高さ46.1cm スタンド奥行14.7cm 幅13cm。**M4と同一数値** | 同上 / support.apple.com(M4: 121557) |
| 重量 | 4.42kg(10C) / 4.44kg(12C) | 同上 |
| 電源 | 143W 外付けACアダプタ, マグネット式コネクタ | 同上 |
| カメラ/音 | 12MPセンターフレーム, 3マイク, 6スピーカー(ウーファー2組+ツイーター2) | 同上 |
| 色(7色) | ブルー/パープル/ピンク/オレンジ/イエロー/グリーン/シルバー | 同上 |
| 修理構成(M4) | 修理マニュアル項目: ディスプレイ, スタンド, VESAアダプタ, USB-Cボード, ロジックボードカバー(EMIシールド), オーディオボード, ファン, Wi-Fi/BTアンテナ, カメラ, フレックスケーブル類, ロジックボード, バッテリー, 筐体 | support.apple.com/121518 |
| ファン(M4 4ポート) | 左右2基。ロジックボードの下に位置し、2基セットで交換 | support.apple.com/120967 |
| 公式に未記載 | 厚さ(M1〜M6とも公式仕様ページに記載なし), 消費電力, 内部配置図, M6のTDP | — |

### 公式画像から読み取ったデザイン (全7色の前面/背面/側面を取得して確認)
- 前面: 白に近い細ベゼル(全色共通 #EDEEF0)。画面下に**色付きの淡色チン**。上部中央にカメラ。
- 背面: 彩度の高い本体色。中央上寄りにロゴ。**左下に細い縦スロット4つ**(USB-C)。
- スタンド: 本体より淡い色の一枚板アルミ。背面に回転軸(ヒンジ)の丸い穴。側面から見ると傾斜した脚+薄い足板。画面はチルト調整可能。
- 実測色(公式画像から採取, 背面/スタンド/チン):
  青 #5882B2/#9EB2CD/#BACEE9, 紫 #8581B4/#ACA3C0/#C9C5E6, ピンク #E16280/#E7A9B6/#FFCFDB, オレンジ #E5734E/#F0B498/#FFCCAF, 黄 #EFD344/#DCCB97/#FDEEB7, 緑 #41965F/#A2BFAD/#B9D8C6, 銀 #D2D3D5/#BBBCBE/#D7D8DA。
- 前面ガラスの比率(銀の公式画像から測定): 本体 547x約375mm, 側/上ベゼル約10-12mm, チン約68mm。

### B. 非公式情報の検証 (独立5件以上の一致で確定)
注意: 内部構造の記事は**すべて 2021年M1 iMac の iFixit 分解を元にした報道**。M4/M6の分解記事は見つからず(M6のMac miniの分解のみ)。報道は互いに元ネタが同一なので「独立した確認」ではなく、**確定度は限定的**。
| 主張 | 一致した出典 | 件数 | 判定 |
|---|---|---|---|
| 本体の厚さ 約11.5mm | iFixit(M4ページ), APH Networks, Primetel, MacStories, MacRumors(M6ガイド, 「外観変更なし」) | 5 | **確定(M1〜M4。M6は同設計と報道のみ)**。Wikipediaは11mm(0.45in)と丸め表記 |
| ロジックボードは下部チン内 | iFixit, Macworld, MacRumors, 9to5Mac, apfelpatient | 5 | **確定(M1)** |
| ファン2基(上位構成)/ベースは1基 | iFixit, Macworld, MacRumors, 9to5Mac, apfelpatient, macandegg(+Apple公式ファンページ) | 6 | **確定** |
| 前面は一枚ガラス+接着(クラシックiMac接着剤) | iFixit, MacRumors, apfelpatient, macandegg, 9to5Mac | 5 | **確定** |
| ディスプレイ背後に大きな薄い金属プレートが2枚 | iFixit, Macworld, MacRumors, 9to5Mac, apfelpatient, macandegg | 6 | **確定** |
| そのプレートはスピーカー室 | iFixit, Macworld, macandegg(MacDailyNewsは放熱と推測) | 3 | 未確定 |
| ディスプレイ基板は上部の細いストリップ | iFixit, Macworld, MacDailyNews, GadgetGuy | 4 | 未確定(5未満) |
| 銅ヒートパイプ+短いヒートシンク2枚(上位構成) | iFixit, Macworld, MacRumors, apfelpatient, Wccftech | 5 | **確定(M1)** |
| Wi-Fi/BTアンテナはAppleロゴ裏が電波の通り道 | MacRumors, apfelpatient, 9to5Mac, MacDailyNews, Engadget | 5 | **確定(M1)** |
| メモリ/SSDは基板直付けで増設スロットなし | iFixit, Engadget, GadgetGuy, 9to5Mac, Apple公式仕様 | 5 | **確定** |
| ボタン電池2個 | iFixit, 9to5Mac, MacDailyNews, macandegg(+Apple部品表に『バッテリーボード』) | 4 | 未確定(電池基板の存在は公式) |
| ディスプレイはLG製の可能性 | iFixit のみ | 1 | 未確定 |
| M6 iMac の分解で内部構造が同じ | 見つからず | 0 | 不明 |
| M6の外観はM4から変更なし | MacRumors, Gizmodo(M4と見分け困難), Xataka(寸法/重量同一表), Apple仕様(寸法同一) | 4 | 未確定(厚さ非公表のため) |

### C. 取得できなかったもの
- 公式のiMac厚さ・内部配置、M6の分解、消費電力(TDP)。
- 一部サイトは403(AppleInsider, TweakTown, iPhone Wired)や404で本文未確認。検索結果の要約のみで、件数には入れていない。
- Apple Newsroom日本語ページは取得できず、米国版で確認。日本価格は報道ベース。

### D. 本設計への反映
- 色: 全7色の実測値を `cad/imac_like_pc.scad` の `color_scheme` に反映。
- 前面: 白ベゼル(#EDEEF0)+淡色チン、背面に細いスロット4つ(I/Oの見た目)。
- 厚さ: iMacは11.5mm。市販パネル+背面板では実現できず、**本機は前面14mm+背面ポッドで総厚70mm**。
- 内部構造は「チン内に小型基板+左右ファン」という公式/多数報道の方式と異なり、本機は市販ITX部品のため背面ポッドに集約。

