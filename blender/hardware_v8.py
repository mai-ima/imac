# ===== hardware_v8.py: build_imac_pc_v8.py から exec される。小部品(ばね/ネジ/スタンドオフ/ラッチ/磁石/ピン/ブッシュ/接地/クリップ等)を全て描画し、model/hardware_list.json に一覧を書き出す =====
HW = []     # (区分, 名称, 数量, 仕様)
def hw(cat, name, qty, spec): HW.append({'cat': cat, 'name': name, 'qty': qty, 'spec': spec})
M['spring'] = principled('spring_steel', '#9aa0a6', 1.0, 0.28); M['pom'] = principled('pom', '#d9d9d6', 0.0, 0.55); M['pe_gy'] = principled('pe_green_yellow', '#7a9b1f', 0.0, 0.5)
M['sus'] = principled('sus304', '#aeb1b4', 1.0, 0.33); M['magnet'] = principled('magnet_nickel', '#8e949b', 1.0, 0.25)
TZ = 5.0     # トレイ上面(スラブ背面からの高さ)
def dz(zl): return Z0 - zl          # 設計z
# ---------- スタンドオフ + ネジ(ITX規格値は U17) ----------
def standoff(tag, x, y, z0, z1, screw_z=None, hexr=3.2):
    icyl(f'standoff_{tag}', hexr, z1 - z0, 'z', x, y, (z0 + z1) / 2, M['sus'], 6)
    if screw_z is not None:
        icyl(f'screw_{tag}_head', 2.8, 2.4, 'z', x, y, screw_z + 1.2, M['alublack'], 16); icyl(f'screw_{tag}_hex', 1.3, .3, 'z', x, y, screw_z + 2.55, M['rubber'], 6)
ITX = ((10.2, 6.4), (165.1, 6.4), (10.2, 163.8), (165.1, 163.8))
for k, (hx, hy) in enumerate(ITX): standoff(f'board{k}', bx + hx, by + hy, TZ, bz, screw_z=bz + 1.6)
hw('スタンドオフ', 'PEM TSOA-M3 6.35mm(基板用)+M3×6ナベ', 4, '基板Mini-ITX穴(規格値 U17)')
px_c, py_c, pz_c = lp('psu'); psw, psh, _ = ls('psu')
for k, (dx, dy) in enumerate(((8, 8), (psw - 8, 8), (8, psh - 8), (psw - 8, psh - 8))):
    standoff(f'psu{k}', px_c + dx, py_c + dy, TZ, pz_c); icyl(f'screw_psu{k}_under', 2.8, 2.4, 'z', px_c + dx, py_c + dy, 1.7, M['alublack'], 16)
rx0, ry0_, rz0 = lp('radiator')
for k, (dx, dy) in enumerate(((10, 10), (110, 10), (10, 267), (110, 267))):
    standoff(f'rad{k}', rx0 + dx, ry0_ + dy, TZ, rz0); icyl(f'screw_rad{k}_under', 2.8, 2.4, 'z', rx0 + dx, ry0_ + dy, 1.7, M['alublack'], 16)
cx0, cy0, cz0 = lp('ctrl_board')
for k, (dx, dy) in enumerate(((4, 4), (51, 4), (4, 146), (51, 146))): standoff(f'ctrl{k}', cx0 + dx, cy0 + dy, TZ, cz0, screw_z=cz0 + 1.6, hexr=2.9)
for k, (dx, dy) in enumerate(((20, 12), (GW - 20, 12))): standoff(f'gpu{k}', gx + dx, gy + dy, TZ, gz)
hw('スタンドオフ', 'PEM TSOA-M3 3.0mm(PSU/ラジエーター/ctrl/GPU)+M3×6', 4 + 4 + 4 + 2, 'SFX規格穴 U17 / ラジエーター穴はARCTIC公式図で確認要')
# ---------- 吊りピン(肩ねじ Ø5×6 + 頭Ø9×3) + SUSブッシュ(Ø16×1.0, キーホール孔付き) + トレイ拘束ネジ ----------
for k, (kx, ky) in enumerate(KH):
    pyk = ky + 12             # 掛けた状態: ピンは細溝の上端
    icyl(f'hang_pin{k}_shoulder', 2.5, 6, 'z', kx, pyk, 3.0, M['sus'], 24)
    icyl(f'hang_pin{k}_head', 4.5, 3, 'z', kx, pyk, TZ + 1.0 + 1.5, M['sus'], 24)
    icyl(f'hang_pin{k}_hexsocket', 1.6, .4, 'z', kx, pyk, TZ + 1.0 + 3.1, M['rubber'], 6)
    b_ = icyl(f'hang_bushing{k}', 8, 1.0, 'z', kx, ky, TZ + .5, M['sus'], 32); mb = b_.modifiers.new('hole', 'BOOLEAN'); mb.object = kh_cut; mb.operation = 'DIFFERENCE'; mb.solver = 'EXACT'
