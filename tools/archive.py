#!/usr/bin/env python3
"""版管理アーカイブ。各ディレクトリ直下の archive/ に、ファイルごとの過去版を連番(vNNN)で保存する。

構成:  <dir>/archive/<名前>/<名前>.vNNN__<日付>_<commit>.<拡張子>   … 直近の版(current世代)
       <dir>/archive/gen-NNN/<名前>/…                              … ロールアップ済みの古い世代
       <dir>/archive/index.json                                   … 版の一覧(元パス, 版, 世代, 日付, commit, sha256)
コマンド:
  auto               git の staged 変更(更新ファイル)について、HEAD の版を保存 (pre-commit から呼ぶ)
  snapshot FILE...   作業ツリーの現行版を保存 (内容が最新版と同一ならスキップ)
  rollup [--keep N] [--days D]  各ファイルで最新N版(既定3)より古い版、またはD日(既定30)より古い版を新世代 gen-NNN に移す
  list [DIR]         一覧表示
ルール: 削除はしない(移動のみ)。復元は archive/ から元の場所へコピー。
"""
import sys, os, json, hashlib, shutil, subprocess, datetime, re
ROOT = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
os.chdir(ROOT)
MANAGED = re.compile(r'^(docs|drawings|model|cad|concept|render|viewer|tools|blender)/.*\.(md|txt|json|svg|dxf|scad|py|sh|png|jpg|glb|html|blend)$')

def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout.strip()

def adir(path):
    return os.path.join(os.path.dirname(path), 'archive')

def idx_load(d):
    p = os.path.join(d, 'index.json')
    return json.load(open(p)) if os.path.exists(p) else {'entries': []}

def idx_save(d, idx):
    os.makedirs(d, exist_ok=True)
    idx['entries'].sort(key=lambda e: (e['src'], e['version']))
    json.dump(idx, open(os.path.join(d, 'index.json'), 'w'), ensure_ascii=False, indent=1)
    lines = ['# archive 索引（自動生成: tools/archive.py）', '', '| 元ファイル | 版 | 世代 | 日付 | commit | 保存先 |', '|---|---|---|---|---|---|']
    for e in idx['entries']:
        lines.append(f"| {os.path.basename(e['src'])} | v{e['version']:03d} | {e['gen']} | {e['date']} | {e['commit']} | {e['file']} |")
    open(os.path.join(d, 'INDEX.md'), 'w').write('\n'.join(lines) + '\n')

def add_version(src, data, date, commit, gen='current'):
    d = adir(src)
    idx = idx_load(d)
    sha = hashlib.sha256(data).hexdigest()
    mine = [e for e in idx['entries'] if e['src'] == src]
    if mine and mine[-1]['sha256'] == sha:
        return None
    if any(e['sha256'] == sha for e in mine):
        return None
    ver = max([e['version'] for e in mine], default=0) + 1
    stem, ext = os.path.splitext(os.path.basename(src))
    rel = os.path.join(stem, f"{stem}.v{ver:03d}__{date}_{commit}{ext}")
    full = os.path.join(d, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'wb').write(data)
    idx['entries'].append({'src': src, 'version': ver, 'gen': gen, 'date': date, 'commit': commit, 'sha256': sha, 'file': rel})
    idx_save(d, idx)
    return full

def cmd_auto():
    out = sh('git', 'diff', '--cached', '--name-status', '--diff-filter=M')
    n = 0
    for line in out.splitlines():
        f = line.split('\t', 1)[1]
        if not MANAGED.match(f) or '/archive/' in f:
            continue
        data = subprocess.run(['git', 'show', f'HEAD:{f}'], capture_output=True).stdout
        c = sh('git', 'log', '-1', '--format=%h|%cs', '--', f).split('|')
        r = add_version(f, data, c[1] if len(c) > 1 else str(datetime.date.today()), c[0])
        if r:
            subprocess.run(['git', 'add', adir(f)]); n += 1; print('archived', r)
    return n

def cmd_snapshot(files):
    for f in files:
        f = os.path.relpath(os.path.abspath(f), ROOT)
        c = sh('git', 'log', '-1', '--format=%h', '--', f) or 'wip'
        r = add_version(f, open(f, 'rb').read(), str(datetime.date.today()), c)
        print('archived' if r else 'same', f, r or '')

def cmd_rollup(keep=3, days=30):
    today = datetime.date.today()
    for d, _, fs in os.walk('.'):
        if os.path.basename(d) != 'archive' or 'index.json' not in fs:
            continue
        idx = idx_load(d)
        gens = [int(m.group(1)) for x in os.listdir(d) if (m := re.match(r'gen-(\d+)$', x))]
        newgen = f"gen-{max(gens, default=0) + 1:03d}"
        moved = 0
        for src in sorted({e['src'] for e in idx['entries']}):
            cur = [e for e in idx['entries'] if e['src'] == src and e['gen'] == 'current']
            keepset = {e['version'] for e in cur[-keep:]}
            for e in cur:
                age = (today - datetime.date.fromisoformat(e['date'])).days
                if e['version'] in keepset and age <= days:
                    continue
                if e['version'] in keepset and len(cur) <= keep:
                    continue
                new = os.path.join(newgen, e['file'])
                os.makedirs(os.path.dirname(os.path.join(d, new)), exist_ok=True)
                subprocess.run(['git', 'mv', os.path.join(d, e['file']), os.path.join(d, new)]) if sh('git', 'ls-files', os.path.join(d, e['file'])) else shutil.move(os.path.join(d, e['file']), os.path.join(d, new))
                e['file'] = new; e['gen'] = newgen; moved += 1
        if moved:
            idx_save(d, idx); print(d, '->', newgen, moved, 'files')

def cmd_list(d=None):
    for dd, _, fs in os.walk(d or '.'):
        if os.path.basename(dd) == 'archive' and 'INDEX.md' in fs:
            print('==', dd); print(open(os.path.join(dd, 'INDEX.md')).read())

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    if a[0] == 'auto': cmd_auto()
    elif a[0] == 'snapshot': cmd_snapshot(a[1:])
    elif a[0] == 'rollup':
        k = int(a[a.index('--keep') + 1]) if '--keep' in a else 3
        dd = int(a[a.index('--days') + 1]) if '--days' in a else 30
        cmd_rollup(k, dd)
    elif a[0] == 'list': cmd_list(a[1] if len(a) > 1 else None)
