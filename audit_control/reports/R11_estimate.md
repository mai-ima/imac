# R11 見積・費用・BOM・RFQ 監査(2026-11-07)
基準: 製造業者へ提出できる実務水準のRFQ。照合は `python3 tools/check_estimate.py`(新規)で機械化。価格は根拠が無いものを全て UNVERIFIED とした。

| ID | 重大度 | ファイル | 問題 | 対応 |
|---|---|---|---|---|
| EST-001 | P0 | handoff/00_見積依頼書.md, tools/gen_handoff.py | RFQに ロット3段階(1/10/100)・図番ごとの表面処理/公差/検査/納期/納品/梱包/秘密保持/見積回答様式が無い(数量「試作1台+3台・10台の目安」のみ) | 修正済み(RFQ全面再構成、共通条件§3、部品別(a)仕様(b)工法・検査・回答欄、回答様式CSV/xlsx) |
| EST-002 | P0 | docs/spec/cost-estimate.md | 旧構成(SF750/RTX5060Ti)の価格を足した「約35.1万円」が現行BOMの根拠に見えた。出典URL・調査日・確度が欄として無い。手書き | 修正済み(tools/gen_estimate.py で生成。単価2点のみ=REFERENCE、総額は算出不能と明記、旧価格は別表) |
| EST-003 | P0 | handoff/00_見積依頼書.md | 現行モデルで増えた特注部品(吸気ダクト・首振りスカート・ネックカラー・ネック外皮)がBOM/RFQに無い。parts.json rad_duct は「CP-25予定」のまま未登録 | 修正済み(model/custom_parts.json に CP-25〜28 を登録。CP-25=ダクト(CANDIDATE)/26=スカート/27=カラー/28=ネック外皮。板厚t2.0・固定方法は仮置きと明記) |
| EST-004 | P1 | tools/gen_handoff.py(RFQ§5) | DFM文のカム板が「SUS304 t6」で、現行(SUS440C HRC58 t10, spec.hinge.balance_cam)と食い違い(docs/spec/hardware-list.md にも同旧値) | 修正済み(RFQ文をspecから生成。hardware-list.mdはgen_hardware_list再実行。hardware_list.json自体はblender生成のため未再生成) |
| EST-005 | P1 | docs/bom-final.md, tools/gen_package.py | ctrl基板の外形が55x150x15で parts.json(55x110x15)と不一致(生成物が古い)。数量・型番・価格確度列が無い。radiatorがcoolerと同一製品なのに別行(二重計上の恐れ) | 修正済み(gen_estimate.py に移管、radiator数量0明記、gen_packageはbom-final出力を停止) |
| EST-006 | P1 | drawings/15_bom_sheet.svg, tools/gen_package.py | BOM図が `if y>232: break` で特注部品を黙って切り捨て(CP-24付近)。数量が全て「1」固定 | 修正済み(行間詰め、切り捨てはassert、数量はprocurement由来。当該図のみ再生成) |
| EST-007 | P1 | handoff/01_BOM_purchased.csv | 主要仕様がJSON文字列の300字切り(途中で壊れる)。型番/数量/単価/出典URL/調査日/確度の列が無い | 修正済み(列追加、境界で省略) |
| EST-008 | P1 | model/parts.json psu | PSU SF1000の出典URLが SF750 のページ(寸法のみ同一想定) | 未修正(parts.jsonは調査領域。procurementとcost-estimateに「SF1000の出典ではない」と明記。UNVERIFIED U47) |
| EST-009 | P1 | model/procurement.json board | 基板価格71,478円はモノタロウ参考値でURL未記録 | UNVERIFIED(REFERENCE扱いに格下げ。再確認要) |
| EST-010 | P1 | model/procurement.json cpu | 108,380円は gaming-st.com 2026-10-25 でURL未記録、調査日2週間前 | UNVERIFIED(REFERENCE) |
| EST-011 | P1 | model/procurement.json | GPU/PSU/冷却/SSD/RAM/ライザー/パネル/ctrl基板/AC口/カメラの国内価格が全て未取得 | UNVERIFIED(推測で埋めず null。未取得10点を明記) |
| EST-012 | P1 | model/procurement.json | 型番未確定で発注不可: ctrl_board, ram, ac_inlet, camera_audio, gpu(U46), riser(直線/右角未決) | 未修正(発注可否列で明示。選定は設計側) |
| EST-013 | P2 | docs/spec/cost-estimate.md | iMac M6の249,800円/289,800円は一次再確認なし | UNVERIFIED(出典Gizmodo報道と明記) |
| EST-014 | P1 | model/custom_parts.json CP-16 | ケーブルクリップ数量: CP-16=24、hardware_list(描画)=7、cables.json経路から再計算(端点除き約20、z≦30で16)と三者不一致 | 未修正(設計判断待ち。check_estimateのKNOWN-OPEN、RFQに暫定と明記) |
| EST-015 | P1 | model/hardware_list.json | CP番号なしの特注/加工品6系統(線材ハンドル、ストライク板、SPCC裏当て板、蛇腹ブーツ、ヒンジ軸Ø12 SUS303、ゴムストッパ/ロータタブ)がBOM/RFQの見積対象外 | 一部修正(RFQ§5に列挙し依頼元判断とした。CP登録は未実施=設計判断) |
| EST-016 | P2 | model/custom_parts.json | CP-08/09/16/17/18 の公差・表面処理が「-」 | 修正済み(「規格品のメーカー規格公差」「なし(規格品の標準仕上げ)」へ) |
| EST-017 | P2 | model/custom_parts.json CP-07 | 実穴パーフォレーション(貫通)の明記・穴数・開口率が無い | 修正済み(約11,300穴・開口率約33%・ウェブ1.6mm。平面投影の概算=UNVERIFIED。blender実装のØ2.4/ピッチ4.0とcheckで照合) |
| EST-018 | P2 | tools/gen_handoff.py | 高さ415.3mm・色数・STEP一覧・CP範囲がハードコード | 修正済み(spec/ファイル一覧/CP配列から生成) |
| EST-019 | P2 | handoff/00_見積依頼書.md | カム板・ダイスプリング・外皮・ドーム等のSTEP未作成が一部のみ記載、CP-23のSTEPは尾部レバーのみ | 修正済み(同梱資料表に明記) |
| EST-020 | P2 | handoff/README.md | 部品図CP-01〜CP-24等の旧記述 | 修正済み |
| EST-021 | P2 | handoff/00_見積依頼書.md | NDA雛形・提出先・期日・納期の根拠が無い | UNVERIFIED(NDA雛形未作成、納期希望は未協議の仮置きと明記) |
| EST-022 | P2 | tools/gen_package.py出力(12_wiring_diagram, 11a, docs/wiring.md) | gen_packageを再実行するとリポジトリ現物と差異(W3長さ341 vs 313、W6文言等)=生成物が手修正されたか生成器が古い | 未修正(範囲外。両者の正を確認要。gen_packageは全体再実行せず15_bom_sheetのみ採用) |
| EST-023 | P2 | docs/spec/hardware-list.md | model/hardware_list.json と不一致(旧カム板仕様) | 修正済み(再生成) |
| EST-024 | P2 | tools/check_estimate.py(新規), tools/run_gates.sh | BOM・見積・model・docs の機械照合が無かった | 修正済み(ID/数量/ロット個数/材質/価格出典/金額混入/小物↔CP/spec寸法を照合し run_gates に追加。KNOWN-OPENは exit 2) |
| EST-025 | P2 | model/custom_parts.json CP-26〜28 | 外皮の板厚・材質・固定方法・質量は仮置き(spec未登録、カラー長11.0はblender内定数) | UNVERIFIED(各CPの open に明記。spec.json への登録は未実施) |
| EST-026 | P3 | handoff/00_見積依頼書.pdf | 旧PDFの生成手順が文書化されていない | 修正済み(Playwrightで html→A3横PDF。手順は本報告のみ。handoff_build.shには未追加) |
| EST-027 | P2 | 台帳 | 台帳(tasks.json)への登録は禁止指示のため未実施 | 未修正(親が EST-001〜027 を登録) |

## 照合結果
`python3 tools/check_estimate.py` → FAIL 0 / KNOWN-OPEN 1(EST-014) / CP 27 / 購入品 14 / 小物 35。stale_check FAIL 0、unittest OK。
