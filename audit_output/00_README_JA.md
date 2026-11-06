# 監査・基盤改修パッケージ(imac / claude/imac-pc-design)

対象: このリポジトリ(Gitで620ファイル追跡。添付ZIPは存在せず、リポジトリを原本として扱った)。日付: 2026-11-06。
原本保全: 変更前はGit履歴+各ディレクトリ`archive/`に保持(削除なし。CP-15.svgは`drawings/parts/archive/CP-15/`へ退避)。

## 成果物
| ファイル | 内容 | 状態 |
|---|---|---|
| 01_FULL_FILE_MANIFEST.csv | 全追跡ファイルのパス/種別/サイズ/SHA-256/構文検査 | 自動生成(`tools/audit_manifest.py`)。内容レビュー列は全件`NO`=台帳登録のみで「検証済み」ではない |
| 03_FINDINGS_REGISTER.md | 指摘と状態(K01〜K25再判定+新規) | 手作成 |
| 12_TEST_RESULTS.txt | 品質ゲート実行ログ | `tools/run_gates.sh` |
| 14_ARCHITECTURE_DECISIONS.md | 現行維持/部分改修/全面再構築の比較と採用 | 手作成 |

## 再現
`tools/run_gates.sh`(旧値走査→fitcheck→cablemodel→cable_check→stability→台帳)。失敗は終了コード1。

## 限界(正直な範囲)
- 実機・実測・専門試験(耐電圧/ガラス強度/ヒンジ寿命/騒音/RF)は未実施=すべてUNVERIFIED/BLOCKED。
- 内部干渉は公称AABB+ケーブル中心線の検査であり、STEP/実測による合格ではない。
- 製造承認・通電承認・量産承認は**いずれも不可**(P0/P1未解決あり)。
