"""業界標準(ISO)準拠の図枠/表題欄ライブラリ。
参照規格: ISO 5457(用紙サイズ/図枠: A3=420×297, 余白 左20/他10, 中心マーク, 区画記号), ISO 7200(表題欄の必須項目: 図面番号/題名/所有者/作成者/承認者/日付/改訂/用紙番号/用紙サイズ/縮尺/投影法/単位),
ISO 128-20(線の種類: 太0.5/細0.25, 破線/一点鎖線), ISO 129-1(寸法記入: 矢印・補助線), ISO 2768-mK(普通公差), ISO 5456-2(第三角法の投影記号), ISO 1101(幾何公差の枠), ISO 1302(表面性状記号)。
使い方: frame(title, num, scale='1:1', material='', finish='', rev='C', sheet='1/1', note='') -> SVG要素の文字列リスト(viewBox 0 0 420 297)。"""
import datetime, os
W, H = 420, 297
DATE = datetime.date.today().isoformat()
OWNER = 'iMac-style PC project (design values, unapproved)'
def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;')
def txt(x, y, s, sz=2.6, a='start', w='normal', fill='#000'): return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{sz}" text-anchor="{a}" font-weight="{w}" fill="{fill}">{esc(s)}</text>'
def ln(x1, y1, x2, y2, sw=.25, dash=''): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def projection_symbol(x, y, third=True):
    """ISO 5456-2 の第三角法(円錐台の正面+右側面)記号。"""
    s = [f'<g transform="translate({x},{y})" stroke="#000" stroke-width=".25" fill="none">']
    # 円錐台の正面図(台形) と 側面図(同心円)  第三角法: 側面図(右)が正面図の右側
    s += ['<path d="M0,2 L9,0 L9,8 L0,6 Z"/>', ln(-1, 4, 10, 4, .15, '3,0.6,0.6,0.6'), '<circle cx="15" cy="4" r="4"/>', '<circle cx="15" cy="4" r="2"/>', ln(10, 4, 20, 4, .15, '3,0.6,0.6,0.6'), ln(15, -1, 15, 9, .15, '3,0.6,0.6,0.6')]
    s.append('</g>'); return ''.join(s)
