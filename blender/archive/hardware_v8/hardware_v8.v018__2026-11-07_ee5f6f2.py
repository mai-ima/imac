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
# ---------- 吊りピン(肩ねじ Ø6 + 頭Ø10×3) + SUSブッシュ(Ø16×1.0, キーホール孔付き) + トレイ拘束ネジ ----------
for k, (kx, ky) in enumerate(KH):
    pyk = ky + 12             # 掛けた状態: ピンは細溝の上端
    icyl(f'hang_pin{k}_shoulder', 3.0, 6, 'z', kx, pyk, 3.0, M['sus'], 24)
    icyl(f'hang_pin{k}_head', 5.0, 3, 'z', kx, pyk, TZ + 1.0 + 1.5, M['sus'], 24)
    icyl(f'hang_pin{k}_hexsocket', 1.6, .4, 'z', kx, pyk, TZ + 1.0 + 3.1, M['rubber'], 6)
    # ブッシュは長丸(16×28): ピンが掛かる溝の上端(ky+12)までを支圧補強する(K-bush: 従来のØ16円板はピン位置に届かなかった)
    for nm_, b_ in (('a', icyl(f'hang_bushing{k}a', 8, 1.0, 'z', kx, ky, TZ + .5, M['sus'], 48)), ('b', icyl(f'hang_bushing{k}b', 8, 1.0, 'z', kx, ky + 12, TZ + .5, M['sus'], 48)), ('c', ibox(f'hang_bushing{k}c', 16, 12, 1.0, kx - 8, ky, TZ, M['sus']))):
        mb = b_.modifiers.new('hole', 'BOOLEAN'); mb.object = kh_cut; mb.operation = 'DIFFERENCE'; mb.solver = 'EXACT'
hw('吊り機構', 'SUS肩ねじ M4・肩径Ø6×6・頭Ø10×3(CP-04)', 4, '品番 U29'); hw('吊り機構', 'SUSブッシュ t1.0 16×28長丸(CP-05)', 4, '支圧補強')
for k, sx_ in enumerate((-60, 60)):
    icyl(f'tray_screw{k}', 3.2, 3.0, 'z', IW_ / 2 + sx_, 14, TZ + 1.5, M['alublack'], 24); icyl(f'tray_screw{k}_hex', 1.6, .3, 'z', IW_ / 2 + sx_, 14, TZ + 3.1, M['rubber'], 6)
hw('固定', 'M3 T10 拘束ネジ(トレイ)', 2, '0.6N·m')
# ---------- トレイハンドル・接地スタッド ----------
for k, sx_ in enumerate((-40, 40)): ibox(f'tray_handle_post{k}', 6, 6, 8, IW_ / 2 + sx_ - 3, IH_ - 18, TZ, M['sus'], .6)
cable('tray_handle_wire', [(IW_ / 2 - 40, IH_ - 15, TZ + 7), (IW_ / 2 - 40, IH_ - 40, TZ + 7), (IW_ / 2 + 40, IH_ - 40, TZ + 7), (IW_ / 2 + 40, IH_ - 15, TZ + 7)], 1.5, M['sus']); hw('取っ手', 'トレイ折りたたみ線材ハンドル(SUS φ3)', 1, '')
icyl('pe_stud_tray', 2.0, 8, 'z', 26, 120, TZ + 4, M['sus'], 12); icyl('pe_nut_tray', 3.5, 2, 'z', 26, 120, TZ + 8, M['sus'], 6)
cable('pe_braid_tray_a', [(26, 120, TZ + 9), (22, 135, TZ + 12), (14, 150, TZ + 3)], 1.6, M['pe_gy']); cable('pe_braid_tray_b', [(26, 120, TZ + 9), (22, 105, TZ + 12), (14, 90, TZ + 3)], 1.6, M['pe_gy'])
hw('接地', 'M4接地スタッド+ナット(トレイ)/ボンディング編組6mm²(トレイ-背板)', 2, 'CP-18 / 導通≤0.1Ω')
# ---------- ドーム固定: 下辺ラッチ6・上辺フック6・磁石12(+SUSディスク)・位置決めピン2 ----------
bot_y = DOME_Y0; top_y = DOME_Y0 + DOME_H
for k, xx in enumerate((-250, -150, -50, 50, 150, 250)):
    cyl(f'latch_cam{k}', 4.0, 7, 'y', xx, bot_y + 5.5, dz(4.5), M['sus'], 20)
    cyl(f'latch_hex{k}', 1.8, .4, 'y', xx, bot_y + 1.7, dz(4.5), M['rubber'], 6)
    box(f'latch_strike{k}', 18, 6, 1.2, xx - 9, bot_y + 4, dz(1.2), M['sus'])
    box(f'hook_tab{k}', 14, 7, 1.5, xx - 7, top_y - 7, dz(5.5), M['alu']); box(f'hook_strike{k}', 16, 8, 1.2, xx - 8, top_y - 9, dz(1.2), M['sus'])
