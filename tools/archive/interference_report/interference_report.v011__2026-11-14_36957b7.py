#!/usr/bin/env python3
"""実形状干渉検査の結果(blender --check-interference が出す JSON)を分類し、model/interference_report.json と docs/interference-report.md を生成する(INTF-01)。
使い方: /tmp/bl/.venv/bin/python blender/build_imac_pc_v8.py --vent-mode texture --check-interference /tmp/intf.json && python3 tools/interference_report.py /tmp/intf.json
分類: (1) 接触のみ(AABB重なりの最小値<0.15mm)=埋め込みでない (2) 意図した一体/嵌合(ALLOW、理由必須) (3) 要対処(残り)。残り(要対処)または『負債ALLOW』(理由に未モデル/保留/未確認を含む=未解決の許容)が0でなければ `--gate` は rc2(UNVERIFIED。合格ではない)。run_gates.sh から `--gate` を呼ぶ。"""
import json, re, sys, os, collections, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOW = [  # (名前正規表現a, 名前正規表現b, 理由)
 (r'^fan_.*_blade\d+$', r'^fan_.*_hub$', 'ファンの羽根とハブは一体品として別メッシュで描いている(実物も一体成形)'),
 (r'^psu_grille_ring\d+$', r'^psu_grille_(ring\d+|spokes)$', 'グリルのリングとスポークは一体品'),
 (r'^psu_body$', r'^psu_socket\d+$', 'モジュラーソケットは筐体前面の開口に嵌合'),
 (r'^pump_(cap_lip|cap_top|housing_body|elbow|swivel_\d|fitting_\d)$', r'^pump_(cap_lip|cap_top|housing_body|elbow|swivel_\d|fitting_\d)$', 'ポンプ筐体・キャップ・エルボ・ホース口は一体成形品を複数の基本形で表現(ARCTIC公式の外形)'),
 (r'^hinge_axle$', r'^(hinge_friction\d|stand_arm_boss\d|stand_arm_strip\d|hinge_tail_lever\d)$', '【要モデル化=台帳INTF-03】ヒンジ軸Ø12が各部品のボアを貫通する嵌合。ボア(穴)を未モデルのため重なって検出される'),
 (r'^cam_roller_pin\d$', r'^cam_roller\d$', 'ローラはピンに回転嵌合(ボア未モデル=INTF-03)'),
 (r'^stand_arm_strip\d$', r'^stand_arm_boss\d$', '側板のストリップとボスは一体品を別基本形で表現'),
 (r'^stand_swivel_(stator|rotor)$', r'^stand_swivel_stop_(l|r|tab)$', 'ストッパ爪は板にねじ止めされた一体の突起(座面は板内へ埋め込み表現=INTF-03)'),
 (r'^cable_plug_', r'^(atx24|eps8|gpu_12v2x6)$', 'プラグと受口の嵌合(嵌入量2mmの設計値。実物は受口内へ挿入される)'),
 (r'^cable_plug_F\d_', r'^board_hdr_', 'ヘッダのプラグは筐体へ1mm嵌合する設計値(基板側のみモデル。ケーブル本体は MDC-FANCABLE で保留)'),
 (r'^ac_inlet_(flange|body|socket)$', r'^ac_inlet_(flange|body|socket)$', 'ACインレットのフランジ・本体・ソケットは一体の部品(別基本形で表現)'),
 (r'^hinge_bolt_head\d$', r'^hinge_bolt\d$', 'ボルト頭と軸は一体品(別基本形で表現)'),
 (r'^vrm_(shroud|trim)$', r'^vrm_(shroud|trim)$', 'VRMシュラウドとトリムは一体の外装部品(別基本形で表現)'),
 (r'^gpu_cradle_(base|wall_[lr])$', r'^gpu_cradle_(base|wall_[lr])$', 'GPUクレードルの底板と側壁は一体の板金折り曲げ品'),
 (r'^gpu_(shroud_body|trim)$', r'^gpu_(shroud_body|trim)$', 'GPUシュラウドと加飾トリムは一体の外装部品'),
 (r'^hinge_friction\d(_cap)?$', r'^hinge_friction\d_cap$', '摩擦板とそのキャップは一体の組立品(キャップは摩擦板へ圧入)'),
 (r'^pe_(nut|stud)_tray$', r'^pe_(nut|stud)_tray$', 'ナットはスタッドにねじ込み(ねじ嵌合, ねじ山は未モデル)'),
 (r'^riser_plug$', r'^(riser\d|pcie_gold)$', 'ライザーのプラグ部はケーブル基板と一体、金端子はPCIeスロットへ挿入される嵌合'),
 (r'^latch_strike\d$', r'^latch_cam\d$', '1/4回転ラッチのカムはストライク板へ圧着(クランプ接触0.7mm)'),
 (r'^hinge_axle$', r'^hinge_(eclip\d|friction\d_cap)$', 'ヒンジ軸がEリング/キャップのボアを貫通(ボア未モデル=INTF-03)'),
 (r'^stand_swivel_bearing$', r'^stand_swivel_friction_ring$', '摩擦リングは軸受座面に圧着する嵌合部品'),
 (r'^hinge_block_base$', r'^hinge_cheek_[lr]$', 'ヒンジブロック台座と頬板は溶接一体の板金品'),
 (r'^io_shield$', r'^io_.*_tongue$', '舌片はI/Oシールドの一部(切起こし)'),
 (r'^cover_back$', r'^hook_tab\d$', '掛け爪はドーム(cover_back)と一体成形の突起(別基本形で表現。台帳MODEL記載)'),
 (r'^hang_bushing\d[abc]$', r'^hang_bushing\d[abc]$', '吊りピンのブッシュ(16x28長丸)は3基本形(円2+矩形)を重ねて1枚の板として表現'),
 (r'^pe_braid_swivel$', r'^pe_lug_(rotor|foot)$', 'PE編組の端は圧着端子(M4リング)にかしめて一体(端子内へ編組端が入る)'),
 (r'^riser\d$', r'^riser_gpu_conn$', 'フレックスライザーの端末はGPU側コネクタ(ZIF)の口へ挿入される(嵌合。ZIFの差込口は未モデル=MDB-004)'),
 (r'^fan_pump_vrm_frame$', r'^pump_housing_body$', '【公差内の重なり0.5mm】VRMファン径Ø55は未確認(U58)、筐体位置はARCTIC図面の画素実測(±0.5〜1mm)。実測公差以内のため寸法確定までUNVERIFIEDとして保留(台帳 MDC/U58)'),
]
def depth(p): return min(p['aabb_overlap_mm'])
DEBT_WORDS = ('未モデル', '要モデル化', '保留', '未確認', 'UNVERIFIED', '未解決')
def is_debt(why): return any(w in why for w in DEBT_WORDS)
def classify(p):
    return next((w for a, b, w in ALLOW if (re.search(a, p['a']) and re.search(b, p['b'])) or (re.search(a, p['b']) and re.search(b, p['a']))), None)
