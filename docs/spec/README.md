# 仕様書一式 索引 (v7)
| 文書 | 内容 |
|---|---|
| system-spec.md | システム/性能/外形/信頼性の総合仕様 |
| custom-parts.md | 特注部品CP-01〜17の個別仕様(材質/加工/公差/表面/接合/試験) |
| joint-matrix.md | 全接合J01〜J18の方式・締付・脱着 |
| wiring-spec.md | 内部配線: ケーブル表、ピン割当、固定点座標、配線ルール |
| ../tilt-swivel-design.md | チルト機構 |
| ../joint-analysis.md | 強度/トルク概算 |
| ../failure-analysis.md | FMEA |
| ../service-manual.md | 整備手順 |
| ../build-guide.md | 製作/組立/試験 |
| 図面 | drawings/01〜16, drawings/parts/CP-*.svg(各部品図) |
生成: tools/gen_specs.py, gen_package.py, gen_mfg_drawings.py, gen_service_drawings.py, joint_calc.py, gen_fmea.py

## v8 追加
| 文書 | 内容 |
|---|---|
| gaming-requirements.md | ゲーム要件(Cyberpunk/CoD/Cities SK2 4K快適)とGPU選定 |
| panel-thermal.md | パネル熱破損リスクと熱設計(断熱/空気層/トレイ分離/温度監視) |
| cost-estimate.md | 価格調査と予算(多くUNVERIFIED) |
| hardware-list.md | 3Dで描画している全小部品の一覧(ばね/ネジ/ラッチ/磁石/ピン等) |
| ../research-notes.md | ケーブル/ホースの曲げ・剛性調査 |
図面: drawings/*.svg は ISO 5457/7200/128/129/2768/5456-2 準拠の図枠(tools/drawlib.py)。配線: tools/cablemodel.py → model/cables.json、検査 tools/cable_check.py。