hw('ドーム固定', '1/4回転ラッチ(拘束, T10)', 6, '下辺, 下面の凹みから操作, 品番 U29'); hw('ドーム固定', 'SPCCストライク板 Niめっき t1.2', 12, 'ラッチ6+フック6'); hw('ドーム固定', '掛け爪フック(ドーム一体)', 6, '上辺, 3mmスライドで掛ける')
mag_pos = [(-200, top_y - 6), (0, top_y - 6), (200, top_y - 6), (-200, bot_y + 6), (0, bot_y + 6), (200, bot_y + 6)]
mag_pos += [(DOME_X0 + 6, DOME_Y0 + DOME_H * f) for f in (.25, .5, .75)] + [(DOME_X0 + DOME_W - 6, DOME_Y0 + DOME_H * f) for f in (.25, .5, .75)]
for k, (mx, my) in enumerate(mag_pos):
    cyl(f'magnet{k}', 4.0, 3, 'z', mx, my, dz(4.5), M['magnet'], 20); cyl(f'magnet_disc{k}', 4.5, 1.0, 'z', mx, my, dz(.5), M['sus'], 20)
hw('ドーム固定', 'ネオジム磁石 N52 φ8×3(ドーム側)', 12, '位置決め補助, 吸着力 U29'); hw('ドーム固定', '磁石相手 SUSディスク φ9×1.0(背板側)', 12, '')
# --- ガスケット/メッシュフィルタの切欠き(INTF-04): ラッチ・フック・磁石が通る位置に外形+1mmのポケットを開ける(実物のガスケットは連続した帯でなく部品位置で切り欠く) ---
def _pocket(nm, x0, y0, z0, w, h, d):
    c_ = box(nm, w, h, d, x0, y0, z0, None, body=False); c_.hide_render = True; BODY_OBJS.append(c_); return c_
_pk = []
for k_, xx_ in enumerate((-250, -150, -50, 50, 150, 250)):
    _pk.append(_pocket(f'pocket_latch{k_}', xx_ - 10.0, bot_y + 2.0, dz(8.0), 20, 11, 9.0))      # ラッチ(Ø8×7)+ストライク(18×6)
    _pk.append(_pocket(f'pocket_hook{k_}', xx_ - 9.0, top_y - 11.0, dz(8.0), 18, 11, 9.0))      # フック(14×7)+ストライク(16×8)
for k_, (mx_, my_) in enumerate(mag_pos): _pk.append(_pocket(f'pocket_mag{k_}', mx_ - 5.5, my_ - 5.5, dz(6.0), 11, 11, 7.0))      # 磁石Ø8+ディスクØ9
for _tn in ('gasket', 'cover_filter'):
    _to = bpy.data.objects.get(_tn)
    if _to is None: continue
    for _p in _pk:
        _m = _to.modifiers.new(_p.name, 'BOOLEAN'); _m.object = _p; _m.operation = 'DIFFERENCE'; _m.solver = 'EXACT'
