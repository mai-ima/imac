# R9 独立コード監査: tools/*.py・tools/run_gates.sh・audit_control/*.py・blender/hardware_v8.py

- 監査日時: 2026-11-06 23:10〜23:40 UTC(読み取り専用。再現用スクリプトは `/tmp/claude-0/-home-user-imac/fbff7c34-cd47-589a-bcf9-44f14d0b0642/scratchpad/` 内のみ)
- 監査基準: HEAD `4050ed9` + 作業ツリー(未コミット変更多数)。**監査中に別セッションが HEAD を `e7a16e1` へ進め、作業ツリーも更新した。** 本書の行番号は読んだ時点の作業ツリー基準で、数行ずれる可能性がある。監査中に修正を確認した項目は表中に「(監査中に修正済)」と明記した。
- 重大度: P0=ゲートが偽PASSを出す/設計の物理が逆(成立しない)、P1=結論を誤らせる・データ喪失・基準の不当な緩和、P2=不整合・旧定数・検査の抜け、P3=軽微(保守性・死コード・表記)。
- 確信度: 高=実行/再計算で再現済み、中=コード読解で確実だが再現は未実施、低=推測を含む。

## 1. 件数サマリ

| 重大度 | 件数 |
|---|---|
| P0 | 4 |
| P1 | 10 |
| P2 | 29 |
| P3 | 13 |
| 合計 | 56 |

## 2. 発見事項

### 2.1 偽PASS・ゲート設計(観点1・4)

