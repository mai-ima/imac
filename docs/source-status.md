# 一次情報の取得可否 (2026-11-03 13:46)

`200`=取得可能。403/429/503/証明書エラーは再試行対象。

| 項目 | 結果(HTTP コード サイズ) | URL |
|---|---|---|
| U04 Noctua NH-L12S spec | 429 40671 | https://noctua.at/en/products/nh-l12s/specification |
| U04 Noctua NH-L12S datasheet | 429 40679 | https://noctua.at/pub/media/blfa_files/infosheet/noctua_nh_l12s_datasheet_es_v3_web.pdf |
| U05 AMD 9800X3D | 200 202686 | https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-7-9800x3d.html |
| U06 ASUS RTX5060Ti techspec | 200 341615 | https://www.asus.com/motherboards-components/graphics-cards/dual/dual-rtx5060ti-o16g/techspec/ |
| U08 SilverStone FX600 | 200 366 | https://www.silverstonetek.com/en/product/info/power-supplies/FX600-G/ |
| U09 LINKUP riser | 000 0 | https://www.linkup-connect.com/products/pcie-5-0-x16-riser-cable |
| U10 Noctua NF-A12x25 | 429 40671 | https://noctua.at/en/nf-a12x25-pwm/specification |
| U11 Samsung 990 PRO HS datasheet | 200 268920 | https://download.semiconductor.samsung.com/resources/data-sheet/Samsung_NVMe_SSD_990_PRO_with_Heatsink_Datasheet_Rev_2.0_10129695053410.pdf |
| U13 Data-Modul LM270WR3-SSC1 | 000 0 | https://data-modul.com/en/products/product-finder/find-your-tft-display/lm270wr3-ssc1 |
| U13 Data-Modul SSC1 spec pdf | 403 308 | https://www.data-modul.com/sites/default/files/products/LM270WR3-SSC1-specification-12053487.pdf |
| U16 ASUS X870-I spec | 200 228306 | https://rog.asus.com/motherboards/rog-strix/rog-strix-x870-i-gaming-wifi/spec/ |
| BOE N50 datasheet | 200 1173319 | https://www.panelook.com/upload/202310/MV270QUM-N50_Ver.0_20210111_202310319200.pdf |

## 追記 2026-11-05 (現行部品の取得状況, サブエージェント監査)
- 取得できた: ASUS X870-I spec/GPU techspec、NVIDIA RTX5060比較表、ARCTIC 2D図面/Spec(A-RGB)、Samsung 990 PRO HSデータシート、Panelook BOE N50 PDF、Noctua NF-A12x25 仕様ページ(検索経由)。
- 取得できない: Corsair(403), Data-Modul(503/403), AMD(WebFetch 503→検索スニペット), ASUS CPUサポートリスト, LINKUP公式。旧部品(NH-L12S, FX600)の行は不採用。
