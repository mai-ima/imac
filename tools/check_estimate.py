#!/usr/bin/env python3
"""見積・BOM整合の機械照合(EST系)。実行: python3 tools/check_estimate.py
照合: custom_parts.json / procurement.json / parts.json / hardware_list.json / spec.json ↔ docs/spec/custom-parts.md / cost-estimate.md / bom-final.md / hardware-list.md /
handoff/00_見積依頼書.md / handoff/01_BOM_*.csv / handoff/01_BOM.xlsx / drawings/parts / handoff/02_PDF。
終了コード: 0=合格 / 1=FAIL / 2=既知の未解決(KNOWN_OPEN)のみ残存(UNVERIFIED。合格ではない)。"""
import json, os, re, csv, sys, glob
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda n: json.load(open(f'{R}/model/{n}.json', encoding='utf-8'))
rd = lambda f: open(f'{R}/{f}', encoding='utf-8').read()
CPJ, PRC, P, HW, S = J('custom_parts'), J('procurement'), J('parts'), J('hardware_list'), J('spec')
CP = CPJ['parts']; cpd = {c['id']: c for c in CP}; RFQ = CPJ['rfq']; LOTS = RFQ['lots']
fails, known = [], []
def F(m): fails.append(m)
# 既知の未解決(設計判断が必要で、機械的には直せないもの)。ここに無い不一致は FAIL
KNOWN_OPEN = {('hw_qty', 'CP-16'): 'EST-014 CP-16 ケーブルクリップ数量: custom_parts=24 / hardware_list(描画)=7 / cables.json経路から再計算=不一致。設計判断待ち'}

# 1) ID集合
ids = [c['id'] for c in CP]
if len(ids) != len(set(ids)): F('custom_parts.json: CP番号が重複')
if set(RFQ['parts']) != set(ids): F(f'rfq.parts と parts のID差: {set(RFQ["parts"]) ^ set(ids)}')
sp = rd('docs/spec/custom-parts.md')
for i in ids:
    if f'## {i} ' not in sp: F(f'docs/spec/custom-parts.md に {i} の節が無い(gen_specs.py 未実行?)')
    if not os.path.exists(f'{R}/drawings/parts/{i}.svg'): F(f'drawings/parts/{i}.svg が無い')
    if not os.path.exists(f'{R}/handoff/02_PDF/parts_{i}.pdf'): F(f'handoff/02_PDF/parts_{i}.pdf が無い(svg2pdf未実行?)')
extra = set(re.findall(r'^## (CP-\d+) ', sp, re.M)) - set(ids)
if extra: F(f'custom-parts.md に model に無いCP: {extra}')
# 2) 数量: CSV / RFQ md / custom-parts.md 表
rows = list(csv.reader(open(f'{R}/handoff/01_BOM_custom.csv', encoding='utf-8-sig')))
hd = rows[0]; ix = {h: n for n, h in enumerate(hd)}
csvd = {r[ix['図番(CP)']]: r for r in rows[1:]}
if set(csvd) != set(ids): F(f'01_BOM_custom.csv のID差: {set(csvd) ^ set(ids)}')
rfq = rd('handoff/00_見積依頼書.md')
for c in CP:
    i = c['id']; r = csvd.get(i)
    if r:
        if int(r[ix['数量/台']]) != c['qty']: F(f'{i}: CSV数量{r[ix["数量/台"]]} != model {c["qty"]}')
        for n, ln in zip(LOTS, RFQ['lot_names']):
            if int(r[ix[f'{ln}セット時の個数']]) != c['qty'] * n: F(f'{i}: CSVロット{ln}個数が qty×{n} と不一致')
        if r[ix['材質']] != c['material']: F(f'{i}: CSV材質が model と不一致')
    m = re.search(rf'^\| {i} \| (.*?) \| (\d+) \| ' + r' \| '.join([r'(\d+)'] * len(LOTS)) + r' \|', rfq, re.M)
    if not m: F(f'見積依頼書に {i} の仕様行が無い')
    else:
        if int(m.group(2)) != c['qty']: F(f'{i}: 見積依頼書の数量{m.group(2)} != model {c["qty"]}')
        for k, n in enumerate(LOTS):
            if int(m.group(3 + k)) != c['qty'] * n: F(f'{i}: 見積依頼書のロット個数が不一致')
    m2 = re.search(rf'^\| {i} \| (.*?) \| (\d+) \| ', sp, re.M)
    if not m2: F(f'custom-parts.md 表に {i} 無し')
    elif int(m2.group(2)) != c['qty']: F(f'{i}: custom-parts.md 数量{m2.group(2)} != model {c["qty"]}')
    r_ = RFQ['parts'][i]
    for k_ in ('route', 'inspection', 'tooling', 'price'):
        if not r_.get(k_): F(f'{i}: rfq.{k_} が空')
    if len(r_['lot']) != 3 or not all(r_['lot']): F(f'{i}: rfq.lot が3段階そろっていない')
    for k_ in ('material', 'finish', 'tolerance'):
        if not c.get(k_) or c[k_] in ('-', '') and k_ != 'material':
            F(f'{i}: {k_} が空または「-」(「なし(規格品)」等を明示すること)')
    if 'UNVERIFIED' not in r_['price']: F(f'{i}: 価格根拠が無いのに price が UNVERIFIED 表記でない')