| ID | 重大度 | ファイルと行 | 再現 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9T-001 | P0 | tools/balance_calc.py L21-24(spring_tau/resid)、L36(sign の探索)。model/balance.json `sign:1` | scratchpad/bal_indep.py(エネルギー法で独立再計算)。a=+40°で重力 +18.04N·m、ばね +15.09N·m(同方向)、合計 +33.1N·m。balance_calc は `tg+spring_tau=2.95` と表示 | 圧縮ばねでアンカーが先端より下にあると、ばね長 l=√(e²+s²-2se·cos a) は a=0 で最小、a>0 で増加する。ばねは伸びる向き=チルト増加方向へ押すため、重力と同じ向きに加わる(U_s は a と共に減る)。コードは `sign=±1` を自由変数にして「小さい残差」の符号(=引張ばね相当)を採用している。圧縮ばねとして物理的に正しい sign=-1 では残差が約33N·m。摩擦5.8N·mでは保持も操作も成立しない。探索範囲(s 50-76, e 20-29)内に物理的に正しい解は無い。strength_check のばね折損エネルギーや docs/mechanisms/01 も同じ誤った前提を引き継ぐ | `sign` 自由度を廃止。ばね力の向きを圧縮ばねの定義(B-A 方向に押す)で固定し、トルクはエネルギー法 `-dU/da` で計算。アンカーを先端の前方(z側)へ置くか引張ばねに変えるなど、l(a) が a 増加で縮む配置を探索変数に加える。再設計後に D04/hardware_v8/docs を再生成 | 高(独立の式で再現。幾何・向きの解釈は設計者に最終確認) |
| R9T-002 | P0 | tools/cable_check.py L62(末尾)。run_gates.sh L5 | `sed -i 's/ref_mm=400/ref_mm=100/'` した複製で実行 → 「総合: 1件の問題」と出力するが `exit=0`(scratchpad/rep) | cable_check.py に `sys.exit` が無く、NG があっても常に終了コード0。run_gates は終了コードだけで合否を判断するため、配線干渉・曲げ半径・長さ超過が検出されても「合格」になる。ゲートとして機能していない | 末尾に `sys.exit(1 if bad else 0)` を追加 | 高 |
| R9T-003 | P0 | tools/run_gates.sh L5-L8 | scratchpad/rep2 の同一ロジックで `exit 2` のゲートが2件あっても最終 `exit=0` | CLAUDE.md は「exit 2=UNVERIFIED は合格ではない」と規定するが、`unv` は表示するだけで最終 `exit $rc` に反映されない(UNVERIFIED があっても exit 0)。CIや人が終了コードだけを見ると UNVERIFIED が合格扱いになる。さらに存在しないスクリプト(`python3 tools/x.py`)も Python が exit 2 を返すため「UNVERIFIED」に分類され、ゲートの欠落・改名が合格に見える | 最終行を `[ $rc -ne 0 ] && exit 1; [ $unv -gt 0 ] && exit 2; exit 0`。UNVERIFIED は専用の戻り値(例: 2)でスクリプト側が明示出力した場合のみ数える(exit 2 の一般エラーと区別するため、ゲート側は `UNVERIFIED:` 標識を標準出力に出す) | 高 |
| R9T-004 | P0 | tools/stability.py 全体 + tools/strength_check.py L1-3 + tools/balance_calc.py L64-66 | 3本とも質量・ばね・重心が推定(UNVERIFIED)と自称するが終了コード0 | 質量・重心・ばね特性が全て推定の上に立つ「OK」を exit 0 として出力する。さらに R9T-001 により balance_calc の「OK」は物理的に誤り。UNVERIFIED の前提を持つゲートを exit 0 にすると、台帳上は PASS に見える | 前提が推定の計算は「条件付き合格」を表す戻り値(2)にするか、`--assume-estimates` を必須にし、既定は2を返す。実測置換後に0へ | 高 |
| R9T-005 | P1 | tools/fitcheck.py L91-92(unv)、L101-103(総合・exit) | `python3 tools/fitcheck.py; echo $?` → UNVERIFIED 2件を表示して exit 0 | UNVERIFIED を数えるが終了コードに反映しない(swivel_calc だけが exit 2)。run_gates の「UNVERIFIED ゲート 1 件」は swivel_calc 1本のみで、実態を過小に見せる | `unverified` が非空なら exit 2(NG があれば exit 1 が優先) | 高 |
| R9T-006 | P1 | tools/fitcheck.py L53(allow)、L61-63 | 出力に `[EXPECTED_OVERLAP] cooler-ssd`。`chk('干渉なし…', ok, …)` は直前までの `ok` を表示するだけ | 許可リスト `allow`(7組)に入れた AABB 重なりは NG にならず、`chk('干渉なし(許容組合せを除く)')` は恒真(`ok` は他の chk の積)。実形状未確認の重なりが永続的に許容される(台帳 K05)。run_gates は `tail -6` で出力を切るため EXPECTED_OVERLAP/WARN 行は人の目にも残らない | 許可ペアごとに最大重なり量の上限と根拠IDを持たせ、超過で NG。重なり件数は exit 2(UNVERIFIED)にする | 高 |
| R9T-007 | P1 | tools/fit_tolerance.py L24-25、spec.json fits.keyhole_rattle_max=0.6、docs/mechanisms/07 の窓表 | `python3 tools/fit_tolerance.py` → 「0.3〜0.568mm / 窓 0.05〜0.6mm [OK]」。窓表は 0.05〜0.20mm | (a) 位置公差積み上げ(0.2)を最小隙間側だけに減算し、最大隙間側(c_hi)に加算していない。c_hi+0.2=0.768mm>0.6 で本来 NG。(b) 窓の上限が 0.2→0.6 に緩和済みで、docs/mechanisms/07 の窓の根拠表は 0.05〜0.20 のまま(文書とゲートが不一致)。「トレイ位置決めは別ピンが担う」という理由で3倍緩和しており、閾値の不当な緩和にあたる | 最大側にも位置公差を加算。窓の緩和には根拠(位置決めピンとの分担計算)を spec に記録し、文書の窓表を生成元から埋め込む | 中 |
| R9T-008 | P1 | tools/fit_tolerance.py L35-40(チルト行)、spec.json hinge.op_target_N=25・friction_aging_loss=0.3・friction_hold_Nm=5.8 | 出力「チルト保持(経年-30%後) 3.74 / 窓 3.69〜」(余裕1.3%)、操作力 24.3N / 窓〜25N | 操作力目標を 20→25N に緩和(spec の doc に「要ユーザー確認」のまま)し、摩擦5.8N·m を保持と操作の両立がギリギリになる値に調整した形になっている。WARN で止まり NG にならない(余裕 1.3%、`margin_warn=0.0`)。さらに保持条件の残差は balance.json の `resid_worst`(静的ファイル)を読むだけで、balance_calc の再計算結果との整合を確認しない | 閾値緩和はユーザー承認を台帳で確認するまで WARN→UNVERIFIED(exit 2)。fit_tolerance は balance_calc を直接 import して同じ計算を使う(balance.json の鮮度確認も行う) | 高 |
| R9T-009 | P1 | tools/gen_mechanisms.py L8(`run`)、L11 | `run()` は `capture_output` で stdout のみ使用、終了コード・stderr を見ない。例えば balance_calc が例外で落ちても docs/mechanisms/01 に空のコードブロックが書かれる | 生成物が失敗を隠す。swivel_calc の exit 2、NG の exit 1 も文書に反映されず「設計書」が合否と無関係に更新される | `check=False` で終了コードを取得し、1なら生成を中止、2なら文書に UNVERIFIED と明記。stderr も出力する | 高 |
| R9T-010 | P1 | tools/consistency_check.py L32(SKIPCTX に `→`・`旧`・`仮置き` 等)、L47、L36-44(例外時 continue)、L26-28(HIST は WARN のみ)。tools/stale_check.py L25、L16、L20-21 | 「ヒンジ軸 z=99 mm → 設計値」は SKIPCTX に `→` があるため検出されない(scratchpad で正規表現を再現) | 前後40〜50文字に `→`/`旧`/`置換` 等があれば全て除外されるため、矛盾の見逃しが容易。HIST は FAIL にならない。読めないファイル・数値変換不能は黙って `continue`。stale_check は `git ls-files` のみ(未追跡ファイルは対象外。consistency は `-co`)。対象拡張子が限られ `.txt`/`.dxf`/handoff が漏れる(handoff は consistency 側でも除外)。事実は約13項目のみ | `→` を除外語から外し、除外は行頭の「(旧)」等の明示マークに限定。読み取り不能・変換不能は FAIL。未追跡も対象に。対象に handoff と `.txt` を追加。FACTS を spec から機械生成 | 高 |
| R9T-011 | P1 | tools/audit_control_init.py L7-9(load)、L60-62 | `tasks.json` が壊れていると `load()` が既定値(空の台帳)を返し、続く `json.dump` が正規台帳を上書き | 唯一の正規台帳を例外握りつぶしで消去できる。file_coverage.csv 側も `except Exception: pass` で同様 | 例外時は中止して終了コード1。書き込み前に `archive.py snapshot` またはバックアップを取る | 高 |
| R9T-012 | P1 | tools/gen_package.py L194-199(docs/bom-final.md, docs/wiring.md を上書き)、tools/layout_search.py L61(model/layout_dome.json 上書き)、tools/cablemodel.py L56-57(run_gates が毎回 model/cables.json を上書き)、tools/audit_manifest.py L39(run_gates が audit_output/ を上書き)、tools/neckgeom.py L51(--write で spec.json 全体を再書き込み)、tools/gen_fmea.py L5-47(FMEA 本体データが生成器内)→ docs/failure-analysis.md 上書き | 作業ツリーは既に生成物が未コミットで変更されている(git status)。今回 run_gates を実行しただけで audit_output/01_FULL_FILE_MANIFEST.csv が更新された(後述 §6) | 生成器は上書き前の検査(手編集の検出・差分確認・`--check`)が無い。archive は commit 時のみで、未コミットの手編集は失われる。bom-final.md は stale_check/consistency_check では履歴(HIST)扱いなのに gen_package が上書きする(位置づけが矛盾)。ゲート(cablemodel/audit_manifest)が正規データ/台帳を書き換えるため「読み取り専用検査」でなくなる | 生成物ヘッダにソースのハッシュを埋め込み、手編集を検出したら中止。ゲートは書き込みを分離(`--write` を明示)。`--check` モードを追加し、生成物が最新かをゲート化 | 高 |
| R9T-013 | P1 | tools/gen_specs.py L84-85(MBR)、tools/cablemodel.py L13-31(mbr) | gen_specs の MBR は W1=30, W2=20, W3=20, W4=15, W5=25, W6=25、その他は既定20。cablemodel の mbr は W1=12, W2=12, W3=20, W4=6, W5=16, W6=14, W7=16, ホース=40 | docs/spec/wiring-spec.md は「最小曲げ半径」を W1=30mm 等と記載するが、cable_check が実際に検査する半径は 12mm。文書が謳う半径を満たすかは検査されていない(ホース H1/H2 は文書20mmだがゲートは40mm)。業者提出資料の数値と検査値が不一致 | MBR を cablemodel の `mbr` から生成する | 高 |
| R9T-014 | P1 | model/spec.json hinge.balance_note(M8調整ねじ ±3%)、tools/gen_mechanisms.py L33(押しねじ M5 ±約80N/本)、tools/gen_mech_sections.py D04 notes(ピールシム ±約27N/本=±7%)、blender/hardware_v8.py(M8 調整ねじを描画) | 3つの調整方式が文書間で食い違う。balance_calc/fit_tolerance は「調整後 荷重±3%・重心±3mm」を前提 | 未調整公差 ±10% を ±3% に追い込む調整範囲が、ピールシムでは ±7% にしか届かない(台帳 SHIM も未解決)。ゲートは到達不能な「調整後公差」で合格している | 調整方式を1つに確定し、調整範囲 ≧ 未調整公差を balance_calc でゲート化 | 中 |

