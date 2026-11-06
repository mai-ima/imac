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
S = json.load(open(f'{R}/model/spec.json')); P = json.load(open(f'{R}/model/parts.json')); CP = json.load(open(f'{R}/model/custom_parts.json'))['parts']
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
buy = [['ID', '品名/型番', 'メーカー', '外形(mm)', '採用状態', '主要仕様', '備考(未確認事項)']]
for k, v in P.items():
    if isinstance(v, dict): buy.append([k, v.get('name', ''), v.get('maker', ''), str(v.get('dims', '')), v.get('status', ''), json.dumps(v.get('facts', {}), ensure_ascii=False)[:300], v.get('note', v.get('status_note', ''))[:300]])
sheet('購入部品', buy, [14, 46, 16, 18, 12, 60, 60])
cus = [['ID', '名称', '数量', '材質', '板厚/t', '外形(mm)', '加工', '公差', '表面処理', '質量kg', '荷重/注意', '状態', '未確認']]
for c in CP: cus.append([c['id'], c['name'], c['qty'], c['material'], c['t'], ' x '.join(f'{v:g}' for v in c['size'] if v), c['process'], c['tolerance'], c['finish'], c['mass_kg'], c['loads'], c['status'], ', '.join(c.get('open', []))])
sheet('特注部品(要見積)', cus, [8, 36, 6, 30, 7, 16, 50, 16, 20, 8, 50, 18, 14])
sheet('小物・締結(3D描画分)', [['区分', '部品', '数量', '仕様/備考']] + [[h['cat'], h['name'], h['qty'], h.get('spec', '')] for h in HW], [14, 70, 8, 50])
unv = [['項目', '内容']]
for ln in open(f'{R}/docs/unverified-tracker.md', encoding='utf-8'):
    if ln.startswith('| U'): p = [x.strip() for x in ln.strip().strip('|').split('|')]; unv.append([p[0], ' / '.join(p[1:4])[:300]])
sheet('未確認事項(U台帳)', unv, [8, 120])
wb.save(f'{H}/01_BOM.xlsx')
for nm, rows in (('01_BOM_purchased', buy), ('01_BOM_custom', cus)):
    csv.writer(open(f'{H}/{nm}.csv', 'w', newline='', encoding='utf-8-sig')).writerows(rows)
# ---------------- DXF/ホール表 ----------------
shutil.copy(f'{R}/drawings/outlines.dxf', f'{H}/04_DXF/outlines.dxf'); shutil.copy(f'{R}/docs/spec/hole-table.md', f'{H}/04_DXF/hole-table.md')
# ---------------- 図面一覧(PDFは別工程で生成) ----------------
svgs = sorted(f for f in os.listdir(f'{R}/drawings') if f.endswith('.svg')) + sorted('v10/' + f for f in os.listdir(f'{R}/drawings/v10') if f.endswith('.svg')) ; psv = sorted(f for f in os.listdir(f'{R}/drawings/parts') if f.endswith('.svg'))
json.dump(dict(sheets=[f'drawings/{f}' for f in svgs] + [f'drawings/parts/{f}' for f in psv]), open(f'{H}/02_PDF/_sources.json', 'w'), indent=1)
print('BOM/DXF/sources done', len(svgs) + len(psv), 'drawings')

# ---------------- 見積依頼書(md + html) ----------------
grp = {'A 板金/切削(アルミ)+アルマイト': ['CP-02', 'CP-03', 'CP-04', 'CP-05', 'CP-06', 'CP-07', 'CP-09', 'CP-10', 'CP-12', 'CP-13', 'CP-14', 'CP-16', 'CP-19', 'CP-20', 'CP-21', 'CP-22'],
       'B ガラス加工(前面)': ['CP-01'], 'C ばね/レバー/SUS小物・樹脂': ['CP-08', 'CP-11', 'CP-17', 'CP-18', 'CP-23', 'CP-24']}
cpd = {c['id']: c for c in CP}
md = [f'# 試作 見積依頼書(RFQ) — iMac風27型一体型PC(筐体・スタンド)', '', f'発行日 {DATE} / 版: v9 / 図面改訂 D / **状態: PRELIMINARY(未承認の設計値)**', '',
      '> この資料は**見積・DFM(製造性)相談のための依頼**であり、発注承認ではありません。寸法・公差・材質は設計値で、試作前に貴社とのDFM協議で確定します。安全に関わる項目(電源・保護接地・ガラス・ヒンジ強度)は別途の試験・認証が必要です。', '',
      '## 1. 依頼の要点', '- 数量: **試作1台分**(併せて、3台・10台時の単価の目安もご提示ください)。', '- 希望: 部品ごとの**見積(単価/治具・型費/納期)**、**DFMコメント(加工不能・要変更の箇所)**、**代替案**(材質・工法)。',
      '- 提出先/期日: (依頼元で記入)。秘密保持: 本資料は依頼目的以外に使用しないでください。', '',
      '## 2. 製品の概要', '- 27型4Kの一体型PC。前面は強化ガラス+液晶、背面は取り外し可能なアルミのドーム(全面パーフォレーション Ø2.4×ピッチ4.0 千鳥)、内部は市販のPC部品。',
      f'- 外形: 幅{S["body_w"]:g}mm×高さ415.3mm、スラブ厚{S["slab_t"]:g}mm、ドーム最大総厚{S["dome"]["total_t"]:g}mm。スタンド: チルト{S["hinge"]["tilt_min_deg"]:+g}〜{S["hinge"]["tilt_max_deg"]:+g}°、左右首振り±{sw["range_deg"]:g}°、足{st["foot_w"]}×{st["foot_depth"]}mm。', '- 表面: アルマイトII(硫酸) 10〜15µm、色は7色展開(試作は1色)。**接地導通が必要な面はマスキング**(各部品図の指示に従う)。', '',
      '## 3. 見積区分と対象部品']
