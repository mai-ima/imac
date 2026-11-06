# R9 docs/ 独立監査報告書(読み取り専用監査)

- 監査日: 2026-11-06 / 対象: /home/user/imac/docs/ 配下の現行 .md/.txt 全53件(archive/・docs/audit-log.md・spec/archive・mechanisms/archive を除く)
- 照合基準: model/spec.json, model/balance.json, model/parts.json(全文)、model/custom_parts.json(grep と一部抽出のみ。全文通読はしていない)
- 補助確認(読み取りのみ): `tools/stale_check.py`(FAIL0/WARN46)、`tools/consistency_check.py`(FAIL0/WARN11)、`tools/fitcheck.py`(標準出力のみ)、`tools/gen_mechanisms.py` 等の grep、`git ls-files` 件数
- 注意: 監査時点で作業ツリーに他セッションの未コミット変更あり(docs/mechanisms/03・05, service-mechanisms, build-guide, failure-analysis, PROJECT-SUMMARY, blender/*, audit_control/tasks.json ほか)。下記の行番号は作業ツリー(監査時点)基準。再生成後は行がずれる可能性がある。
- 重大度: P0=正規仕様と矛盾し製造・購入・設計判断を誤らせる/要件の根幹, P1=重大な不整合・旧仕様の現行文書への残存, P2=中程度, P3=軽微(誤字・用語・件数ベタ書き等)
- 正規値(照合基準): 総厚190(dome.total_t・内奥行162), 足360×310(前110/後200, ballast3.5kg), ヒンジ軸 z=45/y=10, ばね s=76 e=25 F0=730N(365N/本, 最大584N/本) p=0.6 行程8.08mm 端金物16mm(片側8mm), 尾部レバー t5×幅14×長34(spec.neck.lever_len=34), 横ピンØ8, 摩擦ヒンジ5.8N·m±8%, 操作力≦25N, チルト-15〜+40°, 首振り±60°(保持1.8N·m, ステータ r95=Ø190, ロータ r76=Ø152), ネック基台 z幅66.28, ゴムパッド厚6, 蛇腹ブーツ山10・22〜70mm, ガスケット line_force 0.098N/mm・comp_nom0.33, ラッチ6×90N+側辺フック4×40N。

## 0. 構造的な所見(個別指摘の根本原因)

1. 「生成物」とされる文書(custom-parts.md, hardware-list.md, 01〜07機構書, fitcheck-report.txt, thermal-analysis.md)が、生成元の古い入力・古い出力のまま残っている。特に **model/custom_parts.json 自体が古い値**(CP-07 外形×104, CP-20 150×150, CP-21 144×144, CP-22 124×81, CP-23 長50/M8)を保持しており、docs は忠実に古さを複製している(根は model 側。docs だけ直しても再発する)。`blender/hardware_v8.py` も同様(尾部レバー長50・横ピンØ6・ブーツ山8/10〜56mm・ステータØ110・保持1.6N·m)。
2. docs/tilt-swivel-design.md の §1,§3〜§8 は「自動生成物を含む」と称しつつ、旧版(s=65, F0=700N, 軸z=40, 足300×290)の出力を貼り付けたまま。**同名機構の正本(docs/mechanisms/01〜03)と数値が全面的に食い違う**。`tools/consistency_check.py` はこのファイルで WARN を出しているのに、ゲートは FAIL にせず放置されている。
3. `tools/stale_check.py` の HIST 許容リストが docs/bom-final, docs/logo-catalog, docs/spec/performance-benchmark, docs/unverified-tracker, docs/source-status, docs/research-* を「履歴扱い」にして FAIL から外しており、現行文書として読まれる文書の旧値残存を検出できない。また 190mm 化前の `inner = total_t - 28 # 129-28=101` というコメント/コードが stale_check 内に残る。
4. 件数・版・日付のベタ書き(U01〜U61、FMEA42項目、CP-01〜17、J01〜J18、git追跡1091件、版 v7/v9/v10 の混在)が多数。

## 1. 指摘一覧

(列: ID / 重大度 / ファイル:行 / 原文 / なぜ問題か / 修正案 / 確信度)

### 1-A. チルト・バランサ・ヒンジ関連(最重要)

| ID | 重大度 | ファイル:行 | 原文 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9D-001 | P0 | docs/tilt-swivel-design.md:20-42 (§3) | 「採用(2本合計): s=65mm e=25mm / 最長側荷重 F0=700N(1本350N, 最大 525N/本) / 荷重変化率 p=0.5 → ばね定数 20.4N/mm/本 / ストローク8.6mm … 摩擦保持 公称4.5N·m(公差±15%) … 操作力=…19.9N(目標≦20N)」 | 正本 balance.json は s=76, F0=730N, p=0.6, 行程8.08mm。摩擦は5.8N·m±8%, 操作力目標≦25N。01_tilt_balancer.md §4 と全項目が食い違う。README/system-spec/CP-11 がこのファイルを「チルト機構の詳細」として参照するため、読者が旧値を設計値と誤認する | §3 を balance_calc.py の最新出力(01 §4 と同一)で置換するか、本文を削って 01_tilt_balancer.md へのリンクのみにする。生成物は gen_mechanisms.py 側に取り込む | 高 |
| R9D-002 | P0 | docs/tilt-swivel-design.md:47 (§4 転倒安定) | 「スタンド(首振りユニット込み) 6.8kg = 22.3kg / 頭部重心 z=40 y=195 / ヒンジ軸 z=40.0 y=10.0 / 首振り軸 z=40.0 / 足 z=-56〜226 … 上端高さ 512mm」 | 正本はヒンジ軸 z=45(02_swivel.md §7 は z=45, 22.5kg, 上端532mm)。同じ解析が二つの文書で異なる値。consistency_check も WARN | 02_swivel.md §7 の出力に置換、または参照のみに | 高 |
| R9D-003 | P0 | docs/tilt-swivel-design.md:10 | 「MODIFY スタンド足 220×230 → **300×290**(前100/後190)、バラスト 2.0 → **3.0kg**」 | 現行は足360×310(前110/後200)・ballast3.5kg。§4 本文は「幅360」と書いており同一文書内でも矛盾 | 「360×310(前110/後200)・3.5kg」に更新し、履歴は付録へ | 高 |
| R9D-004 | P0 | docs/tilt-swivel-design.md:111,141-142 (付録A) | 「現行軸は z=40, y=10」(L142) / 「現行は文末「v9 更新」と docs/tilt-swivel-design.md」(L111) | 現行軸は z=45。付録の「現行」記述自体が旧値(z=40)で、さらに自己参照(本ファイルが本ファイルを参照)。ユーザー指定の最重要定数(z=45/y=10)に反する | z=45 へ訂正。L111 の参照先を 01_tilt_balancer.md に変更 | 高 |
| R9D-005 | P1 | docs/tilt-swivel-design.md:42,43,102 | 「荷重±10%…摩擦ヒンジ(合計6N·m)」「ばね軸は−19°〜+9°揺動するため…テレスコ式ガイドが必要」「ばね座に荷重調整ねじ(M8)」 | 正本: 摩擦5.8N·m, 揺動-16〜+7°, 案内なし自立(01 §4), 調整はアンカーブリッジ長穴±3mm+押しねじM5(01 §3)。テレスコ式ガイド(=旧ガイドロッド)・M8調整ねじは旧仕様 | 旧記述を削除し 01 へ誘導 | 高 |
| R9D-006 | P1 | docs/tilt-swivel-design.md:18,84,85,103 | 「首振り用170mm・ヒンジ用90mmのループ…」「U52 首振り保持トルク1.6N·m」「U53 … 1.6N·m÷0.31m≈5N」 | 首振り保持トルクは spec.swivel.holding_torque_Nm=1.8(02_swivel.md は1.8→5.8N)。1.6/5N は旧値。tracker U52/U53 も同様 | 1.8N·m/5.8N に統一 | 高 |
| R9D-007 | P1 | docs/tilt-swivel-design.md:99 | 「ロータをØ144、ネック基台t8(124×72)をM5×4で固定」 | spec.swivel.rotor_r=76→Ø152, 基台 z幅=66.28(02/03 は 124×66.28)。Ø144/72 は旧 | Ø152, 124×66.3 に訂正 | 高 |
| R9D-008 | P1 | docs/tilt-swivel-design.md:100 | 「尾部レバー(t5×幅14×長50)」 | spec.neck.lever_len=34(01_tilt_balancer.md §3 は長34)。長50は旧 | 長34 | 高 |
| R9D-009 | P1 | docs/tilt-swivel-design.md:69,72,81 | 「頭部最低点の足上面からの最小すき間 48.5mm」「スラブ下縁-カバー上端の最小すき間 3.2mm … 35段階 → [WARN] 蛇腹ブーツ/ガード未設計(U53)」「R-sw 指挟み保護が未設計」 | 03/06 は「すき間 22.8〜67.2mm・4段階・蛇腹ブーツ設計済 [OK]」「最小すき間32.5mm」。ブーツは spec.neck.boot で設計済みなのに本書は「未設計」。旧出力 | 03 §4 の出力へ置換、R-sw を「ブーツ設計済(U53で試験待ち)」に | 高 |
| R9D-010 | P1 | docs/tilt-swivel-design.md:38,63 (§4) 「ACコード…最小≈93N」 | 02_swivel.md §7 は 85N、最小転倒角 12.3°(本書 12.9°)、最悪 前28/後34/横36(02 は 28/33/35) | 同一計算の二重管理で値が不一致 | R9D-002 と同じ | 高 |
| R9D-011 | P1 | docs/tilt-swivel-design.md:107-143 (付録A) | 見出し「# ヒンジ(チルト機構)設計 v1」「### 結論: カウンターバランス+対称摩擦ヒンジ…定荷重ばね…」「Reell PHL/PHC級の対称トルクヒンジ(2〜4個)」「質量は layout 由来の massmodel(13.7kg)」 | 注記で旧版と断っているが、定荷重ばね/カム案・z=43/38・-5〜+25°・「操作≤20N」が現行文書本体に長文で残り、検索・引用で現行値と誤認されやすい。stale_check が WARN | 付録Aを archive へ移す(スタブ化)か、全段落に【旧】接頭辞を付ける | 中 |
| R9D-012 | P1 | docs/tilt-swivel-design.md:2,9,9 他 | 付録A冒頭「(旧 tilt-swivel-design.md を統合)」(L107) | 実際に統合されたのは hinge-design.md(docs/hinge-design.md スタブは「tilt-swivel-design.md(付録A)に統合」と記載)。名称の取り違え | 「旧 hinge-design.md」に訂正 | 高 |
| R9D-013 | P1 | docs/mechanisms/03_neck_and_load_path.md:19 | 「−15°側: レバー側縁 z=−(50·sin15°+7·cos15°)=約−19.7 … +40°側: z=50·sin40°+7·cos40°=約37.5 … パッドはゴム(厚≈2mm)」 | spec.neck.lever_len=34, pad_thick=6。生成器 tools/gen_mechanisms.py:144 は既に lever_len・pad_thick を参照する形に修正済みで、出力(docs)が再生成されていない。34 で計算すると約−15.6/+23.5(パッド近面 -15.06/26.2 と整合)。50 は旧値 | `python3 tools/gen_mechanisms.py` で再生成し、手編集を残さない | 高 |
| R9D-014 | P1 | docs/mechanisms/01_tilt_balancer.md:11 vs :63 vs :81 | §1「落下エネルギー約0.95J、…レバー応力33MPa」/§6「落下E≒0.95J, ω≈1.6rad/s」/§7「落下E=0.52J(I=0.78kg·m², ω≈1.2rad/s) … 応力 36 MPa」 | 同一文書内で単一故障時のエネルギー・角速度・応力が3箇所で食い違う(§1,§6 は手書き固定、§7 のみ計算値) | §1,§6 を strength_check 出力から埋め込む | 高 |
| R9D-015 | P1 | docs/mechanisms/01_tilt_balancer.md:63 | 「ばねは折損しても飛散しないガイド筒内」 | §4 は「案内なしで自立」「ガイド不要」と説明しており、ガイド筒は旧ガイドロッド方式の残存。構造も部品表(§3)に無い(記述だけの機構) | 「ガイド筒」を削除、または§3 に部品として追加 | 高 |
| R9D-016 | P2 | docs/mechanisms/01_tilt_balancer.md:8 vs :47 | §1「(最大摩擦+公称残差)/0.41m で評価」/§4「(最大摩擦+最悪残差)/0.41 = 24.3N」 | 評価式が文書内で食い違う(公称残差なら (6.26+3.24)/0.41=23.2N)。tilt-swivel-design.md:102 も「公称残差」。07 は「最悪」。24.3N が正規出力 | 式を「最悪残差」に統一 | 高 |
| R9D-017 | P2 | docs/mechanisms/01_tilt_balancer.md:8,47 / 07_fits_and_feel.md:17-18 | 「操作力≦25N」(旧20Nから変更。07は「要ユーザー確認」) | 24.3N/25N の余裕は2.8%、経年-30%後保持は最小摩擦3.74N·m対最悪残差3.69N·m(余裕1.4%)で07がWARN。01 §1 は「要求」として確定表記だが根拠は未承認(spec.hinge.doc に「根拠は要ユーザー確認」)。PRINCIPLES A6(片手で滑らか)と20→25N緩和の承認が未記録 | 01 §1 に「未承認の暫定値」と明記し、audit-log に決定記録。余裕確保の再設計案(摩擦の±8%→±5%等)を併記 | 中 |
| R9D-018 | P2 | docs/mechanisms/01_tilt_balancer.md:30 vs tilt-swivel-design.md:22 | 「頭部 m=15.4kg dz=1 dy=185mm」 / 「dz=-0」 | 同じ頭部の重心オフセット dz が文書間で1 vs 0。さらに joint-analysis は 重心 z=46/dz=1, tilt-swivel §4 は z=40 | dz=1(z=46)に統一 | 中 |
| R9D-019 | P2 | docs/mechanisms/01_tilt_balancer.md:20 | 「ばね端金物(上:ロッドエンド / 下:トラニオン) 片側8mm…荷重調整は…押しねじM5」 vs spec.json hinge.balance_note「荷重調整ねじ(M8)」 | 端金物16mmは整合(片側8mm×2)。調整手段が文書により「押しねじM5/長穴±3mm」「M8調整ねじ」で食い違い(M8は旧ばね座ねじ)。model/spec.json:balance_note, docs/spec/hardware-list.md:18, custom-parts.md:28,402, tilt-swivel-design.md:102 が M8 | M8 を M5押しねじ+アンカーブリッジに全箇所統一 | 高 |
| R9D-020 | P2 | docs/mechanisms/01_tilt_balancer.md:24 | 「摩擦ヒンジ Reell PHL/PHC級(最大3.4N·m×2を想定)」で保持5.8N·m | 3.4×2=6.8N·m が上限、設計5.8±8%(5.34〜6.26)は PHL 範囲内だが「0.9〜3.4」の根拠調整機構(摩擦ヒンジの「調整式」化。spec.hinge.doc「調整式の摩擦ヒンジ」)が部品表に無い=調整機構が記述のみ | 摩擦調整ねじ等の調整部品を§3に追加するか「調整式」を削除 | 中 |

### 1-B. 特注部品仕様 custom-parts.md / hardware-list.md / hole-table.md / joint-matrix.md / standard-parts.md

| ID | 重大度 | ファイル:行 | 原文 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9D-021 | P0 | docs/spec/custom-parts.md:13,150,154 (CP-07) | 「596×377.3×104」「縁の内奥行6mm→内面最大101mm(smoothstep, run 64mm)、外面最大総厚はスラブ25+104=129」 | 現行は総厚190(内奥行162)。製造図の根拠となる特注部品表のドーム深さが旧値(129/101)。model/custom_parts.json も同値で、fitcheck 等は spec を使うため整合ゲートで拾えない。ドームはホース垂直出口のため深さ拡大が主要変更点 | CP-07 外形深さ=165(190-25)、内面最大162、総厚190。custom_parts.json を修正して再生成 | 高 |
| R9D-022 | P0 | docs/spec/custom-parts.md:25-26,355,370 (CP-20/21) | CP-20「150×150」「Ø150×t6ステータ…ストッパポスト(Ø10鋼芯, r78, ±66.6°)」/ CP-21「144×144」「Ø144×t6ロータ…ストッパタブ半径64〜82」 | spec.swivel: stator_r=95(Ø190), rotor_r=76(Ø152), stop_r=86。02_swivel.md は Ø190/Ø152/r86/±66.7°。軸受OD100に対しステータØ150では PCD90 の M5×6 が収まるが stop_r 78 は旧。製造部品の外形・ストッパ半径がずれる | CP-20: Ø190 r86 ±66.7°, CP-21: Ø152 に更新(custom_parts.json から) | 高 |
| R9D-023 | P1 | docs/spec/custom-parts.md:27,385,389 (CP-22) | 「124×81」「基台t8 124×72」 | 基台 z幅=66.28(02: 124×66.2784, 03: z -28.06〜38.22)。72/81 は旧 | 124×66.3 | 高 |
| R9D-024 | P1 | docs/spec/custom-parts.md:28,402,412,413 (CP-23) | 「レバー SUS304 t5×幅14×長50」「外形50×14」「調整ねじ M8」「ばね軸は-19〜+9°揺動」「寿命: 25,000回(行程8.6mm)」 | 長34・押しねじM5・揺動-16〜+7°・行程8.08mm(balance.json, 01 §3-4)。旧値 | 正値へ。custom_parts.json 修正 | 高 |
| R9D-025 | P1 | docs/spec/custom-parts.md:17,223 (CP-11) | 「合計保持6N·m」 | 摩擦保持は5.8N·m±8% | 5.8N·m | 高 |
| R9D-026 | P1 | docs/spec/custom-parts.md:216 (CP-10) | 「チルト保持トルク最大±7.5〜20N·m(質量実測前)」「未解決: … 足幅の拡大」 | 旧質量見積りの値。現行最大は+40°で約18.0N·m(01 §4)、足は既に360×310に拡大済み。さらに相手部品に「CP-11ヒンジ」とあるがヒンジはネック上(足へはCP-20経由) | 値・未解決項目を更新、相手部品を CP-20 に | 高 |
| R9D-027 | P1 | docs/spec/custom-parts.md:10 vs :91,96 vs :102,106 | 表「頭Ø10×4」/L91「頭Ø10×4」/L96「頭Ø10×t3(頭高さを3に統一)」/L106「未解決: 肩径5mm品の品番/せん断強度」/表L10「肩長3.0」 vs model/custom_parts.json「肩径Ø6 h8×6.0(支圧部=トレイ+ブッシュ3.0)」 | 頭高4/3、肩長3.0/6.0が文書内・json との間で不一致。肩径5mm品は旧(Ø6へ変更済と同一エントリL102に明記)なのに「未解決」に残存。05_tray は「肩Ø6 h8×3.0・頭Ø10×t3」 | 頭t3・肩長を一本化(jsonの6.0なら支圧部設計を再確認)。L106 を削除 | 中 |
| R9D-028 | P1 | docs/spec/custom-parts.md:69,102 | CP-03「トレイ吊りピン座M3×4(肩径5mm)」 vs CP-04「背板M4(PEM TSOA)」 | 同一ファイル内で背板側ピン座がM3/Ø5(旧)とM4/Ø6(現行)で矛盾。hole-table.md:30,32 も「背板M3(ピン)」 | CP-03 を M4(TSOA) に、hole-table の見出しも M4 に | 高 |
| R9D-029 | P1 | docs/spec/standard-parts.md:12 / docs/service-mechanisms.md:16 / docs/build-guide.md:10 / docs/joint-analysis.md:48-50 | 「ショルダーねじ M3×Ø5 h8×3.0」「SUS肩ねじ M3・肩径Ø5…0.8N·m」「ピン肩径5.0mmのせん断応力 1.7 MPa」 | 現行(CP-04/05機構書/J04/hardware-list)は M4・肩Ø6・1.7N·m。Ø5は強度不成立(199MPa)で廃止済み(CP-04 L102)。standard-parts(調達リスト)が旧のまま=誤発注リスク。stale_check の検出語に無い | 全て M4×Ø6 に更新し joint_calc の肩径も 6.0 に | 高 |
| R9D-030 | P2 | docs/spec/custom-parts.md:143 / docs/mechanisms/05_tray_hanging_service.md:5,15 / docs/joint-analysis.md:7,48 / docs/service-mechanisms.md:28 | 「総質量約6.2kg」(CP-06)/「約6.6kg」(05, service-manual:15, service-mechanisms)/「6.9kg」(joint-analysis §3, 1019N/1699N) | トレイ質量が3種。30G荷重(1942N/2025N/…)と1点荷重が変わる | massmodel から一本化して生成 | 高 |
| R9D-031 | P2 | docs/mechanisms/05_tray_hanging_service.md:15 vs 03:39, 01:77, custom-parts.md:102 | 「上側2点のみ…1点約978N」「曲げ約114MPa」 | strength_check 出力は「971N/点」「114MPa」。CP-04 は 978N/115MPa。6.6kg×30G/2=971N が正。数値が3通り | 971N/114MPa に統一 | 高 |
| R9D-032 | P2 | docs/spec/joint-matrix.md:8 | 「30G: せん断50MPa/支圧65MPa」 | 05 は「せん断≈35MPa/支圧約54MPa」、joint-analysis は 51.9/68MPa(6.9kg, Ø5)。J04 は Ø6 と書きながら Ø5 計算の値 | 05 の値(Ø6)に更新 | 中 |
| R9D-033 | P1 | docs/spec/hardware-list.md:23 | 「尾部レバー SUS304 t5×幅14×長50 (e=25mm)+横ピン Ø6」 | 正本: 長34・横ピンØ8(SUS630)。同表L20 は「両端揺動ピン(Ø8 17-4PH)」で自己矛盾。元は blender/hardware_v8.py / hardware_list.json | 長34, 横ピンØ8 に修正し生成器から再出力 | 高 |
| R9D-034 | P1 | docs/spec/hardware-list.md:19 | 「ゴム蛇腹ブーツ(シリコーン UL94 V-0, 山8, 伸縮10〜56mm)」 | spec.neck.boot: 山10, 22〜70mm。06_pinch_guard.md も 山10/22〜70 | 山10, 22〜70mm | 高 |
| R9D-035 | P1 | docs/spec/hardware-list.md:40 | 「ステータ板・ロータ板 A5052 Ø110×t6 … 保持トルク1.6N·m」 | Ø190/Ø152, 1.8N·m | 修正 | 高 |
| R9D-036 | P2 | docs/spec/hardware-list.md:20,22 | 「ばね軸は±19°揺動するため両端ピン支持のテレスコ式ガイドが必要」/「ヒンジ軸 Ø12 SUS×150」 | 01: -16〜+7°・案内なし・軸×132(D03)。ガイド(旧ガイドロッド)残存、軸長150 vs 132 | 修正 | 高 |
| R9D-037 | P2 | docs/spec/hardware-list.md:7-8 vs standard-parts.md:11 vs service-mechanisms.md:18 | スタンドオフ「14+4」(計18)/「約60」/「約40」 | 同じ部品の数量が3通り | hardware_list.json を正として他を参照 | 中 |
| R9D-038 | P2 | docs/spec/hardware-list.md:10,14 vs standard-parts.md:16 | 「SPCCストライク Niめっき t1.2 12(ラッチ6+フック6)」「磁石相手 SUSディスク φ9×1.0(背板側) 12」 vs standard-parts「ストライク SPCC t1.2…磁石の相手」 | 磁石の相手がSPCCストライクかSUSディスクか不明。ストライクはラッチ/フック用との記述もあり二重定義。SUS304/316 は非磁性寄りで磁石相手に不適の恐れ(SUS430でない限り) | 磁石相手の材質を一本化(SPCC or SUS430) | 中 |
| R9D-039 | P2 | docs/spec/hardware-list.md:36 vs custom-parts.md:21 | 「ケーブルクリップ(POM) 7」 vs CP-16「数量 24」 | 数量不一致 | 一本化 | 中 |
| R9D-040 | P2 | docs/spec/hole-table.md:39-40,43 vs custom-parts.md:158,155 | hole-table「下辺スロット: I/O 120×28 / GPU出力 142×26 / AC 32×32」「パーフォレーション…縁から39.0mm」 vs CP-07「I/Oスロット120×22 / GPU 142×20 / AC 32×26」「縁から36mm内側」 | 同じ開口寸法が二つの文書で異なる | 正本をどちらかに決め生成元を一本化 | 高 |
| R9D-041 | P1 | docs/spec/hole-table.md:40 / custom-parts.md:156,199 / 04:8 / joint-matrix.md:11 / hardware-list.md:13 / service-manual.md:8 | 「上辺フック爪 14×7 ×6」「上辺フック6点が反力を受ける」 | spec.dome_seal.side_hooks=4(各40N, 左右辺の掛け爪)と fit_tolerance.py の容量計算(6×90+4×40=700N)は「側辺フック×4」前提だが、docs 全体に側辺フックの記述・穴位置・部品行が一切ない。07 だけが「側辺フック4×40N」。→ 容量計算にだけ存在し、図面/部品表/ホール表に無い機構(記述だけ/実体無し) | CP-07/CP-09/hole-table/hardware-list/J07 に側辺フック×4 を追加、または spec とfit_toleranceの前提を削る | 高 |
| R9D-042 | P2 | docs/spec/joint-matrix.md:11 vs spec.dome_seal / 04:10 | 「ラッチ60N以上/点×6」「閉合力≤約340N(U30)」(service-mechanisms F11 も60N以上) | 04/CP-09/spec は 90N/点、最大反力225〜284N(低閉合力ガスケット)。60N・340N は旧ガスケット(0.175N/mm)案 | 90N/点・最大284N に更新 | 高 |
| R9D-043 | P2 | docs/spec/custom-parts.md:178-183 (CP-08) vs spec.json dome_seal | 「線荷重 ≦0.08N/mm @圧縮30% … 公称156N/最大225N(spec.dome_seal)」 | spec.dome_seal は line_force_N_per_mm=0.098(191N), comp_nom=0.33(33%)。「(spec.dome_seal)」と出典を示しながら値が一致しない。04 §2 も 30%/156N/225N、07 は圧縮18.5〜43%・80〜284N(spec ベース)。最大反力 225N vs 284N で「ラッチ容量≧反力×1.5」の基準が 337N(04,CP-09) と 426N(07) | spec 値(0.098, 33%, 最大284N)で CP-08/04/CP-09 を再生成 | 高 |
| R9D-044 | P2 | docs/mechanisms/04_dome_latch_gasket.md:10 vs 07:12 | 「回転トルク0.08〜0.18N·m」 vs 「0.0637〜0.226N·m」 | 同じラッチのトルク範囲が不一致(CP-09も0.08〜0.18) | 07 の計算値に合わせる | 高 |
| R9D-045 | P2 | docs/spec/custom-parts.md:152 | 「ガスケット反力最大約340N(要低圧縮)」(CP-07 荷重/条件) | CP-08 は最大225N、07は284N。340Nは不採用の旧案 | 更新 | 高 |
| R9D-046 | P2 | docs/spec/custom-parts.md:18,252 vs hardware-list.md:35 / failure-analysis.md:17 | CP-12「設計(未実装:Blender/図面未反映)」vs hardware-list「RF窓 PC樹脂t2.0 … 1」(3Dに描画している部品の一覧に掲載)/FMEA#11「未設計→TODO」 | RF窓が「実装済」(hardware-list は「3Dモデルに実際に描画している」と宣言)か「未実装」かが矛盾。無線性能の成立性(U31)が記述のみ | 実態を確認し両方を揃える | 中 |
| R9D-047 | P2 | docs/spec/custom-parts.md:166 | CP-07 相手部品「CP-13フィルタドロワー」 vs CP-13「黒メッシュフィルタ(ドーム内面追従の殻)」 | 用語ゆれ(ドロワー=旧引出式フィルタ、現行は磁石保持の殻) | 「フィルタ(殻)」に統一(failure-analysis#35「磁石式スライドフィルタ」も) | 高 |
| R9D-048 | P2 | docs/spec/custom-parts.md:136 vs :125, build-guide.md:10, 05:13 | CP-06 加工「角R18」/形状「角R38(ドーム内角に合わせる)」/05「角R38」/build-guide「角R18」 | R18とR38が同居 | R38に統一(build-guide も) | 中 |
| R9D-049 | P3 | docs/spec/custom-parts.md:68-77 | 「アース端子(M4, 皮膜マスク)」と「アース端子スタッド M4」、「アンビリカル貫通開口(30×10)」と「アンビリカル貫通開口 30×10」が重複記載 | 重複項目 | 重複削除 | 高 |
| R9D-050 | P2 | docs/spec/README.md:6,4,14 | 「特注部品CP-01〜17」「接合J01〜J18」「v7」「drawings/01〜16」 | 実際は CP-01〜CP-24(CP-15欠番)、J01〜J19。README が旧件数のまま(ベタ書き)。docs/README.md からリンクもされていない | 件数を書かず「custom-parts.md 参照」に。CP-15 は欠番と明記 | 高 |
| R9D-051 | P3 | docs/spec/custom-parts.md:3 | 「色=spec.json palette」 | OK だが `fastener_plating=SUS304(A2-70)` は A2-70 は SUS304 相当の強度区分で、並記は混乱を招く表記(軽微) | 「SUS(A2-70)」へ | 低 |
| R9D-052 | P2 | docs/spec/grounding-spec.md:6-13 / joint-matrix.md:19 / CP-18 | grounding-spec の構成図に首振り跨ぎ編組(170mm)・ヒンジ跨ぎ編組(90mm)が無い(「ヒンジブロック/スタンド」に編組1本)。J19は「編組×2→背板→編組×2→ドーム/ヒンジ」 | v9 で首振り軸が追加されたのに PE 系統の仕様書が v7 のまま。tilt-swivel/02 は編組ループ、model/pe_braids.json は存在。接地導通≤0.1Ωの設計根拠が仕様書に無い | grounding-spec と CP-18 に跨ぎ編組を追記 | 中 |

### 1-C. 機構書 02〜07、およびシステム仕様

| ID | 重大度 | ファイル:行 | 原文 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9D-053 | P1 | docs/mechanisms/06_pinch_guard.md:19-25 vs 03:25 | 06「-15°: 22.7 … +40°: 65.3」 vs 03「すき間 22.8〜67.2mm(最小: チルト-15°)」 | 同じすき間範囲が文書間で22.7/22.8, 65.3/67.2 と不一致(最大はブーツ範囲70mmとの余裕に関わる) | 同一関数から生成 | 高 |
| R9D-054 | P2 | docs/mechanisms/03_neck_and_load_path.md:25,30 | 「蛇腹ブーツで隙間を塞ぐ設計 [OK(範囲内)]」と、直後 L30「総合: OK(…挟み込みはWARN)」 | 同一出力ブロック内で OK と WARN が併存。ゲート文言の旧文字列が残存 | motion_check の総合文言を現状に合わせる | 中 |
| R9D-055 | P2 | docs/mechanisms/07_fits_and_feel.md:31,34 vs :12,14 | 窓の根拠表「吊りピン隙間 0.05〜0.20mm」「ヒンジ軸隙間 0〜0.04mm」 vs 判定「窓 0.05〜0.6mm」「窓 0〜0.02mm」 | 判定結果の窓と根拠表の窓が異なる(基準を緩めた/変えた経緯が無い=偽PASS懸念)。吊りピン窓を0.20→0.6に広げた理由は判定行の注にしか無い | 根拠表を判定の窓に同期し、緩和理由を記録 | 高 |
| R9D-056 | P2 | docs/mechanisms/02_swivel.md:25 vs spec.json fits | 「μ=0.1(PTFE)〜0.15(ゴム系)」 | spec.fits.swivel_mu=[0.1,0.18]。343〜514Nも 0.15 基準で、0.18 の場合は 286N | μ範囲を spec に合わせる | 中 |
| R9D-057 | P3 | docs/mechanisms/02_swivel.md:45 | 「足 z=-51〜231 幅360」(区間282mm) | 足は奥行310(前110/後200)。282mm は支持多角形(ゴム脚外接)と思われるが説明が無く、足寸法と読み違える | 「(ゴム脚外接)」と注記 | 中 |
| R9D-058 | P2 | docs/mechanisms/02_swivel.md:20 / 03:6 | ネック基台「t8 124×66.2784」 | 4桁小数のまま露出(下の桁は意味のない丸め前値)。他箇所は 66.3 | 小数1桁に | 中 |
| R9D-059 | P1 | docs/spec/system-spec.md:15 vs :28 | L15「ラジエーターP12 Pro×2は外気直吸気。ケースファン無し: 正圧のプレナムを全面格子とPSU/GPUファンで排気」 vs L28「ドームの六角穴(約32%開口)で吸排気、ラジエーター排気/GPU吸気/ケース排気の3経路」 | 冷却方式が同一文書内で矛盾(外気直吸気+正圧 vs ラジエーター排気3経路)。「六角穴」は v6 の局所穴で、v7 以降は Ø2.4千鳥の全面格子(design-philosophy §3。開口率33%)。32% vs 33% も不一致 | v7 以降の方式に統一 | 高 |
| R9D-060 | P1 | docs/spec/system-spec.md:19 | 「GPUは5060 Ti 16GBが上回る見込み」 | GPUは5070 Ti に変更済み(同ファイルL11)。比較基準行のみ旧GPU。performance-benchmark.md:5,8 も 5060 Ti | 5070 Ti(再計測要)に更新 | 高 |
| R9D-061 | P1 | docs/spec/system-spec.md:18 / gaming-requirements.md:12 / fitcheck-report.txt:18 / thermal-analysis.md:16 | 「ピーク約611W(CPU230+GPU300+他45+パネル36), PSU使用率61%」 | 現行 fitcheck.py 出力は「他61+パネル45 = 636W 使用率64%」、thermal は「≈630W・63%」、gaming-requirements は発熱636W、thermal 発熱合計688W(AC)、fitcheck 発熱655W。電力収支の数値が5通り | power_budget.py を単一源として全文書に埋め込む | 高 |
| R9D-062 | P2 | docs/spec/system-spec.md:1,4 | タイトル「システム仕様書 v7 (2026-11-05)」 | 内容は v9/v10(首振り、ドーム190)。docs/README は「現行: v9」。版表記の混在(v7/v9/v10)。README が「仕様の正本」と位置付ける文書の版が古い | 版・日付を現行に | 中 |
| R9D-063 | P2 | docs/spec/system-spec.md:41,43 | 「FMEA42項目」「U01〜U61。件数は台帳が正: 手書きしない」 | FMEA は46件。台帳は U01〜U60(U61 欠落)。「手書きしない」と書きながら手書き | 件数を削除して台帳参照のみ | 高 |
| R9D-064 | P1 | docs/unverified-tracker.md (全体) vs spec.json:219 / 07:9 / system-spec.md:43 | spec.dome_seal.doc「(U61)」、07「根拠はメーカー確認 U61」、system-spec「U01〜U61」 | 台帳に U61 が存在しない。参照先不在(壊れた参照) | U61 を台帳に追加(ガスケット下限線荷重0.04N/mmの根拠確認) | 高 |
| R9D-065 | P2 | docs/spec/system-spec.md:35 | 「着脱 … 前面モジュール20回」/CP-02「組立/分解20回」 | 前面モジュールは接着一体で分解不可(P1, J02廃止, service-manual G)。試験項目が実体の無い機構を対象にしている | 項目削除 | 中 |
| R9D-066 | P3 | docs/spec/system-spec.md:22 | 「背面ドーム最大総厚190mm(縁の内奥行6mm, 傾斜64mm)(縁は薄く…)」 | 括弧が二重で読みにくい | 文整理 | 低 |

### 1-D. 旧仕様の残存(整備・製作・熱・配線)

| ID | 重大度 | ファイル:行 | 原文 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9D-067 | P0 | docs/service-mechanisms.md:40 | 「ヒンジ軸は重心の背面側(z=43mm, y=10mm)」 | 正規は z=45。stale_check の禁止パターン `z\s*=\s*43\b` は「z=43mm」では語境界(\b)が成立せず検出されない(ゲートの正規表現の欠陥)。整備書の取付位置の根拠 | z=45 に修正(原因: 作業ツリーでの編集が反映途中の可能性もあるため再確認) | 高 |
| R9D-068 | P1 | docs/service-mechanisms.md:36 / failure-analysis.md:11,37 / (spec.cooler.note) | 「ホース出口はポンプの下向き」「ホース出口を下向き」「ホース出口方向を下向き(実装済)」 | spec/parts.json/wiring/ U57: ホース出口は上面から垂直(+z)。下向きは旧(誤)モデル。FMEA#5,#31 の対策が成立しない | 「上面垂直出口+曲げ半径確保(総厚190化)」に更新 | 高 |
| R9D-069 | P1 | docs/service-mechanisms.md:28,31,25 (§3.2,§3.3) vs 05:16,CP-17:22,panel-driver:17, J18 | 「アンビリカル(250mm …)」「余長250mm=トレイを100mm引いても届く長さ」 vs 05/CP-17/W5「全長380mm(経路約270+整備余長100)」 | アンビリカル長が250 vs 380。panel-driver・J18・service-mechanisms は250のまま。250では「100mm引き出し」条件を満たさない(経路274mm>250) | 380に統一 | 高 |
| R9D-070 | P1 | docs/service-mechanisms.md:26 vs spec.dome_seal | 「EMIガスケット(圧縮30%程度の低閉合力品, ≤0.175N/mm)」 | 0.175N/mm は不採用の旧案(04,CP-08)。採用は≦0.08〜0.098N/mm。FMEA#9「低圧縮ガスケット(≤0.175N/mm)」「上辺フック6点」も同様 | 更新 | 高 |
| R9D-071 | P1 | docs/failure-analysis.md:39 (#33) | 「CGが高い(15.5kg)、足が小さい … 足を幅260×奥行245へ」 | 足は360×310(旧260×245/220×215)。質量も15.5kg(頭部のみ15.4kg、スタンド込みは22.5kg)。service-manual:5「本体は約15.5kg(スタンド込)」も不正(スタンド込22.5kg)=2人作業の判断根拠に関わる | 360×310、スタンド込み約22.5kg に | 高 |
| R9D-072 | P2 | docs/failure-analysis.md:20 (#14) / thermal | 「温度分離(8mm空間)」 | パネル背面〜背板は空気層4.0mm+断熱3.0mm(panel-thermal v7.2)。8mmは根拠不明の旧値 | 現行に | 中 |
| R9D-073 | P2 | docs/failure-analysis.md (全体) | FMEA 46件 | ばね1本折損(01 §6で最重要の単一故障)、首振り軸受(ガタ/予圧抜け)、蛇腹ブーツ破損、ストッパ破損、PE編組の断線が行として存在しない(01/02 に抜粋のみ)。FMEA の網羅性欠落で RPN 順位が機能しない | gen_fmea.py に追加 | 中 |
| R9D-074 | P1 | docs/spec/panel-thermal.md:22,21 (v7.2表) | 「ドーム総厚 116mm → 129mm(内奥行101mm…)」 | 現行190mm/162mm。表は履歴だが「v7.2」止まりで現行値への注記が無く、ドーム総厚の根拠文書として読まれる(総厚190の主張とずれる) | 「(v8 以降は 190mm、spec.json 参照)」を併記 | 中 |
| R9D-075 | P1 | docs/spec/design-philosophy.md:36 | 「厚み116mmの根本的な薄型化(…不可能に近い)」「縁内奥行6mm・傾斜70mm」「スタンド足を260×245→300×290(v9。旧220×215)(+鋼板ballast 2kg…」「最大傾斜約65°→40°以内へ」 | 監査記録(R3時点)だが、足寸法は「v9」とまで書きつつ現行(360×310, 3.5kg)と一致せず、run は64mm(70は旧)。現行設計書としては混乱 | 「[R3 時点の記録]」と明示し現行値を併記 | 中 |
| R9D-076 | P1 | docs/fitcheck-report.txt:4,5,6-14,19,20,21 | 「ポッド内寸 590.0 x 371.3 x 101.0 mm」「前面スラブ厚 … 隙間1.0 … = 18.3」「PCIe補助電源: GPU 8ピン x1 <- SF750 の 6+2 ピン」「パネル電源 … SF750」「発熱636W」 | 現行 fitcheck.py の実行結果は 奥行162.0、12V-2x6(UNV)、SF1000、電力636W/64%、発熱655W。docs のレポートは再生成されておらず旧仕様(101/SF750/8ピン)を現行成果物として提示 | `python3 tools/fitcheck.py > docs/fitcheck-report.txt` を run_gates に組込み | 高 |
| R9D-077 | P2 | tools/fitcheck.py (出力) / docs/fitcheck-report.txt:4 vs spec.json:v7_notes, CP-02 | 「前面スラブ厚: ガラス1.1+エアギャップ0.9+パネル13.3+隙間1.0+背板2.0 = 18.3 <= 25.0 (余裕6.7)」 | 正規スタックは 24.3(空気層4.0+断熱3.0を含む)で余裕0.7。fitcheck の式が旧(隙間1.0)のため「余裕6.7」と誤った安心を与える | fitcheck のスタック式を spec(CP-02)に合わせる | 高 |
| R9D-078 | P1 | docs/spec/panel-driver.md:17,19 | 「ハーネス全長250mm(整備余長込み)」「12V供給: W4(SATA/周辺, 59mm設計)」 | 380mm(CP-17/W5)・W4 は24mm(wiring.md)。旧値 | 380mm / 24mm | 高 |
| R9D-079 | P1 | docs/wiring.md:11,12 / spec/wiring-spec.md:12,13 / service-mechanisms.md:34 / failure-analysis.md:44(#38) / standard-parts.md:6 | W6「設計長456」「内部延長600mm級」 vs 「C13(約576mm経路)」「経路576mm」「約600mm」 | ACケーブル長が456/576/600の3通り | cables.json 由来の値に統一 | 中 |
| R9D-080 | P2 | docs/wiring.md:11 / wiring-spec.md:12 | 「全長380mm=整備余長100mm込み=整備余長込み」 | 同義語が重複(生成文字列の連結ミス) | 生成器の文字列修正 | 高 |
| R9D-081 | P2 | docs/wiring.md:13 / wiring-spec.md:14 | W7「ctrl_board 映像入力(…型番未確定 U51)」 | U51 は台帳上「ダイスプリング型番」。ID 衝突(W7用の未確認項目は別番号が必要) | 新規 U 番号を採番 | 高 |
| R9D-082 | P2 | docs/spec/wiring-spec.md:72,81 | 「PCIe 6+2: 12V×3 / GND×5(8ピン)。GPU TGP 180W+PCIeスロット75W上限」「番号タグ(W1〜W5)」 | GPUは12V-2x6(TGP300W)でW3は12V-2x6。W1〜W7+H1,H2 まで存在 | 12V-2x6 の記述・W1〜W7 に | 高 |
| R9D-083 | P2 | docs/wiring.md:18 / wiring-spec.md:8-16 | 「最小曲げ半径: 24p/EPS/PCIe は線外径の6倍以上(約30mm)」と表の「W2 20mm(外径の約6倍)」「W1 30mm(外径の約6倍)」 vs research-notes.md:70「外径の3〜4倍(ATX24=30mm, EPS/PCIe=20mm)」 | 同じ30mm/20mmの根拠が「6倍」と「3〜4倍」で食い違う。ホースは research-notes「75mm以上(6×OD)」vs wiring「40mm仮置き」で不一致 | 根拠倍率とホース半径を一本化(U45) | 中 |
| R9D-084 | P2 | docs/research-notes.md:59 | 「12V-2x6/12VHPWR(参考: 本機は8ピン使用)」 | GPUは12V-2x6(W3, parts.json)。service-manual.md:18「8ピンを抜く」・fitcheck-report も8ピン | 12V-2x6 に統一(service-manual D も) | 高 |
| R9D-085 | P2 | docs/thermal-analysis.md:12,13,14 | 「51.603603603603574」「45.44444444444444」「688.048048048048」 | 丸め無しの浮動小数がそのまま表に出ている(生成器の書式指定漏れ)。「DC 636W→AC 688W」の差(PSU損失)を発熱に含める点は fitcheck(655W)・gaming-requirements(636W)と不統一 | `:.0f` 指定、発熱定義を統一 | 高 |
| R9D-086 | P2 | docs/thermal-analysis.md:19 vs :36 vs system-spec.md:15 | 「正圧でグリルとケースファンから排出」 | 「ケースファン無し」(system-spec/fitcheck)と矛盾。不合格時対策の「ケースファン増設(2基)」(L44)と整合させるなら「現状ケースファン0」と明記すべき | 用語統一 | 中 |
| R9D-087 | P2 | docs/mechanisms/05_tray_hanging_service.md:16 / build-guide.md:21 vs service-manual.md:15 | 05「アンビリカル(全長380mm、整備余長100mm込み)」/ build-guide「W5(アンビリカル)」 vs service-manual C「トレイを12mm持ち上げ…背面へ約100mm引く」 | 引き出し量100mmは整合。ただし service-mechanisms の250mmと衝突(R9D-069)。ここは整合 | (参考) | 低 |
| R9D-088 | P1 | docs/joint-analysis.md:61,57-59 | 「EMIガスケット閉合力 0.175N/mm=341N …磁石12個は約84N(未検証)で不足。ガスケットを低圧縮…計6点以上」 | 04/CP-08 では低閉合力品(0.08〜0.098N/mm)採用で結論が変わっている。本書は旧結論を「結論」として保持。さらに「4分の1回転ラッチ…上側にも増設して計6点」は現行(下辺6+上辺フック6)と異なる説明 | joint_calc.py の出力を更新 | 高 |
| R9D-089 | P2 | docs/joint-analysis.md:25-45 | 質量表「重心 z=46mm, y=195mm」、§2 の保持トルク表が -5〜+25° のみ、「問題: 最大 11.9 N·m」、改善案B「dy 185→100…約6.5N·m」 | チルト範囲は-15〜+40°(最大18.0N·m)。表と問題提起が旧範囲のまま。「採用 ヒンジ軸 z=40mm」(L42)も z=45 違反(consistency_check WARN) | 表を-15〜+40°で再生成、z=45 に | 高 |
| R9D-090 | P2 | docs/joint-analysis.md:6 | 「## 1. 質量見積り(v6)」 | 現行は SF1000 等を含み v9 以降。版表示が古い | 版名更新 | 低 |
| R9D-091 | P2 | docs/build-guide.md:12 | 「スタンド+ヒンジ A6063 押出+定トルクヒンジ / CNC / 硬質アルマイト / 図面05 / 切削加工業者+市販ヒンジ」 | 現行はダイスプリング2本+尾部レバー+対称摩擦ヒンジ(調整式)+クロスローラ軸受の首振りユニット。「定トルクヒンジ」は旧(U20 も「定トルクヒンジ」)。外注区分に軸受/ばね/摩擦ヒンジの調達が無い | 製法表をCP-10/20〜23に合わせ更新 | 高 |
| R9D-092 | P2 | docs/build-guide.md:21-22,25 | 「吊りピン×4(M3・肩径Ø5 肩ねじ, 0.8N·m)」「接地編組(CP-18)と導通」「ヒンジブロック(貫通M6×4…6N·m)」「吊りピン」 | M4・Ø6・1.7N·m が現行(R9D-029)。組立順にスタンド(首振りユニット・バランサ調整)の工程が無い(01 §5 の組立調整手順が build-guide に未統合) | 更新 | 高 |
| R9D-093 | P2 | docs/build-guide.md:35 | 「残: DIMM2枚の厚み…ホース曲げ半径…」 | U49/U57 のホース関連は「ドーム深さ拡大で曲げ代確保」(spec.dome._note_v10)と状態が変わっているが台帳は「設計課題」のまま(下記R9D-099) | 更新 | 中 |
| R9D-094 | P1 | docs/service-manual.md:5,8,9 | 「本体は約15.5kg(スタンド込)」「下辺ラッチ6点…上辺フックを外す」 | スタンド込22.5kg(joint-analysis)。重量表示は安全上の注意(2人作業)の根拠 | 22.5kg(頭部15.4kg+スタンド7.1kg) | 高 |
| R9D-095 | P2 | docs/service-manual.md:2 | 「旧版: docs/archive/service-manual/」 | 存在確認OK(リンク切れではない)。ただし版は「v7」のまま(バランサ調整・首振りユニット・蛇腹ブーツ交換の手順が無い。01 §5 の調整手順は L3 整備だが service-manual に未記載) | H節に追記 | 中 |
| R9D-096 | P2 | docs/service-mechanisms.md:3,43,1 | 「(v7, 2026-11-05 全面改訂)」「変更履歴(v6→v7)」「肩ねじM3.5×4→M3×Ø5」 | 現行は M4×Ø6(R9D-029)。変更履歴自体が現行と逆行。stale_check 非検出 | 履歴は別節に隔離し現行値を表示 | 高 |

### 1-E. 台帳・索引・要約・調査ノート・履歴文書

| ID | 重大度 | ファイル:行 | 原文 | なぜ問題か | 修正案 | 確信度 |
|---|---|---|---|---|---|---|
| R9D-097 | P2 | docs/unverified-tracker.md:57-61 | U50〜U54 の行が5列(「次に試す取得先」列が無い)で、L56 の空行で表が分断されヘッダ無しの別表になる | 表レンダリング崩れ(最終列がずれて「最終確認」が「状態」列に入る) | 列を揃え空行を除く | 高 |
| R9D-098 | P2 | docs/unverified-tracker.md:50-53,57,58,59 | U51「行程8.6mm…荷重変化率35%」U52「保持トルク1.6N·m」U53「約5N@画面端」 | 現行 行程8.08mm/p=0.6/1.8N·m/5.8N(07 では 3.84〜9.35N)。台帳の数値が旧 | 更新 | 高 |
| R9D-099 | P2 | docs/unverified-tracker.md:55,64,25(U49,U57,U23) | U49「ラジエーター下端〜ドーム縁の余地が約24mm…設計課題」U57「ドーム内奥行101mmでは曲げ代が取れない可能性」 | ドームは190mm/内奥行162に拡大済み(spec._note_v10, fitcheck「ホース上端149.2 >=5mm」[OK])。状態が「設計課題」のまま=対応済の記録が無い(曲げ半径U45は未確認のまま) | 状態を「190mm化で幾何成立。曲げ半径はU45待ち」に | 高 |
| R9D-100 | P2 | docs/unverified-tracker.md:11-14,40,42,26,10 | U05(9800X3D), U06/U07/U36(5060 Ti), U34(SF750), U02「NH-L12Sとの干渉」, U20「定トルクヒンジ」, U25「13.3kg推定 vs 19kg」, U28「ヒンジ軸のz位置最適化 未実施」 | 項目名が旧部品・旧状態。U28 は z=45 で確定済(spec.v7_notes)。U25 は 15.4kg が現行推定。U44 は「調査中」だがCPUは9950X3Dに決定済 | 「不採用/解消」ステータスを付け現行項目に置換 | 高 |
| R9D-101 | P3 | docs/unverified-tracker.md:3 vs PRINCIPLES.md:21 | 「定期的に再調査して更新する」 vs 「5時間ごとに再調査(8日間)」 | 頻度の記述が不一致。U01〜U22 の最終確認が 11/03 のままで、5時間周期の履歴証跡が無い(PRINCIPLES B6 が記述だけの仕組み) | 台帳に再調査ログ列を追加するか、頻度記述を統一 | 中 |
| R9D-102 | P2 | docs/PROJECT-SUMMARY.md:5-8,11-13,23,26 | 「git追跡 1091件 = 現行 311 + 履歴archive 780」「drawings 46」「未確認事項 60件」 | 監査時点の git ls-files は 1105件(archive 740)、drawings 48。自動生成物だがコミットとずれる(件数ベタ書き)。system-spec は U01〜U61 と書き 60 と不一致 | 生成をゲートに組込むか件数を記載しない | 高 |
| R9D-103 | P3 | docs/PROJECT-SUMMARY.md:41,58,127-161 | 一行要約が「docs/drawings/py/svg/viewer」「drawings/parts/CP」等、パス区切りで切れた断片、および basename のみの一覧 | 要約の自動抽出の不具合(区切り文字 "/" で文を切断)と、ディレクトリ接頭辞無しの列挙でリンク先が曖昧 | 要約を2文目まで取る/フルパス表記 | 中 |
| R9D-104 | P3 | docs/PROJECT-SUMMARY.md:161,157-159 | 「blender/build_imac_pc.py」「build_imac_pc_v6.py」「build_imac_pc_v8.py」の3版並置の役割が不明 | 旧版は archive へ移す方針(CLAUDE.md)に反して blender/ 直下に残る(読者が現行版を判別できない) | 旧版を archive へ移動(削除はしない) | 中 |
| R9D-105 | P3 | docs/README.md:11,27 | L11「旧: …service-mechanisms.md / service-manual.md / build-guide.md」だが system-spec・spec/README は現行扱い。L27「design.md(v4の旧設計。冒頭に「旧版」注記)」 | design.md の冒頭に「旧版」注記が実際には無い(タイトルが「v4」とあるのみ)。README の記述だけで注記が無い | design.md 冒頭に旧版注記を追加、README の分類を整理 | 高 |
| R9D-106 | P3 | docs/README.md:1-30 | spec/README.md への導線が無い。「現行: v9」と各文書 v7 が混在 | 孤立ファイル(spec/README.md はこの索引以外から辿れない/内容も旧) | 索引に追加 or spec/README を廃止スタブ化 | 中 |
| R9D-107 | P1 | docs/design.md:4,9,12,16 | 「前面スラブ18mm」「Flex ATX電源」「安価なB650I系ボード、Ryzen 5 7600」「背面メッシュ吸気+上下スリット(実形状の穴)」「背面左下の縦スロット4つ」「cad/imac_like_pc.scad: 旧設計・27型反映未了」 | 現行スラブ25, PSU=SFX SF1000, CPU=9950X3D, 通気=Ø2.4全面格子, ポート開口=3スロット(design-philosophy)。README は「冒頭に旧版注記」とするが実際には無く、現行文書として読まれる | 冒頭に【旧版 v4】注記+現行値への誘導 | 高 |
| R9D-108 | P2 | docs/design.md:5 | 「総厚190mm(spec.json)」と L4「前面スラブ18mm」が同居 | 同一文書内で新旧が混在(総厚は更新済で他が旧)。190-18=172 ≠ 内奥行162+3 | スラブ25に | 高 |
| R9D-109 | P1 | docs/anatomy.md:34 / research-notes.md:136 | 「背面ポッドに集約(70mm厚)」「前面14mm+背面ポッドで総厚70mm」 | 総厚190mm(consistency_check WARN)。「ポッド」も旧名称(現行は「ドーム」。spec.json の pod.* は legacy) | 190mm・「ドーム」に | 高 |
| R9D-110 | P3 | docs/design.md:12,anatomy.md:34, audit-criteria.md:37, fitcheck-report.txt:5 | 用語「ポッド」 | 「ドーム」と「ポッド」「ポッド内寸」が混在(spec.json は pod.* を legacy としK01で一本化済み) | 「ドーム内寸」に統一 | 高 |
| R9D-111 | P2 | docs/spec/performance-benchmark.md:5-8,18,25 | 「RTX 5060 Ti 16GB は M6 内蔵GPUを大きく上回る」「Ryzen 7 9800X3D…」「電源使用率65%(491W/750W)」「発熱増(約504W)」 | 決定後(9950X3D・5070 Ti・SF1000)の最新値(636W/64%)に更新されていない。「要点」が決定前の結論(9800X3Dでは満たせない)のまま先頭に残り、現行判断が読み取れない。日付も「2026-11-05調査」だが「M6 2026-11-06発売」と記載(日付前後関係) | 先頭に「決定: 9950X3D」「5070 Ti」を置き、旧比較は【履歴】に | 高 |
| R9D-112 | P3 | docs/spec/cost-estimate.md:13,10 | 「本機は確認できた主要4点(CPU+MB+PSU旧+GPU旧)だけで約35.1万円」「Noctua NF-A12x25r参考」 | 旧PSU・旧GPUを含む合計をiMac比較に使っている(現行構成の合計ではない)。Noctuaは不採用部品 | 現行構成(SF1000/5070 Ti)で再集計または未確認と明記 | 中 |
| R9D-113 | P2 | docs/logo-catalog.md:7,11,39-47 | 「AMD Ryzen 7 9800X3D (IHS刻印)」「ASUS Dual GeForce RTX 5060 Ti 16GB OC」 | 現行BOMはRyzen 9 9950X3D/PNY 5070 Ti。確認済み項目が不採用部品で、現行部品のロゴ・刻印が未確認(U15)。見出し構造も「調査中」の後に「確認済」小節が続く | 現行部品の調査へ置換し旧は履歴に | 高 |
| R9D-114 | P3 | docs/source-status.md:1,7-11 | 「(2026-11-03 13:46)」U04 NH-L12S / U05 9800X3D / U06 5060Ti / U08 FX600 | 取得結果が3日前、旧部品を含む。「追記」で不採用と書くが表は残る。現行部品(SF1000/ARCTIC 非RGB/PNY)の取得状況が無い | check_sources.py で再生成 | 中 |
| R9D-115 | P3 | docs/research-notes.md:5-8 | 見出し「## 1.」直下に「## 保持トルク」「m=19kg…軸z=63…当方の概算 m=13.3kg」 | 見出しレベル不統一(##が章と節で混在)。数値は調査時点の旧質量(現行15.4kg)で注記なし | 見出し修正、「[調査時点]」を明記 | 中 |
| R9D-116 | P2 | docs/research-notes.md:39,41-42 | 「→実在値「<1 lb/in ≈ 0.175N/mm」を joint_calc の閉合力計算に採用…ラッチ増設が必要」「M3ねじ・肩径5mmへ見直し」 | 現行採用と逆(低閉合力品0.08N/mm、M4×Ø6)。調査→設計反映の最新状況が無く、結論欄が旧 | 「D. 本設計への反映」に最新決定を追記 | 中 |
| R9D-117 | P3 | docs/spec/gaming-requirements.md:1,10 | 「サブエージェント調査」「model/layout.json v8」 | 版表示が v8(現行 v9/v10)。「判定」の根拠がレビュー未取得(暫定)と自己記載。GPU寸法は報道2件(HotHardware/GamesRadar)のみで、PRINCIPLES B1「非公式は5件以上一致」を満たさないまま設計の寸法基準になっている | 5件ルール未達の旨を明記(parts.json は assumed で整合) | 中 |
| R9D-118 | P3 | docs/spec/panel-thermal.md:10,28 | 「現設計(v7.1)の問題」「設計変更(v7.2)」 | 版表記が古いまま(現行 v9/v10)。「35℃環境でも48℃以下」「合格≤40℃(25℃)」は目標値で整合 | 版表記整理 | 低 |
| R9D-119 | P3 | docs/mechanisms/README.md:13 vs CLAUDE.md | 「model/custom_parts.json が単一源」と明記しているが、実際は custom_parts.json 自体が古い(構造的所見1) | 「単一源」宣言が実態と乖離 | custom_parts.json 更新後に宣言を維持 | 中 |
| R9D-120 | P3 | docs/spec/system-spec.md:26 | 「L3パネル/スタンド」 | service-manual では スタンド/ヒンジが H(L3)、パネル G(L3)。OK。ただし 02 の「予圧調整は整備時」「ばね調整は整備者(L3)のみ」は整備マニュアルに手順無し(R9D-095) | (参考) | 低 |
| R9D-121 | P3 | docs/audit-criteria.md:10,22,37 | 「B: 寸法±0.5mm超〜±2mm」と「全部品の外形が公式寸法と一致(±0.5mm)」、用語「ポッド」 | 基準自体は整合。ただし「ループは全カテゴリが A になるまで終了しない」(L3)と現行台帳(UNVERIFIED多数)で終了条件が成立しないまま運用。条件文に「U残存時の扱い」を明記すべき | 終了条件の運用規則を整理 | 低 |
| R9D-122 | P3 | docs/spec/hole-table.md:3 / panel-driver.md:2 | 「規格値/仮値(U17/U29)を含む」「監査C-10対応」「K10追加」等の内部管理記号が本文に露出 | 外部業者提出物(handoff)に流用される場合に意味不明。軽微 | 用語集または脚注 | 低 |
| R9D-123 | P3 | docs/spec/gaming-requirements.md:12 vs thermal-analysis.md:23-25 | 「CPU 83℃推定→要再計算」 | thermal-analysis で再計算済(83℃/再循環で97℃超過)。要再計算の注記が残存 | 注記更新 | 中 |
| R9D-124 | P3 | docs/spec/standard-parts.md:6 / 12 / wiring-spec.md:13 | 「内部延長C13(約600mm)」 | R9D-079。W6 設計456mm で実長整合を要確認 | R9D-079 と同時修正 | 低 |
| R9D-125 | P3 | docs/spec/design-philosophy.md:36-37, 39-43 | P2 の判定「不適合/適合」表(v6→v7)に現行(v9以降)の首振りユニット・ブーツ・蛇腹の露出外観(P1/P2 適合性)の再判定が無い | ネック・ブーツ(シリコーン)・首振り軸は外面に見える部品。PRINCIPLES A1/A4(外面締結なし/塗装で偽装しない/連続曲面)に対する再監査記録が無い | v9 後の適合監査を追記 | 中 |

## 2. 件数サマリ

- 総計 125 件(うち R9D-087 は参考(整合確認)、R9D-120/124 は参考・低)
- 重大度: P0 = 7 / P1 = 40 / P2 = 56 / P3 = 22 (自己集計: 表の重大度列の集計)
- 分類別(重複あり): 数値矛盾 72, 旧仕様残存 31(うち 9800X3D/SF750/5060Ti 系 8, M8調整ねじ/ガイドロッド系 6, 足220/260系 3, z=40/43 系 5), 壊れた参照/参照先不在 3 (U61, tilt-swivel の自己参照, PROJECT-SUMMARY 断片), 未実装・記述だけの機構 7 (側辺フック×4, 摩擦ヒンジ調整機構, ばねガイド筒, RF窓実装状態, 前面モジュール20回試験, PE跨ぎ編組の仕様書欠落, PRINCIPLES B6 の5時間再調査), 軽微(誤字・用語・書式・件数ベタ書き) 25

(注) 「リンク切れ」は docs/ 内の Markdown リンクと主要バッククォート参照を機械検査した結果、実在しないパスは 0(docs/spec/grounding-spec.md:9 の `皮膜マスク` は括弧付き本文で誤検出)。壊れているのは「U61」等の論理参照のみ。

## 3. 確認範囲(偽の確認をしない)

### 3-1. 実際に開いて読んだファイル(計 53 + 照合基準)
docs/ 現行 53 件(すべて Read/cat で全文確認):
PRINCIPLES.md, README.md, PROJECT-SUMMARY.md, design.md, anatomy.md, bom-final.md, build-guide.md, service-manual.md, service-mechanisms.md, tilt-swivel-design.md, joint-analysis.md, wiring.md, thermal-analysis.md, failure-analysis.md, fitcheck-report.txt, source-status.md, audit-criteria.md, unverified-tracker.md, logo-catalog.md, research-notes.md, 統合スタブ10件(research-joints, design-v6, selection-v5, hinge-design, research-hinge, research-cables, bom-verified, research, model-pipeline, design-package-index), mechanisms/ 8件(README, 01〜07), spec/ 15件(README, system-spec, design-philosophy, gaming-requirements, performance-benchmark, cost-estimate, hardware-list, hole-table, joint-matrix, panel-driver, panel-thermal, grounding-spec, standard-parts, custom-parts, wiring-spec)。
照合基準: CLAUDE.md(先頭150行全文), model/spec.json(全文), model/balance.json(全文), model/parts.json(全文。通読は圧縮出力で実施)。
補助: tools/stale_check.py・consistency_check.py・fitcheck.py の実行出力、tools/stale_check.py の冒頭40行、gen_mechanisms.py・neckgeom.py 等の grep、`git ls-files`/`git status` の件数確認、docs内リンクの機械検査。

### 3-2. 未確認・未通読(明示)
- 除外指定: docs/audit-log.md, docs/archive/**, docs/spec/archive/**, docs/mechanisms/archive/**(指示により対象外。存在確認のみ)
- model/custom_parts.json: 全文は読んでいない(CP-04/06/07/20〜23 の size/material と数カ所の grep のみ)。「json 自体が古い」は上記抽出範囲での確認であり、他の CP の値は未検証
- model/hardware_list.json: 行数(34)と数量計(138)の確認のみ。各行の値は未通読(hardware-list.md が json の忠実な出力と仮定)
- model/cables.json, layout*.json, pump.json, pe_braids.json, hardware_list.json の各値: 未通読(W6=456 等はdocs間の相互矛盾としてのみ指摘。cables.json との突合は未実施)
- audit_control/SESSION_STATE.md, tasks.json, audit_output/*, tools/*.py の全文(grep範囲を除く), blender/*.py(grep範囲を除く), drawings/*, handoff/*: 未通読。CP-04 の md と json の差(肩長3.0/6.0)は json 側の変更が未再生成の可能性があり、他セッションの作業ツリー変更中のため確度「中」
- 3Dモデル/図面との照合、実機・試験が必要な項目: 実施していない(UNVERIFIED のまま)

### 3-3. 確度に関する留意
- R9D-067 の検出漏れ理由: stale_check.py の正規表現 `z\s*=\s*43\b` は直後が「mm」だと \b が成立せずマッチしない(推定、コード読みによる。実際のマッチ試験は未実施)。service-mechanisms.md:40 に z=43mm が現存することは確認済み。
- 重大度 P0 は「ユーザー指定の最重要定数(総厚190・足360×310・軸z=45/y=10・ばね s=76/e=25/F0=730N 等)に直接反する値が、現行の主要文書で設計値として提示されているもの」に限定した。