def frame(title, num, scale='1:1', material='-', finish='-', rev='C', sheet='1/1', note='', tol='ISO 2768-mK', third=True, size='A3'):
    o = []
    o.append('<rect width="100%" height="100%" fill="#fff"/>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="#000" stroke-width=".18"/>')                 # 用紙外形(トリム)
    o.append(f'<rect x="20" y="10" width="{W-30}" height="{H-20}" fill="none" stroke="#000" stroke-width=".7"/>')               # 図枠: 左20/他10, 太線0.7(ISO 5457)
    for k in range(1, 9):
        x = 20 + (W - 30) * k / 8
        if k < 8: o += [ln(x, 10, x, 15, .25), ln(x, H - 10, x, H - 15, .25)]
        o += [txt(20 + (W - 30) * (k - .5) / 8, 13.2, str(k), 2.4, 'middle'), txt(20 + (W - 30) * (k - .5) / 8, H - 11.4, str(k), 2.4, 'middle')]
    for k in range(1, 4): y = 10 + (H - 20) * k / 4; o += [ln(20, y, 25, y, .25), ln(W - 10, y, W - 15, y, .25)]
    for k, lab in enumerate('DCBA'): o += [txt(15, 10 + (H - 20) * (k + .5) / 4 + 1, lab, 2.4, 'middle'), txt(W - 5, 10 + (H - 20) * (k + .5) / 4 + 1, lab, 2.4, 'middle')]
    o += [ln(1, H / 2, 6, H / 2, .5), ln(W - 6, H / 2, W - 1, H / 2, .5), ln(W / 2 + 5, 1, W / 2 + 5, 6, .5), ln(W / 2 + 5, H - 6, W / 2 + 5, H - 1, .5)]      # 中心マーク
    # 表題欄(ISO 7200): 右下 180×40
    bx, by, bw, bh = W - 10 - 180, H - 10 - 44, 180, 44
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#fff" stroke="#000" stroke-width=".5"/>')
    o += [ln(bx, by + 14, bx + bw, by + 14, .25), ln(bx, by + 26, bx + bw, by + 26, .25), ln(bx + 100, by + 14, bx + 100, by + bh, .25), ln(bx + 140, by + 14, bx + 140, by + bh, .25), ln(bx + 100, by + 35, bx + bw, by + 35, .25)]
    o += [txt(bx + 2, by + 4, '題名 / Title', 1.9, fill='#555'), txt(bx + 2, by + 11, title, 4.6, w='bold'),
          txt(bx + 2, by + 18, '所有者 / Owner', 1.9, fill='#555'), txt(bx + 2, by + 23.5, OWNER, 2.6),
          txt(bx + 2, by + 30, '材質 / Material', 1.9, fill='#555'), txt(bx + 2, by + 34, str(material)[:60], 2.3), txt(bx + 2, by + 38.5, '表面処理 / Finish', 1.9, fill='#555'), txt(bx + 2, by + 42, str(finish)[:60], 2.3),
          txt(bx + 102, by + 18, '図面番号 / Drawing No.', 1.9, fill='#555'), txt(bx + 102, by + 24, f'IMAC-PC-{num}', 4.0, w='bold'),
          txt(bx + 102, by + 30, '普通公差 / General tol.', 1.9, fill='#555'), txt(bx + 102, by + 33.5, tol, 2.3),
          txt(bx + 142, by + 18, '改訂 / Rev.', 1.9, fill='#555'), txt(bx + 142, by + 24.5, rev, 4.0, w='bold'), txt(bx + 142, by + 30, '用紙 / Sheet', 1.9, fill='#555'), txt(bx + 142, by + 33.5, f'{size}  {sheet}', 2.3),
          txt(bx + 102, by + 4, '縮尺 / Scale', 1.9, fill='#555'), txt(bx + 102, by + 10.5, scale, 3.6, w='bold'), txt(bx + 142, by + 4, '単位 / Unit', 1.9, fill='#555'), txt(bx + 142, by + 10.5, 'mm', 3.6, w='bold'),
          txt(bx + 102, by + 38.5, '作成 / Drawn', 1.9, fill='#555'), txt(bx + 102, by + 42, f'Claude {DATE}', 2.3), txt(bx + 142, by + 38.5, '承認 / Approved', 1.9, fill='#555'), txt(bx + 142, by + 42, '未承認(設計値)', 2.3)]
    o.append(projection_symbol(bx - 26, by + 30, third))
    o.append(txt(bx - 26, by + 24, '第三角法 / 3rd angle' if third else '第一角法 / 1st angle', 2.0))
    # 改訂履歴(ISO 7200の補助): 表題欄の左
    rx = bx - 100; ry = by + 6
    o += [f'<rect x="{rx}" y="{ry}" width="70" height="38" fill="#fff" stroke="#000" stroke-width=".25"/>', ln(rx, ry + 5, rx + 70, ry + 5, .25), ln(rx + 8, ry, rx + 8, ry + 38, .25), ln(rx + 40, ry, rx + 40, ry + 38, .25),
          txt(rx + 2, ry + 3.6, 'Rev', 2.0), txt(rx + 10, ry + 3.6, '内容 / Description', 2.0), txt(rx + 42, ry + 3.6, '日付', 2.0),
          txt(rx + 2, ry + 9, 'A', 2.0), txt(rx + 10, ry + 9, '初版(v6)', 2.0), txt(rx + 42, ry + 9, '2026-11-03', 2.0), txt(rx + 2, ry + 14, 'B', 2.0), txt(rx + 10, ry + 14, 'ドーム/トレイ/v7', 2.0), txt(rx + 42, ry + 14, '2026-11-05', 2.0),
          txt(rx + 2, ry + 19, rev, 2.0), txt(rx + 10, ry + 19, 'v8: 5070Ti/SF1000/断熱/再配置', 2.0), txt(rx + 42, ry + 19, DATE, 2.0)]
    if note: o.append(txt(22, by - 2, note[:150], 2.4))
    o.append(txt(22, 18.5, '注: 寸法は設計値(未承認)。製造前に最終BOMで再生成・公差協議。一般公差 ISO 2768-mK, 面取り/バリ処理は注記なき限り C0.2。', 2.3, fill='#444'))
    return o
def dim_h(x1, x2, y, label, off=6):
    """ISO 129: 補助線は寸法から1〜2mm離し3mm突出、矢印は塗り(閉)、寸法値は線の上。"""
    return [ln(x1, y + 1, x1, y + off + 2, .18), ln(x2, y + 1, x2, y + off + 2, .18), ln(x1, y + off, x2, y + off, .25), f'<path d="M{x1},{y+off} l3,-1 v2 z M{x2},{y+off} l-3,-1 v2 z" fill="#000"/>', txt((x1 + x2) / 2, y + off - 1, label, 2.8, 'middle')]
def dim_v(y1, y2, x, label, off=-6):
    return [ln(x - 1, y1, x + off - 2, y1, .18), ln(x - 1, y2, x + off - 2, y2, .18), ln(x + off, y1, x + off, y2, .25), f'<path d="M{x+off},{y1} l-1,3 h2 z M{x+off},{y2} l-1,-3 h2 z" fill="#000"/>', f'<text x="{x+off-1:.2f}" y="{(y1+y2)/2:.2f}" font-size="2.8" text-anchor="middle" transform="rotate(-90 {x+off-1:.2f} {(y1+y2)/2:.2f})">{esc(label)}</text>']