for g_, ids in grp.items():
    md += [f'### {g_}', '', '| ID | 名称 | 数量 | 材質 | 加工 | 状態/未確認 |', '|---|---|---|---|---|---|']
    for i in ids:
        c = cpd.get(i)
        if c: md.append(f"| {i} | {c['name']} | {c['qty']} | {c['material']} | {c['process'][:120]} | {c['status']} / {', '.join(c.get('open', [])) or '-'} |")
    md.append('')
md += ['## 4. 同梱資料', '| 資料 | 場所 | 備考 |', '|---|---|---|',
      '| 図面PDF(A3, 三角法, ISO 5457枠) | `02_PDF/` | 全体図01〜16+部品図CP-01〜CP-24。**未承認(PRELIMINARY)** |', '| 3Dデータ(STEP) | `03_STEP/` | スタンド系の特注部品(CP-10/20/21/22/23)。**ドーム・背板・トレイ・ガラスのSTEPは未作成**(外形は DXF/図面。3D曲面は`viewer/imac_pc.glb`は表示用で加工用ではない) |',
      '| 外形DXF・穴表 | `04_DXF/` | 背板/トレイ/ドーム/ガラスの外形・穴(実寸mm・レイヤ別)。DXFを正とする |', '| BOM | `01_BOM.xlsx` / `01_BOM_*.csv` | 購入部品・特注部品・小物・未確認事項(U台帳) |', '']
md += ['## 5. 貴社へお願いしたいDFM確認(特に重要)', '1. **ドーム(CP-07)**: 内奥行6→101mmの滑らかな曲面(角R50)を、試作は5軸CNC削り出し、量産は絞り/ハイドロフォームで成立するか。t2.0を局所t4.0(縁フランジ)・t4.2(磁石ボス)に増肉する案の可否。全面穿孔(Ø2.4×ピッチ4.0)の工程順(穿孔→成形/成形→穿孔)と変形。',
       '2. **ガラス(CP-01)**: 化学強化ガラスt1.1+カメラ穴Ø4.0の加工可否と最小コーナーR、印刷(黒縁)の工法。', '3. **アルマイト**: 接地導通面のマスキング方法と、色差(部品間)の管理方法。', '4. **首振り/チルト部品(CP-20〜23)**: 板厚・穴位置公差、SUSレバー(t5×14×50)のレーザー+曲げ、キー溝加工。',
       '5. **締結**: スタンドオフ/ピン/磁石ポケットの座面、ねじ長・ピッチの標準部品への置換提案。', '', '## 6. 受入検査(試作)', '- 寸法: 主要外形±0.3mm、穴位置±0.1mm(背板/トレイ/ドーム固定穴)。平面度: 背板0.3mm、ガスケット面0.3mm。', '- 外観: アルマイトのムラ・傷・バリ(エッジC0.2)。検査成績書(寸法・膜厚)の添付をお願いします。', '',
       '## 7. 未確定・注意事項(貴社へ正直にお伝えします)', '- 質量・重心・ばね特性・軸受定格は**推定/未確認**です(U25〜U27, U50〜U52)。強度は概算(`tools/strength_check.py`)で、疲労・FEAは未実施です。',
       '- ヒンジ/首振りの**型番未選定**: ダイスプリング(JIS金型用)、クロスローラ軸受(OD100/ID60×12)。貴社に調達可能な代替品のご提案があれば歓迎します。', '- **指挟み保護**(蛇腹ブーツ/ガード)は未設計です(U53)。ご提案をお願いします。',
       '- 内部の市販部品(CPU/GPU/基板等)は本依頼の対象外です。BOMは参考情報です。', '- 図面の正式なGD&T、展開図/曲げ線、STEP(ドーム等)は未整備です。貴社DFM後に更新して再提出します。']
open(f'{H}/00_見積依頼書.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
import markdown
html = markdown.markdown('\n'.join(md), extensions=['tables'])
open(f'{H}/00_見積依頼書.html', 'w', encoding='utf-8').write('<html><head><meta charset="utf-8"><style>body{font-family:"Noto Sans CJK JP","Hiragino Sans",sans-serif;font-size:10.5pt;line-height:1.55;margin:18mm}table{border-collapse:collapse;width:100%;font-size:8.5pt}td,th{border:1px solid #999;padding:3px 5px;vertical-align:top}th{background:#e8ecf4}h1{font-size:17pt}h2{font-size:13pt;border-bottom:2px solid #305496}h3{font-size:11pt}blockquote{background:#fff4d6;margin:0;padding:6px 10px;border-left:4px solid #e0a800}code{background:#eee}</style></head><body>' + html + '</body></html>')
print('RFQ done')
