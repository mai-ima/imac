#!/usr/bin/env python3
"""実形状干渉検査の結果(blender --check-interference が出す JSON)を分類し、model/interference_report.json と docs/interference-report.md を生成する(INTF-01)。
使い方: /tmp/bl/.venv/bin/python blender/build_imac_pc_v8.py --vent-mode texture --check-interference /tmp/intf.json && python3 tools/interference_report.py /tmp/intf.json
分類: (1) 接触のみ(AABB重なりの最小値<0.15mm)=埋め込みでない (2) 意図した一体/嵌合(ALLOW、理由必須) (3) 要対処(残り)。残りが0でなければ run_gates は UNVERIFIED(rc2)。"""
import json, re, sys, os, collections, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOW = [  # (名前正規表現a, 名前正規表現b, 理由)
 (r'^fan_.*_blade\d+$', r'^fan_.*_hub$', 'ファンの羽根とハブは一体品として別メッシュで描いている(実物も一体成形)'),
 (r'^board_hdr_.*[a-z0-9]$', r'^board_hdr_.*_pin\d+$', 'ヘッダのピンは筐体へ挿入されている(筐体上面から突出)'),
 (r'^psu_grille_ring\d+$', r'^psu_grille_(ring\d+|spokes)$', 'グリルのリングとスポークは一体品'),
 (r'^ssd_body$', r'^ssd_slit\d+$', 'スリット印刷(厚み0.08mmの面)'),
 (r'^psu_body$', r'^psu_socket\d+$', 'モジュラーソケットは筐体前面の開口に嵌合'),
 (r'^pump_(cap_lip|cap_top|housing_body|elbow|swivel_\d|fitting_\d)$', r'^pump_(cap_lip|cap_top|housing_body|elbow|swivel_\d|fitting_\d)$', 'ポンプ筐体・キャップ・エルボ・ホース口は一体成形品を複数の基本形で表現(ARCTIC公式の外形)'),
 (r'^hinge_axle$', r'^(hinge_friction\d|stand_arm_boss\d|stand_arm_strip\d|hinge_tail_lever\d)$', '【要モデル化=台帳INTF-03】ヒンジ軸Ø12が各部品のボアを貫通する嵌合。ボア(穴)を未モデルのため重なって検出される'),
 (r'^cam_roller_pin\d$', r'^cam_roller\d$', 'ローラはピンに回転嵌合(ボア未モデル=INTF-03)'),
 (r'^stand_arm_strip\d$', r'^stand_arm_boss\d$', '側板のストリップとボスは一体品を別基本形で表現'),
 (r'^stand_swivel_(stator|rotor)$', r'^stand_swivel_stop_(l|r|tab)$', 'ストッパ爪は板にねじ止めされた一体の突起(座面は板内へ埋め込み表現=INTF-03)'),
 (r'^cable_plug_', r'^(atx24|eps8|gpu_12v2x6)$', 'プラグと受口の嵌合(嵌入量2mmの設計値。実物は受口内へ挿入される)'),
 (r'^clip_pad\d+$', r'^clip_post\d+$', 'クリップのパッドとポストは一体品'),
]
def depth(p): return min(p['aabb_overlap_mm'])
def main(src):
    d = json.load(open(src)); touch = 0; allowed = collections.Counter(); rest = []
    for p in d['pairs']:
        if depth(p) < 0.15: touch += 1; continue
        why = next((w for a, b, w in ALLOW if (re.search(a, p['a']) and re.search(b, p['b'])) or (re.search(a, p['b']) and re.search(b, p['a']))), None)
        if why: allowed[why] += 1
        else: rest.append(p)
    rest.sort(key=lambda p: -depth(p))
    out = {'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'objects': d['objects'], 'pairs_total': len(d['pairs']), 'touch_only': touch, 'allowed': dict(allowed), 'remaining': len(rest), 'remaining_pairs': rest[:400],
           'note': '深さ=2物体のAABB重なりの最小軸(近似)。三角形交差のある対のみ。実際の貫入量ではなく上限の目安。'}
    json.dump(out, open(f'{R}/model/interference_report.json', 'w'), ensure_ascii=False, indent=1)
    L = ['# 実形状 干渉・埋め込み検査(INTF-01)', '', f'- 検査: Blender 評価済みメッシュのBVH交差(`blender/build_imac_pc_v8.py --check-interference`)、{d["objects"]}物体、交差対 {len(d["pairs"])}。', f'- 接触のみ(深さ<0.15mm): {touch} / 意図した一体・嵌合(ALLOW): {sum(allowed.values())} / **要対処: {len(rest)}**', '', '## ALLOW(理由つき)']
    L += [f'- {w}: {n}対' for w, n in allowed.items()]
    L += ['', '## 要対処(深さ順・上位80)', '| 物体A | 物体B | 三角形交差 | AABB重なり[x,y,z] mm | 深さ(近似) |', '|---|---|---|---|---|']
    L += [f'| {p["a"]} | {p["b"]} | {p["tri_pairs"]} | {p["aabb_overlap_mm"]} | {depth(p):.2f} |' for p in rest[:80]]
    open(f'{R}/docs/interference-report.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('remaining', len(rest), 'touch', touch, 'allowed', sum(allowed.values()))
if __name__ == '__main__': main(sys.argv[1])
