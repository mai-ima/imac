#!/usr/bin/env python3
"""model/hardware_list.json(blender/hardware_v8.py が出力)から docs/spec/hardware-list.md を生成する。手書きしない(旧値の残存防止)。"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hw = json.load(open(f'{R}/model/hardware_list.json'))
o = ['# 小部品を含む全部品一覧 (自動生成: blender/hardware_v8.py → model/hardware_list.json → tools/gen_hardware_list.py)', '',
     '3Dモデルに**実際に描画している**小部品の一覧(ばね・ネジ・ラッチ・磁石・ピン・スタンドオフ・クリップ・接地・首振り・バランサ等)。型番未選定のものは備考にU番号を記載。', '',
     '| 区分 | 部品 | 数量 | 仕様/備考 |', '|---|---|---|---|']
for h in sorted(hw, key=lambda x: (x['cat'], x['name'])): o.append(f"| {h['cat']} | {h['name']} | {h['qty']} | {h.get('spec', '')} |")
o.append(''); o.append(f'合計 {len(hw)} 行 / 数量計 {sum(h["qty"] for h in hw)}')
open(f'{R}/docs/spec/hardware-list.md', 'w').write('\n'.join(o) + '\n')