for k, (dxp, dyp) in enumerate(((-180, top_y - 6), (140, top_y - 6))): cyl(f'dowel_pin{k}', 2.0, 8, 'z', dxp, dyp, dz(4.0), M['sus'], 16)
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
ibox('gpu_cradle_base', GW, 10, 3, gx, gy - 14, TZ, M['alublack'], .6); ibox('gpu_cradle_wall_l', 4, 10, 9, gx - 2, gy - 14, TZ, M['alublack'], .6); ibox('gpu_cradle_wall_r', 4, 10, 9, gx + GW - 2, gy - 14, TZ, M['alublack'], .6)
for k_, xx_ in enumerate((gx + 18, gx + GW - 18)): icyl(f'gpu_bracket_screw{k_}', 2.6, 5, 'y', xx_, gy - 3, gz + 38, M['steel'], 12) if False else None
hw('支持', 'GPU低背ステー(A5052 t2.0, z5〜14: ホース/ポート挿抜空間を避ける)+ブラケットねじ', 1, 'CP-14 / ホース(z16〜)との干渉無し')
cyl('power_button', 3.0, 4, 'y', X0 + bx + 40, DOME_Y0 + 18, dz(12), M['alu'], 20); hw('操作', '電源ボタン(モーメンタリ, 背面左下の凹み内)', 1, '型番未選定')
rf_zl = d_inner(30) - 8          # 平板をドーム内面(上辺から30mmの最も浅い所)より下に置く(傾斜に突き出さない)
ibox('rf_window_plate', 60, 30, 2, IW_ / 2 - 30, IH_ - 60, rf_zl, principled('pc_rf', '#202226', 0, .5)); hw('無線', 'RF窓 PC樹脂t2.0(格子裏, Wi-Fi 7アンテナ×2)', 1, 'CP-12 / U31: 平板をドーム上辺の浅い位置に取付(形状要検討)')
for k, xx in enumerate((IW_ / 2 - 20, IW_ / 2 + 20)): ibox(f'antenna{k}', 30, 1.5, 1.5, xx - 15, IH_ - 45, rf_zl - 2, M['rubber'], .2)
ibox('am5_backplate', 70, 70, 3, bx + sx_ - 35, by + sy_ - 35, bz - 3, M['alublack'], .8); hw('冷却', 'AM5バックプレート+ばね付きM4×4(ポンプ固定)', 1, 'ARCTIC付属')
# ---------- ヒンジ機構(全部品): ヒンジブロック/摩擦ヒンジ/ばね/カム/ストッパ/軸/Eクリップ/貫通ボルト+裏当て ----------
hb = lambda name, w, h, d, x, y, z, mat, body=True, bev=.6: box(name, w, h, d, x, y, z, mat, bevel=bev, body=body)
hb('hinge_block_base', 150, 22, 2, -75, 0, -SLAB - 2, M['stand']); hb('hinge_cheek_l', 6, 22, 34, -75, 0, -SLAB - 34, M['stand']); hb('hinge_cheek_r', 6, 22, 34, 69, 0, -SLAB - 34, M['stand'])
hb('hinge_cover', 138, 22, 2, -69, 0, -SLAB - 36, M['stand'])
hb('hinge_backing_plate', 140, 22, 3, -70, 0, -SLAB + 2, M['sus']); hb('hinge_doubler', 144, 22, 4, -72, 0, -SLAB + 5, M['alu'])     # 背板の前(チン空洞側): 裏当て鋼板140幅+補強板144幅(ボルト±62を覆う)
for k, (bxx, byy) in enumerate(((-62, 5), (-62, 17), (62, 5), (62, 17))):
    cyl(f'hinge_bolt{k}', 3.0, 14, 'z', bxx, byy, -SLAB - 2, M['sus'], 16); cyl(f'hinge_bolt_head{k}', 5.2, 3, 'z', bxx, byy, -SLAB - 3.5, M['sus'], 6)     # 底板(z-27〜-25)から背板・裏当て・補強板を貫通
