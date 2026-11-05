#!/usr/bin/env python3
"""転倒安定性の概算。質量はカタログ値/推定値(未実測)。実測後に値を更新すること。
モデル: 前面ガラス面を鉛直に近い角度(チルト)で立てた本体+背面ドーム+スタンド。足(奥行 foot_d)の前端・後端を転倒の支点とする。"""
import json, math, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{R}/model/spec.json')); P = json.load(open(f'{R}/model/parts.json'))
# (名前, 質量kg, 重心位置 (奥行方向z mm: 前面ガラス=0, 背面が+) , 重心の高さ y mm: 本体下端=0) — 推定
masses = [
 ("パネル", 2.45, 8, 208), ("前面ガラス", 1.3, 0.5, 208), ("スラブ背板+アルミ筐体(推定)", 4.5, 15, 208),
 ("ドームシェル(推定)", 4.0, 60, 205), ("基板+CPU+クーラー(推定1.2kg)", 1.2, 55, 210), ("GPU(推定1.0kg)", 1.0, 40, 205),
 ("電源(0.96kg)", 0.96, 30, 150), ("ファン2+制御基板+ケーブル(推定0.8kg)", 0.8, 30, 200), ("スタンド(アルミ一枚板, 推定)", 1.8, 40, -40)]
tot = sum(m for _, m, _, _ in masses); cz = sum(m * z for _, m, z, _ in masses) / tot; cy = sum(m * y for _, m, _, y in masses) / tot
print(f"総質量(推定) {tot:.1f} kg / 重心 z={cz:.0f}mm(前面ガラスから背面側), y={cy:.0f}mm")
foot_d = S['stand']['foot_depth']; ZC = (S['slab_t'] + S['pod']['total_t'] if 'pod' in S else 0) / 2
# 足の中心はヒンジ(=スタンド腕)の位置と同じと仮定。足は前後に foot_d/2 ずつ張り出す。
for tilt in (-5, 0, 25):
    a = math.radians(tilt)
    # チルトで上端が後ろへ倒れる(+): 重心の z が増える方向。簡易に重心をヒンジ(y=0, z=zc)まわりに回転
    zc = (S['slab_t'] + S['dome']['total_t']) / 2 if 'dome' in S else 60
    dz = cz - zc; dy = cy - 0
    z_cg = zc + dz * math.cos(a) + dy * math.sin(a)   # 後方へ傾けるとz_cgが増える
    front = zc - foot_d / 2; back = zc + foot_d / 2
    margin_back = back - z_cg; margin_front = z_cg - front
    ok = margin_back > 0 and margin_front > 0
    print(f"チルト{tilt:+3d}°: 重心z={z_cg:6.1f} / 足の範囲 {front:.0f}〜{back:.0f} → 後方余裕 {margin_back:6.1f}mm, 前方余裕 {margin_front:6.1f}mm  [{'OK' if ok else 'NG(転倒の恐れ)'}]")