### 2.2 計算・数式(観点5)

| ID | 重大度 | ファイルと行 | 再現 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9T-015 | P2 | tools/strength_check.py L38-39 | 手計算: 基台M5×4引張。M=38.6N·m、ボルト列間隔46mm の偶力 → 1列 T=M/zspan=839N、1ボルト 420N → 29.6MPa。コードは `(M/(2*zspan))/(2*A_s)` = 14.8MPa | 偶力の腕に対して `2*zspan` で割り、さらに本数 2 で割るため二重に1/2。応力を過小評価(約1/2)。許容300MPaに対し余裕が大きく結論は変わらないが式が誤り | `(M/zspan)/2/A_s` に修正 | 高 |
| R9T-016 | P2 | tools/strength_check.py L38(0.12)、L46(Tq=18.0/2)、L20-22 付近の 0.019/Lsp=53/Lp=25.0 | 0.12m は頭部重心水平オフセットの手入力、18.0N·m は τg(40°) の手入力(balance_calc は 18.04 を計算) | 質量・重心・幾何が変わっても更新されない。`abs(MM.head_cg()[3][0][3] if False else 0.12)` は死コードで意図が不明 | massmodel/spec から導出して使う | 高 |
| R9T-017 | P2 | tools/strength_check.py L28-31(ストッパ荷重) | M_push(50N×0.41m)のみで評価 | +40°/-15°端のストッパは、押し荷重に加え端での重力残差(R9T-001 の訂正後は最大≈33N·m)を受ける。ばね側のトルクも加算が必要。現行計算はこれを含まない | ストッパ荷重 = 押し + 端の正味トルク(最悪)/レバー長 で再評価 | 中 |
| R9T-018 | P2 | tools/balance_calc.py L58-62 | `slen=(lmax-HW)/13.0` のみ | ばねの線材せん断応力(Wahl 補正)、固着長、疲労(25,000回)が未検査。F=584N/本、平均径13mm・線径3mm(推定)だとτ≈0.97GPa(Wahl 係数約1.35 を含む手計算)で、JIS金型ばねの許容を超える可能性がある。ゲート出力は「OK」 | ばね選定を UNVERIFIED として出力(exit 2)。線径・自由長・固着長・応力をパラメータ化して検査 | 中(仕様が推定のため) |
| R9T-019 | P2 | tools/motion_check.py L46(ばね上座) | `rect(-22,-6, HY-BE-3, HY-BE, …)` y∈[-18,-15] | blender/hardware_v8.py の上座は `HY-BE-HW_`(=-23)。端金物(balance_end_hw_mm=16)導入後も干渉モデルが旧位置のまま(約5-8mm上)。ゲートは実機位置の干渉を見ていない | hardware_v8 と同じ式 `HY-BE-HW/2` を使う | 中 |
| R9T-020 | P2 | tools/motion_check.py L23(mn_desk)、L24-29、L111-112、L122 | `mn_desk`(机面すき間)は計算・表示するだけで判定に使わない。「挟み込みはWARN」と表示するが WARN を出す経路が無い。`ok_low` は `-72 >= -72`(余裕0。s≦76 の上限が本検査に合わせて決められている) | 結果を使わない判定・実装されていない WARN 表示。余裕0で合格 | 机面すき間の下限を判定。WARN は集計して exit 2 にする。ok_low に余裕を設ける | 高 |
| R9T-021 | P2 | tools/motion_check.py(HEAD 辞書が L41 と L43 で二重定義、`PO=29.0` 未使用、L107 の shear 式が `if False else` の連鎖、L82 `gap()` も `if False else`) | 目視 | 死コードで意図が読めず、監査・保守が困難。PE 編組の端点 r=62/75、ヒンジ底板の座標(-27,-25,-61…)も手入力 | 死コード削除。座標は spec/neck から導出 | 高 |
| R9T-022 | P2 | tools/motion_check.py(摩擦ヒンジΘ22・軸・Eクリップを HEAD に含めない)、台帳 HINGE-D22 | 摩擦ヒンジΘ22(軸y=10で底面y=-1)は掃引モデルに無い | 「掃引干渉 OK」の対象外。ブーツ内空間への突出は未検査 | HEAD に円柱(多角形近似)を追加 | 中 |
| R9T-023 | P2 | tools/fit_tolerance.py L22-23(ガスケット) + spec.json dome_seal.side_hooks=4 | 容量700N = 下辺ラッチ540N + 側辺フック160N。DXF(gen_mfg_drawings)/hardware_v8/hardware-list に側辺フックは無い(上辺フック×6 のみ)。docs/mechanisms/04 は「公称156N/最大225N/≦0.08N/mm」だがspecは0.098N/mm(公称190.8N、最大284N) | ゲートが存在しない部品の保持力を算入。合格判定は側辺フック無しでも成立(426≦540)するため結論は変わらないが、仕様と文書が不一致。最小線荷重0.04N/mmの下限根拠は台帳U61(未確認)で、余裕2.8% | 実在する部品のみ算入。文書は spec から埋め込み | 高 |
| R9T-024 | P2 | tools/fit_tolerance.py L42、tools/swivel_calc.py L23 | 495.0(画面高さ-軸受)と 0.31m、0.41m が複数ファイルに手入力。swivel_calc は holding_torque_Nm(1.8)を使い、fit_tolerance は μ·F·r(1.19〜2.90N·m)を使う | 同じ量を別の式で評価。spec の holding_torque_Nm が fit_tolerance の窓に入るかを検査していない | holding_torque を μ·F·r から導出し1箇所に | 中 |
| R9T-025 | P3 | tools/power_budget.py L23 | `heat_sum == ac` は `psu_loss=ac-dc` の定義から恒真 | 「保存則の検査」と称するが恒真で何も検査しない | 実機の入力電力・各発熱源から独立に集計して比較(実測待ちなら UNVERIFIED) | 高 |
| R9T-026 | P3 | tools/power_budget.py(効率の階段関数 0.925→0.91) | 目視 | 70%負荷で効率が不連続に低下。許容 0.7 の境界と同じ値 | 補間する | 中 |
| R9T-027 | P2 | tools/thermal_calc.py(末尾に `sys.exit` なし)、run_gates の対象外 | docs/thermal-analysis.md に「CPU(B: 再循環・最悪) 97℃ 超過」と生成されるが終了コード0 | 熱は「超過」と判定される条件を持つのにゲートでなく、合否に影響しない。joint_calc/neckgeom も同様に非ゲート | thermal_calc をゲートに入れ、超過で exit 1、仮定は exit 2 | 高 |
| R9T-028 | P2 | tools/stability.py L21 付近、tools/massmodel.py L31-35(head リスト) | 手計算: tilt=-15°, swivel=0 → tz=26.96, 前余裕 67.96mm, F=28.1N(出力と一致) | 数式は正しい(独立再計算で一致)。ただし ram・riser・ファン・ホース冷却液等が質量表に無く(推定誤差の方向が非保守的)、足の質量を支持中心(z=90)に置く。全て UNVERIFIED なのに exit 0(R9T-004) | 質量表を part.json から導出。感度(質量±10%)をゲートに含める | 中 |
| R9T-029 | P3 | tools/swivel_calc.py L18 | `M_shock = 2.0*M_static + M_push*0.0` | 「衝撃2G」の根拠が無い式で、`*0.0` の死項。出力文に「ストッパ衝撃 etc.」の未完成記述 | 衝撃条件を規格(落下・輸送)から定義 | 高 |
| R9T-030 | P3 | tools/neckgeom.py L40(comp_dn/up の手入力)、spec.json neck.doc(「レバー長50」) | spec の doc は「レバー(長さ50)」、実値 lever_len=34 | 導出値(pad_*_z 等)は手動実行しないと更新されず、鮮度ゲートが無い | motion_check 側でパッド位置の導出式と spec の一致を検査 | 中 |