hw('ヒンジ', 'M6貫通ボルト(ヒンジブロック→背板, 裏当て鋼板)', 4, '6N·m+ネジロック'); hw('ヒンジ', 'SPCC裏当て板 t3 140×22 / A5052補強板 t4 144×22', 2, 'U29')
cyl('hinge_axle', 6.0, 132, 'x', 0, HY, ZC, M['steel'], 48, body=False)
for k, xx in enumerate((-45, 45)): cyl(f'hinge_friction{k}', 11, 22, 'x', xx, HY, ZC, M['alublack'], 32); cyl(f'hinge_friction{k}_cap', 8, 3, 'x', xx + (12 if xx > 0 else -12), HY, ZC, M['steel'], 24)
hw('ヒンジ', '摩擦ヒンジ(Reell PHL/PHC級, 対称トルク)', 2, '寿命50,000回 / U27')
# ---- チルト・バランサ(R9T-001で再設計): ヒンジブロック底面のカム板(x=±14) + ローラ従動子 + 案内ロッド付き圧縮ダイスプリング2本。tools/balance_calc.py / model/balance.json ----
BAL = json.load(open(os.path.join(ROOT, 'model', 'balance.json'))); BCm = S['hinge']['balance_cam']
RHO0, RR, XS_ = BCm['rho0_mm'], BCm['roller_r_mm'], BCm['spring_x_mm']; BS = BAL['s']; CT_ = BCm['cam_t_mm']
def prism_x(name, pts_zy, x0, x1, mat, body=True):
    """(z,y)多角形(設計座標)を x0〜x1 へ押し出したメッシュ。"""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    lo = [bm.verts.new(V(x0, y, z)) for z, y in pts_zy]; hi = [bm.verts.new(V(x1, y, z)) for z, y in pts_zy]
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    for i in range(len(pts_zy)): j = (i + 1) % len(pts_zy); bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); me.materials.append(mat); return link(ob, body)
cs_ = BAL['cam_surface_head_frame']                                                                        # 実カム面(頭部座標。ストッパ余長込み)
cam_pts = [(ZC + cs_[0][1], HY - 10)] + [(ZC + zl_, HY + yl_) for _, zl_, yl_ in cs_] + [(ZC + cs_[-1][1], HY - 10)]
for k, sx_ in enumerate((-1, 1)):
    xc_ = sx_ * XS_
    hb(f'hinge_tail_lever{k}', S['neck']['lever_t'], S['neck']['lever_len'], S['neck']['lever_w'], sx_ * 26.5 - S['neck']['lever_t'] / 2, HY - S['neck']['lever_len'], ZC - S['neck']['lever_w'] / 2, M['sus'])        # ストッパ用の尾部レバー(耳板一体)
    prism_x(f'hinge_cam_plate{k}', cam_pts, xc_ - CT_ / 2, xc_ + CT_ / 2, M['sus'])                              # カム板(頭部側, SUS440C焼入れ)
    cyl(f'cam_roller{k}', RR, BCm['roller_w_mm'], 'x', xc_, HY - RHO0, ZC, M['steel'], 48, body=False)         # ローラ(0°位置)
    cyl(f'cam_roller_pin{k}', 3.0, BCm['roller_w_mm'] + 6, 'x', xc_, HY - RHO0, ZC, M['steel'], 24, body=False)
    yct = HY - RHO0 - RR - BCm['carrier_h_mm']
    hb(f'cam_carrier{k}', 2 * (BCm['spring_od_mm'] / 2 + 1), BCm['carrier_h_mm'], 2 * (BCm['guide_rod_z_mm'] + BCm['guide_rod_d_mm'] / 2), xc_ - (BCm['spring_od_mm'] / 2 + 1), yct, ZC - (BCm['guide_rod_z_mm'] + BCm['guide_rod_d_mm'] / 2), M['sus'], body=False)   # キャリア(ばね上座+ブッシュ)
    LS = BAL['lmax']; ysb = HY - BS + BCm['seat_t_mm']
    _n = 79000.0 * BCm['spring_wire_mm'] ** 4 / (8 * (BCm['spring_od_mm'] - BCm['spring_wire_mm']) ** 3 * BAL['k_spring'])      # 有効巻数 n = G d^4/(8 D^3 k)
    coil(f'spring_die{k}', (BCm['spring_od_mm'] - BCm['spring_wire_mm']) / 2, BCm['spring_wire_mm'], LS, _n, (xc_, ZC), ysb, M['spring'], axis='y', ends=1.0, per_turn=28, seg=10, body=False)       # ダイスプリング実形状(0°の取付長)。座巻き各1巻
    cyl(f'spring_spigot_bot{k}', 5.7, 3.0, 'y', xc_, ysb + 1.5, ZC, M['sus'], 32, body=False)      # 座側スピゴットØ11.4(ばね内径Ø12へ嵌まる=位置決め, MDD-002)
    cyl(f'spring_spigot_top{k}', 5.7, 3.0, 'y', xc_, ysb + LS - 1.5, ZC, M['sus'], 32, body=False)      # キャリア側スピゴット
    hb(f'spring_seat_bot{k}', 2 * (BCm['spring_od_mm'] / 2 + 1), BCm['seat_t_mm'], 2 * (BCm['guide_rod_z_mm'] + BCm['guide_rod_d_mm'] / 2), xc_ - (BCm['spring_od_mm'] / 2 + 1), HY - BS, ZC - (BCm['guide_rod_z_mm'] + BCm['guide_rod_d_mm'] / 2), M['sus'], body=False)
    for zz_ in (-1, 1): cyl(f'cam_guide_rod{k}_{zz_}', BCm['guide_rod_d_mm'] / 2, yct + BCm['carrier_h_mm'] - (HY - BS), 'y', xc_, (yct + BCm['carrier_h_mm'] + HY - BS) / 2, ZC + zz_ * BCm['guide_rod_z_mm'], M['steel'], 24, body=False)   # 案内ロッド(基台に固定, キャリアが摺動)
