#!/usr/bin/env python3
"""公式/一次情報URLの取得可否を確認し、状態を表示する(以前403/429だったものが取得可能になったかの検知用)。
実行: python3 tools/check_sources.py  → 結果を docs/source-status.md に書き出す。"""
import subprocess, datetime, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS = {
 "U04 Noctua NH-L12S spec": "https://noctua.at/en/products/nh-l12s/specification",
 "U04 Noctua NH-L12S datasheet": "https://noctua.at/pub/media/blfa_files/infosheet/noctua_nh_l12s_datasheet_es_v3_web.pdf",
 "U05 AMD 9800X3D": "https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-7-9800x3d.html",
 "U06 ASUS RTX5060Ti techspec": "https://www.asus.com/motherboards-components/graphics-cards/dual/dual-rtx5060ti-o16g/techspec/",
 "U08 SilverStone FX600": "https://www.silverstonetek.com/en/product/info/power-supplies/FX600-G/",
 "U09 LINKUP riser": "https://www.linkup-connect.com/products/pcie-5-0-x16-riser-cable",
 "U10 Noctua NF-A12x25": "https://noctua.at/en/nf-a12x25-pwm/specification",
 "U11 Samsung 990 PRO HS datasheet": "https://download.semiconductor.samsung.com/resources/data-sheet/Samsung_NVMe_SSD_990_PRO_with_Heatsink_Datasheet_Rev_2.0_10129695053410.pdf",
 "U13 Data-Modul LM270WR3-SSC1": "https://data-modul.com/en/products/product-finder/find-your-tft-display/lm270wr3-ssc1",
 "U13 Data-Modul SSC1 spec pdf": "https://www.data-modul.com/sites/default/files/products/LM270WR3-SSC1-specification-12053487.pdf",
 "U16 ASUS X870-I spec": "https://rog.asus.com/motherboards/rog-strix/rog-strix-x870-i-gaming-wifi/spec/",
 "BOE N50 datasheet": "https://www.panelook.com/upload/202310/MV270QUM-N50_Ver.0_20210111_202310319200.pdf",
}
rows = []
for k, u in URLS.items():
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '-o', '/dev/null', '-w', '%{http_code} %{size_download}', '-A', 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36', u], capture_output=True, text=True)
    out = (r.stdout or r.stderr.strip()[:60] or 'ERR').strip(); rows.append((k, u, out))
    print(f"{out:>18}  {k}")
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
open(f'{R}/docs/source-status.md', 'w', encoding='utf-8').write(f"# 一次情報の取得可否 ({now})\n\n`200`=取得可能。403/429/503/証明書エラーは再試行対象。\n\n| 項目 | 結果(HTTP コード サイズ) | URL |\n|---|---|---|\n" + '\n'.join(f"| {k} | {o} | {u} |" for k, u, o in rows) + '\n')
