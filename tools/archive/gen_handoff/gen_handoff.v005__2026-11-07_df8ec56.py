#!/usr/bin/env python3
"""業者提出パッケージ(handoff/)の生成。実行: /tmp/bl/.venv/bin/python tools/gen_handoff.py(cadquery/openpyxl が必要)
内容: STEP(スタンド系の特注部品) / BOM(xlsx+csv) / 見積依頼書 / 図面PDFの入力一覧 / DXF / ハッシュ一覧。
すべて PRELIMINARY(未承認の設計値)。発注承認ではなく、見積・DFM相談のための資料。単一源は model/*.json。"""
import json, os, csv, shutil, hashlib, math, datetime
import cadquery as cq
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); H = f'{R}/handoff'
for d in ('03_STEP', '04_DXF', '02_PDF'): os.makedirs(f'{H}/{d}', exist_ok=True)
S = json.load(open(f'{R}/model/spec.json')); P = json.load(open(f'{R}/model/parts.json')); CPJ_ALL = json.load(open(f'{R}/model/custom_parts.json')); CP = CPJ_ALL['parts']; CPJ_GEN = CPJ_ALL['general']
HW = json.load(open(f'{R}/model/hardware_list.json')); BAL = json.load(open(f'{R}/model/balance.json'))
st, sw, nk = S['stand'], S['swivel'], S['neck']; DATE = datetime.date.today().isoformat()
# ---------------- STEP(部品座標: 原点=部品中心/板の中心, Z=板厚方向) ----------------
def hole_ring(wp, pcd, n, dia, ang0=0):
    pts = [(pcd / 2 * math.cos(math.radians(ang0 + 360 * k / n)), pcd / 2 * math.sin(math.radians(ang0 + 360 * k / n))) for k in range(n)]
    return wp.pushPoints(pts).hole(dia)
