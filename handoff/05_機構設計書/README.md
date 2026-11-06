# 特殊機構の専用設計書(docs/mechanisms/)

| 番号 | 機構 | 主な部品/コード |
|---|---|---|
| 01 | [チルトバランサ](01_tilt_balancer.md) | 尾部レバー・ダイスプリング・摩擦ヒンジ / `tools/balance_calc.py` |
| 02 | [左右首振り](02_swivel.md) | クロスローラ軸受・摩擦リング・ストッパ・PE編組 / `tools/swivel_calc.py`, `stability.py` |
| 03 | [ネック構造・ストッパ・荷重経路](03_neck_and_load_path.md) | 基台・側板・タイプレート・前後カバー / `motion_check.py`, `strength_check.py` |
| 04 | [背面ドーム着脱](04_dome_latch_gasket.md) | ラッチ・フック・ピン・磁石・EMIガスケット / `dfm_check.py` |
| 05 | [トレイ吊りと引き出し](05_tray_hanging_service.md) | キーホール・SUSブッシュ・拘束ネジ・アンビリカル |
| 06 | [指挟み保護(蛇腹ブーツ)](06_pinch_guard.md) | シリコーン蛇腹ブーツ / `motion_check.py` |

これらは `tools/gen_mechanisms.py` が生成する(手で直さず、model/*.json か tools の計算を直す)。単一源: `model/spec.json`(hinge/swivel/neck/stand)、`model/balance.json`、`model/custom_parts.json`。
