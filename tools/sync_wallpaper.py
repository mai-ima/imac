#!/usr/bin/env python3
"""spec.json の wallpaper を viewer/index.html の /*WALL*/ ... /*ENDWALL*/ に埋め込む(単一源の同期)。"""
import json, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = {k: v for k, v in json.load(open(f'{R}/model/spec.json'))['wallpaper'].items() if not k.startswith('_')}
p = f'{R}/viewer/index.html'; s = open(p, encoding='utf-8').read()
S_ = json.load(open(f'{R}/model/spec.json'))
s = re.sub(r'DOME_T=\d+', f"DOME_T={S_['dome']['total_t']}", s)      # 設計値の同期
s = re.sub(r'/\*WALL\*/.*?/\*ENDWALL\*/', '/*WALL*/const WALLPAPER=' + json.dumps(W) + ';/*ENDWALL*/', s, flags=re.S)
open(p, 'w', encoding='utf-8').write(s); print('wallpaper synced:', list(W))
