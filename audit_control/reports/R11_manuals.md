# R11 組立・整備マニュアル類の品質監査と改修(2026-11-07)

- 対象: docs/build-guide.md, docs/service-manual.md, docs/service-mechanisms.md, docs/README.md, docs/INDEX.md, handoff/05_機構設計書(= docs/mechanisms の複製)ほか手順書的文書。
- 基準: 公式マニュアル体裁(番号付き・1手順1動作、工具/トルク/部品番号、CAUTION/NOTE、図番、前提・所要時間、チェックリスト、トラブルシュート)と model/*.json(正規)との整合。
- 方針: 3文書は手書きでなく `tools/gen_manuals.py`(単一源 model/*.json + tools/massmodel.py)から生成する形に変更。旧版は `docs/archive/{build-guide,service-manual,service-mechanisms,README,INDEX}/` に tools/archive.py で保存済み(削除なし)。
- 重大度: P0=仕様矛盾で製造・安全を誤らせる / P1=重大な不整合・旧仕様残存 / P2=中 / P3=軽微。

| ID | 重大度 | ファイル | 問題 | 対応 |
|---|---|---|---|---|
| MAN-001 | P0 | service-manual.md H, service-mechanisms.md 3.8 | 「ストッパ位置でバランスばねを固定(ばね解放)」は旧レバー+圧縮ばね方式の手順。現行はカム+ダイスプリング2本(合計1350N常時圧縮)で、この固定法は成立せず、そのままヒンジ取り外しを案内すると蓄勢ばねによる人身事故の恐れ | 修正済み: 旧記述削除。警告を追加し、ばね保持治具が無い間はヒンジブロック取り外し(H-6以降)とバランサ分解(K)を BLOCKED と明記。治具の設計は UNVERIFIED のまま(新規課題) |
| MAN-002 | P0 | build-guide.md §1 | 「スタンド+ヒンジ: 定トルクヒンジ」「チルト25,000回(ヒンジ)」は旧仕様。現行はカム式バランサ(CP-23)+摩擦ヒンジ(CP-11)、-15〜+40° | 修正済み: 製法表を CP-10/20/21/22/23 に更新 |
| MAN-003 | P0 | build-guide.md §3(組立1) | 吊りピンのトルク 0.8N·m。正規(CP-04, mechanisms/05, joint-matrix J04)は 1.7N·m+ネジロック。文書間で二重管理が食い違い | 修正済み: custom_parts.json の値を自動取得して 1.7N·m。PEM引抜耐力は U29 未検証と併記 |
| MAN-004 | P0 | service-mechanisms.md §2 F11 / §3.1 | ラッチ「60N以上/点」、ガスケット「≤0.175N/mm」は旧値。正規は spec.dome_seal: 90N/点×6、0.098N/mm(公称156N/最大225N)。旧値のままでは「閉まらない」ガスケットを許容する | 修正済み: dome_seal から生成 |
| MAN-005 | P1 | service-mechanisms.md F4 | 肩ねじ「h8×3.0」。正規 CP-04 は h8×6.0(支圧部=トレイ+ブッシュ3.0) | 修正済み |
| MAN-006 | P1 | service-mechanisms.md §3.3/§5 | アンビリカル長が「380mm」と変更履歴の「250mm」で自己矛盾 | 修正済み: CP-17 から 380mm(整備余長100込み)に統一、履歴に変更点を記録 |
| MAN-007 | P1 | service-mechanisms.md §3.8 | 「バランスばね+摩擦ヒンジ(docs/tilt-swivel-design.md)」。参照先は旧版数値(s=65, F0=700N, z=40)の文書で、現行値と食い違う | 修正済み: カム式の現行値(balance.json)と mechanisms/01 を参照。tilt-swivel-design.md は「設計経緯(引用不可)」として docs/README.md に注記 |
| MAN-008 | P1 | service-manual.md 全般 | スタンド外皮(首振りスカート+ネック外皮)、首振りユニット(クロスローラ軸受)、指挟みブーツ、バランサ調整の整備手順が無い | 修正済み: 手順 H(外皮)/I(首振り)/J(ブーツ)/K(バランサ)を追加。外皮の固定方式は SHAPE-01 で未確定のため UNVERIFIED |
| MAN-009 | P1 | service-manual.md 全般 | 工具表・部品番号(CP/F/W)・図番・前提・所要時間・復旧チェックリスト・トラブルシュートが無く、手順は1行に複数動作を詰め込み | 修正済み: 全手順を「前提/所要/工具/部品/図」表+番号付き1動作手順+チェックリスト+トラブルシュートに再構成。所要時間は全て「設計見積・未実測」と明記 |
| MAN-010 | P1 | build-guide.md §3 | 組立順が1行に複数動作。W番号が W1〜W5 のみ(W6 AC、W7 内部DP、H1/H2 ホースが欠落)。ctrl基板配線の説明誤り | 修正済み: S1〜S6 に分割、W1〜W7/H1,H2、クリップ範囲(z≦30)を wiring.md/hardware_list と整合 |
| MAN-011 | P2 | service-mechanisms.md F6 / standard-parts.md | スタンドオフ数量が文書間で不一致(F6「約40」、standard-parts「約60」、hardware_list 4+14=18) | 一部修正: 手順書側は hardware_list(18)に合わせ不一致を明記。docs/spec/standard-parts.md(手書き)は未修正 → 台帳登録要 |
| MAN-012 | P2 | build-guide.md §2 | 購入前確認の U 番号が旧(U06=GPU 5060Ti、U09 の GPU+ライザー、U13 のみ)。GPUは5070 Ti(U46)、ライザー U60、制御基板 U37/U42、冷却 U33/U58、電源 U47 が欠落 | 修正済み: 現行台帳番号の表に更新(件数・状態の手書きは廃止し台帳参照) |
| MAN-013 | P2 | build-guide.md §5 | 「既知の設計課題(2026-11-05 更新)」が解消済み/古い内容を手書き保持(DIMM厚、smoothstep 等) | 修正済み: 台帳(unverified-tracker.md, tasks.json)参照へ置換 |
| MAN-014 | P1 | service-manual.md A / service-mechanisms.md F12 / mechanisms/04 | ドームフックが「上辺×6」(CP-09, hardware_list, mechanisms/04)と「左右辺の側辺フック×4(各40N)」(spec.dome_seal)で食い違う。ガスケット反力を受ける構造に関わる | UNVERIFIED: 手順書に注記。正規の確定(model側)は未了。mechanisms/04 の生成器 tools/gen_mechanisms.py:176-190 と spec の整合が必要 |
| MAN-015 | P2 | service-manual.md | 「5分待つ」の根拠がPSU公式でない | 修正済み: 一般的な目安で PSU公式値は UNVERIFIED(U47)と明記 |
| MAN-016 | P2 | service-manual.md, build-guide.md | 質量 22.5kg が massmodel 推定値であること、受入試験の合格基準が案であることが未明記。表面温度48℃(IEC 62368-1)は要確認のまま断定 | 修正済み: 質量は massmodel から生成し推定と明記。試験は「合格基準案・全項目未実施」の表(No./方法/基準/根拠・状態)に再構成、48℃は UNVERIFIED と明記 |
| MAN-017 | P2 | service-manual.md | 首振り操作力を「約5N」(旧)と記載し得る。mechanisms/02 の正規計算は 5.8N(保持1.8N·m/0.31m) | 修正済み: 計算値 5.8N を生成(U53 未試験) |
| MAN-018 | P2 | docs/README.md | 版表記が「v9」、service-mechanisms/service-manual/build-guide を「旧」に分類(実際は現行の手順書)、手順書への導線無し | 修正済み: v10モデル表記、§2A「組立・整備の手順書」を追加、tilt-swivel-design.md は設計経緯(引用不可)と注記 |
| MAN-019 | P3 | docs/INDEX.md | 組立・整備の手順書が索引に無い | 修正済み |
| MAN-020 | P2 | service-manual.md G / build-guide S1 | パネル固定M3(約18)の本数・トルク(0.3〜0.4N·m)・ねじ頭(T6/T10)は出典が弱い。BOE公式Fig.6は23穴で使用18穴は暫定(U55) | UNVERIFIED: 本文に明記して確定扱いを回避 |
| MAN-021 | P2 | service-manual.md F | ポンプばね付きネジの工具・締付トルクは ARCTIC 公式の取付説明で未確認 | UNVERIFIED: 明記(出典欠落、ARCTIC公式要確認) |
| MAN-022 | P2 | build-guide.md S1 | 組立姿勢(ガラス面を下にしてよいか)と外皮取付時期、スタンド取付工程が設計根拠なし | UNVERIFIED: 明記。試作1号で確定 |
| MAN-023 | P2 | service-manual.md H/I, service-mechanisms.md F13〜F15 | ネック基台M5×4、軸受M5×12、カム板M4×2 のトルク・工具が model に無い | UNVERIFIED: 手順に「UNVERIFIED」と記載(U50 ほか) |
| MAN-024 | P2 | handoff/05_機構設計書/* | docs/mechanisms の複製。手書き手順書ではないが、04 の「上辺フック6点で受ける」は MAN-014 と同じ不整合、整備上の手順(5節)が公式体裁でない | 未修正(生成物。tools/gen_mechanisms.py / gen_handoff.py 側で対応要。本件は報告のみ) |
| MAN-025 | P2 | docs/failure-analysis.md(生成物) | ガスケット「≤0.175N/mm」「340N vs 磁石84N」が旧値のまま(現行 0.098N/mm・ラッチ主体) | 未修正(生成器 tools/gen_fmea.py を直す必要あり) |
| MAN-026 | P2 | docs/tilt-swivel-design.md | 旧数値(s=65, F0=700N, 軸z=40, 足300×290 等)を含み、手順書から参照されていた。R9D-001〜012 で既指摘 | 未修正(手順書側は参照を外し注記のみ。archive 化は別タスク) |
| MAN-027 | P3 | docs/spec/standard-parts.md ほか手書き | 旧記述(スタンドオフ約60 等)と hardware_list の二重管理 | 未修正(MAN-011 と同じ) |
| MAN-028 | P2 | 手順書全体 | ばね保持治具、スタンド外皮固定、整備時の頭部支持台は設計に存在しない | 未解決(新規課題。台帳登録が必要。親が tasks.json に登録すること) |
| MAN-029 | P3 | tools/stale_check.py | model/procurement.json で FAIL 1(旧PSU SF1000 の記述)。本件のスコープ外 | 未修正(報告のみ) |

## 検証
- `python3 tools/gen_manuals.py` 実行で3文書を再生成。リンク先(wiring.md, spec/grounding-spec.md, mechanisms/ 等)の実在を確認。
- `python3 tools/consistency_check.py`: FAIL 0 / WARN 6(3文書に関する警告は0)。`tools/stale_check.py`: 3文書に関する指摘なし(FAIL 1 は model/procurement.json で既存・別件)。
- `tools/run_gates.sh` と `audit_control/validate_state.py` は未実行(気づき: 親側で実行・tasks.json 登録を依頼)。
- 実機・専門試験が必要な項目(所要時間、ばね保持、PSU放電、各トルク、受入試験)は全て UNVERIFIED のまま。
