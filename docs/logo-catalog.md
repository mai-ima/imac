# ロゴ・刻印・意匠カタログ (公式製品画像から目視で確認)

方針: 見つかるまで調べ続ける。公式画像を取得して目視で確認できた項目だけを「確認済」とし、画像そのもの(著作物)はリポジトリに含めず、URLと観察結果のみ記録する。ブランドのロゴは図形そのものを再掲せず、**文字表記(ワードマーク)と配置で再現**する。

## 確認済

### AMD Ryzen 7 9800X3D (IHS刻印)
- 出典画像: [AMD公式 製品画像](https://www.amd.com/content/dam/amd/en/images/products/processors/ryzen/2900400-ryzen-7-9800x3d.jpg)
- IHS(ヒートスプレッダ)中央に **「AMD」と「RYZEN」の2行**、灰色のサテン仕上げの正方形。パッケージは黒+オレンジの縁取り、**「7」**、「AMD 3D V-CACHE TECHNOLOGY」の帯。

### ASUS Dual GeForce RTX 5060 Ti 16GB OC
- 出典画像: [カード全体](https://dlcdnwebimgs.asus.com/files/media/5a253095-ba19-4d3b-a0d5-a9a66e80df72/v1/img/kv/pd.png) / [バックプレート](https://dlcdnwebimgs.asus.com/files/media/5a253095-ba19-4d3b-a0d5-a9a66e80df72/v1/img/cooling/backplate.png)
- **シュラウド**: 黒。**銀(白金色)の角ばった台形のアクセントパネルが2つ**(ファンの間と両端)。
- **ファン**: 黒い軸流ファン2基(長さ方向に並ぶ)。各ファン中心に**クロームのリング付きの円形ハブ**があり、**「ASUS」ロゴ(文字)**が刻まれている。
- **文字**: 側面の縁に縦書きで白い **「GEFORCE RTX」**、上部に輪郭だけの **「DUAL」**、下側ファン付近に縦書き **「ASUS」**。
- **補助電源**: 8ピンがカードの端(下側ファン側の縁)にあり、黒い切り欠きの中。
- **バックプレート**: **つや消しダークグレーの金属**。**六角形のエンブレム**(様式化されたロゴ)と、そこから伸びる**細い銀の線**(回路図風)、**三角形の通気口**(フィンが見える)、**ネジ(トルクス風)4〜5本**、PCIeの金メッキ端子と取付ブラケット(銀)。
- 備考: 実機でのロゴ位置の正確な座標は画像のパースのため未測定(カード長さ方向の比率で近似)。

### ASUS ROG STRIX X870-I GAMING WIFI
- 出典画像: [基板全体](https://dlcdnwebimgs.asus.com/files/media/eea81117-e480-4d63-acdb-b7fb5b1c3691/v1/img/kv/pd.png) / [別アングル](https://dlcdnwebimgs.asus.com/files/media/eea81117-e480-4d63-acdb-b7fb5b1c3691/v1/img/style/id-design.png)
- **向き**: I/O=左、PCIe=下、DIMM=右(マニュアルのレイアウト図と一致)。
- **PCB**: 黒。基板の右縁にオレンジ/金色のメッキ縁。
- **左のI/O側**: 背の高い黒いVRMヒートシンクとI/Oカバー。カバーに**ピクセル調の「ROG」風モチーフと「FOR THOSE WHO DARE」の刻印**(銀・黒のメッシュ柄)。
- **下辺のM.2/PCIeカバー**: **「ROG」と大きな「STRIX」(ピクセル書体)**の刻印、**クロームのリング形パーツ2つ**。
- **ソケット**: ニッケル色のAM5ソケットに**「AMD RYZEN」と「AM5」の刻印**、黒いバックプレート固定の4ボルト、ロードレバー。
- **シルク**: 縦書きの **「STRIX X870-I GAMING WIFI」**、**「R1.01」**、**「SF1S」**、「CPU_FAN」「AIO」「CHA_FAN」「PCIEX16(G5)」「DIMM_A」「TX_PWR」等の端子名。
- **24ピン**: 右上、黒い大型コネクタ。DIMMスロットは2本の黒い細長いスロット。

## 調査中(取得できていない)
| 製品 | 次に試すこと |
|---|---|
| Samsung 990 PRO ヒートシンク付き | Samsung公式画像(半導体ページ)、製品ギャラリー |
| DDR5メモリ(型番確定後) | 各社公式製品画像 |
| 水冷AIO・電源(選定中) | 選定後に各社公式画像 |
| Noctua NF-A12x25 | Noctua公式画像(429の場合は再試行) |
| パネル背面ラベル・制御基板 | Panelook画像、Data-Modul |

### Samsung 990 PRO with Heatsink 1TB (MZ-V9P1T0CW)
- 出典画像(Samsung公式 NZ製品ギャラリー): `https://images.samsung.com/is/image/samsung/p6pim/nz/mz-v9p1t0cw/gallery/nz-990-pro-with-heatsink-nvme-m2-ssd-mz-v9p1t0cw-534155635` 〜 `...-534155640`(番号違いで6枚)
- **ヒートシンク(上面)**: 黒。**赤いスリット(斜めの平行な溝)が左上寄りに約6本**、右下寄りに別に約4本の小さな赤いスリット群。**「SAMSUNG」**の灰色ワードマークが左下寄り。
- **裏面ラベル(黒地)**: **「SAMSUNG」**(左上)、**「990 PRO」**(「PRO」が赤)、赤い下線、**「with Heatsink」**、**「PCIe 4.0 NVMe M.2 SSD」**、大きな **「1TB」**、右側に**適合マーク類(UKCA / CE / KC / UL / 認証マーク)**、最下部に小さな注意書き(SAMSUNG PO BOX..., WARNING 等)。
- **端部**: 左端にM.2固定ネジ用の半円の切り欠き、右端に金メッキ端子。

### ARCTIC Liquid Freezer III Pro 240 (公式仕様・図面)
- 出典: [仕様書](https://www.arctic.de/media/8d/19/d2/1744191002/Spec_Sheet_Liquid_Freezer_III_Pro_240_A-RGB_EN.pdf) / [2D図面](https://support.arctic.de/products/liquid-freezer-iii-pro-240-argb/techdocs/LF3%20Pro%20240%20ARGB%202D%20Drawing.pdf)
- ラジエーター 277×120×38mm(アルミ)、ファン厚25mm(合計 約63mm)、ポンプ 108.47×Ø91×68.5mm(VRMファン含む)、ホース450mm(外径12.4/内径6.0)、重量1665g、保証6年、AM5対応。ロゴ/刻印の意匠は未確認(画像取得予定)。