hw('吊り機構', 'SUS肩ねじ M3・肩径Ø5×6・頭Ø9×3(CP-04)', 4, '品番 U29'); hw('吊り機構', 'SUSブッシュ t1.0 Ø16(CP-05)', 4, '支圧補強')
for k, sx_ in enumerate((-60, 60)):
    icyl(f'tray_screw{k}', 3.2, 3.0, 'z', IW_ / 2 + sx_, 14, TZ + 1.5, M['alublack'], 24); icyl(f'tray_screw{k}_hex', 1.6, .3, 'z', IW_ / 2 + sx_, 14, TZ + 3.1, M['rubber'], 6)
hw('固定', 'M3 T10 拘束ネジ(トレイ)', 2, '0.6N·m')
# ---------- トレイハンドル・接地スタッド ----------
for k, sx_ in enumerate((-40, 40)): ibox(f'tray_handle_post{k}', 6, 6, 8, IW_ / 2 + sx_ - 3, IH_ - 18, TZ, M['sus'], .6)
cable('tray_handle_wire', [(IW_ / 2 - 40, IH_ - 15, TZ + 7), (IW_ / 2 - 40, IH_ - 40, TZ + 7), (IW_ / 2 + 40, IH_ - 40, TZ + 7), (IW_ / 2 + 40, IH_ - 15, TZ + 7)], 1.5, M['sus']); hw('取っ手', 'トレイ折りたたみ線材ハンドル(SUS φ3)', 1, '')
icyl('pe_stud_tray', 2.0, 8, 'z', 40, 40, TZ + 4, M['sus'], 12); icyl('pe_nut_tray', 3.5, 2, 'z', 40, 40, TZ + 8, M['sus'], 6)
cable('pe_braid_tray_a', [(40, 40, TZ + 9), (40, 60, TZ + 12), (60, 70, TZ + 9)], 1.6, M['pe_gy']); cable('pe_braid_tray_b', [(40, 40, TZ + 9), (30, 52, TZ + 14), (20, 66, TZ + 9)], 1.6, M['pe_gy'])
hw('接地', 'M4接地スタッド+ナット(トレイ)/ボンディング編組6mm²(トレイ-背板)', 2, 'CP-18 / 導通≤0.1Ω')
# ---------- ドーム固定: 下辺ラッチ6・上辺フック6・磁石12(+SUSディスク)・位置決めピン2 ----------
bot_y = DOME_Y0; top_y = DOME_Y0 + DOME_H
for k, xx in enumerate((-250, -150, -50, 50, 150, 250)):
    cyl(f'latch_cam{k}', 4.0, 7, 'y', xx, bot_y + 5.5, dz(4.5), M['sus'], 20)
    cyl(f'latch_hex{k}', 1.8, .4, 'y', xx, bot_y + 1.7, dz(4.5), M['rubber'], 6)
    box(f'latch_strike{k}', 18, 10, 1.2, xx - 9, bot_y + 8, dz(1.2), M['sus'])
    box(f'hook_tab{k}', 14, 7, 1.5, xx - 7, top_y - 7, dz(5.5), M['alu']); box(f'hook_strike{k}', 16, 8, 1.2, xx - 8, top_y - 9, dz(1.2), M['sus'])
hw('ドーム固定', '1/4回転ラッチ(拘束, T10)', 6, '下辺, 下面の凹みから操作, 品番 U29'); hw('ドーム固定', 'SPCCストライク板 Niめっき t1.2', 12, 'ラッチ6+フック6'); hw('ドーム固定', '掛け爪フック(ドーム一体)', 6, '上辺, 3mmスライドで掛ける')
mag_pos = [(-200, top_y - 10), (0, top_y - 10), (200, top_y - 10), (-200, bot_y + 10), (0, bot_y + 10), (200, bot_y + 10)]
mag_pos += [(DOME_X0 + 10, DOME_Y0 + DOME_H * f) for f in (.25, .5, .75)] + [(DOME_X0 + DOME_W - 10, DOME_Y0 + DOME_H * f) for f in (.25, .5, .75)]
for k, (mx, my) in enumerate(mag_pos):
    cyl(f'magnet{k}', 4.0, 3, 'z', mx, my, dz(4.5), M['magnet'], 20); cyl(f'magnet_disc{k}', 4.5, 1.0, 'z', mx, my, dz(.5), M['sus'], 20)
