#!/usr/bin/env python3
"""転倒安定性(v7): 質量/重心は tools/massmodel.py(layout由来, 推定)。足はヒンジ軸を基準に前 foot_front/後 foot_back、幅 foot_w。
出力: 前後の転倒余裕(チルト別)と、上端(地面から約0.5m)を押して転倒する最小水平力の概算。"""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{R}/tools')
import massmodel as MM
S = MM.S; hm, cz, cy, _ = MM.head_cg(); ms = MM.stand_mass()
hz, hy = S['hinge']['axis_z_from_glass'], S['hinge']['axis_y']; st = S['stand']
front = hz - st['foot_front']; back = hz + st['foot_back']      # 前面ガラス基準z: 足の前端/後端(前=小さい値)
ground_y = -st['drop'] - 6; top_h = (MM.H - ground_y) / 1000.0
print(f"ディスプレイ部 {hm:.1f}kg + スタンド {ms:.1f}kg = {hm+ms:.1f}kg / 重心(頭部) z={cz:.0f}mm y={cy:.0f}mm / ヒンジ軸 z={hz} y={hy} / 足 z={front:.0f}〜{back:.0f}mm 幅{st['foot_w']}mm / 上端高さ {top_h*1000:.0f}mm")
res = []
for tilt in (-5, 0, 10, 25):
    a = math.radians(tilt); dz = cz - hz; dy = cy - hy
    zc = hz + dz * math.cos(a) + dy * math.sin(a)                 # 後方へ倒すと重心zが増える
    # 全体重心(スタンドは足の中央付近 z=(front+back)/2 と仮定)
    zt = (hm * zc + ms * (front + back) / 2) / (hm + ms)
    mb, mf = back - zt, zt - front; F_f = (hm + ms) * 9.81 * mf / 1000 / top_h; F_b = (hm + ms) * 9.81 * mb / 1000 / top_h
    print(f"チルト{tilt:+3d}°: 全体重心z={zt:6.1f} 前方余裕 {mf:6.1f}mm 後方余裕 {mb:6.1f}mm → 上端を前へ押す転倒力≈{F_f:.0f}N / 後ろへ≈{F_b:.0f}N [{'OK' if mf>40 and mb>40 else 'NG'}]")
    res.append((tilt, mf, mb))
Fl = (hm + ms) * 9.81 * (st['foot_w'] / 2 / 1000) / (top_h * 0.9)
print(f"横転(幅{st['foot_w']}mm): 上端を横へ押す転倒力≈{Fl:.0f}N。目標: 前後左右とも≥40N(指で押して倒れない)。")