### 2.3 旧定数・単位・座標(観点2)

| ID | 重大度 | ファイルと行 | 再現 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9T-031 | P2 | tools/gen_drawing.py L3-9、L25、L61-70 | `W,panel_w,panel_h,bezel,chin=547,527,296.5,10,68`、slab_t=14、pod_t=70、「RTX5060 SOLO」「23.8型」「総厚190」の混在 | 旧24型コンセプト値のまま concept/blueprint.svg を上書き生成する。spec.json を一切参照しない(単一源に反する)。誤って再実行すると旧図が最新に見える | 廃止して archive へ(スタブを残す)、または spec 駆動へ | 高 |
| R9T-032 | P2 | tools/gen_mfg_drawings.py L11(`S['pod']['total_t'/'h'/'side_margin']`)、L53/L136/L54(590, 371.3, 36)、L63 のコメント「12+75*smoothstep」、L177(x=298、y=357.3 の文字固定) | spec.pod は `_legacy`(参照禁止)。POD_T/POD_H/POD_W は未使用 | stale_check は `['pod']['wall']` だけを禁止しており他の pod キーを検出しない。590/371.3/596/377.3/298 は spec(body_w, panels, inset)から導出可能で、寸法変更時に DXF と hole-table.md が静かにずれる | 全て dome/inset から導出。pod 参照を禁止リストに追加 | 高 |
| R9T-033 | P2 | tools/gen_mfg_drawings.py L44(02: 吊りピンを `px0+(3+kx)*sc`、x反転なし)、L54(03: `DW-ix0-x_-a_`、x反転あり)、L163-164(DXF ドーム: 反転なし)、tools/gen_service_drawings.py L19(「背面側から見た配置」、反転なし) | 同一のトレイ座標 x を図ごとに反転する/しない。03 は「背面から見た図: x反転」と注記、06 は「背面側から見た」と書いて反転なし | トレイ座標は「ドーム内側の左下原点」。図ごとに視点と反転が不統一で、左右非対称部品(IO/GPU/AC スロット、位置決めピン2本、キーホール)の左右が図面間で食い違う可能性が高い(業者提出の DXF と SVG の整合)。Blender 側の対応は build_imac_pc_v8.py 側で未確認 | 座標系(視点・x向き)を spec に1つ定義し、全生成器で共通関数を使う | 中 |
| R9T-034 | P2 | tools/gen_package.py L92(「前面スラブ(t18)」)、L133(「…611W/SF1000 61%」)、L153(発熱表: 230+300+40+35+30=635W、PSU損失35W)、L171(W1〜W5) | power_budget: DC636W・AC688W・PSU損失52W・使用率64%。配線は W1〜W7+H1/H2。slab_t=25 | 手書き固定値が単一源(power_budget/spec)と食い違う図面を出力する。fitcheck の発熱はコミット e7a16e1 で power_budget 参照へ修正済みだが gen_package は未修正 | spec/power_budget から埋め込む | 高 |
| R9T-035 | P2 | tools/gen_specs.py L55(J07「掛け爪フック×6」「ラッチ60N以上/点」「閉合力≤約340N」)、L66(J18「250mm」)、L91-96(GPU TGP180W、PCIe 6+2、「W1〜W5」)、L99(IW=590, IH=371.3)、L42(`if y > 150: break`) | spec: latch_hold_N=90、閉合力は190.8〜284N、アンビリカル全長380(余長100)、GPU TGP 300W・12V-2x6。L42 は注記行が長いと `break` で以降の特徴・接合を図面から黙って捨てる | docs/spec の接合マトリクス・配線仕様に旧値が残り、部品図の記載内容が静かに欠落する | 固定表を spec/custom_parts から生成。欠落時は警告 | 高 |
| R9T-036 | P2 | tools/gen_handoff.py L85(高さ415.3)、L80(「版: v9」)、L96(「内奥行6→101mm」)、L97(「SUSレバー(t5×14×50)」) | spec: 内奥行 6→162(総厚190)、lever_len=34、バージョン v10 | 業者向けRFQ(見積依頼書)に旧寸法が残る。stale_check は handoff の数値の文脈を見ない | spec から埋め込み。RFQ を consistency_check の対象に | 高 |
| R9T-037 | P3 | tools/gen_handoff.py L33-35(側板プロファイルを `Workplane('YZ')` に (z,y) 順で与える)、L40 の `if False else` | cadquery の YZ 面ではローカル x=Y, y=Z。(z,y) で与えると部品座標が入れ替わる(部品単体の STEP としては成立するが組立座標では回転が必要) | STEP の軸の取り方が未文書。未検証(cadquery 未実行) | 部品座標系をコメントに明記/検証 | 低 |
| R9T-038 | P2 | tools/gen_service_drawings.py L54(「傾斜 60mm」run=64)、L62(「余長250mm」)、L61-65(丸数字⑭へ飛ぶ)、L68(`st[:78]`/`st[78:156]` で長文を切る)、L26-34(死関数 free_point)、L17(T() が & < を無害化しない) | 目視 | 旧値、番号欠落、156文字を超える手順の黙った切り捨て(手順が欠ける) | 折り返し処理、spec 参照 | 高 |
| R9T-039 | P2 | tools/gen_fmea.py L36-37(「足を幅260×奥行245」)、L51(「経路576mm」)、「M6ネジ」「CG15.5kg」、RPN≥150 の扱い(ゲート無し) | 現行: 足360×310、AC 経路456mm、頭部15.35kg | FMEA の本体データが生成器に埋まっており旧値のまま。RPN≥150 の項目に対する合否ゲートが無く、`failure-analysis.md` は単なる一覧 | データを model/ に移し、RPN≥150 を台帳連動のゲートに | 高 |
| R9T-040 | P2 | blender/hardware_v8.py L13(ITX 穴)、L16-25(PSU・ラジエーター穴)、L53/L58(磁石 `top_y-6`・ポスト `top_y-6`) vs tools/gen_mfg_drawings.py L141-150、L169(磁石 10mm、ポスト `DHd-20`)、gen_package L48 | 同じ穴座標が3箇所に手入力。磁石位置: Blender は縁から6mm、DXF は10mm。位置決めピン: Blender は `top_y-6`、hole-table は y=357.3(上縁から20mm) | 3Dモデル・DXF・穴表が相互に不一致の位置を示す(業者提出データ vs 3D)。単一源(model/)が無い | 穴座標を model/holes.json に集約 | 高 |
| R9T-041 | P2 | blender/hardware_v8.py L124(`stand_neck_bolt … if False else None`)、`gpu_bracket_screw`(`if False else None`)、hw() の「ネック基台 M5×4」「ブラケットねじ」 | hardware-list.md の見出しは「3Dモデルに実際に描画している」 | 描画していない部品を一覧は載せる。台帳が実物と乖離 | 描画するか、一覧から除くか注記 | 高 |
| R9T-042 | P3 | blender/hardware_v8.py(監査中に修正済: 尾部レバー長50、ブーツ山8・伸縮10〜56、摩擦リング1.6N·m、ステータ Ø110 等の旧文字列は作業ツリーで spec 参照に置換済) | git diff HEAD で確認。HEAD 版には旧値が残る | 修正がコミット前。コミット漏れの確認 | コミットして台帳を更新 | 高 |
| R9T-043 | P2 | tools/cablemodel.py L10(HZ=143.0)、tools/fitcheck.py L83(143.0+6.2) | 同じホース高さを2箇所に手入力 | ドーム総厚やホース曲げ半径(U45 仮置き40mm)を変えても fitcheck の隙間検査は更新されない | 共有定数化 | 高 |
| R9T-044 | P2 | tools/cable_check.py L25(`W_=590.0,H_=371.3,Rc=47.0`)、L49(`-3` の手入力)、L37(ホースの端9点=約27mmを除外)、L60(`da[7:-7]` で端21mmの近接を無視、`len>14` でなければ 99) | 短いケーブル(W4 など)は近接検査が事実上スキップ(`md=99`) | 端部の除外幅が大きく、スタブ周りの干渉を見逃す。ドーム寸法は spec から導出すべき | 除外幅を部品ごとの実寸から決定。短尺は別の検査 | 高 |
| R9T-045 | P3 | tools/cablemodel.py L55(長さ検査は上限 ref_mm のみ) | 目視 | 「PSU付属長」が超過するのみ検出。不足(余長不足)は未検査 | 最小余長を導入 | 中 |
| R9T-046 | P3 | tools/massmodel.py L1-2(z 背面+)、tools/motion_check.py L35(ZC=-hz)、tools/gen_cad_drawings.py L52(ZC=-hz)、tools/neckgeom.py L48 | 座標系が「背面+」と「設計座標(前面ガラス=0、背面負)」で併存。変換 `ZC=-hz` が各所に重複 | PRINCIPLES の設計座標と massmodel/balance/stability が逆符号。符号反転のミスを誘発する。現状のコードの符号は一貫している(§4 の独立再計算で確認) | 変換関数を1つに | 高 |

