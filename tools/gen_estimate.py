#!/usr/bin/env python3
"""見積・費用文書の生成: docs/spec/cost-estimate.md と docs/bom-final.md。実行: python3 tools/gen_estimate.py
元データ: model/parts.json(購入品の寸法/状態/出典), model/procurement.json(型番/数量/単価/出典/調査日/確度), model/custom_parts.json(特注+rfq属性), model/hardware_list.json(小物)。
手で書かない。価格の根拠が無い数値は入れない(UNVERIFIED)。"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda n: json.load(open(f'{R}/model/{n}.json', encoding='utf-8'))
P, PR, CPJ, HW = J('parts'), J('procurement'), J('custom_parts'), J('hardware_list')
CP = CPJ['parts']; RFQ = CPJ['rfq']; LOTS = RFQ['lots']; BUY = PR['purchased']
ORDER = [k for k in P if isinstance(P[k], dict)]
yen = lambda v: f'{v:,}' if v is not None else '**UNVERIFIED**'
dims = lambda d: 'x'.join(f'{v:g}' for v in d)

# ---------- docs/bom-final.md ----------
bm = ['# 部品表 BOM(自動生成: tools/gen_estimate.py / 元データ model/parts.json + model/procurement.json + model/custom_parts.json)', '',
      '購入品は parts.json の全エントリ(radiator は cooler と同一製品で数量0=二重計上しない。rad_duct は特注 CP-25)。状態: official=メーカー公式資料で確認 / retail=小売・報道の一致 / assumed=未確認 / CANDIDATE=未採用候補。', '',
      '## 1. 購入品', '', '| ID | 名称/型番 | メーカー | 数量 | 外形mm | 状態 | 発注可否 | 主な根拠(出典) |', '|---|---|---|---|---|---|---|---|']
for k in ORDER:
    p, b = P[k], BUY[k]
    bm.append(f"| {k} | {b['model']} | {b['maker']} | {b['qty']} | {dims(p['dims'])} | {p['status']} | {b['orderable']} | {(p.get('sources') or [''])[0] or '-'} |")
bm += ['', f"基板上部品: {PR['board_components_note']}", '',
       '## 2. 特注部品(要見積。詳細は docs/spec/custom-parts.md、見積条件は handoff/00_見積依頼書.md)', '', '| CP | 名称 | 数量/台 | 材質 | 状態 |', '|---|---|---|---|---|']
for c in CP: bm.append(f"| {c['id']} | {c['name']} | {c['qty']} | {c['material']} | {c['status']} |")
cls = {}
for h in HW:
    for m, kind, cp, f, note in PR['hw_class']:
        if h['name'].startswith(m) or m in h['name']: cls.setdefault(kind, []).append(h); break
KN = {'cp_child': 'CP部品の構成要素(CP側で見積)', 'standard': '規格品(購入)', 'kit': '購入品に付属', 'custom_no_cp': '特注・加工品でCP番号なし(要登録検討)'}
bm += ['', '## 3. 小物・締結(3D描画分 model/hardware_list.json。区分は procurement.json hw_class)', '', '| 区分 | 行数 | 数量計 |', '|---|---|---|'] + [f"| {KN.get(k, k)} | {len(v)} | {sum(x['qty'] for x in v)} |" for k, v in cls.items()]
open(f'{R}/docs/bom-final.md', 'w', encoding='utf-8').write('\n'.join(bm) + '\n')

# ---------- docs/spec/cost-estimate.md ----------
priced = [(k, BUY[k]) for k in ORDER if BUY[k]['unit_price_jpy'] is not None]
sub = sum(b['unit_price_jpy'] * b['qty'] for k, b in priced)
unp = [k for k in ORDER if BUY[k]['unit_price_jpy'] is None and BUY[k]['qty'] > 0]
md = ['# 価格調査と予算(自動生成: tools/gen_estimate.py / 元データ model/procurement.json)', '',
      '**状態: 概算(UNVERIFIED)。確定した総額は存在しない。** 価格の根拠(出典URL+調査日)が無い数値は載せない。国内実売を直接確認できた項目は無い(下表の2点も第三者掲載値の転記=REFERENCE)。',
      '', '価格確度: ' + ' / '.join(f'**{k}** = {v}' for k, v in PR['price_status_legend'].items()), '',
      '## 1. 購入品(型番・メーカー・数量・単価・出典・調査日・価格確度)', '', '| ID | 型番 | メーカー | 数量 | 単価(税込円) | 価格確度 | 出典 | 調査日 | 備考 |', '|---|---|---|---|---|---|---|---|---|']
for k in ORDER:
    b = BUY[k]
    md.append(f"| {k} | {b['model']} | {b['maker']} | {b['qty']} | {yen(b['unit_price_jpy'])} | {b['price_status']} | {b['price_source'] or '-'} | {b['price_surveyed'] or '-'} | {b['price_note']} |")
md += ['', f"- 単価が記録されている購入品: {len(priced)}点({', '.join(k for k, _ in priced)})。合計 **{sub:,}円(参考。REFERENCEのみの小計であり総額ではない)**。",
       f"- 単価が未取得(UNVERIFIED)の購入品: {len(unp)}点({', '.join(unp)})。これらと特注部品の価格が無いため、**BOM総額は算出不能**(推測で埋めない)。",
       '- 型番が確定していない(発注不可)購入品は docs/bom-final.md の「発注可否」欄を参照。', '',
       '## 2. 特注部品(見積依頼中の対象。単価は全件 UNVERIFIED)', '',
       '特注部品の価格は社内に根拠が無い。handoff/00_見積依頼書.md で試作1・小ロット10・量産100の3段階を依頼する。表の数量は1セット(1台分)あたり×セット数。', '',
       '| CP | 名称 | 数量/台 | ' + ' | '.join(f'{n}セット時の個数' for n in RFQ['lot_names']) + ' | 工法区分 | 型・治具の想定 | 価格 |', '|---|---|---|' + '---|' * len(LOTS) + '---|---|---|']
for c in CP:
    r = RFQ['parts'][c['id']]
    md.append(f"| {c['id']} | {c['name']} | {c['qty']} | " + ' | '.join(str(c['qty'] * n) for n in LOTS) + f" | {r['route']} | {r['tooling']} | {r['price']} |")
md += ['', '## 3. 旧構成の参考価格(現行BOMでは使わない)', '', '| 品目 | 価格(円) | 出典 | 備考 |', '|---|---|---|---|'] + [f"| {s['item']} | {s['price_jpy']:,} | {s['source']} | {s['note']} |" for s in PR['superseded_prices']]
md += ['', '## 4. 比較(参考・未再確認)', '', f"{PR['comparison_ref']['item']}。出典: {PR['comparison_ref']['source']}。{PR['comparison_ref']['note']}。",
       '本機は「性能を制限しない」方針のため、全部品と特注外装を含めると上記iMacを大きく上回る見込みだが、**総額の数値は根拠が無いため示さない**(当初の「予算≦iMac」は撤回済み)。', '',
       '## 5. 次の作業', '- 購入品: 価格.com/ツクモ/ドスパラ/ヨドバシ/Amazon の直接確認(出典URLと調査日を procurement.json に記録)。型番未確定品(ctrl_board / ram / ac_inlet / camera_audio / gpu)の型番確定が先。',
       '- 特注部品: handoff/ の見積依頼書で板金・切削・ガラス業者へ依頼(回答を受けたら price を更新)。', '- 照合: `python3 tools/check_estimate.py`(BOM・見積・model・docs の数量/型番/価格/寸法の機械照合)。']
open(f'{R}/docs/spec/cost-estimate.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print('estimate docs written; priced', len(priced), 'unpriced', len(unp), 'subtotal', sub)
