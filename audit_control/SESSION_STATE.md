# SESSION_STATE(再開の起点) — 更新: 2026-11-12 02:00 JST(干渉検査ループ: 要対処 377→28)
## 目的
iMac風27型4K一体型ゲーミングPC設計の全面監査・改修。ユーザーが止めるまで継続。必ず日本語、時刻はJST。仮説で決定しない(実証→決定)。

## ユーザーの恒常指示(忘れない。詳細は CLAUDE.md / docs/PRINCIPLES.md)
- 設計思想不変(Apple哲学オマージュ・ロゴ無し/修理性/内部は市販品・外装のみ特注/実物に忠実/公式一次資料優先/未確認はUNVERIFIED)。旧ファイルは削除せず archive、PRは頼まれた時のみ、claude/imac-pc-design へ commit&push。
- 全タスクを台帳(audit_control/tasks.json)に登録・更新。軽微な問題も全件。完了しても止めない。
- **サブエージェント監査は毎回超厳格**(AUD-STRICT)。**部品の干渉・埋め込み・コネクタ・端子挿抜空間・ケーブル端末まで細部**(INTF-01)。**U(未確認)項目は後ほど調査**(UNV-01)。
- 最近の指示: 「穴が実際に空いていない」→実穴化 / 「バネが描写されていない」→コイル化 / 「基板上の部品配置も完全制作」 / 「設計図・配置図は具体的な形まで・実物配置・再計算再設計」 / 「公式マニュアルを参考に設計図を一部改修、全低品質部分(マニュアル・設計図・配置図・見積書・部品/全体3D)を改修」 / 「形がiMac思想に基づいていない点を修正」。

## 現在地(2026-11-08 夜 JST): 3Dモデル「実物クオリティ化」ループ(台帳 QUAL-06)
- 公開ビューア(iMac風PC 設計モデル): https://claude.ai/artifact/G4ChbrBdfPzYxDdAMH2agP (v5=2026-11-14 11:10 JST 公開: ケーブル/PE編組/ヒンジ/AC流入口等の干渉修正を反映。要対処17・負債ALLOW38(R13)。GLB 37.6MB→gzip+base64 10.7MB)・ばね・基板・外皮・実穴を反映。GLB 37.7MB→gzip+base64 10.7MB)
- 実形状干渉検査(INTF-01/02): `blender/build_imac_pc_v8.py --check-interference` → `tools/interference_report.py`。要対処 377→170件。**検査の完了判定は出力ファイルの更新時刻とエラー(SyntaxError等)を必ず確認**(古い結果を読む事故が複数回)。編集後は `ast.parse` で構文確認してから実行。
- 設計規則(CLAUDE.md): 形は引き伸ばさず専用設計。穴=法線方向+弧長等間隔(perf_cutter)、ポート開口=コネクタ別の角丸トンネル(port_tunnels)。
- 修正済み(in_review): ばね幾何(座深さ79.03/スピゴット/spring_x=12.5)、外皮の薄肉化+天板、ブーツ再設計(外皮余白9mm=CP-26〜28更新)、PSU開口殻+4口ソケット、GPU PCB/フィン/ヒートパイプ、VRMフィン、I/O空洞+舌片、ファン7枚+ステーター支柱、ケーブル端プラグ、ガスケット/フィルタの切欠き、首振りボルトの座ぐり、チョーク/キャップ再配置、IHS高さ7.98。
- 保留(blocked・理由つき): MDB-002 ライザー(構造/曲げ半径未確認)、MDC-HOSE ホース450mm(曲げ半径U45未確認)、MDC-FANCABLE ファン配線(コネクタ位置未確認)、MDA-033 SSD位置(M.2カード寸法U56未確認)。
- 残(P1以降): MDA/MDB/MDC/MDD の未着手項目(R12各レポート)、干渉の残り(ヒンジボルト×背板/裏当て、吊りピン×ブッシュ、案内ロッド×キャリア等=穴(ボア)の未モデル INTF-03)、SHAPE-02(PE編組)/03(蛇腹)/04・08(ドーム断面の専用再設計)/05、UNV-01(U項目調査)、R9/R10残、図面lint(12/13/14/15/16等)。
- 再開手順: bash tools/install_hooks.sh; python3 tools/audit_control_init.py; bash tools/run_gates.sh; python3 -m unittest discover -s tests; list_triggers(毎時トリガー生存確認)。
- 運用: commit/pushはまとまった作業ごとに1回。pre-commit/pre-pushフックがCIと同じ検査を実行(FAILなら止まる)。