### 2.4 台帳・運用ツール

| ID | 重大度 | ファイルと行 | 再現 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9T-047 | P2 | tools/audit_manifest.py L44(exit は `type_errs` のみ)、L36-37(`content_reviewed… = 'NO'` 固定) | 構文エラー(SYNTAX_FAIL)があっても exit 0 | 構文破損が合格に見える。ゲートがファイルを書き換える(R9T-012) | `syntax_fail` も終了コードに反映 | 高 |
| R9T-048 | P2 | audit_control/validate_state.py(run_gates.sh のゲート列に無い)、tools/task.py L10-14 | run_gates の14本に validate_state がない(CLAUDE.md は別コマンドとして列挙) | `done` の検査は evidence/verification が空でないことのみ(内容は問わない)。task.py は状態値を検証せず、`done` を証拠なしでも書ける | run_gates に追加。許容状態・証拠形式を検証 | 高 |
| R9T-049 | P2 | tools/dfm_check.py L15-16 | CP-07 以外の23部品は「未定義」を表示して exit 0 | 加工成立性を CP-07 しか見ていないのに「OK」。UNVERIFIED を exit 2 にしない | 未定義があれば exit 2 | 高 |
| R9T-050 | P2 | tools/check_sources.py L7-18(9800X3D・RTX5060Ti・FX600 の旧URL)、L22(curl の HTTP コードを判定せず)、出力 docs/source-status.md を上書き | 目視 | 現行構成(9950X3D/5070Ti/SF1000)の一次資料が監視対象に無い。CAPTCHA/エラーページも「200=取得可能」になる | URL を parts.json から生成。本文の簡易検査 | 高 |
| R9T-051 | P3 | tools/sync_wallpaper.py L9 | `/*WALL*/` が無くても `re.sub` は無変更で "wallpaper synced" を表示。置換文字列に `\` が含まれると正規表現の置換記法として解釈される(`lambda m: …` を使うべき) | 偽成功と文字化けの危険 | `subn` で件数確認、lambda 置換 | 中 |
| R9T-052 | P2 | tools/guard_no_delete.sh L4、tools/pre-commit.hook L3、tools/archive.py L58(`--diff-filter=M`)、L43-46(重複 sha を新版にしない) | `git mv docs/a.md other/a.md` は `--diff-filter=D` に出ない(R として扱われる)ため削除ガードをすり抜ける。`awk '{print $2}'` は空白を含むパスで壊れる。`archive.py auto \|\| true` は失敗を無視。保護対象に tools/・viewer/・handoff/・audit_control/ が無い。.git/hooks は追跡外(クローンで無効) | 「削除はpre-commitで拒否」が回避できる。履歴消去防止の不変条件が保証されない | `--diff-filter=DR` と `-z` 処理、hooks をリポジトリ管理(`core.hooksPath`)、CIで同検査 | 中 |
| R9T-053 | P3 | tools/__pycache__/(`git ls-files` に `.pyc` が含まれる、cpython-313) | `git ls-files tools/__pycache__` | 生成物が追跡され差分ノイズ。実行 Python が 3.11 の環境で別名 pyc が増える | .gitignore と追跡解除 | 高 |
| R9T-054 | P3 | tools/drawlib.py L12(`third` を無視して常に第三角法記号)、L7・L49-50(日付と改訂履歴 `D=v9` の固定)、txt/esc(`>` と `"` を処理しない)、note[:150]・material[:58] の黙った切り捨て | 目視 | 第一角法を指定しても記号は第三角法。改訂欄が現行版(v10)と不一致 | 記号を分岐。改訂を spec 管理 | 高 |
| R9T-055 | P3 | tools/cadviews.py L38(投影が空でも bbox=(0,0,0,0) を返す)、tools/gen_cad_drawings.py(結果の妥当性検査なし)、tools/gen_project_summary.py L23(`date.today()` で再現性なし) | 目視 | HLR 失敗で空図面が「成功」として書き出される | 空なら例外 | 中 |
| R9T-056 | P3 | tools/layout_search.py L15-17(部品寸法が旧値 gpu 120×229 等)、L56(`free` の死コード)、L61(model/ を直接上書き) | 目視 | layout.json と無関係な旧値で layout_dome.json を作る。誤実行で model/ を汚す | 廃止 or layout.json 駆動 | 高 |

