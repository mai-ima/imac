#!/usr/bin/env python3
"""model/x870i_layout.json の部品表から docs/board-components.md を生成する(手で直さない)。"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = json.load(open(os.path.join(ROOT, 'model', 'x870i_layout.json'), encoding='utf-8'))
L = ['# 基板(ROG STRIX X870-I)上の部品配置', '', '生成物: `python3 tools/gen_board_doc.py`(正規ソース `model/x870i_layout.json`)。座標は基板左下を原点とし、x=基板の長辺方向(I/O側が y=0)、単位mm。', '',
     '位置は ASUS マニュアル p.14 の配置図の読み取り(±2mm、第三者ホスト版)。**高さはメーカー資料に無く典型値=UNVERIFIED**。', '',
     '## 主要部品(従来キー)', '| 部品 | x範囲 | y範囲 |', '|---|---|---|']
sx, sy = BL['socket_center']
for n, k in (('ATX_PWR(24pin)', 'atx_pwr'), ('PCIe x16', 'pcie_x16'), ('CPU_12V(EPS 8pin)', 'cpu_12v'), ('チップセット', 'chipset')):
    L.append(f"| {n} | {BL[k]['x'][0]}〜{BL[k]['x'][1]} | {BL[k]['y'][0]}〜{BL[k]['y'][1]} |")
for i, yy in enumerate(BL['dimm_slots']['y']): L.append(f"| DDR5 DIMM_{'AB'[i]} | {BL['dimm_slots']['x'][0]}〜{BL['dimm_slots']['x'][1]} | {yy[0]}〜{yy[1]} |")
L.append(f'| AM5 ソケット中心 | {sx} | {sy} |')
L += ['', '## 追加部品(components)', '| id | 名称 | x範囲 | y範囲 | 高さ | 位置の根拠 | 備考 |', '|---|---|---|---|---|---|---|']
for c in BL['components']:
    L.append(f"| {c['id']} | {c['name']} | {c['x'][0]}〜{c['x'][1]} | {c['y'][0]}〜{c['y'][1]} | {c['h']} | {c['pos_source']} | {c['note']} |")
L += ['', '## 未確認(UNVERIFIED)', *[f'- {u}' for u in BL.get('unverified', [])], '- 追加部品の高さ(典型値)・右縁ヘッダ3個の名称対応・無印金具の正体']
open(os.path.join(ROOT, 'docs', 'board-components.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('docs/board-components.md', len(BL['components']), 'components')