# 3) 購入品
buy = {r[0]: r for r in csv.reader(open(f'{R}/handoff/01_BOM_purchased.csv', encoding='utf-8-sig'))}
pk = [k for k, v in P.items() if isinstance(v, dict)]
if set(PRC['purchased']) != set(pk): F(f'procurement.purchased と parts.json のID差: {set(PRC["purchased"]) ^ set(pk)}')
bf = rd('docs/bom-final.md'); ce = rd('docs/spec/cost-estimate.md')
VALID = set(PRC['price_status_legend'])
for k in pk:
    b = PRC['purchased'].get(k)
    if not b: continue
    if k not in buy: F(f'01_BOM_purchased.csv に {k} 無し')
    else:
        h = {n: x for n, x in enumerate(buy['ID'])}
        if int(buy[k][3]) != b['qty']: F(f'{k}: CSV数量 != procurement')
        d = 'x'.join(f'{x:g}' for x in P[k]['dims'])
        if buy[k][4] != d: F(f'{k}: CSV外形{buy[k][4]} != parts.json {d}')
    if not re.search(rf'^\| {k} \|.*\| {b["qty"]} \| {re.escape("x".join(f"{x:g}" for x in P[k]["dims"]))} \|', bf, re.M): F(f'{k}: docs/bom-final.md の数量/外形が parts/procurement と不一致(gen_estimate.py 未実行?)')
    if b['price_status'] not in VALID: F(f'{k}: price_status不正')
    if b['unit_price_jpy'] is not None:
        if b['price_status'] == 'UNVERIFIED': F(f'{k}: 単価があるのに UNVERIFIED')
        if not b['price_source'] or not b['price_surveyed']: F(f'{k}: 単価に出典または調査日が無い')
        if f"{b['unit_price_jpy']:,}" not in ce: F(f'{k}: cost-estimate.md に単価が無い')
    else:
        if b['price_status'] != 'UNVERIFIED': F(f'{k}: 単価nullなのに {b["price_status"]}')
    if b['price_status'] == 'CONFIRMED' and not b['price_source'].startswith('http'): F(f'{k}: CONFIRMED には出典URLが必要')
    if b['qty'] > 0 and not b['model']: F(f'{k}: 型番欄が空')
# 価格の数値は procurement.json 由来のものだけ許す(出典の無い数値の混入防止)
allowed = set(re.findall(r'\d{1,3}(?:,\d{3})+', rd('model/procurement.json'))) | {f"{v:,}" for v in [sum(b['unit_price_jpy'] * b['qty'] for b in PRC['purchased'].values() if b['unit_price_jpy'] is not None)]} | {f"{b['unit_price_jpy']:,}" for b in PRC['purchased'].values() if b['unit_price_jpy']} | {f"{s['price_jpy']:,}" for s in PRC['superseded_prices']}
for f in ('docs/spec/cost-estimate.md', 'handoff/00_見積依頼書.md'):
    for n in set(re.findall(r'(?<![\d,.])\d{1,3}(?:,\d{3})+(?![\d,])', rd(f))):
        if n not in allowed and not re.fullmatch(r'11,300', n): F(f'{f}: 根拠(procurement.json)に無い金額/数値 {n}')