hw('ヒンジ', f"コイルばね OD{BCm['spring_od_mm']:g}×線径{BCm['spring_wire_mm']:g}(SWOSC-V想定, 1本 {BAL['F0_total']/2:.0f}N(0°)〜{BAL['F_spring_max']:.0f}N, k={BAL['k_spring']:g}N/mm, 自由長≧{BAL['free_length_min']:.0f}mm)+案内ロッドØ{BCm['guide_rod_d_mm']:g}×2+ローラ従動子", 2, 'U26/U51: 型番未確定 / D04')
hw('ヒンジ', f"カム板(SUS440C HRC58 t{CT_:g}, 軸半径約{BAL['rho0']-BAL['roller_r']:.0f}〜{BAL['e']:.0f}mm)", 2, 'balance_calc.py / D04')
hw('ヒンジ', f"尾部レバー(ストッパ用, 耳板一体) SUS304 t5×幅14×長{S['neck']['lever_len']:g}", 2, 'D03')
NKh = S['neck']; LL = NKh['lever_len']
for k, sx_ in enumerate((-1, 1)):    # チルト端ストッパ: 尾部レバー(長さ34, spec.neck.lever_len)の側縁が、-15°側は側板間タイプレート(t6)のゴムパッド、+40°側は前カバー(t6)内面のゴムパッドに当たる
    px0, px1 = NKh['pad_x']; xc = sx_ * (px0 + px1) / 2
    hb(f'hinge_stopper_dn{k}', px1 - px0, 6, NKh['pad_dn_z'][1] - NKh['pad_dn_z'][0], xc - (px1 - px0) / 2, HY - LL * math.cos(math.radians(-15)) - 3, ZC + NKh['pad_dn_z'][0], M['rubber'])
    hb(f'hinge_stopper_up{k}', px1 - px0, 6, NKh['pad_up_z'][1] - NKh['pad_up_z'][0], xc - (px1 - px0) / 2, NKh['tab_y_top'] - 6, ZC + NKh['pad_up_z'][0], M['rubber'])
BTc = S['neck']['boot']; SYS_ = -DROP + S['swivel']['stack_h'] + S['neck']['base_t']
for k_ in range(BTc['convolutions']):      # ゴム蛇腹ブーツ(簡略表示: 角形の山谷リング。実機は伸縮10〜48mm+せん断±10mm)
    yb = S['neck']['cover_top'] + k_ * (0 - S['neck']['cover_top']) / BTc['convolutions']; grow = 3.0 if k_ % 2 else 0.0
    for nm_, (bx_, bz0_, bw_, bd_) in (('f', (-67 - grow, ZC + S['neck']['front_cover_z'][1] + 0.5 + grow, 134 + 2 * grow, 2.0)), ('b', (-67 - grow, ZC + S['neck']['side_z'][0] - 3.0 - grow, 134 + 2 * grow, 2.0))):      # 側板(外側x=62)の外へ(外皮の余白を9mmに拡大して収める)
        hb(f'hinge_boot{k_}{nm_}', bw_, (0 - S['neck']['cover_top']) / BTc['convolutions'] * 0.9, bd_, bx_, yb, bz0_, M['rubber'], bev=.3)