## 3. 各ゲートが検証するもの/しないもの(観点4)

| ゲート | 検証する | 検証しない・限界 | UNVERIFIED の扱い |
|---|---|---|---|
| stale_check | 禁止語(旧値)の正規表現。spec.pod.total_t==dome.total_t | 数値の意味。除外語(旧/比較/置換…)があると素通り。未追跡ファイル | 該当なし |
| consistency_check | 約13項目の数値の文書間一致、md リンク切れ | `→` 等で除外、HIST は WARN のみ、handoff/.txt は対象外 | 該当なし |
| fitcheck | AABB 収まり・重なり(許可リスト有)、電力≦70%、ΔT≦20K、積層厚 | 実形状、許可ペアの重なり量、気流 | UNV を表示するが exit 0(R9T-005) |
| cablemodel | (検査ではなく model/cables.json の再生成) | 検査なし。正規データを書き換える | - |
| cable_check | 経路の AABB 干渉、曲げ半径、長さ上限、近接 | 端部21〜27mm、短尺ケーブル。**終了コード無し(R9T-002)** | 該当なし |
| stability | チルト×首振り格子の静的転倒(前後横)、傾斜10° | 動的転倒、質量実測 | 推定でも exit 0(R9T-004) |
| motion_check | 足とのすき間≧30mm、ネック×頭部のSAT掃引、ストッパ当たり、ブーツ範囲、PE長 | 摩擦ヒンジ円柱、机面、指挟みの実試験 | 「WARN」表示のみ |
| balance_calc | 重力トルクとばね・摩擦の静的釣り合い、操作力、たわみ率、細長比 | **ばね向き(R9T-001)**、ばね応力・疲労・固着長 | 型番・特性が UNVERIFIED だが exit 0 |
| swivel_calc | 軸受要求モーメント・軸力・操作力 | 実軸受定格(未設定) | exit 2(唯一の正しい扱い) |
| power_budget | DC→AC→PSU損失(恒真の保存則) | 実測 | 該当なし |
| dfm_check | CP-07 の溝/ポケット残肉 | CP-07 以外 | 未定義を exit 0 |
| strength_check | 静的・ピーク荷重の応力(SF1.5) | 疲労、FEA、ボルト予圧、ばね応力 | 注記のみで exit 0 |
| fit_tolerance | 公差窓(最悪ケース) | 窓の緩和根拠、位置公差の上側加算 | WARN 止まり |
| audit_manifest | 構文、CP型 | 内容レビュー(NO 固定) | 構文NGでも exit 0 |
| (非ゲート) thermal_calc / joint_calc / neckgeom / validate_state / gen_* | - | run_gates に入らず、生成物の鮮度ゲートも無い | - |
| 未カバーの要求 | 騒音≦38dBA、25,000回耐久、継ぎ目0.5±0.1mm・段差≦0.1mm、修理性L1〜L3、EMI/RF | 該当ゲート無し | 台帳(U)のみ |

