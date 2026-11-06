# プロジェクト要約(自動生成 2026-11-06)

`tools/gen_project_summary.py` が全ファイルを走査して生成。手で直さない。

## 1. 現行の主要数値(model/spec.json)
- 本体: 幅620.0mm×スラブ厚25.0mm、ドーム総厚190mm(内奥行162.0mm。ポンプ垂直出口ホース用)
- スタンド: 足360×310mm、ballast 3.5kg、チルト-15〜+40°、首振り±60°、ヒンジ軸 z=45.0
- バランサ: s=66 e=25 最長側355N/本 p=0.5、摩擦保持5.8N·m±8%、操作力目標≦25N
- 未確認事項(U台帳): 60件(docs/unverified-tracker.md)

## 2. ファイル構成(git追跡 1027件 = 現行 298 + 履歴archive 729)

| ディレクトリ | 現行件数 | 役割 |
|---|---|---|
| (root) | 1 |  |
| audit_output | 5 | 監査台帳・指摘一覧 |
| blender | 23 | 3Dモデル生成(build_imac_pc_v8.py/hardware_v8.py) |
| cad | 1 | OpenSCAD |
| concept | 3 | コンセプト画像 |
| docs | 53 | 仕様・設計書・調査・監査記録 |
| drawings | 44 | 図面(SVG/DXF/PDF入力) |
| handoff | 67 | 業者提出パッケージ |
| model | 14 | 単一源データ(spec/layout/parts/custom_parts/balance/pump/cables…) |
| render | 37 | レンダリング画像 |
| tools | 47 | 生成器・計算・検査ゲート |
| viewer | 3 | Three.jsビューア+GLB |

## 3. 主要ファイル(一行要約)

### tools/