hw('ヒンジ', f"ゴム蛇腹ブーツ(シリコーン UL94 V-0, 山{S['neck']['boot']['convolutions']}, 伸縮{S['neck']['boot']['length_range_mm'][0]}〜{S['neck']['boot']['length_range_mm'][1]}mm)", 1, '指挟み防護(U53)。3Dは簡略表示')
hb('stand_neck_tab', S['neck']['tab_x'][1] - S['neck']['tab_x'][0], S['neck']['tab_y_top'] - S['neck']['cover_top'], S['neck']['front_cover_z'][1] - S['neck']['front_cover_z'][0], S['neck']['tab_x'][0], S['neck']['cover_top'], ZC + S['neck']['front_cover_z'][0], M['stand'], bev=.5)      # 前カバーの立ち上がり(全幅, 側板間で両端支持: +40°ストッパ受け)
hw('ヒンジ', 'ばね座シム(ばね下端の荷重調整 ±0.25mm刻み)', 2, '調整後公差 荷重±3%(spec.hinge) / D04')
hw('ヒンジ', 'ネック基台 t8 + M5×4(ロータ板固定)/タイプレート t6(-15°ストッパ受け)/前カバー t6(+40°ストッパ受け)', 3, 'spec.neck')
for k_, (bx_, bz_) in enumerate(((-40, -12), (40, -12), (-40, 12), (40, 12))):
    cyl(f'stand_neck_bolt{k_}', 2.5, 8.5, 'y', bx_, -DROP + S['swivel']['stack_h'] + 4.25 + 0.0, ZC + bz_, M['sus'], 12) if False else None
hw('ヒンジ', '機械ストッパ ゴムパッド(チルト -15°/+40°。レバー側縁が当たる)', 4, 'strength_check.py')
for k, xx in enumerate((-63.6, 63.6)): cyl(f'hinge_eclip{k}', 7.6, 1.0, 'x', xx, HY, ZC, M['sus'], 24, body=False)
hw('ヒンジ', 'E止め輪(軸Ø12用, 外側)', 2, 'D03'); hw('ヒンジ', 'ヒンジ軸 Ø12 SUS303×132', 1, 'D03')

# ---- 首振りユニット(v9): 足上面(y=-DROP)に固定のステータ板 → クロスローラ軸受 → ロータ板 → ネック。左右±60°。tools/stability.py / motion_check.py ----
SWV = S['swivel']; SY0 = -DROP; SX, SZ = 0.0, ZC           # 垂直首振り軸(スタンド中心線, ヒンジ軸と同じz)
cyl('stand_swivel_stator', SWV['stator_r'], 6, 'y', SX, SY0 + 3, SZ, M['alublack'], 64)                                          # 足に固定: Ø190×6
cyl('stand_swivel_bearing', SWV['bearing_od'] / 2, 12, 'y', SX, SY0 + 12, SZ, M['sus'], 64)                          # クロスローラ(スリューリング)軸受 OD100/ID60×12 (外輪=静止側)
cyl('stand_swivel_bearing_inner', 40, 1.0, 'y', SX, SY0 + 18.5, SZ, M['steel'], 64)                                  # 内輪(回転側)の上面ボス: ロータ板は内輪にだけ接し、外輪とは1mm離れる
cyl('stand_swivel_rotor', SWV['rotor_r'], 6, 'y', SX, SY0 + 22, SZ, M['alublack'], 64)                                          # 回転側: Ø152×6 (y19〜25)
cyl('stand_swivel_friction_ring', 35, 1.5, 'y', SX, SY0 + 6.75, SZ, M['rubber'], 48)                                 # 摩擦リング(内輪下面とステータ上面の間, 波ばね予圧, 保持1.6N·m)
for k in range(6):
    ang = math.radians(k * 60 + 30); bx_, bz_ = SX + SWV['pcd_inner'] / 2 * math.cos(ang), SZ + SWV['pcd_inner'] / 2 * math.sin(ang)
    cyl(f'stand_swivel_bolt{k}', 2.5, 0.6, 'y', bx_, SY0 + 25.3, bz_, M['sus'], 12)                                    # 内輪側 M5×6本(PCD70)の頭