## 今回(2026-11-07 午後)の到達点
- thermal_calc.py 構文修復、ダクトは未採用候補(実証前に決定しない)。SCHED-01: ScheduleWakeup は 20:24:18 JST に到達(予約20:22)を台帳記録。再起動またぎは未検証。毎時トリガー trig_01N4GcNVUWWQLF41Pg8BYUVw(55分UTC)は生存・到達は未観測。
- 形状(SHAPE-01): スタンド外皮(足固定スカート+回転カラー+ネック外皮)で首振り軸受/ネックを隠した。SHAPE-02(PE編組がドラム外)/03(蛇腹の襞が見える)/04(ドームの稜線が硬い=CRT状)/05(ドーム下縁のフック/ラッチ可視)は未修正。
- 実穴(MODEL-HOLE-01): blender の --vent-mode 既定を boolean に。GLBは27.7MB→gzip+base64 7.9MB。viewer/index.html は gzip(DecompressionStream)対応済み。**ビューアでの実機読込検証(Playwright)と Artifact 再公開は未了**。現在の viewer/imac_pc.glb は実穴版だが、バネ(コイル)・基板追加部品・スタンド外皮の最新分を含まない可能性あり → **GLB再書き出しが必要**(`--view front --samples 1 --export viewer/imac_pc.glb` のあと `gzip -9 -c | base64 -w0 > viewer/imac_pc.glb.txt`、約5〜7分)。
- バネ: coil() を追加(ダイスプリング2本・ポンプ取付ばね4本)。`--open-stand`(外皮を外す)と `--only 接頭辞,...`(部分描画)を追加。確認画像は scratchpad/r/spring_view3.png(未確認→次に目視)。
- 基板(#35): model/x870i_layout.json に components 19点、tests/test_board.py、tools/gen_board_doc.py→docs/board-components.md。位置=マニュアルp.14読取(±2mm)、高さ=典型値UNVERIFIED。
- 図面(QUAL-03): tools/gen_layout_drawings.py が 09/10 を実形状で生成(gen_package.pyの09/10は廃止)。tools/drawing_lint.js(文字重なり/題名欄侵入/図枠外)を追加。drawlib: 題名の文字サイズ自動調整と data-frame。gen_mfg/cad/mech/service は再生成済み(regen完了、lint未実行)。

## 実行中/保留(次の具体的操作)
1. **サブエージェント2本(超厳格・日本語・読取+改修・commitしない)**: マニュアル a40e02e872b6ae5cc → audit_control/reports/R11_manuals.md、見積/BOM/RFQ abbbb1a01ee97e96a → R11_estimate.md。完了通知後: 報告を読み、表のID(MAN-/EST-)を tasks.json へ登録→ gates → commit/push。止まっていたら SendMessage で再開。
2. `NODE_PATH=$(npm root -g) node tools/drawing_lint.js drawings/*.svg drawings/v10/*.svg` を実行し、欠陥(特に 12_wiring/02_back_plate/15_bom_sheet の文字重なり・旧記述)を直す。gen_package.py(11〜16)は docs/bom-final.md を上書きするため、見積エージェント完了後に実行。
3. spring_view3.png を目視→バネが見えない/干渉があれば修正(cam/ロッド/シートとの位置、案内ロッドがばね外周より外=Ø20でz±15)。
4. GLB再書き出し→ビューアをPlaywrightで開き gzip読込とバネ・基板を確認→Artifact再公開(URL https://claude.ai/artifact/V6WRDYNxaZ3ZFB7UYPe6d4、overwrite_unread)。
5. INTF-01(実メッシュ干渉・埋め込み・コネクタ挿抜空間・端末): blenderでBVH交差検査を実装→fitcheckへ統合。
6. SHAPE-02〜05、QUAL-04(全図面棚卸し)、QUAL-05(GPU/PSU/ラジエーター/ポンプの実形状化)、UNV-01(Uの調査)、R9/R10残(triaged約265+in_review約80)、R10E熱前提(風量係数0.55・ファン曲線・35℃)、ダクト A/B実証(物理試験が無いためUNVERIFIED)。
7. 再開手順: python3 tools/audit_control_init.py; python3 audit_control/validate_state.py; bash tools/run_gates.sh; python3 tools/consistency_check.py; python3 -m unittest discover -s tests。list_triggers で毎時トリガー生存確認。

## 予約
- ScheduleWakeup: 20:50 JST(11:50 UTC)に /loop を再投入する設定済み(到達したかを SCHED-01 に追記すること)。毎時トリガー: 毎時55分UTC(=毎時55分JST)。両方併用し到達を記録・比較。
- 一回限り: trig_019AF76FZdAhi4pdi7CBgys1(2026-11-11 22:53 JST 定期再調査の停止)。

## 重要な技術メモ
- 座標: 設計 x右・y上・z=0が前面ガラス(背面は負)。Blender=(x,-z,y)、1BU=1mm。ヒンジ軸 z=45,y=10。--focus は「内部座標」x,y,z(X0/Y0/Z0基準; ばね付近は 295,-74,20)。
- numpy警告(ImportError numpy.core)は bpy 起動時の既知ノイズで描画は成功する。
- ゲート: run_gates exit 2=UNVERIFIED(合格でない)。CIは rc≤2 を許容、1で失敗。
