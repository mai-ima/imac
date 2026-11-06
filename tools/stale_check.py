#!/usr/bin/env python3
"""品質ゲート: 現行ファイル(archive除く)に旧値/廃止物が残っていないか、正規データ間の不変条件が成り立つかを検査。
FAIL があれば終了コード1。しきい値を緩めて通さないこと。"""
import json, re, subprocess, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); L = json.load(open(f'{R}/model/layout.json'))
fails = []; warns = []
# 1) 不変条件
if S['pod']['total_t'] != S['dome']['total_t']: fails.append('spec.pod.total_t != dome.total_t')
inner = S['dome']['total_t'] - S['dome']['sheet_t'] * 0 - 28   # 129-28=101 (内奥行): 値の導出はspec側が正
# 2) 旧値/廃止語(現行ファイルのみ)
BAN = [(r'9800X3D', '旧CPU(9950X3Dへ置換済) ※比較対象は例外'), (r'SF750', '旧PSU(SF1000)'), (r'z\s*=\s*43\b', '旧ヒンジ軸z=43'),
       (r'足220×215|foot_depth["\']?\s*[:=]\s*215', '旧スタンド足寸法'), (r'CP-15(?!.*(廃止|removed|欠番))', '廃止CP-15の残存'),
       (r'φ\s*4\.2\s*/\s*(ピッチ|pitch)\s*7', '旧穴φ4.2/ピッチ7'), (r'RTX 5060 Ti', '旧GPU(5070 Ti)'), (r'220\s*[×x]\s*230|220\s*[×x]\s*215', '旧スタンド足220×230/215(現行300×290)'), (r'定荷重ばね|カム式', '旧バランサ(定荷重ばね/カム)'), (r'[-−]5\s*°?\s*(〜|~|/|から)\s*\+?25\s*°', '旧チルト範囲-5〜+25°'), (r'z\s*=\s*38\b', '旧ヒンジ軸z=38'), (r'ballast\s*1\.8|ballast\s*2\.0|ballast2kg', '旧ballast質量'), (r'360\s*N\s*/\s*本|486\s*N|最長側360', '旧ばね荷重(現行は balance.json: 350/525N)'), (r'荷重変化率\s*35\s*%|進行率35', '旧ばね荷重変化率35%(現行 p=0.5)'), (r'stand_neck_side', '旧側面カバー部材名')]
HIST = ('docs/audit-log.md', 'docs/selection-', 'docs/research-', 'docs/source-status', 'docs/unverified-tracker', 'docs/bom-final', 'docs/logo-catalog', 'docs/spec/performance-benchmark', 'docs/spec/gaming-requirements', 'docs/tilt-swivel-design.md', 'docs/tilt-swivel-design.md', 'docs/joint-analysis.md', 'blender/build_imac_pc_v6.py', 'tools/check_sources.py', 'tools/stale_check.py')      # 履歴/比較/出典記録(旧値の言及が目的の文書)。生成物・仕様・コードは対象
files = [f for f in subprocess.check_output(['git', 'ls-files'], cwd=R, text=True).split('\n')
         if f and '/archive/' not in f and not f.startswith('archive/') and f.endswith(('.py', '.json', '.md', '.html', '.svg', '.csv'))
         and not f.startswith('audit_output/') and f != 'tools/stale_check.py']
for f in files:
    try: t = open(f'{R}/{f}', encoding='utf-8').read()
    except Exception: continue
    for pat, why in BAN:
        for m in re.finditer(pat, t):
            ctx = t[max(0, m.start() - 40): m.end() + 40].replace('\n', ' ')
            if re.search(r'旧|比較|変更前|before|supersed|置換|廃止|履歴|stale|旧版|から変更|満たさなくなった|9950X3D-Review|status_note', ctx): continue   # 履歴的言及は許容
            (warns if f.startswith(HIST) else fails).append(f'{f}: {why}: …{ctx}…')
print(f'FAIL {len(fails)} / WARN {len(warns)}')
for x in fails: print('[FAIL]', x)
for x in warns[:80]: print('[WARN]', x)
sys.exit(1 if fails else 0)
