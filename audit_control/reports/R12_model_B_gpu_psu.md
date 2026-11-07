# R12 モデル監査B: GPU / ライザー / PSU (Blender v8) — 超厳格監査 (2026-11-07)

## 1. 監査方法
- 読取専用。対象は blender/build_imac_pc_v8.py L586-646(ライザー/GPU/PSU)、L268-293(make_fan)、model/parts.json(gpu/riser/psu)、model/layout.json(同3件)、model/cables.json(W1〜W7)。ibox引数は (name, w=x, h=y, d=z, x, y, z下端, mat, bevel) と読み、全座標はこれで解釈した。
- 数値は layout.json: gpu pos[262,47.2,8] size[150,290,40]、riser pos[230,67,8]、psu pos[70,218,8] size[125,100,63.5]、board pos[60,30,11.35](Z1=12.95)。
- 実物根拠(今回取得)。公式=A、非公式=B(5件一致未満はUNVERIFIED扱い)。
  - A1 PNY公式 https://www.pny.com/geforce-rtx-5070-ti-slim-models : 型番VCG5070T16DFSXPB1-O、290x150x40mm、2スロット、16-pin補助電源、DP2.1b x3 + HDMI2.1b、PCIe5.0 x16、デュアルファン。ファン径・枚数・コネクタ位置は記載なし。
  - A2 PNYプレス https://www.pny.com/company/press-center/pny-press-releases/pny-announces-new-dual-slot-slim-models-for-nvidia-geforce-rtx-50-series (検索スニペットのみ、本文未取得)。
  - B1 Akiba PC Watch(実機レビュー, 日本語) https://akiba-pc.watch.impress.co.jp/docs/parts_review/showcase/2129282.html : ファン約120mm x2、12V-2x6はカード天面で「約40mm奥まった位置」(解釈はUNVERIFIED)、金属バックプレート片側に大開口でヒートシンク露出、全黒でLEDなし、基板は約170x112mm(片側ファンは基板に被らない)、150mmはPCIe端子からクーラー最上部、ブラケット側へ約45mm突出。
  - B2 Vortez/LetsDataScience(検索スニペット): 120mmデュアルファン。
  - A3 Puget Systems(販売ページ, 準一次) https://www.pugetsystems.com/parts/Power-Supply/Corsair-SF1000-Platinum-1000W-SFX-Power-Supply-15841/ : CP-9020257-NA、W125xH63.5xD100mm、Molex4/SATA8/PCIe 8pin 4/12V-2x6 1/EPS 2、92mmファン(ゼロRPM)。
  - B3 KitGuru https://www.kitguru.net/components/power-supplies/zardon/corsair-sf1000-platinum-2024-psu-review/all/1 : モジュラー部は3段で全てラベル付き、Type-5 Micro-Fit、ファンNR092P 92mm FDB、全黒に銀/白文字、ラベルのレール値83.3A。ソケット総数は記載なし。
  - B4 Caseking https://www.caseking.de/en/corsair-sf-series-sf1000-sfx-power-supply-80-plus-platinum-atx-3.1-pcie-5.1-1-000-watts-black/NECS-179.html : 12V-2x6/PCIeケーブル400mm、SATA445mm。
  - LINKUP AVA5 v2 AG-P5-33SS-020BK-v2: 実在(heise https://preisvergleich.heise.de/linkup-ava5-v2-riser-kabel-ag-p5-33ss-020bk-v2-a3400918.html、200mm直線)。ケーブル幅/厚/曲げ半径は公式未取得 → UNVERIFIED。
- 取得失敗: Corsair公式(403)、12V-2x6/DP/HDMIレセプタクルの規格寸法(PCI-SIG CEM 5.1/VESA/HDMI仕様はこの環境で未取得 → 寸法はUNVERIFIED)。実写真の目視比較はできていない(テキスト記述のみ)。
- 型番: parts.json の SF1000 / LINKUP AVA5 / PNY 5070 Ti Slim は実在を確認(PNYは具体SKU VCG5070T16DFSXPB1-O まで確定可能。parts.jsonが「購入前に確定 U46」としているのは古い)。ただし parts.json psu.sources の URL は SF750(cp-9020284)で SF1000(cp-9020257)ではない=出典不一致。

## 2. 指摘表
| ID | 重大度 | 対象オブジェクト | 問題 | 実物の根拠 | 具体的な修正案 |
|---|---|---|---|---|---|
| MDB-001 | P0 | cable_W3 / gpu_12v2x6 | W3終端 (372,335,55) がコネクタ箱 (x372-394,y315.2-324.2,z38-48) と一致しない。y方向に10.8mm超過、zが7mm上で浮く。しかもケーブルは y294→335 とカード内側から外へ向かい、プラグが刺さる向きでない。コネクタ嵌合が成立していない | 12V-2x6プラグは受口へ軸方向に挿入し、後方35mm直線が必要(cablemodel.py W3注記)。A1 16-pin | 受口の挿入軸を決め(後述MDB-004)、W3終点=プラグ前面を受口開口面に一致、後方35mm直線を挿入軸上に取る。cablemodel.pyのGPU側端点をgpu_12v2x6の開口中心から自動算出し、cable_check.pyに「端点が受口箱内/面上にあるか」判定を追加 |
| MDB-002 | P0 | riser0-5 / riser_plug / riser_gpu_conn | リボン実長が約44mm(ベジェ4点を数値積分)。実物は全長200mm(heise)。残り約150mmの余長の置き場・折り畳み・曲げ半径が未モデルで、実物のライザーでない(干渉検査もこの形に対して行われており無効) | heise: 200mm直線品。幅・最小曲げ半径は未取得でUNVERIFIED | 200mm相当の経路(スロット→上昇→ループ→GPUエッジ)を作る。幅を実測しUNVERIFIEDを解消するまで、経路長=200mmを満たす制約をtools側に追加。長さ検査(ribbon実長=200±2)をゲート化 |
| MDB-003 | P1 | gpu_edge / gpu_pcb | PCIeエッジ x gx-1.2〜gx+1.8 に対しPCB開始 gx+5 → 3.2mmの隙間で浮く。z は gz+3.4〜5.2 でPCB(gz+1.6〜3.2)の上に0.2mmずれて板厚外。エッジはPCBの一部であるべき | PCIe CEM: カードエッジ=PCB板厚1.57±0.1mm。89mm長、金指 | gpu_edge を x gx+5-3(PCBから張り出す)でなくPCBを gx-1.2 まで延長し、エッジ z=gz+1.6 厚1.6、金指は表裏に別メッシュ(幅0.9mm・間隔0.7mm程度、UNVERIFIED)。ブラケット基準位置も合わせる |
| MDB-004 | P1 | riser_gpu_conn | 6x89x8 の黒い箱。GPUエッジがこの中へ挿入されていない(箱 x254.5-260.5、エッジ x260.8〜)。スロット開口・ラッチ・向きが無い。板基板側 pcie_x16(8.6x89x11)と寸法体系が不一致(6 vs 8.6, 8 vs 11) | PCIe x16スロット=高さ約11mm、89mm長、中央にキー(基板側 pcie_x16 の寸法が正) | GPU側コネクタを pcie_x16 と同寸(8.6x89x11)にし、エッジが7mm以上差し込まれる位置にx配置。溝(スロット)を黒箱にBoolean、片側ラッチ爪を追加 |
| MDB-005 | P1 | riser_plug | 板側ブロックが z=Z1+11〜+23 で、スロット上面(Z1+11)の「上に載る」だけ。リボン基板端がスロットに入っていない | pcie_x16 は z Z1〜Z1+11 | プラグ下端を Z1+11-7 まで埋め込み(エッジ挿入深さ。値はPCIe規格で要確認)。スロット側にキー溝、ラッチ解放ボタンを追加 |
| MDB-006 | P1 | riser0-5 | 6本の12mm帯が15mmピッチ、3mm隙間。実物AVA5の形状(単一幅広フラット/複数帯、シールド、端のラミネート)は未確認。素材'rubber'の単色で質感差 | 公式写真未取得 UNVERIFIED | LINKUP公式画像を取得して帯数・幅を確定。確定まで6本分割を「仮」と台帳に注記 |
| MDB-007 | P1 | gpu_pcb | PCBが GW-10 x GL-20 = 140x270、全面を覆う。実物は約170x112(PCIe端子含む)で、片側ファンは基板に被らない非対称構造。内部が全く異なる | B1 | PCBを 112(x) x 170(y) 程度に縮小しエッジ側(x=gx)に寄せ、残りの領域はヒートシンクとファンのみの貫通構造。寸法はB1が非公式1件のためUNVERIFIED、複数レビューで裏取りする |
| MDB-008 | P1 | gpu_heatsink / gpu_hpipe0-4 | ヒートシンクは単なる金属色の直方体(fin無し)、ヒートパイプはその内部に埋まり不可視。バックプレート開口(16個の90x8穴)から見えるのは平らな塊 | B1: バックプレートに大開口でヒートシンク露出 | ヒートシンクを縦フィン(厚0.3mm・ピッチ1.8mm程度、UNVERIFIED)のArray modifierで生成、開口部から見える範囲だけでよい。ヒートパイプはフィン上端へ貫通させ径6/8mmの扁平管を2〜3本、曲げ付き |
| MDB-009 | P1 | gpu_backplate | 16本の90x8mm矩形スリットが規則配置。実物は「片側に大開口」(B1)。全体も150x290の素の平板で、実物の外形(縁の段、ネジ位置)と異なる | B1 | 開口を実写真から輪郭トレース(1〜2個の大開口)、ネジ頭(皿)を4〜6本追加。写真未入手のため形状はUNVERIFIED |
| MDB-010 | P1 | gpu_shroud_body / fan_gpu0,1 | シュラウドは150x290x13の箱+円穴2個。実物は基板外へ張り出すファン非対称、面取り、リブ、ロゴ以外全黒(B1)。ファン穴Ø108+ファン110角枠。実物は約120mmファン(B1,B2) | B1, B2 | ファンを120mmに変更(open_kも再計算)。穴径Ø112程度、中心間隔は実物写真で採寸。シュラウドは縁を斜め面取りし、ファン側の輪郭を段差付きに |
| MDB-011 | P1 | fan_gpu0,1 (make_fan) | ブレード11枚・形状はラジエーター用汎用生成の使い回し。PNY実機の枚数・形状は未確認。枠(frame)はレンダリング非表示で良いが、軸受・ハブのロゴなし/回転方向なども未確認 | 枚数はA1/B1に記載なし → UNVERIFIED | 実機写真で枚数確定(ファン上面写真3件以上)。確定までUNVERIFIED表示。ブレードは翼型断面(ねじれ付き)に |
| MDB-012 | P1 | gpu_12v2x6 | 22x9x10の単なる黒箱。位置も「想定」(コメント)。実物は天面で、B1によれば約40mm奥まった位置(解釈未確定)。16ピン受口形状(2段ピン穴、サイドバンド/センスピン、ラッチ窓)が無い。箱上面 z=48 とシュラウド上面が同一でケーブルの挿入空間がない | B1(位置はUNVERIFIED)、A1(16-pin) | 受口をPCI-SIG CEM 5.1図面の外形で作る(寸法はUNVERIFIED、取得後に確定)。内部に16ピン穴(4x3.0mm間隔、UNVERIFIED)と4個の小センスピン穴。ケース側面にラッチ用の突起。位置はレビュー写真で確定 |
| MDB-013 | P1 | gpu_12v2x6 周辺 | プラグ挿抜空間: 後方35mm直線 + 曲げの経路が、カード上面 z=48 とドーム内面(DOME_DEPTH 90)の間に収まるか未検査。ケーブルは下からPSUへ引き回す(B1) | cablemodel注記: 後方35mm直線 | cable_check.pyにプラグ外形(ハウジング約?mm、UNVERIFIED)をスイープして近傍部品との距離を計算する項目を追加 |
| MDB-014 | P1 | gpu_bracket / gpu_port0-3 | ブラケットは150x1.5x42の素の鋼板色。ポートは3mm厚の黒箱で、ブラケットから1.5mm突出し(ブラケット y-1.5〜0、ポート y-3〜0)、奥のPCB(y+12)まで空洞。実物は板に開いた穴の奥に金属シェルのレセプタクル。通気孔も無い。ブラケット色は未確認 | HDMI/DPレセプタクル寸法はUNVERIFIED(VESA/HDMI仕様未取得)。出力数はA1で確認(DP x3 + HDMI x1) | ポート部をブラケットにBooleanで台形穴(DP=一角欠けの長方形、HDMI=台形)を開け、奥行き約15〜20mm(UNVERIFIED)の金属シェルを配置。PCB基準で z をPCB上面+に合わせる |
| MDB-015 | P2 | gpu_port0-3 | 並びは HDMI,DP,DP,DP の順・ピッチ28mmで決め打ち。実機の順序・ピッチ(DPとHDMIの間隔は通常20mm未満)の根拠なし。z位置 gz+7(PCB上面 gz+3.2 から3.8mm上で浮く) | 順序/ピッチ: UNVERIFIED(Akiba写真未確認) | 実機写真で順序を確定。ピッチはレセプタクル幅+2〜3mm程度の密配置に。zはPCB上面に載せる |
| MDB-016 | P2 | gpu_bracket | 取付フランジ(カード側の折り曲げ、固定ネジ穴)がない。2スロット幅は42mmで妥当(2スロット=約40.6〜41.4)だが長辺150は実際のブラケット高さ(通常約120mm前後+突出約45mm、B1)と整合する確認なし | B1: ブラケット側へ約45mm突出 | ブラケット高さをPCIe端子基準で定義、ネジ穴Ø3.5と折り返し爪を追加 |
| MDB-017 | P2 | gpu_trim | 2基のファン間の銀アクセント帯 1.6x13.1mm。PNY実機は「一部のロゴを除きオールブラック」(B1)であり、銀の帯は実物と相違の可能性が高い | B1 | 実機写真で確認し、無ければ削除して黒のリブに変更 |
| MDB-018 | P2 | gpu_shroud(材質) | 色#17181b粗さ.15・バンプ。実物の質感(マット/シボ)は未確認 | UNVERIFIED | 実写真の反射を確認して粗さを決定 |
| MDB-019 | P2 | gpu 全体 | LED/ロゴ/刻印: 実物は一部ロゴあり(B1)だがロゴは思想上描かない。レンダリングで判別不能になる点を許容できるか台帳でルール化が必要 | B1 | ロゴ位置にロゴ無しの凹み(段差のみ)を作り、台帳に「ロゴ省略」を明記 |
| MDB-020 | P1 | psu_body | 125x100x63.5の中実箱+bevel 1.5。ファンは箱内部に埋没(fan z54〜62 < 上面63.5)で穴がない。実物のSFXは折り板金で稜線は鋭く、ファン開口と通気孔がある | A3, B3 | 上面にØ約90の開口をBoolean、板厚0.8mmの薄肉シェルに。bevel 0.3程度に。内部のファンを見せる |
| MDB-021 | P1 | psu_grille_ring1-4 / psu_grille_spokes | グリルが z=64.2 で本体上面63.5から0.7mm浮く。スポーク6本は同一平面の直方体で厚み0.5 | B3(92mmファンのグリル形状は写真未確認) | z=63.5で接地させ、リング半径は9.5k固定(最外38mm)でなく開口Ø90に合わせる。Corsair画像から同心円/ワイヤ形状を確認(UNVERIFIED) |
| MDB-022 | P0 | psu_label | ラベル 70x38 が x98..168/y30..68(局所)に置かれ、ファンØ92(中心 x62,y50)のグリル領域と重なる。実物のラベルはファン面ではなく側面にある可能性が高い(B3: モジュラー面の反対側にスイッチ類) | B3(ラベル位置: 写真未確認 → UNVERIFIED) | ラベルをファンと重ならない面(側面)へ移動。内容はレール値等が実在(83.3A等)するが、商標/ロゴなし方針と整合を確認 |
| MDB-023 | P0 | psu_socket0-9 | 配置が「2段x5列」の想定(コメントにU59)。B3は「3段・全ラベル付き」。数も10個は根拠不明(Puget: 24pin+EPS2+PCIe4+12V-2x6+SATA/Molex複数)。実物と違う | B3: 3段。総数UNVERIFIED | 公式画像/マニュアル(SF_PLATINUM_User_Manual.pdf はSFシリーズ旧版)で正確なパネル図を取得し、行数・列数・コネクタ種別(24pin=大, 12V-2x6=16pin, EPS/PCIe 8pin=Micro-Fit 4x2)をそれぞれ別形状にする。取得まで台帳UNVERIFIED維持 |
| MDB-024 | P1 | psu_socket(形状) | 全てただの角柱(17x5x11 / 11x5x9)でrubber色。実物はパネルの穴(凹み)に差し込むレセプタクル、キー形状・ラベル。突出4mm(y-4..)で逆に出っ張る | B3 | パネルにBooleanで凹みを開けキー付き穴を作り、周囲に印字(非表示でも可)。ソケット色は黒プラスチック |
| MDB-025 | P1 | cable_W1〜W7 の PSU側端 | ケーブル端にコネクタ(プラグ)ハウジングが無く、裸の円柱がソケット面から2mm手前で始まる。プラグ長さ(Micro-Fit約15〜20mm、UNVERIFIED)と抜き差し空間(PSU前面y<214に必要)が未検査。ケーブル曲げは出口から直後 | B4: ケーブル長400mm/445mm | 各ケーブル端にプラグ箱(24pin=約58x15、8pin=約19x16、UNVERIFIED)を追加し、前面から30mm以上の直進を確保。cable_check.pyにプラグ空間検査を追加 |
| MDB-026 | P2 | psu_body (後面) | ACインレットとスイッチが無い。実物は後面にC14とスイッチ(B3: 反対側にスイッチ)。別部品 ac_inlet(22,8,8)とW1で接続している設計と、PSUに内蔵のC14の関係が曖昧 | B3 | PSU後面にC14受口とスイッチを追加するか、延長ケーブルを使うことを台帳に明記 |
| MDB-027 | P2 | psu_body(色/文字) | 色 sf_body #17181b。実物は黒に銀/白の文字(B3)。印字なし、ネジ・スロット・通気孔なし | B3 | 後面/側面に通気スロット列、側面ネジ4本。印字は商標のため省略を明記 |
| MDB-028 | P2 | fan_psu | 92mm、ブレード9枚、Corsair NR092P(B3)の枚数・形状は未確認。make_fanの汎用形状 | 枚数: UNVERIFIED | 実機写真で枚数確定 |
| MDB-029 | P3 | parts.json gpu/psu | psu.sources が SF750 の URL(cp-9020284)。SF1000(CP-9020257)の一次情報なし。dims[1]/[2] は順序「125,100,63.5」でレイアウトは(x125,y100,z63.5)=H/Dの意味づけが曖昧。GPU: 具体SKU VCG5070T16DFSXPB1-O が公式で確認できたのに「購入前に確定」のまま | A1, A3 | sourcesにA1/A3を追加、nameにSKUを記載、dimsに軸の意味(W,D,H)を注記 |
| MDB-030 | P3 | parts.json gpu.facts | 'pcie: 5.0(レーン数未確認、物理x8の可能性)'。PNY公式はPCIe 5.0 x16(A1)。二重の記述が矛盾 | A1 | 'x16'へ更新(ただしMSI等の「x16(use x8)」表記は別メーカーなので注記) |
| MDB-031 | P2 | gpu 全体(位置) | GPUと基板が同一平面に並び(gz=8, 基板 z11.35)、ライザーでスロットから離す構造が layout の size [24,89,12] と実リボン経路で矛盾(MDB-002)。fitcheckの許可リスト(board-riser, gpu-riser)で干渉を免除しており、実際の嵌合体積を見ていない | fitcheck.py L53 | 許可対象を「嵌合部のみ」に限定し、ライザー実体積と本体の干渉をゲートで見る |
| MDB-032 | P3 | fan_gpu*_frame | 枠が非表示(hide_render)でビュー/断面図面で消える可能性。ドーム内を覗く用途では不可視でよいが、隠すことで干渉検査(BODY_OBJS)から漏れていないか未確認 | - | 干渉検査の対象に含まれるか確認 |

## 3. 優先順位つき作業計画
1. P0(嵌合・物理成立): MDB-001(W3端点とコネクタ一致)、MDB-002(ライザー200mm経路)、MDB-022(ラベルとファン重なり)、MDB-023(ソケット配置の一次資料取得→作り直し)。
2. P1(実物との外観差): MDB-003〜008、010〜014、020、021、024、025。まずGPUのPCIe嵌合(003-005)→12V-2x6(012-013)→ポート(014)→ヒートシンク/バックプレート(008,009)→PSUの開口とソケット。
3. 調査(UNVERIFIED解消): 実機写真(PNY公式/Akiba 12枚)でファン枚数・ポート順・12V-2x6位置、LINKUP公式の幅/曲げ半径、Corsair SF1000のモジュラーパネル図、PCI-SIG CEM 5.1/Micro-Fitの寸法。得られるまで確定扱いにしない。
4. P2/P3(台帳・データ整合): MDB-015〜019, 026〜032、parts.json/layout.jsonの出典・軸注記修正。
5. ゲート強化: cable_check.py にプラグ/受口一致・挿抜空間・ライザー実長検査、fitcheck.py の許可リストを嵌合部限定へ。

注記: 取得できなかった一次資料(Corsair公式403、規格書)に依存する寸法は全て UNVERIFIED。実機写真の目視は未実施のため、外観の「差」は文章記述との比較に基づく。
