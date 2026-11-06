# docs/ 索引(現行: v9)

読み順: ①`spec/system-spec.md`(仕様の正本) → ②`mechanisms/`(特殊機構の専用設計書) → ③部品/BOM → ④解析 → ⑤監査/未確認。**[生成]**は `tools/` が出力する生成物で、手で直さず元データ(`model/*.json`)かスクリプトを直す。

## 1. 仕様(正本)
- [spec/system-spec.md](spec/system-spec.md) システム仕様 / [spec/design-philosophy.md](spec/design-philosophy.md) 設計哲学 / [spec/grounding-spec.md](spec/grounding-spec.md) 保護接地 / [spec/panel-driver.md](spec/panel-driver.md) / [spec/panel-thermal.md](spec/panel-thermal.md) / [spec/standard-parts.md](spec/standard-parts.md) 副資材

## 2. 特殊機構(専用設計書)[生成+手書き]
- [mechanisms/README.md](mechanisms/README.md): 01 チルトバランサ / 02 左右首振り / 03 ネック・ストッパ・荷重経路 / 04 ドーム着脱 / 05 トレイ吊り / 06 指挟み保護 / 07 はめあい・操作感
- 旧: [tilt-swivel-design.md](tilt-swivel-design.md)(チルト・首振りの設計経緯と付録A=旧ヒンジ設計) / [service-mechanisms.md](service-mechanisms.md) / [service-manual.md](service-manual.md) / [build-guide.md](build-guide.md)

## 3. 部品・BOM
- [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)(全ファイル要約・自動生成)
- [bom-final.md](bom-final.md)[生成] / [spec/custom-parts.md](spec/custom-parts.md)[生成] / [spec/hardware-list.md](spec/hardware-list.md)[生成] / [spec/joint-matrix.md](spec/joint-matrix.md)[生成] / [spec/hole-table.md](spec/hole-table.md)[生成] / [logo-catalog.md](logo-catalog.md)

## 4. 解析・配線(生成物)
- [thermal-analysis.md](thermal-analysis.md) / [joint-analysis.md](joint-analysis.md) / [failure-analysis.md](failure-analysis.md) / [wiring.md](wiring.md) / [spec/wiring-spec.md](spec/wiring-spec.md) / [fitcheck-report.txt](fitcheck-report.txt)

## 5. 調査
- [research-notes.md](research-notes.md)(旧 research / research-hinge / research-joints / research-cables を統合) / [spec/gaming-requirements.md](spec/gaming-requirements.md) / [spec/performance-benchmark.md](spec/performance-benchmark.md) / [spec/cost-estimate.md](spec/cost-estimate.md) / [anatomy.md](anatomy.md)

## 6. 監査・未確認
- [audit-criteria.md](audit-criteria.md) / [audit-log.md](audit-log.md) / [unverified-tracker.md](unverified-tracker.md) / [source-status.md](source-status.md)[生成] / `../audit_output/`(台帳・指摘一覧・アーキテクチャ決定)

## 7. 履歴
- [design.md](design.md)(v4の旧設計。冒頭に「旧版」注記) / `*/archive/`(ファイル別・版番号付き。**削除せず**移動のみ。`tools/archive.py`)。退避した文書: design-v6, selection-v5, bom-verified, research(統合), model-pipeline, hinge-design(付録Aへ統合), design-package-index(本書に置換)。

## 8. 提出物・検証
- `../handoff/`(業者提出一式) / `../tools/run_gates.sh`(品質ゲート一括実行)