## 4. 独立再計算の結果(観点5)

| 対象 | 方法 | 結果 |
|---|---|---|
| balance_calc: 重力トルク τg | 式 m·g·(dz·cos a + dy·sin a) とエネルギー微分 -dU_g/da | a=+40°で 18.04N·m。コード値と一致 |
| balance_calc: ばねトルク | エネルギー法 U_s=F0·(d + p·d²/2/stroke)、l=√(e²+s²-2se·cos a) | a=+40°で +15.09N·m(重力と同方向)。コードは -15.09 相当として相殺扱い → **不一致(R9T-001)** |
| balance_calc: 残差/操作力 | (最大摩擦6.264+最悪残差3.689)/0.41 | 24.28N。コード値と一致(ただし R9T-001 により前提が誤り) |
| ばね特性 | たわみ率=stroke(1+1/p)/free = 21.5/56.5 | 38%。コード値と一致 |
| stability | 手計算 tilt -15°, swivel 0: tz=26.96mm、前余裕 67.96mm、F=22.45kg·9.81·0.06796/0.5323 | 28.1N。出力28Nと一致 |
| strength_check: 吊りピン | 971N×2.5mm/(π·6³/32) | 114.5MPa。一致。ネック基台ボルト: 29.6MPa(コード 14.8)→ **不一致(R9T-015)** |
| strength_check: 尾部レバー・軸・横ピン | M=584N·25mm、Z=5·14²/6、Ø12、2荷重の重ね合わせ | 89 / 65 / 145MPa。一致 |
| fit_tolerance | ガスケット 0.098·1947=190.8N、×(c/0.33)^1.5、ラッチ T=F/6·3mm/(π/2)/0.4、はめあい寸法差 | 80.1〜284N、0.0637〜0.226N·m、0.004〜0.024mm、0〜0.019mm。一致。キーホールの最大側のみ位置公差未加算(R9T-007) |
| swivel_calc | M_static=15.35·9.81·0.1192、M_req=(17.95+24.8)·1.5 | 64N·m。一致 |
| power_budget | DC=230+300+45+16+45.44=636.4、効率0.925 | AC 688W。一致(保存則は恒真) |
| thermal 式 | ΔT=P/(ρ·cp·V) | 688W、144m³/h → 14.3K。一致 |
| 座標符号 | tilt+ で上端が背面へ。尾部は前面へ。massmodel/balance/stability/motion の各符号 | 一貫(設計座標への変換 ZC=-hz も正しい)。R9T-001 は符号でなく「ばねの向きの物理」の誤り |

