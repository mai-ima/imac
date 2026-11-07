#!/usr/bin/env python3
"""audit_control/ の台帳を初期化/更新する。tasks.json は唯一の正規タスク台帳(既存IDは上書きしない)。
file_coverage.csv は git ls-files を列挙(既存行の status/証拠は保持)。実行: python3 tools/audit_control_init.py"""
import csv, hashlib, json, os, subprocess, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); AC = f'{R}/audit_control'; os.makedirs(AC, exist_ok=True)
NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
def load(p, d):
    if not os.path.exists(p): return d
    try: return json.load(open(p, encoding='utf-8'))
    except Exception as e: raise SystemExit(f'{p} が壊れている({e})。台帳を上書きしないため中断(R9T-011)。git で復元してください')
T = load(f'{AC}/tasks.json', {'schema': 1, 'tasks': []}); have = {t['id'] for t in T['tasks']}
def add(id, title, sev='P2', typ='verify', origin='master_prompt', size='M', files=(), acc='', next_action='', status='triaged', deps=()):
    if id in have: return
    T['tasks'].append(dict(id=id, title=title, description=title, type=typ, origin=origin, requirement_ids=[], file_paths=list(files), severity=sev, size=size, impact='', dependencies=list(deps), parent_id=None, status=status,
                           history=[[NOW, status, 'seeded']], acceptance_criteria=acc or '原典/コードで再検証し CONFIRMED/PARTIAL/FALSE_POSITIVE/SUPERSEDED/UNVERIFIED を判定、必要なら修正+テスト+台帳更新', evidence=[], verification='', decision='', blocker_reason='', defer_reason='', next_action=next_action)); have.add(id)