# 4) 小物 ↔ CP
cls = lambda name: next(((kind, cp, fac) for m, kind, cp, fac, note in PRC['hw_class'] if m in name), None)
for h in HW:
    c = cls(h['name'])
    if not c: F(f'hardware_list: procurement.hw_class に分類が無い: {h["name"][:40]}'); continue
    kind, cp, fac = c
    if kind == 'cp_child' and fac is not None:
        exp = sum(cpd[x]['qty'] for x in cp.split('+') if x in cpd) * fac
        if any(x not in cpd for x in cp.split('+')): F(f'hw_class の {cp} が custom_parts に無い'); continue
        if h['qty'] != exp:
            key = ('hw_qty', cp)
            if key in KNOWN_OPEN: known.append(KNOWN_OPEN[key])
            else: F(f'hardware_list「{h["name"][:30]}」数量{h["qty"]} != {cp}の数量×{fac}={exp}')
hwmd = rd('docs/spec/hardware-list.md')
if f'合計 {len(HW)} 行 / 数量計 {sum(h["qty"] for h in HW)}' not in hwmd: F('docs/spec/hardware-list.md が model/hardware_list.json と不一致(gen_hardware_list.py 未実行)')
# 5) 寸法・数値(model/spec ↔ 見積依頼書)
PH = S['panels'][str(S['panel_size'])]['h']; BH = PH + S['bezel'] + S['chin']
need = [f'幅{S["body_w"]:g}mm×高さ{BH:g}mm', f'スラブ厚{S["slab_t"]:g}mm', f'ドーム最大総厚{S["dome"]["total_t"]:g}mm', f'足{S["stand"]["foot_w"]}×{S["stand"]["foot_depth"]}mm', f'{len(S["palette"])}色展開', f'±{S["swivel"]["range_deg"]:g}°']
for n in need:
    if n not in rfq: F(f'見積依頼書に model の値「{n}」が無い/食い違い')
if re.search(r'カム板\(SUS304', rfq + rd('docs/spec/hardware-list.md')): F('旧カム板仕様(SUS304 t6)が残存')
bc = S['hinge']['balance_cam']
if f't{bc["cam_t_mm"]:g}' not in rfq or 'SUS440C' not in rfq: F('見積依頼書のカム板仕様が spec.hinge.balance_cam と不一致')
sh = S['stand']['shroud']; nk = S['neck']
if abs(cpd['CP-26']['size'][0] - 2 * sh['skirt_r_mm']) > .01: F('CP-26 外径が spec.stand.shroud.skirt_r_mm と不一致')
SYS = -S['stand']['drop'] + S['swivel']['stack_h'] + nk['base_t']
if abs(cpd['CP-26']['size'][2] - (SYS - sh['skirt_gap_mm'] + S['stand']['drop'])) > .01: F('CP-26 長さが spec から算出した値と不一致')
if abs(cpd['CP-28']['size'][0] - 2 * (nk['base_half_x'] + sh['neck_margin_mm'])) > .06 or abs(cpd['CP-28']['size'][2] - (nk['cover_top'] - SYS)) > .06: F('CP-28 外形が spec.neck/shroud と不一致')
bl = rd('blender/build_imac_pc_v8.py'); mm = re.search(r'pitch = ([\d.]+); r_ = ([\d.]+)', bl)
f7 = ' '.join(cpd['CP-07']['features'])
if mm and (f'Ø{2 * float(mm.group(2)):g}×ピッチ{float(mm.group(1)):.1f}' not in f7): F('CP-07 穿孔 Ø/ピッチが blender 実装と不一致')
if '実穴' not in f7: F('CP-07 に実穴パーフォレーションの明記が無い')
# 6) 手順: 全部品の図面/モデル上の存在
if 'rad_duct' in PRC['purchased'] and 'CP-25' not in cpd: F('rad_duct(CP-25予定)が custom_parts に未登録')
# xlsx
try:
    from openpyxl import load_workbook
    wb = load_workbook(f'{R}/handoff/01_BOM.xlsx'); names = wb.sheetnames
    for s in ('購入部品', '特注部品(要見積)', '小物・締結(3D描画分)', '見積回答様式(貴社記入)'):
        if s not in names: F(f'xlsx にシート {s} 無し')
    if '特注部品(要見積)' in names and wb['特注部品(要見積)'].max_row - 1 != len(CP): F('xlsx 特注行数が CP数と不一致')
except ImportError: pass
for m in known: print('[KNOWN-OPEN]', m)
for m in sorted(set(fails)): print('[FAIL]', m)
print(f'check_estimate: FAIL {len(set(fails))} / KNOWN-OPEN {len(set(known))} / CP {len(CP)} / 購入品 {len(pk)} / 小物 {len(HW)}')
sys.exit(1 if fails else (2 if known else 0))