- `archive.py` — 版管理アーカイブ。各ディレクトリ直下の archive/ に、ファイルごとの過去版を連番(vNNN)で保存する。
- `audit_manifest.py` — 全ファイル台帳(SHA-256/種別/役割/検証状態)を audit_output/01_FULL_FILE_MANIFEST.csv に出力。
- `balance_calc.py` — チルト・バランサ(圧縮ダイスプリング2本+ヒンジ尾部レバー)の寸法探索とゲート。
- `cable_check.py` — 配線の干渉・曲げ半径・長さの検査。部品(layout AABB)との貫通、ケーブル同士の近接、折れ角の曲げ半径(外接円)を判定する。
- `cablemodel.py` — 配線・ホースの経路定義(単一情報源)。layout.json から座標を導き、model/cables.json を出力する。
- `cadviews.py` — cadquery の HLR(隠線処理)で実形状から正投影の線画(見える線/隠れ線)を取り出し、A3図面SVGへ配置する共通部品。
- `check_sources.py` — 公式/一次情報URLの取得可否を確認し、状態を表示する(以前403/429だったものが取得可能になったかの検知用)。
- `dfm_check.py` — 加工成立性(DFM)の簡易ゲート: 薄板への溝/ポケットの残肉 ≥ min_residual を custom_parts.json の dfm 値で検査(CP-07)。
- `drawlib.py` — 業界標準(ISO)準拠の図枠/表題欄ライブラリ。
- `fit_tolerance.py` — 機構の「ゆるゆる/硬すぎ」ゲート: 各インタフェースの公差(IT級・摩擦係数・ばね荷重・圧縮量)を最悪ケースで振り、遊び/操作力/保持力が許容窓に入るかを判定する。
- `fitcheck.py` — 市販部品だけで成立するかの機械チェック(収まり・干渉・電力・風量)。 実行: python3 tools/fitcheck.py
- `gen_anatomy.py` — 実機 iMac(24") の部位・配置図 (公式画像・Apple修理資料・iFixit系報道に基づく)。
- `gen_cad_drawings.py` — 実形状(cadquery)から正投影(第三角法)の図面を生成する: 外部設計図(ARCTIC 2D図面/ASUSマニュアル図)と同水準=多面図+寸法+部品表+題名欄。
- `gen_drawing.py` — cad/imac_like_pc.scad と同じ寸法から 設計図SVG を生成する (単位 mm)。
- `gen_fmea.py` — 故障モード影響解析(FMEA)表を生成する: docs/failure-analysis.md。S=影響度, O=発生頻度, D=検出困難度(1〜10, 設計時の主観評価: 試験で更新)。RPN=S*O*D。
- `gen_handoff.py` — 業者提出パッケージ(handoff/)の生成。実行: /tmp/bl/.venv/bin/python tools/gen_handoff.py(cadquery/openpyxl が必要)
- `gen_hardware_list.py` — model/hardware_list.json(blender/hardware_v8.py が出力)から docs/spec/hardware-list.md を生成する。手書きしない(旧値の残存防止)。
- `gen_mechanisms.py` — 特殊機構の専用設計書を docs/mechanisms/*.md に生成する(数値は model/*.json と tools/*_calc.py の出力から埋め込み、手書きの旧値を残さない)。
- `gen_mfg_drawings.py` — 自作する外装の製造図面を model/spec.json から生成する(DXF + 寸法入りSVG)。
- `gen_package.py` — 設計図一式(基板配置・寸法入り配置図・断面・配線図・エアフロー・分解組立・BOM)を model/*.json から生成する。
- `gen_project_summary.py` — 全(現行)ファイルを走査して docs/PROJECT-SUMMARY.md を生成する: ディレクトリ別の役割と件数、主要ファイルの一行要約、現行の主要数値(spec.jsonから)、未確認件数、ゲート結果。
- `gen_service_drawings.py` — 整備機構の図面(SVG)を model/spec.json と model/layout.json から生成する。
- `gen_specs.py` — 仕様書一式の生成: docs/spec/*.md, drawings/parts/CP-*.svg, drawings/16_cable_clips.svg。
- `guard_no_delete.sh` — 過去の仕様書・設計図・図面・モデルの削除を禁止するガード(pre-commitフックから呼ぶ)。
- `joint_calc.py` — 接合部・ヒンジ・熱膨張などの強度/トルク概算(v6質量見積り)。出力: docs/joint-analysis.md
- `layout_search.py` — ドーム傾斜制約付きの配置探索。部品の長方形(x,y)を乱択+局所探索で配置し、制約を満たす案を出力する。
- `massmodel.py` — 質量・重心モデル(単一情報源)。layout.json の位置から重心を導出する。質量は部品カタログ/推定(未実測, U25)。
- `motion_check.py` — 可動範囲の干渉検査: チルト(ヒンジ軸まわり)×首振り(垂直軸まわり)の全格子で、頭部の包絡(スラブ+ドーム、安全側の直方体)と
- `neckgeom.py` — ネックのストッパ幾何を導出して model/spec.json の neck に書き戻す(--write)。入力: lever_len/lever_w/lever_t/pad_thick と チルト端、出力: パッド・タ
- `power_budget.py` — 電力収支(単一源): シナリオ別に DC負荷 → PSU損失 → AC入力 を同じ式で求め、筐体内で熱になる総量=AC入力(保存則)を検査する。
- `run_gates.sh` — 品質ゲート一括実行(失敗を隠さない)。順序: 正規データ→計算→独立検証→台帳
- `stability.py` — 転倒安定性(v9: チルト×首振りの全格子)。質量/重心は tools/massmodel.py(layout由来, 推定)。
- `stale_check.py` — 品質ゲート: 現行ファイル(archive除く)に旧値/廃止物が残っていないか、正規データ間の不変条件が成り立つかを検査。
- `strength_check.py` — 簡易強度ゲート(手計算級の概算。FEA・疲労・実材料データの代替ではない)。許容応力=降伏/安全率1.5。荷重ケース: バランサ最大ばね力、画面上端50N押し(ストッパ/首振りストッパ)、頭部重量。
- `swivel_calc.py` — 首振り軸受の要求仕様(静荷重+操作荷重+衝撃)と操作力・ストッパ荷重の概算。軸受の実定格(spec.swivel.bearing_moment_rating_Nm)が未設定なら UNVERIFIED。
- `sync_wallpaper.py` — spec.json の wallpaper を viewer/index.html の /*WALL*/ ... /*ENDWALL*/ に埋め込む(単一源の同期)。
- `thermal_calc.py` — 部品別の熱概算(再循環を含む簡易モデル) → docs/thermal-analysis.md。数値は公開仕様+仮定。CFD/実測で置換すること。

### model/

- `b650iax_layout.json`
- `balance.json`
- `cables.json`
- `custom_parts.json`
- `hardware_list.json`
- `layout.json`
- `layout_dome.json`
- `layout_v4_archive.json`
- `parts.json`
- `parts_v4_archive.json`
- `pe_braids.json`
- `pump.json`
- `spec.json`
- `x870i_layout.json`

### docs/

- `PROJECT-SUMMARY.md` — プロジェクト要約(自動生成 2026-11-06)
- `README.md` — docs/ 索引(現行: v9)
- `anatomy.md` — iMac 24インチ 部位と配置
- `audit-criteria.md` — 監査基準 (厳格版)
- `audit-log.md` — 監査ログ (写実性・実在品の再現度)
- `bom-final.md` — 部品表 BOM(自動生成: tools/gen_package.py / 元データ model/parts.json)
- `bom-verified.md` — （統合済み・移転）
- `build-guide.md` — 製作ガイド(自作部品の作り方・調達・組立・試験)
- `design-package-index.md` — （統合済み・移転）
- `design-v6.md` — （統合済み・移転）
- `design.md` — iMac風 一体型ゲーミングPC 設計書 (v4: 全て市販品/外装のみ特注)
- `failure-analysis.md` — 故障モード影響解析 (FMEA) (自動生成: tools/gen_fmea.py)
- `hinge-design.md` — （統合済み・移転）
- `joint-analysis.md` — 接合部・ヒンジ・強度の概算 (自動生成: tools/joint_calc.py)
- `logo-catalog.md` — ロゴ・刻印・意匠カタログ (公式製品画像から目視で確認)
- `model-pipeline.md` — （統合済み・移転）
- `research-cables.md` — （統合済み・移転）
- `research-hinge.md` — （統合済み・移転）
- `research-joints.md` — （統合済み・移転）
- `research-notes.md` — 調査ノート(統合版)
- `research.md` — （統合済み・移転）
- `selection-v5.md` — （統合済み・移転）
- `service-manual.md` — 整備マニュアル v7(設計段階の手順書)
- `service-mechanisms.md` — 取り外し・整備機構の設計 (v7, 2026-11-05 全面改訂)
- `source-status.md` — 一次情報の取得可否 (2026-11-03 13:46)
- `thermal-analysis.md` — 熱解析(部品別・再循環モデル) (自動生成: tools/thermal_calc.py)
- `tilt-swivel-design.md` — チルト拡大・左右首振り(v9)設計 — 自動生成物を含む
- `unverified-tracker.md` — 未確認項目の台帳 (定期的に再調査して更新する)
- `wiring.md` — 配線表(自動生成: tools/gen_package.py)

### docs/mechanisms/

- `01_tilt_balancer.md` — 01 チルトバランサ(ダイスプリング+尾部レバー+摩擦ヒンジ)
- `02_swivel.md` — 02 左右首振り機構(クロスローラ軸受+摩擦リング+角度ストッパ)
- `03_neck_and_load_path.md` — 03 ネック構造・ストッパ・荷重経路
- `04_dome_latch_gasket.md` — 04 背面ドームの着脱機構(ラッチ・フック・位置決め・磁石・EMIガスケット)
- `05_tray_hanging_service.md` — 05 サービストレイの吊り(キーホール)と引き出し
- `06_pinch_guard.md` — 06 指挟み保護(蛇腹ブーツ)
- `07_fits_and_feel.md` — 07 はめあい・操作感の許容窓(「ゆるゆる」でも「硬すぎ」でもない)
- `README.md` — 特殊機構の専用設計書(docs/mechanisms/)

### docs/spec/

- `README.md` — 仕様書一式 索引 (v7)
- `cost-estimate.md` — 価格調査と予算 (2026-11-06, サブエージェント調査。国内実売を直接確認できた項目は少なく大半UNVERIFIED)
- `custom-parts.md` — 特注部品 仕様書 (自動生成: tools/gen_specs.py / 元データ model/custom_parts.json)
- `design-philosophy.md` — デザイン思想と設計規則 (Appleのデザイン哲学をオマージュ) v7
- `gaming-requirements.md` — ゲーム性能要件とGPU選定 (2026-11-06, サブエージェント調査。主要レビュー本文(TechPowerUp/Tom's/DF/GN)は取得不可のため暫定)
- `grounding-spec.md` — 保護接地(PE)・EMC・静電気 仕様 v7
- `hardware-list.md` — 小部品を含む全部品一覧 (自動生成: blender/hardware_v8.py → model/hardware_list.json → tools/gen_hardware_list.py)
- `hole-table.md` — 穴・開口の座標表 (自動生成: tools/gen_mfg_drawings.py)
- `joint-matrix.md` — 接合マトリクス (自動生成: tools/gen_specs.py)
- `panel-driver.md` — パネル駆動(コントローラ基板)仕様と採用ゲート — 監査C-10対応
- `panel-thermal.md` — パネル熱破損リスクと熱設計 (2026-11-06, サブエージェント調査+設計反映)
- `performance-benchmark.md` — 性能比較: 現行 iMac (Apple M6) と本PC (2026-11-05 調査, サブエージェント: 報道/集計値ベース)
- `standard-parts.md` — 標準部品・副資材リスト(BOM補遺, v7) — 監査B-11対応
- `system-spec.md` — システム仕様書 v7 (2026-11-05)
- `wiring-spec.md` — 内部配線仕様 (自動生成: tools/gen_specs.py / 元データ model/cables.json)

### blender/

- `audit_renders.sh` — 監査用の中解像度レンダリング(約5分)。出力: render/audit/
- `build_imac_pc.py` — iMac風 一体型ゲーミングPC の Blender(Cycles) モデル + レンダリング。
- `build_imac_pc_v6.py` — iMac風 一体型ゲーミングPC の Blender(Cycles) モデル + レンダリング。
- `build_imac_pc_v8.py` — iMac風 一体型ゲーミングPC の Blender(Cycles) モデル + レンダリング。
- `hardware_v8.py`
- `render_all.sh` — 高品質レンダリング一式 (Cycles / CPU)。前提: bpy モジュール入りの Python (例: uv venv --python 3.11 && uv pip install bpy pillow)