## 5. 開いたファイルと未確認

- 開いて全体を読んだ(約47本): CLAUDE.md、docs/PRINCIPLES.md、tools/run_gates.sh、stale_check、consistency_check、fitcheck、cablemodel、cable_check、stability、motion_check、balance_calc、swivel_calc、power_budget、dfm_check、strength_check、fit_tolerance、audit_manifest、massmodel、neckgeom、joint_calc、thermal_calc、drawlib、cadviews、layout_search、gen_hardware_list、gen_project_summary、gen_drawing、gen_specs、gen_package、gen_mfg_drawings、gen_mechanisms、gen_handoff、gen_service_drawings、gen_cad_drawings、archive、check_sources、guard_no_delete.sh、pre-commit.hook、task、sync_wallpaper、audit_control_init、audit_control/validate_state.py、blender/hardware_v8.py。
- 一部のみ読んだ(未確認あり): tools/gen_mech_sections.py(L1-230 を読み、L230-340 は grep のみ)、tools/gen_fmea.py(全行を読んだが FMEA の個別数値の妥当性は未検証)、tools/gen_anatomy.py(L1-25 のみ。実機 iMac 24型の解説図なので旧値扱いは対象外)。
- 未確認・未実施: cadquery/ezdxf/Blender が必要な生成器(gen_cad_drawings, gen_mech_sections, gen_handoff, gen_mfg_drawings, hardware_v8)は実行していない(STEP 座標系・DXF の x 反転は読解のみ)。tools/archive/ 配下の旧版、model/*.json の全項目(spec/balance/layout/custom_parts は必要部分のみ)、docs/ 配下の全文。ばねの JIS 許容応力は一般知識による概算で規格表は未照合。Blender の build_imac_pc_v8.py のレイアウト x の取り方(R9T-033)は未確認。
- 監査中に他セッションが変更した対象: fitcheck の発熱(e7a16e1 で power_budget 参照へ修正済み。旧: L95 の電源損失10%固定でパネル発熱を含めなかった)、joint_calc の肩径(作業ツリーで spec 参照へ修正済み。旧: `sh_d = 5.0` にコメントだけ Ø6)、hardware_v8 の旧文字列(作業ツリーで spec 参照へ修正済み)、stale_check の正規表現。いずれも本表の主要項目には含めていない。

## 6. 副作用の申告(読み取り専用の例外)

- 監査冒頭で `bash tools/run_gates.sh` を実行したため、ゲート自身が `audit_output/01_FULL_FILE_MANIFEST.csv` を再生成した(R9T-012 の実例)。`model/cables.json` は内容が同一で差分なし。`tools/__pycache__/cablemodel.cpython-311.pyc` は私が生成したので削除済み。他の作業ツリーの変更は別セッションによるもので、触っていない。
- 再現スクリプトは scratchpad の `bal_indep.py`、`rep/`(tools と model の複製)、`rep2/` のみ。