K = {
 'K01': ('ドームの板厚・内寸(pod.wall/dome.sheet_t/CP-07/03_pod_cover.svg/ビューアWALL)の意味と混在', ['model/spec.json', 'model/custom_parts.json', 'tools/fitcheck.py', 'viewer/index.html']),
 'K02': ('スタンド寸法(足)と転倒計算の世代混在(CP-10/FMEA/joint-analysis)', ['model/spec.json', 'tools/stability.py', 'docs/joint-analysis.md']),
 'K03': ('最大厚・前面積層・公差(116→190mm, 18/19mm, 断面図)', ['model/spec.json', 'drawings/11a_section_AA.svg']),
 'K04': ('カメラ/マイク開口の図面不一致(01_front_glass.svg/CP-01)', ['drawings/01_front_glass.svg', 'drawings/parts/CP-01.svg']),
 'K05': ('fitcheck のAABB例外許可と偽PASS', ['tools/fitcheck.py']),
 'K06': ('stability の40N目標と判定ロジックの一致', ['tools/stability.py']),
 'K07': ('CPU 9950X3D/9800X3Dの情報混在', ['docs/spec/wiring-spec.md', 'docs/thermal-analysis.md']),
 'K08': ('491/504/552/510W の DC/AC/熱境界の混在', ['tools/power_budget.py', 'docs/spec']),
 'K09': ('液晶制御基板(ctrl_board)型番未確定・互換未検証', ['model/parts.json', 'docs/spec/panel-driver.md']),
 'K10': ('GPU→液晶コントローラ映像ケーブル未定義/W4長さ不一致', ['model/cables.json']),
 'K11': ('防塵フィルタ(#100/#150)と通気孔仕様の競合(CP-13)', ['drawings/parts/CP-13.svg']),
 'K12': ('gen_mfg_drawings の旧パラメータ(φ4.2/ピッチ7/pod.wall)', ['tools/gen_mfg_drawings.py']),
 'K13': ('gen_specs/gen_package の固定文言・同期漏れ', ['tools/gen_specs.py', 'tools/gen_package.py']),
 'K14': ('廃止CP-15の残留', ['drawings/parts/CP-15.svg']),
 'K15': ('CP-07 薄板の磁石ポケット深さ/ガスケット溝の成立性', ['model/custom_parts.json']),
 'K16': ('ヒンジ重力トルクの符号・文書間整合(hinge-design/joint-analysis)', ['docs/hinge-design.md', 'docs/joint-analysis.md']),
 'K17': ('6GHz RF窓と金属格子のOTA影響(CP-12)', ['model/custom_parts.json']),
 'K18': ('冷却・騒音・寿命の未実証(再循環/38dBA)', ['tools/thermal_calc.py']),
 'K19': ('要求/U台帳/FMEA件数の相違', ['docs/spec/system-spec.md', 'docs/unverified-tracker.md']),
 'K20': ('ビューアの固定表示値(温度/電力)とGLB差', ['viewer/index.html']),
 'K21': ('カメラ/マイク/スピーカー未選定', ['model/parts.json']),
 'K22': ('質量・重心・締結力の推定依存', ['tools/massmodel.py']),
 'K23': ('fitcheck の固定True(PCIe補助電源/パネル電源)', ['tools/fitcheck.py']),
 'K24': ('SVG/DXFが正式製造データとして不足(GD&T/STEP/穴表)', ['drawings', 'handoff']),
 'K25': ('外部比較・価格・規格の時点違い', ['docs']),
}
A = {'A01': '冷却時の液晶熱経路', 'A02': 'ファン/ポンプ停止のフェイルセーフ', 'A03': '音響と電磁/熱のトレードオフ', 'A04': '表示品質(60Hz/反射/HDR/VRR)', 'A05': 'ガラスの構造・修理性', 'A06': 'I/O人間工学(下向きI/O)', 'A07': '組立順序の成立', 'A08': 'ドーム脱着時のPE再接続', 'A09': '衝撃・輸送・耐久', 'A10': 'コスト・供給・小ロット', 'A11': '安全規格と知財の適用範囲', 'A12': 'データ品質(ハッシュ≠正当性)', 'A13': 'ロールバックと互換性', 'A14': 'セキュリティ/ソフト保守(CDN/ライセンス)', 'A15': 'スコープ優先順位(高性能・薄型・静音・安価・修理性)'}
for k, (t, f) in K.items(): add(k, f'[K] {t}', origin='previous_audit_hypothesis', files=f)
for k, t in A.items(): add(k, f'[A] {t}', origin='previous_audit_hypothesis')
add('M-ART', 'マスター指示の成果物(18〜25: 機能保全マトリクス/追加改修/回帰結果/K-A証拠表/改善案決定表/ChatGPT監査訂正/決定ログ/レビューチェック)を audit_control/ または audit_output/ に整備', 'P2', 'doc', size='L')
add('M-VAL', 'audit_control/validate_state.py(台帳整合の機械検査)を run_gates に組込む', 'P2', 'tool', size='S', status='ready')
add('M-CLAUDEMD', 'CLAUDE.md(恒常規則+台帳参照)を作成', 'P2', 'doc', size='XS', status='ready')
add('D05', '首振り(クロスローラ軸受+摩擦リング+波ばね+ストッパ)の断面図 D05(ハッチ+部品表+注記)', 'P2', 'drawing', 'user_request', 'L', ['tools/gen_mech_sections.py'], next_action='bearing 高さ13・ステータ凹部・摩擦リング+波ばねの断面を作図', status='ready')
add('D06', 'ストッパ(ゴムパッド/ポスト)・ドームラッチ/フック・キーホール吊りの断面図 D06', 'P2', 'drawing', 'user_request', 'L', status='ready')
add('POLY', 'Blenderモデルのポリゴン細分化(ユーザー許可): 曲面セグメント数・ベベル・円筒分割数を増やし、再生成→GLB→ビューア更新(GLB容量上限に注意)', 'P3', 'quality', 'user_request', 'M', ['blender/build_imac_pc_v8.py', 'blender/hardware_v8.py'], status='ready')
add('BAL-HW', 'バランサ端金物長(balance_end_hw_mm=16)を balance_calc/D04/Blender/docs へ反映済みの確認+ばね座屈細長比ゲート追加(done候補)', 'P1', 'fix', 'self', 'S', ['tools/balance_calc.py', 'model/spec.json', 'blender/hardware_v8.py'], status='in_review')
add('PIN-8', 'レバー先端横ピンØ6→Ø8 SUS630(曲げ145MPa)へ変更、strength_check追加(done候補)', 'P1', 'fix', 'self', 'S', ['tools/strength_check.py', 'model/spec.json'], status='in_review')
add('SHIM', '荷重調整方式を M8調整ねじ→ピールシム(±27N/本)へ変更した文書同期(custom_parts.json CP-23/hardware_list)と、調整範囲±10%要求(F±10%→3%)との整合確認', 'P2', 'fix', 'self', 'S', ['model/custom_parts.json'], status='ready', next_action='±27N/本=±7%<±10%(未調整公差)なので工場選別ばねorシム範囲拡大が必要か判定')
add('ANCHOR-6', 'アンカーピン中心が基台上面から6mm(s≦76)の強度/造形成立性と s 上限の再検討(基台座ぐり or 基台高さ変更の代替)', 'P2', 'verify', 'self', 'M', ['tools/balance_calc.py'], status='ready')
add('HINGE-D22', '摩擦ヒンジØ22が軸y=10で底面y=-1に1mm突出(ブーツ内空間)を motion_check へ明示検査', 'P3', 'verify', 'self', 'XS', ['tools/motion_check.py'], status='ready')
add('XCHK', 'consistency_check の対象事実を拡張(ばね/ヒンジ/軸径/部品個数/件数ベタ書き)し、HIST以外の WARN を整理', 'P3', 'tool', 'self', 'S', ['tools/consistency_check.py'], status='ready')
json.dump(T, open(f'{AC}/tasks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# file_coverage
old = {}
try:
    for r in csv.DictReader(open(f'{AC}/file_coverage.csv', encoding='utf-8')): old[r['path']] = r
except Exception: pass
files = subprocess.check_output(['git', 'ls-files', '-co', '--exclude-standard'], cwd=R, text=True).split('\n')
rows = []
for f in sorted(x for x in files if x and os.path.isfile(f'{R}/{x}')):
    h = '(generated)' if f in ('audit_control/file_coverage.csv', 'audit_output/01_FULL_FILE_MANIFEST.csv') else hashlib.sha256(open(f'{R}/{f}', 'rb').read()).hexdigest()[:16]      # 相互参照するこの2つの生成物はハッシュしない(実行のたびの差分ループの原因)
    cls = 'archive' if '/archive/' in f or f.startswith('archive/') else 'generated' if f.startswith(('handoff/', 'render/', 'drawings/', 'audit_output/')) or f.endswith(('.glb', '.glb.txt', '.png')) else 'current'
    o = old.get(f, {})
    rows.append(dict(path=f, class_=cls, size=os.path.getsize(f'{R}/{f}'), sha256_16=h, status=(o.get('status', 'NOT_REVIEWED') if (o.get('sha256_16') == h or o.get('status', 'NOT_REVIEWED') == 'NOT_REVIEWED') else 'CHANGED_RECHECK'), task_ids=o.get('task_ids', ''), evidence=o.get('evidence', '')))
with open(f'{AC}/file_coverage.csv', 'w', encoding='utf-8', newline='') as fo:
    w = csv.DictWriter(fo, fieldnames=['path', 'class_', 'size', 'sha256_16', 'status', 'task_ids', 'evidence']); w.writeheader(); w.writerows(rows)
from collections import Counter
print('tasks', len(T['tasks']), dict(Counter(t['status'] for t in T['tasks']))); print('files', len(rows), dict(Counter(r['status'] for r in rows)))