def save(name, shape): cq.exporters.export(shape, f'{H}/03_STEP/{name}.step'); print('STEP', name)
bt = st['ballast_kg'] / (7.85e-6 * (st['foot_w'] - 24) * (st['foot_depth'] - 24))
foot = cq.Workplane('XY').box(st['foot_w'], st['foot_depth'], 12).edges('|Z').fillet(4)
foot = foot.faces('<Z').workplane().rect(st['foot_w'] - 24, st['foot_depth'] - 24).cutBlind(-bt)          # 下面のballastポケット(鋼板をはめ込み, 底板で蓋)
# ゴム足(Ø20×2.5, 4個)は底カバー(t1.5)に接着する市販品。STEPには含めない(位置: 足の縁から中心まで24mm)
save('CP-10_stand_foot', foot)
stator = cq.Workplane('XY').circle(sw['stator_r']).extrude(6); stator = hole_ring(stator.faces('>Z').workplane(), sw['pcd_outer'], 6, 5.5); stator = hole_ring(stator.faces('>Z').workplane(), 120, 4, 6.6, 45)
save('CP-20_swivel_stator', stator)
rotor = cq.Workplane('XY').circle(sw['rotor_r']).extrude(6); rotor = hole_ring(rotor.faces('>Z').workplane(), sw['pcd_inner'], 6, 5.5, 30)
rotor = rotor.faces('>Z').workplane().pushPoints([(sx * 45, sz) for sx in (-1, 1) for sz in (-12, 34)]).hole(5.5)
save('CP-21_swivel_rotor', rotor)
bz0, bz1 = nk['base_z']; base = cq.Workplane('XY').box(2 * nk['base_half_x'], bz1 - bz0, nk['base_t']).edges('|Z').fillet(3)
base = base.faces('>Z').workplane().pushPoints([(sx * 45, sz - (bz0 + bz1) / 2) for sx in (-1, 1) for sz in (-12, 34)]).hole(5.5)
save('CP-22a_neck_base', base)
SYS = -S['stand']['drop'] + sw['stack_h'] + nk['base_t']; HYv = S['hinge']['axis_y']; zr0, zr1 = nk['side_z']; sx0, sx1 = nk['side_x']; t_side = sx1 - sx0
prof = [(zr0, SYS), (zr1, SYS), (zr1, nk['body_top']), (nk['strip_w'] / 2, nk['body_top']), (nk['strip_w'] / 2, HYv), (-nk['strip_w'] / 2, HYv), (-nk['strip_w'] / 2, nk['body_top']), (zr0, nk['body_top'])]
side = cq.Workplane('YZ').polyline(prof).close().extrude(t_side)           # 断面(z,y)を x 方向に押し出し
side = side.union(cq.Workplane('YZ').workplane(offset=0).center(0, HYv).circle(nk['boss_r']).extrude(t_side)).faces('>X').workplane(centerOption='CenterOfMass').center(0, 0).hole(10.0, t_side)
save('CP-22b_neck_side_plate_x2', side)
save('CP-22c_neck_tie_plate', cq.Workplane('XY').box(2 * sx0, nk['tie_y'][1] - nk['tie_y'][0], nk['tie_z'][1] - nk['tie_z'][0]))
ch = nk['cover_top'] - SYS; save('CP-22d_neck_front_cover_t6', cq.Workplane('XY').box(120, ch, nk['front_cover_z'][1] - nk['front_cover_z'][0]))
save('CP-22e_neck_back_cover_t2', cq.Workplane('XY').box(120, ch, nk['back_cover_z'][1] - nk['back_cover_z'][0]))
lev = cq.Workplane('XY').box(nk['lever_t'], nk['lever_len'] + 12, nk['lever_w']).edges('|X').fillet(2); lev = lev.faces('>X').workplane().center(0, 0).pushPoints([(nk['lever_len'] / 2 - 6 + 6 - BAL['e'] + 0, 0)]).hole(6.0) if False else lev
lev = lev.faces('>X').workplane().pushPoints([(-(nk['lever_len'] / 2 + 6) + 6, 0)]).hole(10.0).faces('>X').workplane().pushPoints([(-(nk['lever_len'] / 2 + 6) + 6 + BAL['e'], 0)]).hole(6.0)
save('CP-23_tail_lever_x2', lev)
# ---------------- BOM(xlsx + csv) ----------------
PRC = json.load(open(f'{R}/model/procurement.json')); RFQ = json.load(open(f'{R}/model/custom_parts.json'))['rfq']; LOTS = RFQ['lots']; LN = RFQ['lot_names']
wb = Workbook(); hdr = Font(bold=True, color='FFFFFF'); fill = PatternFill('solid', fgColor='305496')
def sheet(name, rows, widths):
    ws = wb.create_sheet(name)
    for r in rows: ws.append(r)
    for c in ws[1]: c.font = hdr; c.fill = fill; c.alignment = Alignment(wrap_text=True, vertical='top')
    for i, w in enumerate(widths): ws.column_dimensions[chr(65 + i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'; return ws
wb.remove(wb.active)
def facts_txt(f, lim=400):
    out = ''
    for k_, v_ in (f or {}).items():
        s = f'{k_}={v_}; '
        if len(out) + len(s) > lim: out += '…(省略。全文は model/parts.json)'; break
        out += s
    return out.rstrip('; ')
buy = [['ID', '品名/型番', 'メーカー', '数量', '外形(mm)', '単価(税込円)', '価格確度', '価格の出典', '調査日', '採用状態', '発注可否', '主要仕様', '備考(未確認事項)']]
for k, v in P.items():
    if not isinstance(v, dict): continue
    b_ = PRC['purchased'][k]
    buy.append([k, b_['model'], b_['maker'], b_['qty'], 'x'.join(f'{x:g}' for x in v.get('dims', [])), b_['unit_price_jpy'] if b_['unit_price_jpy'] is not None else 'UNVERIFIED', b_['price_status'], b_['price_source'] or '-', b_['price_surveyed'] or '-', v.get('status', ''), b_['orderable'], facts_txt(v.get('facts')), (b_['price_note'] + ' / ' + v.get('note', v.get('status_note', ''))).strip(' /')])
sheet('購入部品', buy, [14, 46, 16, 6, 18, 12, 12, 40, 11, 12, 24, 60, 70])
def grp_of(i): return next((g for g, ids in GRP.items() if i in ids), 'F 区分未設定')
GRP = {'A 板金/切削(アルミ)+アルマイト': ['CP-02', 'CP-03', 'CP-05', 'CP-06', 'CP-07', 'CP-10', 'CP-13', 'CP-14', 'CP-20', 'CP-21', 'CP-22'],
       'B ガラス加工(前面)': ['CP-01'], 'C 樹脂成形・ダイカット': ['CP-12', 'CP-19', 'CP-24'],
       'D ばね/レバー/規格品・SUS小物': ['CP-04', 'CP-08', 'CP-09', 'CP-11', 'CP-16', 'CP-17', 'CP-18', 'CP-23'],
       'E スタンド外皮・吸気ダクト(v11追加。PROPOSED/CANDIDATE)': ['CP-25', 'CP-26', 'CP-27', 'CP-28']}
cpd = {c['id']: c for c in CP}
cus = [['図番(CP)', '図面', '名称', '数量/台', *[f'{n}セット時の個数' for n in LN], '材質', '板厚/t', '外形(mm)', '工法区分', '加工', f'ロット別工法({"/".join(LN)})', '型・治具の想定', '公差', '表面処理', '質量kg', '荷重/注意', '受入検査', '状態', '未確認', '価格']]
for c in CP:
    r = RFQ['parts'][c['id']]
    cus.append([c['id'], f"02_PDF/parts_{c['id']}.pdf", c['name'], c['qty'], *[c['qty'] * n for n in LOTS], c['material'], c['t'], ' x '.join(f'{v:g}' for v in c['size'] if v), r['route'], c['process'], ' / '.join(r['lot']), r['tooling'], c['tolerance'], c['finish'], c['mass_kg'], c['loads'], r['inspection'], c['status'], ', '.join(c.get('open', [])), r['price']])
sheet('特注部品(要見積)', cus, [9, 20, 36, 6, 8, 8, 8, 30, 7, 16, 24, 50, 40, 24, 16, 20, 8, 40, 40, 18, 20, 18])
cls_of = lambda name: next(((kind, cp, f, note) for m, kind, cp, f, note in PRC['hw_class'] if m in name), ('UNCLASSIFIED', '', 1, ''))
KN = {'cp_child': 'CP部品の構成要素(CP側で見積)', 'standard': '規格品(購入)', 'kit': '購入品に付属', 'custom_no_cp': '特注・加工品(CP番号なし)', 'UNCLASSIFIED': '未分類'}
hwrows = [['ID', '区分', '部品', '数量', '調達区分', '所属CP', '仕様/備考', '価格']]
for n_, h in enumerate(sorted(HW, key=lambda x: (x['cat'], x['name'])), 1):
    kind, cp, f, note = cls_of(h['name']); hwrows.append([f'HW-{n_:02d}', h['cat'], h['name'], h['qty'], KN[kind], cp or '-', (h.get('spec', '') + ' ' + note).strip(), 'UNVERIFIED(価格未取得)'])
sheet('小物・締結(3D描画分)', hwrows, [8, 12, 70, 8, 26, 9, 60, 20])
form = [['図番(CP)', '名称', 'ロット', '個数', '単価[円/個,税別]', '型費[円]', '治具費[円]', 'リードタイム[営業日]', '前提条件', 'DFM指摘・代替案']]
for c in CP:
    for n_, ln in zip(LOTS, LN): form.append([c['id'], c['name'], ln, c['qty'] * n_, '', '', '', '', '', ''])
sheet('見積回答様式(貴社記入)', form, [9, 40, 12, 8, 16, 12, 12, 16, 40, 40])
unv = [['項目', '内容']]
for ln in open(f'{R}/docs/unverified-tracker.md', encoding='utf-8'):
    if ln.startswith('| U'): p = [x.strip() for x in ln.strip().strip('|').split('|')]; unv.append([p[0], ' / '.join(p[1:4])[:300]])
sheet('未確認事項(U台帳)', unv, [8, 120])
wb.save(f'{H}/01_BOM.xlsx')
for nm, rows in (('01_BOM_purchased', buy), ('01_BOM_custom', cus), ('01_BOM_hardware', hwrows), ('01_見積回答様式', form)):
    csv.writer(open(f'{H}/{nm}.csv', 'w', newline='', encoding='utf-8-sig')).writerows(rows)
# ---------------- DXF/ホール表 ----------------
shutil.copy(f'{R}/drawings/outlines.dxf', f'{H}/04_DXF/outlines.dxf'); shutil.copy(f'{R}/docs/spec/hole-table.md', f'{H}/04_DXF/hole-table.md')
# ---------------- 図面一覧(PDFは別工程で生成) ----------------
svgs = sorted(f for f in os.listdir(f'{R}/drawings') if f.endswith('.svg')) + sorted('v10/' + f for f in os.listdir(f'{R}/drawings/v10') if f.endswith('.svg')) ; psv = sorted(f for f in os.listdir(f'{R}/drawings/parts') if f.endswith('.svg'))
json.dump(dict(sheets=[f'drawings/{f}' for f in svgs] + [f'drawings/parts/{f}' for f in psv]), open(f'{H}/02_PDF/_sources.json', 'w'), indent=1)
print('BOM/DXF/sources done', len(svgs) + len(psv), 'drawings')

# ---------------- 見積依頼書(md + html) ----------------
G = RFQ['general']; PH_ = S['panels'][str(S['panel_size'])]['h']; BODY_H = PH_ + S['bezel'] + S['chin']
bc = S['hinge']['balance_cam']; stepfiles = sorted(f[:-5] for f in os.listdir(f'{H}/03_STEP') if f.endswith('.step'))
dome_p = next(f for f in cpd['CP-07']['features'] if f.startswith('全面均一パーフォレーション'))
md = ['# 見積依頼書(RFQ) — iMac風27型一体型PC(筐体・スタンド) 試作1・小ロット10・量産100', '', f'発行日 {DATE} / 版: v11 / 図面改訂 D / **状態: PRELIMINARY(未承認の設計値)** / 見積対象: 特注部品 {CP[0]["id"]}〜{CP[-1]["id"]} 計{len(CP)}種(CP-15は欠番)', '',
      '> この資料は**見積・DFM(製造性)相談のための依頼**であり、発注承認ではありません。寸法・公差・材質は設計値で、試作前に貴社とのDFM協議で確定します。安全に関わる項目(電源・保護接地・ガラス・ヒンジ強度)は別途の試験・認証が必要です。**価格・納期の根拠は当方に無く(UNVERIFIED)、貴社の見積を正とします。**', '',
      '## 1. 依頼の要点',
      f'- ロット(3段階): **{LN[0]}**(1セット=1台分) / **{LN[1]}**(10セット) / **{LN[2]}**(100セット)。各段階の単価・型費・治具費・リードタイムをご提示ください。工法がロットで変わる場合(例: 試作は削り出し、量産は絞り)は段階ごとに工法をお書きください。',
      '- 希望: 部品ごとの**見積**、**DFMコメント**(加工不能・要変更の箇所)、**代替案**(材質・工法)。', '- 提出先/期日/担当: (依頼元で記入)。', '',
      '## 2. 製品の概要',
      '- 27型4Kの一体型PC。前面は強化ガラス+液晶、背面は取り外し可能なアルミのドーム(実穴パーフォレーション Ø2.4×ピッチ4.0 千鳥、貫通)、内部は市販のPC部品。',
      f'- 外形: 幅{S["body_w"]:g}mm×高さ{BODY_H:g}mm、スラブ厚{S["slab_t"]:g}mm、ドーム最大総厚{S["dome"]["total_t"]:g}mm。スタンド: チルト{S["hinge"]["tilt_min_deg"]:+g}〜{S["hinge"]["tilt_max_deg"]:+g}°(カム+ダイスプリング式バランサ)、左右首振り±{sw["range_deg"]:g}°、足{st["foot_w"]}×{st["foot_depth"]}mm。首振り軸受・ネック機構は同色アルマイトの外皮(スカート/カラー/ネック外皮 CP-26〜28)で隠す。',
      f'- 表面: アルマイトII(硫酸) 10〜15µm、色は{len(S["palette"])}色展開(試作は1色)。**接地導通が必要な面はマスキング**(各部品図の指示に従う)。', '',
      '## 3. 共通条件', f'- **{G["nda"]}**', f'- **{G["delivery"]}**', f'- **{G["packing"]}**', f'- **{G["inspection_common"]}**', f'- **{G["lead_time_request"]}**', f'- **{G["currency"]}**', f'- **{G["quote_form"]}** 回答用の表は `01_見積回答様式.csv` / `01_BOM.xlsx`(シート「見積回答様式」)にあります。', f'- **{G["price_status"]}**', f'- 公差: 特記なき限り {CPJ_GEN["tolerance"]}。{CPJ_GEN["burr"]}。アルマイト: {CPJ_GEN["anodize"]}。', '',
      '## 4. 見積対象の特注部品(図番=CP番号。図面は `02_PDF/parts_CP-xx.pdf`)']
for g_, ids in GRP.items():
    md += [f'### {g_}', '', '**(a) 仕様**', '', '| 図番 | 名称 | 数量/台 | ' + ' | '.join(f'{n}個数' for n in LN) + ' | 材質 | 表面処理 | 公差 | 外形mm |', '|---|---|---|' + '---|' * len(LN) + '---|---|---|---|']
    for i in ids:
        c = cpd[i]; md.append(f"| {i} | {c['name']} | {c['qty']} | " + ' | '.join(str(c['qty'] * n) for n in LOTS) + f" | {c['material']} | {c['finish']} | {c['tolerance']} | {' x '.join(f'{v:g}' for v in c['size'] if v) or '-'} |")
    md += ['', '**(b) 工法・検査と回答欄(貴社記入: 各ロットの単価/型費/治具費/リードタイム/前提条件)**', '', '| 図番 | 工法区分 | ロット別工法 | 型・治具の想定 | 受入検査 | 状態 / 未確認 | 回答欄 |', '|---|---|---|---|---|---|---|']
    for i in ids:
        c = cpd[i]; r = RFQ['parts'][i]
        md.append(f"| {i} | {r['route']} | {LN[0]}: {r['lot'][0]} / {LN[1]}: {r['lot'][1]} / {LN[2]}: {r['lot'][2]} | {r['tooling']} | {r['inspection']} | {c['status']} / {', '.join(c.get('open', [])) or '-'} | 別紙様式 |")
    md.append('')
unk = [i for i in cpd if grp_of(i).startswith('F')]
assert not unk, f'見積区分が未設定のCP: {unk}'
nocp = [(h, cls_of(h['name'])) for h in HW if cls_of(h['name'])[0] == 'custom_no_cp']
md += ['## 5. CP番号を持たない付帯品(特注・加工品。見積に含めるか依頼元で判断)', '', '3Dモデルに描画している小物のうち、特注加工が必要でCP番号が未登録のもの。規格品・CPの構成要素は `01_BOM.xlsx` シート「小物・締結」を参照。', '', '| 部品 | 数量/台 | 備考 |', '|---|---|---|']
md += [f"| {h['name']} | {h['qty']} | {cl[3]} |" for h, cl in nocp]
md += ['', '## 6. 購入品(本依頼の対象外。参考: 型番・メーカー・数量・単価・出典・調査日・価格確度)', '', '| ID | 型番 | メーカー | 数量 | 単価(税込円) | 価格確度 | 出典 | 調査日 |', '|---|---|---|---|---|---|---|---|']
for k, v in P.items():
    if isinstance(v, dict): b_ = PRC['purchased'][k]; md.append(f"| {k} | {b_['model']} | {b_['maker']} | {b_['qty']} | {b_['unit_price_jpy'] if b_['unit_price_jpy'] is not None else 'UNVERIFIED'} | {b_['price_status']} | {b_['price_source'] or '-'} | {b_['price_surveyed'] or '-'} |")
md += ['', f"単価がある2点も第三者掲載値の転記(REFERENCE)で確定価格ではありません。詳細は docs/spec/cost-estimate.md。{PRC['board_components_note']}", '',
       '## 7. 同梱資料', '| 資料 | 場所 | 備考 |', '|---|---|---|',
       '| 図面PDF(A3, 三角法, ISO 5457枠) | `02_PDF/` | 全体図01〜16+部品図(CP番号ごと `parts_CP-xx.pdf`)。**未承認(PRELIMINARY)** |',
       f'| 3Dデータ(STEP) | `03_STEP/` | {", ".join(stepfiles)}。**ドーム・背板・トレイ・ガラス・外皮(CP-25〜28)・カム板・ダイスプリングのSTEPは未作成**(外形は DXF/図面。`viewer/imac_pc.glb`は表示用で加工用ではない) |',
       '| 外形DXF・穴表 | `04_DXF/` | 背板/トレイ/ドーム/ガラスの外形・穴(実寸mm・レイヤ別)。DXFを正とする |',
       '| BOM・回答様式 | `01_BOM.xlsx` / `01_BOM_*.csv` / `01_見積回答様式.csv` | 購入部品・特注部品・小物・見積回答様式・未確認事項(U台帳) |', '']
md += ['## 8. 貴社へお願いしたいDFM確認(特に重要)',
       f'1. **ドーム(CP-07)**: 内奥行6→162mm(総厚190mm)の滑らかな曲面(角R50)を、試作は5軸CNC削り出し、量産は絞り/ハイドロフォームで成立するか。t2.0を局所t4.0(縁フランジ)・t4.2(磁石ボス)に増肉する案の可否。**{dome_p}**。全面穿孔の工程順(穿孔→成形/成形→穿孔)と変形、穿孔数に応じた加工費の見積。',
       '2. **ガラス(CP-01)**: 化学強化ガラスt1.1+カメラ穴Ø4.0の加工可否と最小コーナーR、印刷(黒縁)の工法。', '3. **アルマイト**: 接地導通面のマスキング方法と、色差(部品間・ロット間)の管理方法。外皮(CP-26〜28)とスタンド系(CP-10/20〜22)の同色管理。',
       f'4. **首振り/チルト部品(CP-20〜23)**: 板厚・穴位置公差、カム板(SUS440C HRC{58} t{bc["cam_t_mm"]:g}, プロファイル公差±0.05)のワイヤ放電+熱処理+研削、尾部レバー(SUS304 t{nk["lever_t"]:g}×{nk["lever_w"]:g}×{nk["lever_len"]:g})のレーザー加工、ダイスプリング(OD{bc["spring_od_mm"]:g}×線径{bc["spring_wire_mm"]:g}, k={bc["k_spring_N_mm"]:g}N/mm, 1本の荷重{bc["F0_total_N"]/2:g}N@0°)の市販品有無。',
       '5. **締結**: スタンドオフ/ピン/磁石ポケットの座面、ねじ長・ピッチの標準部品への置換提案。',
       f'6. **外皮(CP-26〜28)**: 円筒外皮Ø{cpd["CP-26"]["size"][0]:g}×長さ{cpd["CP-26"]["size"][2]:g}(スカート)/Ø{cpd["CP-27"]["size"][0]:g}×{cpd["CP-27"]["size"][2]:g}(カラー)の板金ロールかCNC旋削か、すき間0.5mm(全周均一)の管理方法、足・ネックへの隠し固定(未設計)の提案。', '', 
       '## 9. 未確定・注意事項(貴社へ正直にお伝えします)',
       '- 質量・重心・ばね特性・軸受定格は**推定/未確認**です(U25〜U27, U50〜U52)。強度は概算(`tools/strength_check.py`)で、疲労・FEAは未実施です。',
       '- ヒンジ/首振りの**型番未選定**: ダイスプリング(JIS金型用)、クロスローラ軸受(OD100/ID60×12)。貴社に調達可能な代替品のご提案があれば歓迎します。', '- **指挟み保護**(蛇腹ブーツ/ガード)は未設計です(U53)。ご提案をお願いします。',
       '- CP-25(吸気ダクト)は未採用の候補で、熱効果は未実証です(R10E-001)。CP-26〜28(外皮)は形状のみ決まった提案段階で、板厚・固定方法は仮置きです(SHAPE-01)。',
       '- CP-16(ケーブルクリップ)の数量24は暫定で、配線経路から再計算した個数と一致していません(要確定)。',
       '- 内部の市販部品(CPU/GPU/基板等)は本依頼の対象外です。BOMの購入品は参考情報で、型番未確定の品目があります。', '- 図面の正式なGD&T、展開図/曲げ線、STEP(ドーム等)は未整備です。貴社DFM後に更新して再提出します。']
open(f'{H}/00_見積依頼書.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
import markdown
html = markdown.markdown('\n'.join(md), extensions=['tables'])
open(f'{H}/00_見積依頼書.html', 'w', encoding='utf-8').write('<html><head><meta charset="utf-8"><style>body{font-family:"Noto Sans CJK JP","Hiragino Sans",sans-serif;font-size:10.5pt;line-height:1.55;margin:18mm}table{border-collapse:collapse;width:100%;font-size:8.5pt}td,th{border:1px solid #999;padding:3px 5px;vertical-align:top}th{background:#e8ecf4}h1{font-size:17pt}h2{font-size:13pt;border-bottom:2px solid #305496}h3{font-size:11pt}blockquote{background:#fff4d6;margin:0;padding:6px 10px;border-left:4px solid #e0a800}code{background:#eee}</style></head><body>' + html + '</body></html>')
print('RFQ done')