hw('ドーム固定', 'ネオジム磁石 N52 φ8×3(ドーム側)', 12, '位置決め補助, 吸着力 U29'); hw('ドーム固定', '磁石相手 SUSディスク φ9×1.0(背板側)', 12, '')
for k, (dxp, dyp) in enumerate(((-180, top_y - 20), (140, top_y - 20))): cyl(f'dowel_pin{k}', 2.0, 8, 'z', dxp, dyp, dz(4.0), M['sus'], 16)
hw('ドーム固定', '位置決めピン Ø4 H7×8(非対称)', 2, '')
# ---------- ケーブルクリップ(トレイ上、ケーブル高さz≤30の区間のみ。それ以外は部品へ結束) ----------
nclip = 0
for c_ in CABJ:
    if c_['kind'] != 'cable': continue
    pts = c_['path']; acc = 0.0
    for a_, b_ in zip(pts, pts[1:]):
        acc += math.dist(a_, b_)
        if acc >= 60 and b_[2] <= 30:
            acc = 0.0; nclip += 1
            ibox(f'clip_pad{nclip}', 12, 8, .8, b_[0] - 6, b_[1] - 4, TZ, M['pom'], .2); ibox(f'clip_post{nclip}', 3, 6, max(1, b_[2] - TZ - 1), b_[0] - 1.5, b_[1] - 3, TZ + .8, M['pom'], .3)
hw('配線', 'ケーブルクリップ(POM, 粘着/PEM)', nclip, 'トレイ上 z≤30の区間のみ(他は部品へ結束)')
# ---------- GPUクレードル・電源ボタン・RF窓・AM5バックプレート ----------
ibox('gpu_cradle_base', GW, 10, 3, gx, gy - 14, TZ, M['alublack'], .6); ibox('gpu_cradle_wall_l', 4, 10, 36, gx - 2, gy - 14, TZ, M['alublack'], .6); ibox('gpu_cradle_wall_r', 4, 10, 36, gx + GW - 2, gy - 14, TZ, M['alublack'], .6)
ibox('gpu_cradle_lever', 40, 4, 6, gx + GW / 2 - 20, gy - 12, TZ + 30, M['sus'], .6); hw('支持', 'GPUクレードル(A5052 t2.0+POM当て, 工具なしクランプ)', 1, 'CP-14')
cyl('power_button', 3.0, 4, 'y', X0 + bx + 40 - X0 + 0, DOME_Y0 + 18, dz(12), M['alu'], 20); hw('操作', '電源ボタン(モーメンタリ, 背面左下の凹み内)', 1, '型番未選定')
rf_zl = d_inner(30) - 8          # 平板をドーム内面(上辺から30mmの最も浅い所)より下に置く(傾斜に突き出さない)
ibox('rf_window_plate', 60, 30, 2, IW_ / 2 - 30, IH_ - 60, rf_zl, principled('pc_rf', '#202226', 0, .5)); hw('無線', 'RF窓 PC樹脂t2.0(格子裏, Wi-Fi 7アンテナ×2)', 1, 'CP-12 / U31: 平板をドーム上辺の浅い位置に取付(形状要検討)')
for k, xx in enumerate((IW_ / 2 - 20, IW_ / 2 + 20)): ibox(f'antenna{k}', 30, 1.5, 1.5, xx - 15, IH_ - 45, rf_zl - 2, M['rubber'], .2)
ibox('am5_backplate', 70, 70, 3, bx + sx_ - 35, by + sy_ - 35, bz - 3, M['alublack'], .8); hw('冷却', 'AM5バックプレート+ばね付きM4×4(ポンプ固定)', 1, 'ARCTIC付属')
# ---------- ヒンジ機構(全部品): ヒンジブロック/摩擦ヒンジ/ばね/カム/ストッパ/軸/Eクリップ/貫通ボルト+裏当て ----------
hb = lambda name, w, h, d, x, y, z, mat, body=True, bev=.6: box(name, w, h, d, x, y, z, mat, bevel=bev, body=body)
hb('hinge_block_base', 150, 22, 4, -75, 0, -SLAB - 4, M['stand']); hb('hinge_cheek_l', 6, 22, 32, -75, 0, -SLAB - 32, M['stand']); hb('hinge_cheek_r', 6, 22, 32, 69, 0, -SLAB - 32, M['stand'])
hb('hinge_cover', 138, 22, 2, -69, 0, -SLAB - 34, M['stand'])
hb('hinge_backing_plate', 90, 22, 3, -45, 0, -SLAB + 2, M['sus']); hb('hinge_doubler', 110, 22, 4, -55, 0, -SLAB + 5, M['alu'])
for k, (bxx, byy) in enumerate(((-55, 5), (-55, 17), (55, 5), (55, 17))):
    cyl(f'hinge_bolt{k}', 3.0, 26, 'z', bxx, byy, -SLAB - 9, M['sus'], 16); cyl(f'hinge_bolt_head{k}', 5.2, 3, 'z', bxx, byy, -SLAB - 5.5, M['sus'], 6)
