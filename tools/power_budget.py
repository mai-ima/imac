#!/usr/bin/env python3
"""電力収支(単一源): シナリオ別に DC負荷 → PSU損失 → AC入力 を同じ式で求め、筐体内で熱になる総量=AC入力(保存則)を検査する。
二重計上を避ける: パネル/コントローラはPSU 12Vから給電されるDC負荷として1回だけ数える。PSU損失はAC入力−DC出力。
値の出典: CPU PPT/GPU TGPは parts.json(公式TDP/TGP+仮定)、パネル最大37.3W(BOE公式)、その他は仮定(UNVERIFIED)。"""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(f'{R}/model/parts.json'))
cpu_ppt = P['cpu']['facts']['ppt_w']; gpu_tgp = P['gpu']['facts']['tgp_w']; psu_w = P['psu']['facts']['provisional_w']
PANEL_MAX, PANEL_EFF = 37.3, 0.90          # パネル最大消費(BOE公式)と電源変換効率(仮定)
def psu_eff(dc):
    f = dc / psu_w      # 80PLUS Platinum 代表(230V): 10%:~90, 20%:~92, 50%:~94, 100%:~91 → 保守的に割り引く(未検証)
    return 0.86 if f < 0.05 else 0.89 if f < 0.10 else 0.915 if f < 0.2 else 0.925 if f < 0.7 else 0.91
SCEN = {   # CPU, GPU, 基板/RAM/SSD, ファン/ポンプ, パネル輝度比
    'アイドル': (25, 15, 25, 3, 0.35), 'ゲーム(CPU 120W+GPU 280W)': (120, 280, 40, 14, 1.0), '最大(CPU PPT+GPU TGP同時)': (cpu_ppt, gpu_tgp, 45, 16, 1.0)}
def budget(name):
    c, g, b, f, pl = SCEN[name]; panel = PANEL_MAX * pl / PANEL_EFF + 4       # 4W: コントローラ基板
    dc = c + g + b + f + panel; eff = psu_eff(dc); ac = dc / eff
    return dict(name=name, cpu=c, gpu=g, board=b, fans=f, panel=panel, dc=dc, eff=eff, ac=ac, psu_loss=ac - dc, heat=ac)
if __name__ == '__main__':
    ok = True
    print('シナリオ | CPU | GPU | 基板等 | ファン | パネル+制御 | DC計[W] | PSU効率 | AC入力[W] | PSU損失[W] | 筐体内発熱=AC入力[W]')
    for n in SCEN:
        r = budget(n); heat_sum = r['cpu'] + r['gpu'] + r['board'] + r['fans'] + r['panel'] + r['psu_loss']
        good = abs(heat_sum - r['ac']) < 1e-6 and r['dc'] <= 0.7 * psu_w; ok &= good
        print(f"{n} | {r['cpu']:.0f} | {r['gpu']:.0f} | {r['board']:.0f} | {r['fans']:.0f} | {r['panel']:.1f} | {r['dc']:.0f} | {r['eff']*100:.1f}% | {r['ac']:.0f} | {r['psu_loss']:.0f} | {r['heat']:.0f} [{'OK' if good else 'NG'}]")
    print(f'PSU {psu_w}W: 最大シナリオ使用率 {budget("最大(CPU PPT+GPU TGP同時)")["dc"]/psu_w*100:.0f}%(目標≦70%)。AC入力はコンセント側、DC計はPSU出力(PSU損失はAC−DC)。')
    sys.exit(0 if ok else 1)
