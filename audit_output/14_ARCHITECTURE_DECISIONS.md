# アーキテクチャ決定(ADR-001)
選択肢: (A)現行延命 (B)部分改修+検証基盤の追加 (C)データモデル/生成器の全面再構築。
採用: **B**。理由: model/*.jsonを単一源とする生成パイプライン(spec/layout/parts/custom_parts/cables→docs/drawings/Blender/GLB/viewer)は機能しており、欠陥の主因は「旧値の無言残存」と「偽PASS」。全面再構築は工数大でリスク>効果。
追加した基盤: `tools/stale_check.py`(旧値・不変条件ゲート), `tools/audit_manifest.py`(全ファイル台帳+SHA-256), `tools/run_gates.sh`(ゲート一括), fitcheckの`unv()`(UNVERIFIED計上), cable_checkの小物障害物。
撤回条件: JSONスキーマ化(単位・座標系・ID)を要するほど不整合が再発する場合は(C)へ移行。
未実施(次): JSON Schema導入、生成器と検証器の完全分離、Pydantic化、CI(GitHub Actions)。