def main(src):
    d = json.load(open(src)); touch = 0; allowed = collections.Counter(); rest = []; apairs = []
    for p in d['pairs']:
        if depth(p) < 0.15: touch += 1; continue
        why = classify(p)
        if why: allowed[why] += 1; apairs.append({'a': p['a'], 'b': p['b'], 'depth_mm': round(depth(p), 3), 'aabb': p['aabb_overlap_mm'], 'tri_pairs': p['tri_pairs'], 'reason': why, 'debt': is_debt(why)})
        else: rest.append(p)
    rest.sort(key=lambda p: -depth(p)); apairs.sort(key=lambda q: -q['depth_mm'])
    debt = [q for q in apairs if q['debt']]
    out = {'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'objects': d['objects'], 'pairs_total': len(d['pairs']), 'touch_only': touch, 'allowed': dict(allowed), 'allowed_pairs': apairs, 'allowed_debt': len(debt), 'remaining': len(rest), 'remaining_pairs': rest[:400],
           'note': '深さ=2物体のAABB重なりの最小軸(近似)。三角形交差のある対のみ。実際の貫入量ではなく上限の目安。allowed_debt=許容理由に未モデル/保留/未確認を含む対(=未解決。合格ではない)。ケーブル等の曲線オブジェクト・非表示物は検査対象外(R13参照)。'}
    json.dump(out, open(f'{R}/model/interference_report.json', 'w'), ensure_ascii=False, indent=1)
    L = ['# 実形状 干渉・埋め込み検査(INTF-01)', '', f'- 検査: Blender 評価済みメッシュのBVH交差(`blender/build_imac_pc_v8.py --check-interference`)、{d["objects"]}物体、交差対 {len(d["pairs"])}。', f'- 接触のみ(深さ<0.15mm): {touch} / 意図した一体・嵌合(ALLOW): {sum(allowed.values())}(うち**負債ALLOW(未解決の許容)={len(debt)}**) / **要対処: {len(rest)}**', '- 注意: ケーブル(曲線)・非表示物・完全内包は検出できない(audit_control/reports/R13_interference_allow.md)。', '', '## ALLOW(理由つき)']
    L += [f'- {w}: {n}対' for w, n in allowed.items()]
    L += ['', '## 負債ALLOW(未解決のまま許容している対。合格ではない)', '| 物体A | 物体B | 深さ(近似mm) | 理由 |', '|---|---|---|---|']
    L += [f'| {q["a"]} | {q["b"]} | {q["depth_mm"]} | {q["reason"][:80]} |' for q in debt]
    L += ['', '## ALLOW 深さ上位20(深い貫入を許容していないか確認用)', '| 物体A | 物体B | 深さ(近似mm) | 理由 |', '|---|---|---|---|']
    L += [f'| {q["a"]} | {q["b"]} | {q["depth_mm"]} | {q["reason"][:60]} |' for q in apairs[:20]]
    L += ['', '## 要対処(深さ順・上位80)', '| 物体A | 物体B | 三角形交差 | AABB重なり[x,y,z] mm | 深さ(近似) |', '|---|---|---|---|---|']
    L += [f'| {p["a"]} | {p["b"]} | {p["tri_pairs"]} | {p["aabb_overlap_mm"]} | {depth(p):.2f} |' for p in rest[:80]]
    open(f'{R}/docs/interference-report.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('remaining', len(rest), 'debt_allow', len(debt), 'touch', touch, 'allowed', sum(allowed.values()))
def gate():
    """保存済みJSONから判定: 要対処>0 または 負債ALLOW>0 なら rc2(UNVERIFIED。合格ではない)。JSONが無ければ rc1。"""
    f = f'{R}/model/interference_report.json'
    if not os.path.exists(f): print('interference_report.json なし'); return 1
    j = json.load(open(f)); n = j['remaining'] + j.get('allowed_debt', 0)
    print(f"干渉: 要対処={j['remaining']} 負債ALLOW={j.get('allowed_debt', 'n/a')} (生成 {j['generated']})"); return 2 if n > 0 else 0
if __name__ == '__main__':
    if sys.argv[1] == '--gate': sys.exit(gate())
    main(sys.argv[1])