for k in range(6):
    ang = math.radians(k * 60); bx_, bz_ = SX + SWV['pcd_outer'] / 2 * math.cos(ang), SZ + SWV['pcd_outer'] / 2 * math.sin(ang)
    cyl(f'stand_swivel_bolt_o{k}', 2.5, 2, 'y', bx_, SY0 - 0.2, bz_, M['sus'], 12)                                   # 外輪側 M5×6本(PCD90)はステータ下面から(頭は足内)
_SA = math.degrees(math.asin((5.0 + 5.0) / SWV['stop_r']))       # 接触角の補正: ポスト半径4+タブ半幅5 を半径60で見た角度
for sgn, nm in ((-1, 'l'), (1, 'r')):    # 角度ストッパ: ステータ上のゴムポスト(r=60, ±(60+補正)°)と、ロータ側タブ(同じ高さ y19〜25)
    ang = math.radians(90 + sgn * (SWV['range_deg'] + _SA)); cyl(f'stand_swivel_stop_{nm}', 5.0, 25, 'y', SX + SWV['stop_r'] * math.cos(ang), SY0 + 12.5, SZ + SWV['stop_r'] * math.sin(ang), M['rubber'], 16)
box('stand_swivel_stop_tab', 10, 6, SWV['stop_r'] + 4 - (SWV['rotor_r'] - 8), SX - 5, SY0 + 19, SZ + SWV['rotor_r'] - 8, M['sus'], bevel=.5, body=False)
hw('首振り', 'クロスローラ軸受(スリューリング) OD100/ID60×12', 1, 'U50: 型番未選定(IKO/THK/NSKの小径品を想定)')
hw('首振り', f"ステータ板Ø{2*SWV['stator_r']:g}・ロータ板Ø{2*SWV['rotor_r']:g} A5052 t6 / 摩擦リング+波ばね", 2, f"保持トルク{SWV['holding_torque_Nm']:g}N·m(D05)")
hw('首振り', 'M5ボルト 内輪PCD70×6 / 外輪PCD90×6(型番カタログ値は U50 で確認)', 12, ''); hw('首振り', 'ゴムストッパ(±60°)+ロータタブ', 3, '')
hw('接地', 'スイベル跨ぎ編組(ネック→足, 余長でねじれ±60°を許容)', 1, 'CP-18')
din = lambda x, y, z: (x - X0, y - Y0, Z0 - z)      # 設計座標→内部座標
PEJ = json.load(open(os.path.join(ROOT, 'model', 'pe_braids.json')))
cable('pe_braid_swivel', [din(58, SY0 + 27, SZ - 8), din(75, SY0 + 34, SZ - 30), din(95, SY0 + 22, SZ - 70), din(85, SY0 + 14, SZ - 105), din(60, SY0 + 10, SZ - 100), din(60, SY0 + 5, SZ - 75), din(70, SY0 - 1, SZ - 55)], 1.8, M['pe_gy'])      # ネック(回転側)→足(固定側): ループで ±60° に追従(長さ model/pe_braids.json)
cable('pe_braid_hinge', [din(-45, 12, -27 - 12), din(-48, 4, -27 - 8), din(-52, -6, -27 - 14), din(-50, -8, -27 - 26), din(-47, 0, -27 - 34), din(-45, 8, -27 - 40)], 1.8, M['pe_gy'])      # 頭部ヒンジブロック→ネック側: ストッパ(x±20〜32)の掃引域を避けx=-45〜-52のループ
json.dump(HW, open(os.path.join(ROOT, 'model', 'hardware_list.json'), 'w'), ensure_ascii=False, indent=1)