hw('ヒンジ', 'M6貫通ボルト(ヒンジブロック→背板, 裏当て鋼板)', 4, '6N·m+ネジロック'); hw('ヒンジ', 'SPCC裏当て板 t3 90×22 / A5052補強板 t4', 2, 'U29')
cyl('hinge_axle', 5.0, 150, 'x', 0, HY, ZC, M['steel'], 24, body=False)
for k, xx in enumerate((-45, 45)): cyl(f'hinge_friction{k}', 11, 22, 'x', xx, HY, ZC, M['alublack'], 32); cyl(f'hinge_friction{k}_cap', 8, 3, 'x', xx + (12 if xx > 0 else -12), HY, ZC, M['steel'], 24)
hw('ヒンジ', '摩擦ヒンジ(Reell PHL/PHC級, 対称トルク)', 2, '寿命50,000回 / U27')
cyl('spring_spool', 9, 40, 'x', 0, HY + 1, ZC - 8, M['spring'], 32); cyl('spring_spool_flange_l', 11, 2, 'x', -21, HY + 1, ZC - 8, M['sus'], 32); cyl('spring_spool_flange_r', 11, 2, 'x', 21, HY + 1, ZC - 8, M['sus'], 32)
_bm = bmesh.new()      # 定荷重ばねの帯(幅40, 厚0.3): スプールに巻き付く
_pts = [V(0, HY + 1 + 9.15 * math.sin(a_), ZC - 8 + 9.15 * math.cos(a_)) for a_ in [i * math.pi / 12 for i in range(0, 13)]]
for i in range(len(_pts) - 1):
    v0, v1 = _pts[i], _pts[i + 1]; _bm.faces.new([_bm.verts.new((v0.x - 20, v0.y, v0.z)), _bm.verts.new((v0.x + 20, v0.y, v0.z)), _bm.verts.new((v1.x + 20, v1.y, v1.z)), _bm.verts.new((v1.x - 20, v1.y, v1.z))])
_me = bpy.data.meshes.new('spring_strip'); _bm.to_mesh(_me); _bm.free(); _me.materials.append(M['spring']); _so = bpy.data.objects.new('spring_strip', _me); _so.modifiers.new('s', 'SOLIDIFY').thickness = 0.3; link(_so)
cyl('hinge_cam', 12, 4, 'x', 0, HY, ZC, M['sus'], 40); hb('hinge_cam_hook', 6, 8, 4, -3, HY + 18, ZC - 2, M['sus'])
hw('ヒンジ', '定荷重ばね/カム式バランサ(ばね帯 幅40×t0.3+スプール+カム, 金属製保持)', 1, '型番 U26')
hb('hinge_stopper_up', 12, 8, 10, -6, HY + 12, ZC - 14, M['steel']); hb('hinge_stopper_dn', 12, 8, 10, -6, HY - 20, ZC - 14, M['steel']); hw('ヒンジ', '機械ストッパ(-5°/+25°)', 2, '')
for k, xx in enumerate((-70, -22, 22, 70)): cyl(f'hinge_eclip{k}', 7.2, 1.2, 'x', xx, HY, ZC, M['sus'], 24, body=False)
hw('ヒンジ', 'Eクリップ(軸Ø10用)', 4, ''); hw('ヒンジ', 'ヒンジ軸 Ø10 SUS×150', 1, '')
din = lambda x, y, z: (x - X0, y - Y0, Z0 - z)      # 設計座標→内部座標
cable('pe_braid_hinge', [din(-30, 6, -SLAB - 6), din(-30, -10, -SLAB - 20), din(-30, -40, ZC - 6)], 1.8, M['pe_gy']); hw('接地', 'ヒンジ跨ぎ可とう編組(背板→スタンド)', 1, 'CP-18')
json.dump(HW, open(os.path.join(ROOT, 'model', 'hardware_list.json'), 'w'), ensure_ascii=False, indent=1)
