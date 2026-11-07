# リポジトリ構成(責務・正本・生成物・archive)
| パス | 役割 | 区分 | 編集 |
|---|---|---|---|
| model/*.json | 設計の単一源(spec/parts/layout/custom_parts/cables/balance/pump/hardware_list…) | 正本 | 手編集可(balance.json/cables.json/hardware_list.json は生成) |
| tools/ | 計算・検証ゲート・生成器・台帳ツール | コード | 可 |
| tests/ | 不変条件・負例テスト(unittest) | コード | 可 |
| blender/ , viewer/ | 表示用モデル生成(bpy)・Webビューア(GLB base64) | 生成+ソース | build_*.py/hardware_v8.py/index.html のみ手編集 |
| drawings/ , handoff/ | 図面(SVG/DXF/PDF)・業者提出物 | 生成物 | 禁止(tools/handoff_build.sh で再生成) |
| docs/ | 仕様・設計書。docs/mechanisms・docs/PROJECT-SUMMARY.md・docs/fitcheck-report.txt は生成 | 混在 | 生成物は禁止 |
| audit_control/ | 台帳(tasks.json, file_coverage.csv, resolutions.json, ARCHIVE_INDEX.json, reports/) | 管理 | tools/task.py, ledger_import.py 経由 |
| archive/ , */archive/ | 旧版(実体は復元可能)。現行の検証入力にしない | 履歴 | 追記のみ |
| audit_output/ | 旧監査の出力(manifest は生成) | 履歴/生成 | 禁止 |
再生成順: model → tools/gen_* → tools/handoff_build.sh → blender export → viewer。ゲート: `bash tools/run_gates.sh`(exit 2=UNVERIFIED)。
