# 指摘台帳(2026-11-06時点。重大度P0〜P3 / 状態PASS・FAIL・WARN・UNVERIFIED・BLOCKED)
出典区分: [コード実行結果][ZIP原文=リポジトリ][独立計算][仮定][未検証]

| ID | 旧K | 重大度 | 内容と根拠 | 状態 |
|---|---|---|---|---|
| F01 | K23 | P1 | `tools/fitcheck.py`のPCIe補助電源/パネル電源が`chk(..., True, ...)`固定PASSだった。→`unv()`新設でUNVERIFIEDとして計上、総合文言も「UNVERIFIEDは合格でない」に変更 [コード実行結果: fitcheck末尾] | 修正済(再発防止はstale_check未対応→要テスト) |
| F02 | K07/K13 | P2 | 現行ファイルに旧CPU/PSU/GPU記述が残存。`tools/stale_check.py`新設(履歴語を含む文脈は許容)で51件WARN検出。うち現行資産の実害(build_v8のコメント, system-spec「z=43/足215」)は修正。docsの旧選定文書は履歴として残置 | 一部修正/WARN維持 |
| F03 | K14 | P3 | 廃止CP-15.svgが現行`drawings/parts/`に残存→archiveへ退避 | 修正済 |
| F04 | K06 | P2 | stability.pyは目標を前25N/後20N/横30N(N基準)で判定。旧「40N」文言は設計基準と不一致→基準が正。チルト+25°後方27N、−5°前方31Nなど全[OK] [コード実行結果] | 設計基準で PASS(実測UNVERIFIED) |
| F05 | R4 | P1 | ヒンジ軸と背板/ブロック底板の干渉(z=38)→z=40へ、裏当て鋼板140幅+補強板追加、M6貫通ボルト | 修正(幾何のみ。強度は未試験 BLOCKED) |
| F06 | R4 | P1 | トレイ外周がドーム固定ハードと干渉→トレイ570×351.3で外周10mm空け、ハードを外周帯へ | 修正(AABB) |
| F07 | R4 | P1 | ケーブル/ホース干渉・近接: W5, H1/H2。cable_checkに小物障害物とより厳しい端点判定を追加し全ケーブルOK [コード実行結果] | 修正(中心線検査。実物UNVERIFIED) |
| F08 | K05 | P2 | cooler-ram AABB重なりWARN継続(ポンプ vs DIMM)。最終「OK」はWARNを無視していた→実物確認要 | WARN/UNVERIFIED |
| F09 | K09 | P1 | コントローラ基板型番未選定(U37)、eDP/12V互換未検証 | BLOCKED(購入ゲート不可) |
| F10 | K10 | P2 | GPU→液晶コントローラ映像経路(W5)は定義・経路検査済。実コネクタ/レーン仕様は型番未選定のため未検証 | UNVERIFIED |
| F11 | K17/K18 | P1 | 6GHz RF窓と穿孔の影響、全面通気孔圧損・38dBA・液晶背面温度は未実測 | UNVERIFIED |
| F12 | K22/K24 | P1 | 質量・重心は推定、STEP/GD&T付き正式加工図なし。図面は「PRELIMINARY」 | BLOCKED(加工発注ゲート不可) |
| F13 | K19/K20 | P2 | 未確認台帳U01〜U49。viewer固定値(温度・電力)の整合は要再点検 | WARN |
| F14 | K01/K02/K03 | P2 | 壁厚/板厚/スタンド足寸法の旧新混在は`spec.json`を単一源として現行値に統一(pod.total_t=dome.total_t, 足220×230)。stale_checkが不変条件を検査 | 解決(残差はstale_check WARN) |
| F15 | K08 | P2 | DC/AC/熱の電力表記の区別 | 再検証未了(thermal_calcとviewerの二重計上確認が次タスク) |
| F16 | K15 | P2 | CP-07 磁石ポケット深3.1mm/t2.0mmの成立性 | 未再検証(次タスク) |
| F17 | K04/K11/K12/K16/K21/K25 | – | 個別の再判定は未了 | UNVERIFIED |

誤検出の訂正: 旧K06「40N未達」は旧基準の話で、現基準(N基準)ではPASS。ただし基準値の妥当性自体は未確認。
