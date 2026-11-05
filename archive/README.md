# archive/ — 過去の仕様書・設計図・モデルの保存場所

**ルール: 過去の仕様書・設計図・モデル・図面は削除しない。** 置き換える場合は、置き換え前の版を必ず `archive/` に残す(ファイル名に日付とコミットIDを付ける)。誤って削除した場合は、履歴から復元してここに戻す。

- `archive/<元のパス>/<名前>__<日付>_<コミット>.<拡張子>` : 同名ファイルの過去の版(現行版は元の場所にある)
- `archive/deleted/<元のパス>` : 削除されたファイルを、削除の直前の版から復元したもの

主な内容: 旧設計書(design.md の各版)、旧コンセプト図(concept.svg)、旧OpenSCADモデルとレンダリング(24型・旧ポッド版)、旧仕様(model/*.json の各版)。
復元コマンド例: `git show <コミット>:<パス> > <パス>`。


---
## 新方式 (v2): ファイルごとの版管理アーカイブ
各ディレクトリ直下の `archive/` に、ファイル単位で過去版を連番で保存する(`docs/archive/`, `drawings/archive/`, `model/archive/`, `cad/archive/`, `concept/archive/`, `render/archive/`, `tools/archive/` …)。

- `<dir>/archive/<名前>/<名前>.vNNN__<日付>_<commit>.<拡張子>` : 直近の版(current 世代)
- `<dir>/archive/gen-NNN/<名前>/…` : ロールアップ済みの古い世代(定期的に新世代へ移動)
- `<dir>/archive/INDEX.md`, `index.json` : 版の一覧(sha256付き)
- 自動化: `git commit` のたびに pre-commit フックが、更新されたファイルの**更新前の版**を自動保存(`tools/archive.py auto`)。フックは `tools/pre-commit.hook`(`.git/hooks/pre-commit` にコピー)。
- 手動: `python3 tools/archive.py snapshot <ファイル>` / `list` / `rollup --keep 3 --days 30`(古い版を新世代へ。**移動のみ、削除なし**)。
- 定期ロールアップ: 5時間ごとの再調査トリガーのたびに `rollup` を実行する。
- 上記の旧方式 `archive/<dir>/…__日付_commit.*` の46ファイルは、新方式へ版番号付きで取り込み済み(旧ファイルは履歴として残す)。
