#!/usr/bin/env python3
"""iMac風 一体型ゲーミングPC の Blender(Cycles) モデル + レンダリング。
実行: python build_imac_pc.py --view front --color silver --out render/x.png   (bpy モジュール版 / Blender 5.0)
      blender -b -P build_imac_pc.py -- --view front ...                     (Blender本体)
寸法は model/spec.json から読み込む(単位 mm, 1 Blender単位 = 1 mm)。
座標系: 設計図(Three.js版/OpenSCAD版)の (x右, y上, z手前) を Blender の (x, -z, y) に変換して使用。
"""
import bpy, bmesh, math, json, os, sys, random, argparse
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
S = json.load(open(os.path.join(ROOT, 'model', 'spec.json')))

ap = argparse.ArgumentParser()
ap.add_argument('--color', default='silver'); ap.add_argument('--view', default='front')
ap.add_argument('--out', default=os.path.join(ROOT, 'render', 'blender_test.png'))
ap.add_argument('--res', default='1600x900'); ap.add_argument('--samples', type=int, default=64)
ap.add_argument('--cut', action='store_true'); ap.add_argument('--tilt', type=float, default=0); ap.add_argument('--swivel', type=float, default=0)
ap.add_argument('--flat', action='store_true', help='写実化パス(ベベル/粗さのムラ/ソフトボックス/床反射/被写界深度/AgX)を無効にする'); ap.add_argument('--explode', type=float, default=0); ap.add_argument('--phase', type=float, default=0.3)
ap.add_argument('--open-stand', action='store_true', help='スタンド外皮(スカート/カラー/ネック外皮/カバー)を外して内部機構(ばね・カム等)を見せる'); ap.add_argument('--only', default='', help='カンマ区切りの名前接頭辞に一致するオブジェクトだけを描画(部分確認用)'); ap.add_argument('--check-interference', default='', help='実メッシュ同士の交差(BVH)を検査しJSONへ書き出して終了(INTF-01)'); ap.add_argument('--debug-keyhole', action='store_true', help='キーホール位置でトレイ板に穴が開いているかを数値で確認して終了'); ap.add_argument('--with-duct', action='store_true', help='未採用候補: 吸気分離ダクトを描画'); ap.add_argument('--poly', type=float, default=1.0, help='ポリゴン密度係数(円筒分割数・面取り分割を倍率で増やす。GLB容量に注意)'); ap.add_argument('--panel', type=int, default=S['panel_size']); ap.add_argument('--save-blend', default='')
ap.add_argument('--vent-mode', default='boolean'); ap.add_argument('--vent-step', type=float, default=4.0); ap.add_argument('--vent-r', type=float, default=1.2); ap.add_argument('--export', default=''); ap.add_argument('--focus', default=''); ap.add_argument('--dist', type=float, default=500); ap.add_argument('--az', type=float, default=0); ap.add_argument('--el', type=float, default=20); ap.add_argument('--lens', type=float, default=70); ap.add_argument('--frames', type=int, default=0)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
A = ap.parse_args(argv)
POLY_INIT = A.poly

# ---------------- 寸法 ----------------
PW, PH = S['panels'][str(A.panel)]['w'], S['panels'][str(A.panel)]['h']
BEZ, CHIN, SLAB = (S['bezel'] if A.panel == 27 else 10), S['chin'], S['slab_t']
W = S['body_w'] if A.panel == 27 else 547.0
H = PH + BEZ + CHIN
POD_T, POD_H, WALL = S['dome']['total_t'], S['pod']['h'], S['dome']['inner_wall_offset_mm']      # 総厚はdome.total_tに一本化
POD_W = W - S['pod']['side_margin']
IN_W, IN_D = POD_W - 2 * WALL, POD_T - SLAB - WALL
ST_W, DROP, FOOT = S['stand']['w'], S['stand']['drop'], S['stand']['foot_depth']
ZC = -S['hinge']['axis_z_from_glass']      # ヒンジ軸のz(前面ガラスから)。docs/tilt-swivel-design.md
X0, Y0, Z0 = -W / 2 + S['dome']['inset_left_right'] + WALL, S['dome']['inset_bottom'] + WALL, -SLAB      # 内部座標の原点(ドーム内側の左下)

# ---------------- ユーティリティ ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 0.001; scene.unit_settings.length_unit = 'MILLIMETERS'
COLL = bpy.data.collections.new('imac_pc'); scene.collection.children.link(COLL)
BODY_OBJS = []      # チルト対象(本体+ポッド+内部)

def V(x, y, z): return Vector((x, -z, y))
def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexc(h, a=1.0):
    h = h.lstrip('#'); r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return (lin(r), lin(g), lin(b), a)

def link(ob, body=True):
    COLL.objects.link(ob)
    if body: BODY_OBJS.append(ob)
    return ob

POLY = POLY_INIT
def smooth(ob, bevel=0.0, seg=2, curved=False):
    seg = max(seg, int(round(seg * POLY)))
    """面取りは小さな平面ファセット(切削アルミ風)。曲面(円筒の側面)のみスムースシェーディング。"""
    if bevel > 0:
        m = ob.modifiers.new('bevel', 'BEVEL'); m.width = bevel; m.segments = seg; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(40)
    if curved:
        for p in ob.data.polygons: p.use_smooth = abs(p.normal.z) < 0.9   # 円筒の側面だけ滑らか、キャップは平面

def box(name, w, h, d, x, y, z, mat, bevel=0.0, body=True, uv=False):
    """設計図座標: 最小コーナー(x,y,z)から (幅w, 高h, 奥行d)。uv=True で X-Z 平面の平面投影UVを付与(GLBにもテクスチャが載る)。"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    if uv:
        lay = bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            for l in f.loops: l[lay].uv = (l.vert.co.x + .5, l.vert.co.z + .5)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); ob.location = V(x + w / 2, y + h / 2, z + d / 2)
    if mat: me.materials.append(mat)
    smooth(ob, bevel); return link(ob, body)

def cyl(name, r, length, axis, cx, cy, cz, mat, seg=48, bevel=0.0, body=True):
    """設計図座標の中心(cx,cy,cz)・軸 'x'|'y'|'z'(y=上, z=奥行)。"""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    seg = min(192, max(seg, int(round(seg * POLY))))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=length)   # 軸=Blender Z
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    # Blender Z軸 = 設計図 y。z軸(設計図) = Blender Y -> X軸回転90°、x軸 -> Y軸回転90°
    if axis == 'z': ob.rotation_euler = (math.pi / 2, 0, 0)
    elif axis == 'x': ob.rotation_euler = (0, math.pi / 2, 0)
    ob.location = V(cx, cy, cz)
    if mat: me.materials.append(mat)
    smooth(ob, bevel, curved=True); return link(ob, body)

# 内部座標(Three.js版と同じ: z は背面方向が正)
def ibox(name, w, h, d, x, y, zl, mat, bevel=0.0, uv=False): return box(name, w, h, d, X0 + x, Y0 + y, Z0 - zl - d, mat, bevel, uv=uv)
def coil(name, rm, d, L, n, c, y0, mat, axis='y', ends=1.0, per_turn=28, seg=8, body=True, hand=1):
    """実形状のコイルばね(圧縮ばね)。rm=平均コイル半径, d=線径, L=全長, n=有効巻数, c=軸の中心(設計座標の他2軸), y0=下端(軸方向)。
    両端は座巻き(ピッチ=線径, 研削端面) ends 巻 + 有効巻 n。axis: 'y'(上下)|'z'(奥行)|'x'。"""
    nt = n + 2 * ends; pa = max((L - (2 * ends + 1) * d) / n, d)      # 有効部ピッチ
    def h_of(u):      # u=0..nt 巻 -> 軸方向高さ
        e0 = min(u, ends); mid = max(0.0, min(u - ends, n)); e1 = max(0.0, u - ends - n)
        return d / 2 + e0 * d + mid * pa + e1 * d
    N = int(nt * per_turn); me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []
    def loc(a, h):
        ca, sa = math.cos(a), math.sin(a)
        return {'y': (c[0] + rm * ca, y0 + h, c[1] + rm * sa), 'z': (c[0] + rm * ca, c[1] + rm * sa, y0 + h), 'x': (y0 + h, c[0] + rm * ca, c[1] + rm * sa)}[axis]
    pts = [loc(hand * 2 * math.pi * (i / per_turn), h_of(i / per_turn)) for i in range(N + 1)]
    for i, p in enumerate(pts):
        pa_, pb_ = pts[max(i - 1, 0)], pts[min(i + 1, N)]; T = Vector(pb_) - Vector(pa_); T.normalize()
        ctr = {'y': (c[0], p[1], c[1]), 'z': (c[0], c[1], p[2]), 'x': (p[0], c[0], c[1])}[axis]
        R = Vector(p) - Vector(ctr); R.normalize(); B = T.cross(R); B.normalize()
        rings.append([bm.verts.new(V(*(Vector(p) + (d / 2) * (math.cos(2 * math.pi * k / seg) * R + math.sin(2 * math.pi * k / seg) * B)))) for k in range(seg)])
    for i in range(N):
        for k in range(seg): bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    for p_ in me.polygons: p_.use_smooth = True
    ob = bpy.data.objects.new(name, me); me.materials.append(mat); return link(ob, body)
def icyl(name, r, length, axis, cx, cy, czl, mat, seg=48): return cyl(name, r, length, axis, X0 + cx, Y0 + cy, Z0 - czl, mat, seg)

# ---------------- マテリアル ----------------
def principled(name, color, metal=0.0, rough=0.5, coat=0.0, coat_rough=0.03, emit=None, estr=0.0, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(color); b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    for k, v in (('Coat Weight', coat), ('Coat Roughness', coat_rough)):
        if k in b.inputs: b.inputs[k].default_value = v
    if emit:
        b.inputs['Emission Color'].default_value = hexc(emit); b.inputs['Emission Strength'].default_value = estr
    return m

def add_bump(m, scale=900.0, strength=0.04, dist=0.05):
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); no = nt.nodes.new('ShaderNodeTexNoise'); bu = nt.nodes.new('ShaderNodeBump')
    no.inputs['Scale'].default_value = scale; no.inputs['Detail'].default_value = 8; bu.inputs['Strength'].default_value = strength; bu.inputs['Distance'].default_value = dist
    nt.links.new(tc.outputs['Object'], no.inputs['Vector']); nt.links.new(no.outputs['Fac'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])

def img_material(name, path, rough=0.5, metal=0.0, emission=False, strength=1.0, alpha_from_red=False, mapping=None):   # mapping未指定=UV使用
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(path); tx.image.colorspace_settings.name = 'sRGB'
    if mapping:   # オブジェクト座標のX,Z(幅,高さ)平面にテクスチャを投影
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = mapping[0]; mp.inputs['Location'].default_value = mapping[1]
        sp = nt.nodes.new('ShaderNodeSeparateXYZ'); cb = nt.nodes.new('ShaderNodeCombineXYZ')
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], sp.inputs['Vector'])
        nt.links.new(sp.outputs['X'], cb.inputs['X']); nt.links.new(sp.outputs['Z'], cb.inputs['Y']); nt.links.new(cb.outputs['Vector'], tx.inputs['Vector'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emission:
        b.inputs['Base Color'].default_value = (0, 0, 0, 1)
        nt.links.new(tx.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = strength
    else:
        nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
    if alpha_from_red:
        nt.links.new(tx.outputs['Color'], b.inputs['Alpha'])   # 赤チャンネル≒輝度で穴を抜く
        m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    return m

# ---------------- テクスチャ生成(PIL) ----------------
from PIL import Image, ImageDraw, ImageFilter, ImageFont
TEXDIR = os.path.join(ROOT, 'blender', 'textures'); os.makedirs(TEXDIR, exist_ok=True)

def wallpaper(path, base, light):
    """本体色ごとの壁紙(spec.wallpaper の4停止点グラデーション+柔らかいリボン)。ビューアの drawScreen と同じ配色。"""
    w, h = 2560, 1440
    stops_hex = S['wallpaper'].get(A.color, S['wallpaper']['silver']); cs = [tuple(int(x[i:i + 2], 16) for i in (1, 3, 5)) for x in stops_hex]
    def col(t):
        t = min(1.0, max(0.0, t)) * (len(cs) - 1); i = min(len(cs) - 2, int(t)); u = t - i
        return tuple(int(cs[i][k] + (cs[i + 1][k] - cs[i][k]) * u) for k in range(3))
    img = Image.new('RGB', (w, h)); px = img.load()
    for y in range(h):
        for x in range(w): px[x, y] = col(x / w * .62 + (1 - y / h) * .38)
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(over)
    for i in range(7):
        cx = 60 + i * 390; d.rounded_rectangle((cx - 150, -400, cx + 150, h + 400), 150, fill=(255, 255, 255, 30 if i % 2 else 14))
    over = over.rotate(-16, resample=Image.BICUBIC, center=(w / 2, h / 2)).filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert('RGBA'), over).convert('RGB'); d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle((0, 0, w, 36), fill=(20, 20, 40, 110))
    d.rounded_rectangle((w / 2 - 340, h - 124, w / 2 + 340, h - 36), 38, fill=(255, 255, 255, 80))
    for i in range(9): d.rounded_rectangle((w / 2 - 310 + i * 72, h - 110, w / 2 - 258 + i * 72, h - 58), 13, fill=(255, 255, 255, 190))
    img.save(path)

def pcb_tex(path, w, h, seed, base, trace, label=''):
    rr = random.Random(seed); sc = 8; W_, H_ = int(w * sc), int(h * sc)
    img = Image.new('RGB', (W_, H_), base); d = ImageDraw.Draw(img)
    for _ in range(int(w * h / 18)):
        x, y = rr.random() * W_, rr.random() * H_; pts = [(x, y)]
        for _ in range(4):
            if rr.random() < .5: x += (rr.random() - .5) * 220
            else: y += (rr.random() - .5) * 220
            pts.append((x, y))
        d.line(pts, fill=trace, width=int(2 + rr.random() * 4))
    for _ in range(int(w * h / 40)):
        x, y = rr.random() * W_, rr.random() * H_; d.ellipse((x - 3, y - 3, x + 3, y + 3), fill='#b88a3a')
    if label:
        try: f = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 34)
        except Exception: f = None
        d.text((30, H_ - 60), label, fill='#d8d8d8', font=f)
    img.save(path)

def vent_alpha(path, centers, pod_w, pod_h, ppm=4):
    img = Image.new('RGB', (int(pod_w * ppm), int(pod_h * ppm)), 'white'); d = ImageDraw.Draw(img); step = 7.0
    for cx, cy, R in centers:
        yy = -R; row = 0
        while yy <= R:
            xx = -R
            while xx <= R:
                x = xx + (step / 2 if row % 2 else 0)
                if math.hypot(x, yy) < R - 3:
                    px_, py_ = (cx + x) * ppm, (pod_h - (cy + yy)) * ppm; r = 2.1 * ppm; d.ellipse((px_ - r, py_ - r, px_ + r, py_ + r), fill='black')
                xx += step
            yy += step * .87; row += 1
    img.save(path)

# ---------------- 色・マテリアル定義 ----------------
base_c, stand_c, chin_c = S['palette'][A.color]
wp = os.path.join(TEXDIR, f'wallpaper_{A.color}.png'); wallpaper(wp, base_c, chin_c)
M = {}
M['body'] = principled('anodized_body', base_c, 1.0, 0.38); add_bump(M['body'])
M['stand'] = principled('anodized_stand', stand_c, 1.0, 0.34); add_bump(M['stand'])
def _mix(a, c2, t): return '#%02x%02x%02x' % tuple(int(int(a[i:i + 2], 16) * (1 - t) + int(c2[i:i + 2], 16) * t) for i in (1, 3, 5))
chin_v = _mix(chin_c, base_c, .5); bezel_v = _mix(chin_c, '#ffffff', .3)      # viewer/index.html の setColor と同じ配色(前面の色差を明確に)
M['chin'] = principled('painted_chin', chin_v, 0.0, 0.28, coat=1.0, coat_rough=0.04)
M['glass'] = principled('front_glass', bezel_v, 0.0, 0.06, coat=1.0, coat_rough=0.02)
M['screen'] = img_material('display', wp, emission=True, strength=1.1)
M['black'] = principled('black_glass', '#050507', 0.0, 0.05, coat=1.0)
M['dark'] = principled('dark_plastic', '#101114', 0.0, 0.55)
M['plastic'] = principled('plastic', '#1a1c20', 0.0, 0.5)
M['steel'] = principled('steel', '#b4b9c0', 1.0, 0.32)
M['alu'] = principled('alu', '#c4c8cf', 1.0, 0.38)
M['alublack'] = principled('alu_black', '#25272c', 0.9, 0.42)
M['gold'] = principled('gold', '#d4a94a', 1.0, 0.28)
M['copper'] = principled('copper', '#c4743b', 1.0, 0.3)
M['white'] = principled('white_plastic', '#e9e9e4', 0.0, 0.5)
M['cap'] = principled('cap', '#1b1d22', 0.3, 0.4)
M['chip'] = principled('chip', '#101113', 0.2, 0.35)
M['led'] = principled('led', '#101010', 0.0, 0.3, emit='#4cff88', estr=6.0)
M['inner'] = principled('inner_floor', '#8b8f96', 0.7, 0.55)
M['beige'] = principled('fan_beige', '#d9c7a6', 0.0, 0.55)
M['brown'] = principled('fan_brown', '#6b4a31', 0.0, 0.5)
M['rubber'] = principled('rubber', '#0e0f12', 0.0, 0.75)
M['smd'] = principled('smd', '#2b2d31', 0.5, 0.4)
M['yellow'] = principled('cable_yellow', '#d4a017', 0.0, 0.6)
M['red'] = principled('cable_red', '#b82a1e', 0.0, 0.6)
M['led_blue'] = principled('led_blue', '#101010', 0.0, 0.3, emit='#9fd0ff', estr=4.0)

# ---------------- 本体 ----------------
def rbox(name, w, h, d, x, y, z, mat, r, seg=8):
    """平面の角を R=r に丸めた板(前面スラブ/ガラス用)。(x,y,z)=最小角、厚み d は -z 方向(box と同じ向き)。"""
    cx, cy = x + w / 2, y + h / 2; pts = []
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for k in range(seg + 1):
            t = math.radians(a0 + 90 * k / seg); pts.append(((w / 2 - r) * sx + r * math.cos(t), (h / 2 - r) * sy + r * math.sin(t)))
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    top = [bm.verts.new((cx + px, -(z) if False else 0, 0)) for (px, py) in pts] if False else None
    top = [bm.verts.new(V(cx + px, cy + py, z + d)) for (px, py) in pts]; bot = [bm.verts.new(V(cx + px, cy + py, z)) for (px, py) in pts]
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    for i in range(len(pts)): j = (i + 1) % len(pts); bm.faces.new((top[i], top[j], bot[j], bot[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new(name, me); me.materials.append(mat)
    bv = ob.modifiers.new('bevel', 'BEVEL'); bv.width = 0.6; bv.segments = 2; bv.limit_method = 'ANGLE'
    return link(ob)
CR_ = S.get('corner', 10)      # 前面の平面角R(spec.json corner)
rbox('slab', W, H, SLAB - 1.1, -W / 2, 0, -SLAB, M['body'], CR_)                 # スラブ(背板一体の枠): 前面1.1mmはガラス
rbox('front_glass', W, H, 1.1, -W / 2, 0, -1.1, M['glass'], CR_)                # 化学強化ガラス t1.1 (前面z=0 でスラブ縁と面一)
box('display', PW, PH, 0.02, -PW / 2, CHIN, 0.0, M['screen'], uv=True)               # ガラス裏の表示を面上で簡略表現
box('chin_print', W - 5, CHIN - 4, 0.02, -W / 2 + 2.5, 2, 0.0, M['chin'])             # ガラス裏面印刷(塗装ではない)
cyl('camera', 2.0, 0.04, 'z', 0, H - 5, 0.02, M['black'], 24)                       # カメラ窓 Ø4.0
for sx in (-1, 0, 1): cyl(f'mic{sx}', 0.5, 0.04, 'z', sx * 60 + (35 if sx == 0 else 0), H - 5, 0.02, M['black'], 12)  # マイク穴 Ø1.0 ×3(実物は3マイク。位置はApple非公表=仮置き)

# ---------------- 内部部品 ----------------
rotors = []
def make_fan(name, size, depth, n, frame_mat, blade_mat, hub_mat, cx, cy, czl, hub_k=.19, open_k=.46):
    """内部座標 (cx,cy,czl)=ファン底面中心。軸=背面方向(+z local)。"""
    wc = Vector((X0 + cx, Y0 + cy, Z0 - czl - depth / 2))     # 設計図座標での体積中心
    fr = box(name + '_frame', size, size, depth, wc.x - size / 2, wc.y - size / 2, wc.z - depth / 2, frame_mat, bevel=1.2)
    cut = cyl(name + '_hole', size * open_k, depth + 2, 'z', wc.x, wc.y, wc.z, None, 64, body=False); cut.hide_render = True; BODY_OBJS.append(cut)
    bm = fr.modifiers.new('hole', 'BOOLEAN'); bm.object = cut; bm.operation = 'DIFFERENCE'; bm.solver = 'EXACT'
    rotor = bpy.data.objects.new(name + '_rotor', None); rotor.location = V(wc.x, wc.y, wc.z); link(rotor)
    hub = cyl(name + '_hub', size * hub_k, depth * .7, 'z', wc.x, wc.y, wc.z, hub_mat, 48); hub.parent = rotor; hub.location = (0, 0, 0)
    hub.rotation_euler = (math.pi / 2, 0, 0)
    L = size * open_k - size * (hub_k - .02) - 1; R0 = size * (hub_k - .02)
    pts = []
    def qb(p0, c, p1, n_=8): return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]) for t in [i / n_ for i in range(n_ + 1)]]
    pts = qb((0, -size * .065), (L * .55, -size * .11), (L, -size * .05)) + qb((L, size * .04), (L * .5, size * .15), (0, size * .08))
    me = bpy.data.meshes.new(name + '_blade'); bmm = bmesh.new(); t = .7; pitch = .42
    def tf(x, z, y): return Vector((x + R0, y, z)) if True else None
    top, bot = [], []
    for (x, z) in pts:
        zz = z * math.cos(pitch); yy = z * math.sin(pitch)
        top.append(bmm.verts.new((x + R0, yy + t / 2, zz))); bot.append(bmm.verts.new((x + R0, yy - t / 2, zz)))
    bmm.faces.new(top); bmm.faces.new(list(reversed(bot)))
    for i in range(len(pts)): j = (i + 1) % len(pts); bmm.faces.new((top[i], bot[i], bot[j], top[j]))
    bmm.normal_update(); bmm.to_mesh(me); bmm.free(); me.materials.append(blade_mat)
    for i in range(n):
        b = bpy.data.objects.new(f'{name}_blade{i}', me); b.parent = rotor; b.rotation_euler = (0, i * 2 * math.pi / n, 0); link(b)
        b.location = (0, 0, 0)
    # ステーター支柱(MDC): 静止側。ハブのモーター座をフレームへ固定する3本の細い支柱(回転しない)。本数・幅は典型値=UNVERIFIED。ファンの底面側(軸方向の下端)に置く
    for si in range(3):
        a_ = si * 2 * math.pi / 3 + math.pi / 6; ln = size * open_k - size * (hub_k - .02) + 1.5; mid = size * (hub_k - .02) + ln / 2 - 0.75
        sp = box(f'{name}_stator{si}', ln, 1.6, 2.4, 0, 0, 0, frame_mat, bevel=.2)
        sp.rotation_euler = (0, 0, a_); sp.location = Vector((wc.x + mid * math.cos(a_), wc.y + mid * math.sin(a_), wc.z - depth * .5 + 1.4))
    rotors.append(rotor); return rotor

# ==================== v6: ドーム背面シェル + サービストレイ + 内部部品(model/layout.json 駆動) ====================
DM = S['dome']; DOME_W = W - 2 * DM['inset_left_right']; DOME_X0 = -W / 2 + DM['inset_left_right']
DOME_Y0 = DM['inset_bottom']; DOME_H = H - DM['inset_bottom'] - DM['inset_top']
DOME_DEPTH = POD_T - SLAB            # スラブ背面からドーム最頂部(外面)まで = 90
IW_, IH_ = DOME_W - 2 * WALL, DOME_H - 2 * WALL     # 内寸 590 x 371
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def d_inner(inset): return DM['edge_inner_depth'] + (DOME_DEPTH - WALL - DM['edge_inner_depth']) * ease(inset / DM['run'])   # 内面の深さ(内部座標z)
def rrect(a, b, r, seg=10):
    pts = []
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for k in range(seg + 1):
            t = math.radians(a0 + 90 * k / seg); pts.append((sx * (a - r) + r * math.cos(t) * 1.0 if False else (a - r) * sx + r * math.cos(t), (b - r) * sy + r * math.sin(t)))
    return pts
def dome_shell(name='cover_back', mat=None, dshift=0.0, ushift=0.0, solid=True):
    cx, cy = DOME_X0 + DOME_W / 2, DOME_Y0 + DOME_H / 2
    a0, b0, r0 = DOME_W / 2 - ushift, DOME_H / 2 - ushift, DM['corner_r'] - ushift
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []; uvd = {}
    insets = [0, 0] + [DM['run'] * (k / 32) for k in range(1, 33)]      # 断面を32分割(旧12: 折れ線が粗い=MDD-024)
    for i, ins in enumerate(insets):
        dep = 0 if i == 0 else max(d_inner(ins) + WALL + dshift, 0.5)
        rr = max(r0 - ins, 6)      # 内側へオフセットした角丸矩形(角R=R0-inset)
        ring = []
        for (px, py) in rrect(a0 - ins, b0 - ins, rr):
            v_ = bm.verts.new(V(cx + px, cy + py, -SLAB - dep)); uvd[v_] = ((px + DOME_W / 2) / DOME_W, (py + DOME_H / 2) / DOME_H); ring.append(v_)
        rings.append(ring)
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for j in range(n):
            k = (j + 1) % n; bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    lay = bm.loops.layers.uv.new('UVMap')
    for f_ in bm.faces:
        for l_ in f_.loops: l_[lay].uv = uvd[l_.vert]      # 設計x-yへの平面投影UV(穿孔テクスチャ用)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); me.materials.append(mat or M['body'])
    so = ob.modifiers.new('wall', 'SOLIDIFY'); so.thickness = DM['sheet_t'] if solid else 0.8; so.offset = 1      # 板厚2.0(spec.dome.sheet_t)
    if solid and A.vent_mode == 'texture':
        bv = ob.modifiers.new('edge', 'BEVEL'); bv.width = 0.7; bv.segments = 2; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(35)
    for p in me.polygons: p.use_smooth = len(p.vertices) == 4      # 平坦部(ngon)はフラット
    link(ob)
    # 法線が背面(-設計z = Blender +Y)を向くことを保証
    if sum(p.normal.y for p in me.polygons) < 0:
        for p in me.polygons: p.flip()
        me.update()
    return ob
# ---- 穿孔: v7.1 は透過テクスチャ(Ø2.4×ピッチ4.0, 千鳥)。--vent-mode boolean なら実穴(GLB出力用の軽量版) ----
def perf_texture(path, ppm=5.0):
    wpx, hpx = int(DOME_W * ppm), int(DOME_H * ppm); img = Image.new('L', (wpx, hpx), 255); d_ = ImageDraw.Draw(img)
    x0_, x1_, y0_, y1_ = WALL + 36, WALL + IW_ - 36, WALL + 36, WALL + IH_ - 36; pitch = 4.0; r_ = 1.2; row = 0; y_ = y0_
    while y_ <= y1_:
        x_ = x0_ + (pitch / 2 if row % 2 else 0)
        while x_ <= x1_:
            cxp, cyp = x_ * ppm, hpx - y_ * ppm; d_.ellipse((cxp - r_ * ppm, cyp - r_ * ppm, cxp + r_ * ppm, cyp + r_ * ppm), fill=0); x_ += pitch
        y_ += pitch * .866; row += 1
    img.save(path)
if A.vent_mode == 'texture':
    pp = os.path.join(TEXDIR, 'dome_perf.png'); perf_texture(pp)
    M['body_perf'] = img_material('anodized_body_perf', pp, rough=0.38, metal=1.0, alpha_from_red=True)
    nt_ = M['body_perf'].node_tree; tx_ = [n for n in nt_.nodes if n.bl_idname == 'ShaderNodeTexImage'][0]
    nt_.nodes['Principled BSDF'].inputs['Base Color'].default_value = hexc(base_c)
    for l_ in list(nt_.links):
        if l_.to_socket.name == 'Base Color': nt_.links.remove(l_)
    nt_.links.new(tx_.outputs['Color'], nt_.nodes['Principled BSDF'].inputs['Alpha'])   # 画像の輝度=不透明度(黒=穴)
    tx_.image.alpha_mode = 'CHANNEL_PACKED'; tx_.image.colorspace_settings.name = 'Non-Color'
    dome = dome_shell('cover_back', M['body_perf'])
else:
    dome = dome_shell()
# 内側の黒メッシュフィルタ(穴越しに内部を見せない: Apple的P7)
M['filter'] = principled('mesh_filter', '#08090b', 0.2, 0.7)
dome_filter = dome_shell('cover_filter', M['filter'], dshift=-6.0, ushift=4.0, solid=False)
# 吸排気の六角配列穴(ドーム平坦部〜傾斜部)。ゾーンは内部座標(x0,y0,x1,y1): 水冷ラジエーター上、ケースファン上、GPUファン上
def vent_cutter(name, zones, step=7.0, hr=2.1, margin=22):
    bmc = bmesh.new()
    for (zx0, zy0, zx1, zy1) in zones:
        zx0, zy0 = max(zx0, margin), max(zy0, margin); zx1, zy1 = min(zx1, IW_ - margin), min(zy1, IH_ - margin)
        row = 0; y_ = zy0
        while y_ <= zy1:
            x_ = zx0 + (step / 2 if row % 2 else 0)
            while x_ <= zx1:
                bmesh.ops.create_cone(bmc, cap_ends=True, segments=8, radius1=hr, radius2=hr, depth=DOME_DEPTH + 10,
                                      matrix=Matrix.Translation(V(X0 + x_, Y0 + y_, Z0 - DOME_DEPTH / 2)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
                x_ += step
            y_ += step * .87; row += 1
    me = bpy.data.meshes.new(name); bmc.to_mesh(me); bmc.free()
    ob = bpy.data.objects.new(name, me); ob.hide_render = True; link(ob); return ob
def perf_cutter(name, hr=1.2, pitch=4.0, ins_start=None, L=7.0):
    """背面ドームの穿孔カッター(専用設計): 穴は曲面の**法線方向**に開け、面に沿った**等間隔**(ピッチ4.0)で配置する。
    平面へ投影して垂直に開ける方式(穴が傾斜で長穴に伸びる)は採らない。傾斜部=リング状に面の弧長で等間隔、平坦部=千鳥格子。"""
    ins_start = ins_start if ins_start is not None else 36 + WALL; run = DM['run']; K = DOME_DEPTH - WALL - DM['edge_inner_depth']
    bmc = bmesh.new(); cx, cy = DOME_X0 + DOME_W / 2, DOME_Y0 + DOME_H / 2; a0, b0, r0 = DOME_W / 2, DOME_H / 2, DM['corner_r']; n_holes = [0, 0]
    def wprime(ins): tt = max(0.0, min(1.0, ins / run)); return K * 6 * tt * (1 - tt) / run      # d(深さ)/d(縁からの距離)
    def wdepth(ins): return d_inner(ins) + WALL
    def ring(a, b, r, step, phase):      # 角丸矩形の周を弧長で等間隔に標本化: [(x,y,外向き単位法線ux,uy)]
        sx, sy = a - r, b - r; per = 2 * (2 * sx) + 2 * (2 * sy) + 2 * math.pi * r; n = max(8, int(per / step)); ds = per / n
        segs = [(2 * sx, 'b'), (math.pi * r / 2, 'a'), (2 * sy, 'r'), (math.pi * r / 2, 'a'), (2 * sx, 't'), (math.pi * r / 2, 'a'), (2 * sy, 'l'), (math.pi * r / 2, 'a')]
        # 弧は「角の中心+半径×(cos,sin)」で扱う(直線と交互に並ぶ順序: 下辺→右下弧→右辺→右上弧→上辺→左上弧→左辺→左下弧)
        out = []; accs = []; acc = 0.0
        for ln, kind in segs: accs.append((acc, ln, kind)); acc += ln
        centers = {1: (sx, -sy, -math.pi / 2), 3: (sx, sy, 0.0), 5: (-sx, sy, math.pi / 2), 7: (-sx, -sy, math.pi)}
        for i in range(n):
            s = (i + phase) * ds % per
            for idx, (a_, ln, kind) in enumerate(accs):
                if s < a_ + ln or idx == len(accs) - 1:
                    u = (s - a_) / max(ln, 1e-9)
                    if kind == 'b': out.append((-sx + 2 * sx * u, -b, 0.0, -1.0))
                    elif kind == 'r': out.append((a, -sy + 2 * sy * u, 1.0, 0.0))
                    elif kind == 't': out.append((sx - 2 * sx * u, b, 0.0, 1.0))
                    elif kind == 'l': out.append((-a, sy - 2 * sy * u, -1.0, 0.0))
                    else:
                        ccx, ccy, ang0 = centers[idx]; ang = ang0 + u * math.pi / 2; out.append((ccx + r * math.cos(ang), ccy + r * math.sin(ang), math.cos(ang), math.sin(ang)))
                    break
        return out
    def add(px, py, w, nx, ny, nz):
        ax = Vector((nx, -nz, ny)); ax.normalize(); rot = Vector((0, 0, 1)).rotation_difference(ax).to_matrix().to_4x4()
        bmesh.ops.create_cone(bmc, cap_ends=True, segments=8, radius1=hr, radius2=hr, depth=L, matrix=Matrix.Translation(V(cx + px, cy + py, -SLAB - w)) @ rot)
    # (1) 傾斜部: 弧長で等間隔のリング(法線方向に開口)
    ins = ins_start; k = 0; step_ring = pitch * 0.866
    while ins < run - 0.8:
        wp = wprime(ins); r = max(r0 - ins, 6.0)
        for (x, y, ux, uy) in ring(a0 - ins, b0 - ins, r, pitch, 0.5 * (k % 2)):
            nrm = math.sqrt(wp * wp + 1.0); add(x, y, wdepth(ins), wp * ux / nrm, wp * uy / nrm, -1.0 / nrm); n_holes[0] += 1
        ins += step_ring / math.sqrt(1.0 + wp * wp); k += 1
    # (2) 平坦部: 千鳥格子(面は水平=法線は背面方向)
    x0 = run - WALL + pitch / 2; x1 = IW_ - x0; y0 = x0; y1 = IH_ - x0
    row = 0; yy = y0
    while yy <= y1:
        xx = x0 + (pitch / 2 if row % 2 else 0)
        while xx <= x1:
            bmesh.ops.create_cone(bmc, cap_ends=True, segments=8, radius1=hr, radius2=hr, depth=L, matrix=Matrix.Translation(V(X0 + xx, Y0 + yy, -SLAB - wdepth(run))) @ Matrix.Rotation(math.pi / 2, 4, 'X')); n_holes[1] += 1; xx += pitch
        yy += step_ring; row += 1
    me = bpy.data.meshes.new(name); bmc.to_mesh(me); bmc.free(); ob = bpy.data.objects.new(name, me); ob.hide_render = True; link(ob); print('perf holes: slope', n_holes[0], 'flat', n_holes[1]); return ob
LAY = {i['id']: i for i in json.load(open(os.path.join(ROOT, 'model', 'layout.json')))['items']}
def lp(k): return LAY[k]['pos']
def ls(k): return LAY[k]['size']
rx, ry, _ = lp('radiator'); gx, gy, gz = lp('gpu')
if A.vent_mode == 'boolean':
    vc = perf_cutter('cover_vents', hr=A.vent_r, pitch=A.vent_step)
# 下辺の傾斜面に開口(ポート引き込み): I/O / GPU出力 / ACインレット。各ポート高さに合わせた細いスロット(v7.1)
bx, by, bz = lp('board')
def cutbox(name, x0, y0, z0, w, h, d):
    c = ibox(name, w, h, d, x0, y0, z0, None); c.hide_render = True; BODY_OBJS.append(c); return c
ax_, ay_, az_ = lp('ac_inlet')
WIN = S['windows']
def port_tunnels(name, rects, y0, y1, r=2.0):
    """ポート開口の専用設計: コネクタ1つ(列)ごとに、外形+すき間の**角丸長方形**を、プラグの挿抜方向(設計y: 縁から基板側)へ押し出した「トンネル」を切り出す。
    巨大な箱で切り欠いて面を引き伸ばさない。rects=[(x0,x1,z0,z1)](内部座標, zはスラブ背面から)。互いに重ならない前提(ブーリアンの多様体性)。"""
    bmt = bmesh.new()
    for (xa, xb, za, zb) in rects:
        rr = min(r, (xb - xa) / 2 - .01, (zb - za) / 2 - .01); pts = rrect((xb - xa) / 2, (zb - za) / 2, rr, 6); xm, zm = (xa + xb) / 2, (za + zb) / 2
        lo = [bmt.verts.new(V(X0 + xm + px, Y0 + y0, Z0 - (zm + pz))) for (px, pz) in pts]; hi = [bmt.verts.new(V(X0 + xm + px, Y0 + y1, Z0 - (zm + pz))) for (px, pz) in pts]
        bmt.faces.new(lo[::-1]); bmt.faces.new(hi)
        for q in range(len(pts)): q2 = (q + 1) % len(pts); bmt.faces.new((lo[q], lo[q2], hi[q2], hi[q]))
    bmesh.ops.recalc_face_normals(bmt, faces=bmt.faces[:]); me = bpy.data.meshes.new(name); bmt.to_mesh(me); bmt.free()
    ob = bpy.data.objects.new(name, me); ob.hide_render = True; link(ob); BODY_OBJS.append(ob); return ob
_mg = 1.0      # 開口のすき間(外形+1.0mm)
_io_cols = [(15.0, 34.0, -0.5, 27.0), (40.0, 55.0, 1.0, 22.0), (58.5, 73.5, 5.0, 20.5), (76.0, 91.0, 0.5, 15.5), (93.0, 110.0, 0.5, 30.0), (113.0, 122.0, 3.0, 32.0)]      # 列A〜E+SMA: ポート外形の包絡(p.26読み取り)
c_io = port_tunnels('cover_io_cutter', [(bx + x0_ - _mg, bx + x1_ + _mg, bz + 1.6 + z0_ - _mg, bz + 1.6 + z1_ + _mg) for (x0_, x1_, z0_, z1_) in _io_cols], WIN['io_y0'] - 2, by - 1.0)
c_ac = port_tunnels('cover_ac_cutter', [(ax_ - 2, ax_ + 30, az_ - 2, az_ + 22)], WIN['io_y0'] - 2, ay_ + 30)      # C13プラグ(30x22)の挿抜
c_gpu = port_tunnels('cover_gpu_cutter', [(gx + 20 + k * 28 - _mg, gx + 20 + k * 28 + w_ + _mg, gz + 7 - _mg, gz + 13.5 + _mg) for k, w_ in enumerate((15, 16, 16, 16))], WIN['gpu_y0'] - 2, gy - 1.0)      # HDMI+DP×3: 1ポートずつ
c_acf = port_tunnels('cover_acflange_cutter', [(ax_ - 4.5, ax_ + 32.5, az_ - 4.5, az_ + 24.5)], ay_ - 6.0, ay_ + 3.0, r=3.0)      # ACインレットのフランジ(36x28 t3)の座ぐり(ポケット)
mods_ = [('io', c_io), ('gpu', c_gpu), ('ac', c_ac), ('acf', c_acf)] + ([('vents', vc)] if A.vent_mode == 'boolean' else [])
for nm, c in mods_:
    for tgt in ((dome,) if nm == 'vents' else (dome, dome_filter)):
        m_ = tgt.modifiers.new(nm, 'BOOLEAN'); m_.object = c; m_.operation = 'DIFFERENCE'; m_.solver = 'MANIFOLD'
# EMIガスケット(ドーム縁の黒い導電ファブリック)
def gasket():
    cx, cy = DOME_X0 + DOME_W / 2, DOME_Y0 + DOME_H / 2; me = bpy.data.meshes.new('gasket'); bm = bmesh.new()
    o = [bm.verts.new(V(cx + px, cy + py, -SLAB - .1)) for (px, py) in rrect(DOME_W / 2 - 2.2, DOME_H / 2 - 2.2, DM['corner_r'] - 2)]
    i2 = [bm.verts.new(V(cx + px, cy + py, -SLAB - .1)) for (px, py) in rrect(DOME_W / 2 - 4.4, DOME_H / 2 - 4.4, DM['corner_r'] - 4)]
    n = len(o)
    for j in range(n): k = (j + 1) % n; bm.faces.new((o[j], o[k], i2[k], i2[j]))
    bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new('gasket', me); me.materials.append(M['rubber'])
    so = ob.modifiers.new('t', 'SOLIDIFY'); so.thickness = 3.0; so.offset = -1; return link(ob)
gasket()
# スタンド(足+腕)。ヒンジ機構(ばね/摩擦ヒンジ/ブロック等)は後段の hardware で全部品を描画
FT = 12.0; fw = S['stand']['foot_w']; HY = S['hinge']['axis_y']
box('stand_foot', fw, FT, FOOT, -fw / 2, -DROP - FT, ZC - S['stand']['foot_back'], M['stand'], bevel=S['stand']['shroud']['foot_edge_r_mm'], body=False)
BT = S['stand']['ballast_kg'] / (7.85e-6 * (fw - 24) * (FOOT - 24))      # 鋼板ballastの厚さ[mm]=質量から算出(spec.jsonが単一源)
box('stand_ballast', fw - 24, BT, FOOT - 24, -(fw - 24) / 2, -DROP - FT + 3, ZC - S['stand']['foot_back'] + 12, M['steel'], body=False)   # 足内の鋼板ballast
for sx_ in (-1, 1):
    for sz_ in (-1, 1): cyl('stand_rubber_foot', 10, 2.5, 'y', sx_ * (fw / 2 - 24), -DROP - FT - 1.25, ZC - S['stand']['foot_back'] + FOOT / 2 + sz_ * (FOOT / 2 - 24), M['rubber'], 24, body=False)
NK = S['neck']; ARM_H = DROP - S['swivel']['stack_h'] + HY + 11      # 首振りユニットの上からヒンジ軸+11まで
SY_NECK = -DROP + S['swivel']['stack_h']; SY_SIDE = SY_NECK + NK['base_t']      # 基台の上から側板
box('stand_neck_base', 2 * NK['base_half_x'], NK['base_t'], NK['base_z'][1] - NK['base_z'][0], -NK['base_half_x'], SY_NECK, ZC + NK['base_z'][0], M['stand'], bevel=1.0, body=False)    # ネック基台(ロータ板にM5×4で固定)
for _k, _sx in enumerate((-NK['side_x'][1], NK['side_x'][0])):      # ネック側板: 本体+ストリップ+軸ボス(ヒンジブロックの壁の回転域=軸から半径13mm以内を避ける)
    box(f'stand_arm{_k}', NK['side_x'][1] - NK['side_x'][0], NK['body_top'] - SY_SIDE, NK['side_z'][1] - NK['side_z'][0], _sx, SY_SIDE, ZC + NK['side_z'][0], M['stand'], bevel=1.2)
    box(f'stand_arm_strip{_k}', NK['side_x'][1] - NK['side_x'][0], HY - NK['body_top'], NK['strip_w'], _sx, NK['body_top'], ZC - NK['strip_w'] / 2, M['stand'], bevel=.8)
    cyl(f'stand_arm_boss{_k}', NK['boss_r'], NK['side_x'][1] - NK['side_x'][0], 'x', _sx + (NK['side_x'][1] - NK['side_x'][0]) / 2, HY, ZC, M['stand'], 40)
box('stand_neck_tie', 2 * NK['side_x'][0], NK['tie_y'][1] - NK['tie_y'][0], NK['tie_z'][1] - NK['tie_z'][0], -NK['side_x'][0], NK['tie_y'][0], ZC + NK['tie_z'][0], M['stand'], bevel=.8)      # 側板をつなぐタイプレート t6(-15°ストッパの受け)
for _k, (_zz0, _zz1) in enumerate((NK['back_cover_z'], NK['front_cover_z'])):      # 前後カバー(前は t6 の構造板: +40°ストッパの受け。後ろは指の進入防止の t2)
    _zc0, _zc1 = (ZC + _zz0, ZC + _zz1) if _zz1 > _zz0 else (ZC + _zz1, ZC + _zz0)
    box(f'stand_neck_cover{_k}', 2 * NK['side_x'][0], NK['cover_top'] - SY_SIDE, _zz1 - _zz0, -NK['side_x'][0], SY_SIDE, ZC + _zz0, M['stand'], bevel=.6)
SH = S['stand']['shroud']      # 思想適合(P2/P4): 首振り軸受・ネック機構を同色の外皮で隠す(機構は内部に残す)
_sl = SY_NECK - SH['skirt_gap_mm'] + DROP      # 足に固定の円筒スカート(軸受ステータ〜ロータ側面を隠す)
def hollow(ob, thick=2.0):
    """外皮を肉厚 thick[mm] の薄肉殻にする(内向きSOLIDIFY)。中身が詰まった塊として内部機構と交差しないようにする。"""
    m = ob.modifiers.new('wall', 'SOLIDIFY'); m.thickness = thick; m.offset = -1; m.use_even_offset = True
    ob.modifiers.move(len(ob.modifiers) - 1, 0); return ob
def tube(name, r, length, cx, cy, cz, mat, seg=96):      # 両端開口の円管(軸=設計y)。肉厚はhollow()で付ける
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=max(seg, int(round(seg * POLY))), radius1=r, radius2=r, depth=length); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); ob.location = V(cx, cy, cz); me.materials.append(mat)
    for p_ in me.polygons: p_.use_smooth = True
    return link(ob, False)
hollow(tube('stand_skirt', SH['skirt_r_mm'], _sl, 0, -DROP + _sl / 2, ZC, M['stand']))
_cl = 11.0      # ネックと一緒に回る円筒カラー(ロータ上面・PE編組の取り回しを隠す。スカートとの隙間0.5mm)
hollow(tube('stand_neck_collar', SH['skirt_r_mm'], _cl, 0, SY_NECK + _cl / 2, ZC, M['stand']))
# SHAPE-06: ネックカラー上面の環状天板(肉厚2mm)。ばね座(y=HY-s)より下に置き、薄肉化で開いた上面を閉じる。ネック外皮の開口部は残す(機構が通る)
_cap_y = SY_NECK + _cl - 4.2
_cap = cyl('stand_neck_collar_cap', SH['skirt_r_mm'] - 2.2, 2.0, 'y', 0, _cap_y + 1.0, ZC, M['stand'], 96, bevel=1.0, body=False)
_hole = box('stand_neck_collar_cap_hole', 2 * (NK['base_half_x'] + SH['neck_margin_mm'] + 0.5), 8.0, (NK['front_cover_z'][1] - NK['back_cover_z'][0]) + 2 * (SH['neck_margin_mm'] + 0.5), -(NK['base_half_x'] + SH['neck_margin_mm'] + 0.5), _cap_y - 3.0, ZC + NK['back_cover_z'][0] - (SH['neck_margin_mm'] + 0.5), None, body=False)      # 外皮の外形+0.5mmの開口(外皮が貫通する); _hole.hide_render = True
_mb = _cap.modifiers.new('hole', 'BOOLEAN'); _mb.object = _hole; _mb.operation = 'DIFFERENCE'; _mb.solver = 'EXACT'
_m = SH['neck_margin_mm']
_sh = box('stand_neck_shroud', 2 * (NK['base_half_x'] + _m), NK['cover_top'] - SY_NECK, (NK['front_cover_z'][1] - NK['back_cover_z'][0]) + 2 * _m, -(NK['base_half_x'] + _m), SY_NECK, ZC + NK['back_cover_z'][0] - _m, M['stand'], bevel=SH['edge_r_mm'], body=False)
_bm = bmesh.new(); _bm.from_mesh(_sh.data); bmesh.ops.delete(_bm, geom=[f_ for f_ in _bm.faces if abs(f_.normal.z) > 0.9], context='FACES_ONLY'); _bm.to_mesh(_sh.data); _bm.free(); hollow(_sh)      # 上下を開いた薄肉の4面壁(上端は頭部のヒンジ機構が出入りする。首振りに合わせて回転)
for _n in ('stand_neck_shroud', 'stand_foot'): bpy.data.objects[_n].modifiers['bevel'].segments = max(6, int(round(6 * POLY)))      # 大きな面取りは滑らかな曲面に
ARM_OBJ = bpy.data.objects['stand_arm0']; BODY_OBJS.remove(ARM_OBJ); [BODY_OBJS.remove(bpy.data.objects[n_]) for n_ in ('stand_arm1', 'stand_arm_strip0', 'stand_arm_strip1', 'stand_arm_boss0', 'stand_arm_boss1') if bpy.data.objects[n_] in BODY_OBJS]

# ---- テキスト(刻印/印字): 背面から読める向き。(x,y)=内部座標、zl=スラブ背面からの高さ、rot=度(面内) ----
def label(txt, size, x, y, zl, mat, rot=0, ext=0.05, name=None, align='CENTER'):
    cu = bpy.data.curves.new(name or ('t_' + txt[:8]), 'FONT'); cu.body = txt; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'; cu.extrude = ext
    ob = bpy.data.objects.new(name or ('t_' + txt[:8]), cu); cu.materials.append(mat)
    ob.matrix_world = Matrix.Translation(V(X0 + x, Y0 + y, Z0 - zl)) @ Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'X') @ Matrix.Rotation(math.radians(rot), 4, 'Z')
    return link(ob)

# ---- 追加マテリアル ----
M['pcb_black'] = principled('asus_pcb', '#0b0c0e', 0.0, 0.42)
M['shroud'] = principled('asus_shroud', '#141518', 0.3, 0.38); add_bump(M['shroud'], 600, .02)
M['silver_trim'] = principled('silver_trim', '#aeb3ba', 1.0, 0.30)
M['print_w'] = principled('print_white', '#e8e8e8', 0.0, 0.5)
M['print_red'] = principled('print_red', '#d1202b', 0.0, 0.45)
M['rad_black'] = principled('rad_black', '#16171a', 0.5, 0.5)
M['hose'] = principled('hose', '#0d0e10', 0.0, 0.55)
M['noctua_beige'] = principled('noctua_frame', '#cdb994', 0.0, 0.55); M['noctua_brown'] = principled('noctua_blade', '#6b4a31', 0.0, 0.5)
M['sf_body'] = principled('sf_body', '#17181b', 0.4, 0.5); M['sf_label'] = principled('sf_label', '#d0d3d8', 0.0, 0.6)

# ---- サービストレイ(A5052 t2.0, 590x371.3, 角R44) z3〜5 + 断熱シート(z0〜3) + キーホール(実孔) ----
KH = [tuple(k) for k in json.load(open(os.path.join(ROOT, 'model', 'layout.json')))['keyholes']]
def slab_plate(name, a, b, r, zl0, zl1, mat):
    cx, cy = X0 + IW_ / 2, Y0 + IH_ / 2; me = bpy.data.meshes.new(name); bm = bmesh.new(); pts = rrect(a, b, r, 8)
    top = [bm.verts.new(V(cx + px, cy + py, Z0 - zl1)) for (px, py) in pts]; bot = [bm.verts.new(V(cx + px, cy + py, Z0 - zl0)) for (px, py) in pts]
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    for i in range(len(pts)): j = (i + 1) % len(pts); bm.faces.new((top[i], top[j], bot[j], bot[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); me.materials.append(mat); return link(ob)
tray_obj = slab_plate('tray_plate', IW_ / 2 - 10, IH_ / 2 - 10, 38, 3.0, 5.0, principled('tray_alu', '#8d9198', 1.0, 0.42))      # 外周10mmを空ける(ドーム固定ハード用)
insul_obj = slab_plate('tray_insulation', IW_ / 2 - 12, IH_ / 2 - 12, 36, 0.0, 3.0, principled('insul_sheet', '#3b3a37', 0.0, 0.85))
_bm = bmesh.new()
for (kx, ky) in KH:      # キーホール: 頭が通る丸穴 Ø10.2 + 上方向 12mm の細溝 W6.3(spec.fits.keyhole_slot_w。トレイを12mm下げて掛ける)
    bmesh.ops.create_cone(_bm, cap_ends=True, segments=48, radius1=5.1, radius2=5.1, depth=12, matrix=Matrix.Translation(V(X0 + kx, Y0 + ky, Z0 - 4.0)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
    bmesh.ops.create_cube(_bm, size=1.0, matrix=Matrix.Translation(V(X0 + kx, Y0 + ky + 6, Z0 - 4.0)) @ Matrix.Diagonal((S['fits']['keyhole_slot_w'], 12, 12, 1)))
    bmesh.ops.create_cone(_bm, cap_ends=True, segments=32, radius1=S['fits']['keyhole_slot_w'] / 2, radius2=S['fits']['keyhole_slot_w'] / 2, depth=12, matrix=Matrix.Translation(V(X0 + kx, Y0 + ky + 12, Z0 - 4.0)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))      # 溝の終端は半円(R=溝幅/2): 肩ねじ(R3.0)を受ける
_me = bpy.data.meshes.new('tray_keyhole_cutter'); _bm.to_mesh(_me); _bm.free(); kh_cut = bpy.data.objects.new('tray_keyhole_cutter', _me); kh_cut.hide_render = True; link(kh_cut)
for _o in (tray_obj, insul_obj):
    _m = _o.modifiers.new('keyholes', 'BOOLEAN'); _m.object = kh_cut; _m.operation = 'DIFFERENCE'; _m.solver = 'EXACT'; _m.use_self = True

# ===== Mini-ITX 基板: ASUS ROG STRIX X870-I GAMING WIFI (170x170、レイアウトは公式マニュアル図の実測) =====
BL = json.load(open(os.path.join(ROOT, 'model', 'x870i_layout.json')))
pcbp = os.path.join(TEXDIR, 'pcb_x870i.png'); pcb_tex(pcbp, 170, 170, 9, '#0b0c0e', '#1c1f24', '')
ibox('board_pcb', 170, 170, 1.6, bx, by, bz, img_material('pcb_x870i', pcbp, rough=.45), uv=True)
Z1 = bz + 1.6          # 基板上面
IOX = BL['io_x_ranges']
# 後部I/O(下向き): 公式図でx範囲確定、ブロック内の並びは未確認(代表的な構成で配置)
io_x0, io_x1 = IOX['HDMI_U10G34'][0] - 2, IOX['M2_WIFI'][1] + 2
_ios = ibox('io_shield', io_x1 - io_x0, 26, 30, bx + io_x0, by - 2, Z1, M['steel'])      # I/Oブロック実高≈28〜30mm(ASUS p.26実測)。シャーシ開口規格44.45とは別
def port(name, xc, zc, w, h, inner=None):
    """背面I/Oポート(MDA-009): シールド(中実ブロック)にコネクタ形の**空洞**を開け、内部に色つきの舌片(USB-A=赤/黒、Type-C=薄板)を置く。
    外形 w×h は面板(フランジ)、空洞は (w-3)×(h-3)×深さ12。寸法の根拠: USB-A開口12.5×5.12 / Type-C 8.34×2.56(USB-IF)。ポートごとの舌片・接点の細部はUNVERIFIED。"""
    x0, z0 = bx + xc - w / 2, Z1 + zc - h / 2
    fl = ibox(name + '_shell', w, 0.8, h, x0, by - 3.4, z0, M['steel'], .2)
    ct = cutbox(name + '_cavity', bx + xc - (w - 3) / 2, by - 3.6, Z1 + zc - (h - 3) / 2, w - 3, 12.6, h - 3)
    for tgt in (fl, _ios):
        m_ = tgt.modifiers.new(name, 'BOOLEAN'); m_.object = ct; m_.operation = 'DIFFERENCE'; m_.solver = 'EXACT'
    if w >= 9:       # 舌片(コネクタ内の基板): Type-Cは薄い板、Type-A/RJ45/HDMIは空洞の中央に1枚
        ibox(name + '_tongue', w - 8, 9.0, 1.0 if h < 5 else 1.4, bx + xc - (w - 8) / 2, by - 1.0, Z1 + zc - 0.5, inner or M['dark'], .1)
mid = lambda k: (IOX[k][0] + IOX[k][1]) / 2
# リアI/O配置: ASUS公式マニュアル p.26 の図(外側から見た並び)を読み取り。左→右:
#  列A(x15〜34): USB 10G赤(Type-A)×2 縦積み / HDMI    列B(x40〜55): ボタン(CLR_CMOS/BIOS FlashBack) / USB 10G赤 / USB4 40G Type-C
#  列C(x59〜73): USB 2.0 Type-A ×2 縦積み             列D(x77〜91): USB 2.0 Type-A / USB4 40G Type-C
#  列E(x93〜112): RJ45(2.5GbE) / USB 10G赤 / USB 10G Type-C   Wi-Fi: SMAアンテナ ×2 縦積み(x113〜122)。各列内の上下位置は図の読み取り(±2mm程度)
usb_red = principled('usb_red', '#c8202b', 0, .5); usb2_in = principled('usb2_black', '#15161a', 0, .5)
port('io_a10g_1', 24.5, 23.3, 14.5, 7, usb_red); port('io_a10g_2', 24.5, 15.0, 14.5, 7, usb_red); port('io_hdmi', 24.5, 2.8, 15, 6.5)
port('io_btn_clr', 44, 19.6, 6.5, 3.9); port('io_btn_fb', 51, 19.6, 6.5, 3.9); port('io_a10g_3', 47.5, 12.9, 14.5, 7, usb_red); port('io_usb4_c1', 47.5, 3.0, 9, 3.6)
port('io_usb2_1', 66, 16.5, 14.5, 7, usb2_in); port('io_usb2_2', 66, 9.0, 14.5, 7, usb2_in)
port('io_usb2_3', 83.5, 11.6, 14.5, 7, usb2_in); port('io_usb4_c2', 83.5, 2.7, 9, 3.6)
port('io_rj45', 101.5, 23, 16, 13.5, M['alu']); port('io_a10g_4', 101.5, 11.9, 14.5, 7, usb_red); port('io_usbc_10g', 101.5, 3.0, 9, 3.6)
for k, zz in enumerate((6.9, 28.4)): icyl(f'io_sma{k}', 3.2, 5, 'y', bx + 117.5, by - 5, Z1 + zz, M['gold'], 20)
# VRMヒートシンク(ファン付)・I/Oカバー: 高さは公式資料で未確認(仮置き、docs/unverified-tracker.md)
_vs = ibox('vrm_shroud', 93, 36, 5, bx + 13, by + 24, Z1, M['shroud'], 1.5)      # ベース板(厚5)
_pcx, _pcy = lp('cooler')[0] + 45.5, lp('cooler')[1] + ls('cooler')[1] / 2      # ポンプ円盤中心(後段の pcx/pcy と同じ式)
for _k in range(21):
    _fx = bx + 10 + _k * 4.55
    if _fx < bx + 13.6: continue      # ヘッダ(VRM_HS_FAN x1.6〜11.1)+プラグを避けて、シュラウド(x13〜)の上にだけフィンを置く
    if any(abs((_fx + 0.6) - (_pcx + _dx)) < 6.0 and (by + 25.5) - 6.0 < (_pcy + _dy) < (by + 25.5 + 33) + 6.0 for (_dx, _dy) in ((-27, -45), (27, -45), (-27, 45), (27, 45))): continue      # フィン(x幅1.2, y範囲 by+25.5〜+58.5)がねじ(Ø9逃げ+ばね)に当たるものだけ除く      # ねじ逃げ(Ø9+ばね)の位置にはフィンを立てない
    ibox(f'vrm_fin{_k}', 1.2, 33, 9, _fx, by + 25.5, Z1 + 5, M['shroud'], .2)      # フィン21枚(厚1.2×高9, ピッチ4.55): 高さ14=ベース5+フィン9。形状・枚数は公式に無い=UNVERIFIED      # 高さ・形状は公式資料に無い(未確認の仮置き)。ポンプのケージ下端(z≈27.5)以下に抑えた
ibox('vrm_trim', 93, 1.2, 14.1, bx + 13, by + 24, Z1, M['silver_trim'])      # 前縁トリム
label('ROG', 9, bx + 28, by + 44, Z1 + 22, M['print_w'], name='txt_rog', ext=0.08); label('FOR THOSE WHO DARE', 2.6, bx + 52, by + 30, Z1 + 22, M['silver_trim'], name='txt_ftwd', ext=0.08)
icyl('vrm_fan_ring', 12, 1.0, 'z', bx + 96, by + 42, Z1 + 22.5, M['alublack'], 32)
# チョーク・コンデンサ・MOSFET(CPUソケット周り): 公式写真の一般配置(個数は未確認)
for i in range(4): ibox(f'choke{i}', 7, 7, 4.5, bx + 10 + i * 7.6, by + 62, Z1, M['cap'], .5)      # チョーク4個(個数・位置は公式に無い=UNVERIFIED。CPUソケット(x41〜101)の外=x10〜40へ配置)
for i in range(3): icyl(f'cap{i}', 3.2, 9, 'z', bx + 13 + i * 10.0, by + 74, Z1 + 4.5, M['cap'], 20)      # コンデンサ3個(同上)
def smd_cloud(name, n, x0, y0, w, h, zl, seed, avoid, mat=None):
    """基板上の小型チップ部品(抵抗/MLCC)の雲: 実物同様の密度で散布(個数は典型値, 実物と一致する保証はない)。"""
    rr_ = random.Random(seed); me = bpy.data.meshes.new(name); bmm = bmesh.new(); k = 0
    for _ in range(n * 3):
        if k >= n: break
        x, y = x0 + rr_.random() * w, y0 + rr_.random() * h
        if any(a_[0] - 2.5 < x < a_[0] + a_[2] + 2.5 and a_[1] - 2.5 < y < a_[1] + a_[3] + 2.5 for a_ in avoid): continue      # チップ寸法ぶん(最大1.6mm)+余裕で避ける
        r_ = bmesh.ops.create_cube(bmm, size=1.0); vs = r_['verts']
        sx, sy = (1.6, .8) if rr_.random() < .5 else (.8, 1.6)
        bmesh.ops.scale(bmm, vec=(sx, sy, .5), verts=vs); bmesh.ops.translate(bmm, vec=(x, y, zl + .25), verts=vs); k += 1
    bmm.to_mesh(me); bmm.free(); ob = bpy.data.objects.new(name, me); me.materials.append(mat or M['smd'])
    for v in me.vertices: v.co = V(X0 + v.co.x, Y0 + v.co.y, Z0 - v.co.z)
    return link(ob)
sx_, sy_ = BL['socket_center']
smd_cloud('board_smd', 900, bx + 2, by + 2, 166, 166, Z1, 11, [(bx + 8, by + 24, 98, 36), (bx + sx_ - 30, by + sy_ - 30, 60, 60), (bx + 4, by + 138, 160, 20), (bx + 13, by + 158, 52, 12), (bx + 156, by + 42, 12, 92), (bx + 129, by + 46, 22, 20), (bx + 128, by + 78, 28, 62), (bx + 0, by - 2, 125, 26)] + [(bx + _c['x'][0], by + _c['y'][0], _c['x'][1] - _c['x'][0], _c['y'][1] - _c['y'][0]) for _c in BL.get('components', [])] + [(bx + _hx - 4, by + _hy - 4, 8, 8) for _hx, _hy in ((10.2, 6.4), (165.1, 6.4), (10.2, 163.8), (165.1, 163.8))] + [(bx + 10, by + 62, 29.8, 7), (bx + 9.8, by + 70.8, 26.4, 6.4)] + [(lp('cooler')[0] + 45.5 + _dx - 4, lp('cooler')[1] + ls('cooler')[1] / 2 + _dy - 4, 8, 8) for _dx, _dy in ((-27, -45), (27, -45), (-27, 45), (27, 45))])
# ---- 基板上の追加部品(model/x870i_layout.json components: マニュアルp.14の読み取り。高さは典型値=UNVERIFIED) ----
for _c in BL.get('components', []):
    _w, _d = _c['x'][1] - _c['x'][0], _c['y'][1] - _c['y'][0]
    _nm = 'board_' + _c['id']
    ibox(_nm, _w, _d, _c['h'], bx + _c['x'][0], by + _c['y'][0], Z1, M.get(_c['color'], M['dark']), .3)
    if _c['kind'] == 'header':      # ピン(金色)を上面に見せる
        _n = max(2, int(max(_w, _d) / 2.54)); _lx = _w >= _d
        for _k in range(_n): ibox(f'{_nm}_pin{_k}', 0.6 if _lx else _w * .5, _d * .5 if _lx else 0.6, 0.3, bx + _c['x'][0] + (( _k + .5) * _w / _n - .3 if _lx else _w * .25), by + _c['y'][0] + (_d * .25 if _lx else (_k + .5) * _d / _n - .3), Z1 + _c['h'], M['gold'])
# AM5ソケット + Ryzen 9 9950X3D (IHS刻印: 'AMD' 'RYZEN' の2行のみ確認済)
sx_, sy_ = BL['socket_center']
ibox('socket', 60, 60, 4, bx + sx_ - 30, by + sy_ - 30, Z1, principled('socket', '#2a2c31', 0, .5))
ibox('cpu_ihs', 40, 40, 3.98, bx + sx_ - 20, by + sy_ - 20, Z1 + 4, principled('ihs', '#9da3ab', 1.0, .28), .6)      # AM5 IHS上面=基板上面+7.98mm(MDA-017: 規格値7.98±0.60, 二次情報)
label('AMD', 4, bx + sx_ - 8, by + sy_ + 5, Z1 + 7.98, M['print_w'], name='txt_ihs_amd', ext=0.08); label('RYZEN', 3.2, bx + sx_ - 8, by + sy_ - 1, Z1 + 7.98, M['print_w'], name='txt_ihs_ryzen', ext=0.08)   # 公式画像で確認済の2行のみ
# チップセット(ヒートシンク) / PCIe x16 / ATX24 / EPS / M.2 ドーターカード
ibox('chipset_sink', 21, 19, 9, bx + 129, by + 47, Z1, M['alublack'], .6)
ibox('pcie_x16', 8.6, 89, 11, bx + 157.4, by + 43, Z1, M['dark'], .3); ibox('pcie_gold', 2, 60, .4, bx + 160.7, by + 57, Z1 + 11.0, M['gold'])
ibox('atx24', 50.1, 10, 15, bx + 13.4, by + 159, Z1, M['white'], .4); ibox('eps8', 11.8, 18.1, 11, bx + 1.6, by + 2.4, Z1, M['dark'], .3)
ibox('m2_daughter', 25, 61, 1.6, bx + 131, by + 77, Z1 + 8, M['pcb_black'])      # M.2ドーターカード: 公式p.14の点線枠 y78.5〜136.8(x131〜156)。高さ+8mm・延びる向きは未確認(U56)
ibox('m2_btob_conn', 21, 4.5, 8, bx + 134, by + 104, Z1, M['dark'], .3)             # BTOBコネクタ: 公式p.14実測 y≈104〜108, x134〜155(従来 y52〜58 は誤り)
for k_, yy_ in enumerate((2, 56)): icyl(f'm2_card_post{k_}', 2.6, 8, 'z', bx + 143.5, by + 78 + yy_, Z1 + 4, M['alu'], 6)   # 固定ポスト(位置は未確認の仮置き)
for i in range(2): ibox(f'dimm_slot{i}', BL['dimm_slots']['x'][1] - BL['dimm_slots']['x'][0], BL['dimm_slots']['y'][i][1] - BL['dimm_slots']['y'][i][0], 8, bx + BL['dimm_slots']['x'][0], by + BL['dimm_slots']['y'][i][0], Z1, M['plastic'], .3)
# DDR5 DIMM x2 (大手品・型番未定: ブランドロゴは入れず仕様ステッカーのみ)
for i in range(2):
    y0_, y1_ = BL['dimm_slots']['y'][i]
    ibox(f'dimm{i}_body', 133.35, y1_ - y0_ - 0.6, 36, bx + 9.8, by + y0_ + .3, Z1 + 8, principled('dimm_spreader', '#1b1c20', .8, .35), .6)
    ibox(f'dimm{i}_sticker', 60, .2, 10, bx + 40, by + y1_ - .6 if i == 0 else by + y0_ + .1, Z1 + 24, M['sf_label'])
# ===== M.2 SSD: Samsung 990 PRO with Heatsink (80.15x25x8.88, 黒ヒートシンク+赤スリット)。ドーターカード(基板+8mm, 厚1.6)の上に載り、端のM.2ネジで固定 =====
sd = lp('ssd'); sd_z = Z1 + 8 + 1.6          # カード上面
ibox('ssd_body', 25, 80.15, 8.88, sd[0], sd[1], sd_z, principled('ssd_sink', '#101113', .7, .4), .5)
for k in range(6): ibox(f'ssd_slit{k}', 22, 1.2, .08, sd[0] + 1.5, sd[1] + 14 + k * 8, sd_z + 8.88, M['print_red'])
label('SAMSUNG', 4.2, sd[0] + 12.5, sd[1] + 62, sd_z + 8.88, M['print_w'], rot=90, name='txt_samsung', ext=0.08)
icyl('m2_screw', 1.6, 3, 'z', sd[0] + 12.5, sd[1] + 78.5, sd_z + 1.5, M['steel'], 12)      # M.2固定ネジ(M2)

# ===== CPU水冷 ARCTIC Liquid Freezer III Pro 240: ポンプ(Ø91 × 68.5)。コールドプレートはIHS上面に接する =====
cl = lp('cooler'); cs = ls('cooler'); pcx, pcy = cl[0] + 45.5, cl[1] + cs[1] / 2      # CPU中心(=円盤中心)。ポンプ筐体は+x側に17.5mm張り出す(hose長450mmでラジエーターへ届くため。-x側はVRM/EPS、+y側はDIMM、-y側はVRMと干渉。layout: x=cl[0]..cl[0]+108.47)
pump_mat = principled('arctic_pump', '#18191c', 0.4, 0.4)
PJ = json.load(open(os.path.join(ROOT, 'model', 'pump.json')))      # ARCTIC 2D図面の実測値(単一源。tools/gen_cad_drawings.py の図面と同じ)
def pbox(name, xr, yr, zr, mat, bev=0.8): ibox(name, xr[1] - xr[0], yr[1] - yr[0], zr[1] - zr[0], pcx + xr[0], pcy + yr[0], cl[2] + zr[0], mat, bev)
def pcyl(name, d, zr, mat, cx=0.0, cy=0.0, seg=64): icyl(name, d / 2, zr[1] - zr[0], 'z', pcx + cx, pcy + cy, cl[2] + (zr[0] + zr[1]) / 2, mat, seg)
cp_ = PJ['coldplate']; pbox('pump_coldplate_sq', cp_['x'], cp_['y'], cp_['z'], M['copper'], .5)                  # 銅コールドプレート(約40.1×43.6, 中心は円盤中心から+2mm)
pbox('pump_base_block', (-PJ['base']['size'][0] / 2, PJ['base']['size'][0] / 2), (-PJ['base']['size'][1] / 2, PJ['base']['size'][1] / 2), PJ['base']['z'], pump_mat, 1.0)
for k_ in range(PJ['cage']['ribs']):      # VRMファンを囲むアーチ状リブの開放ケージ
    an_ = math.radians(k_ * 360 / PJ['cage']['ribs']); pbox(f'pump_cage_rib{k_}', (PJ['cage']['r'] * math.cos(an_) - 2, PJ['cage']['r'] * math.cos(an_) + 2), (PJ['cage']['r'] * math.sin(an_) - 2, PJ['cage']['r'] * math.sin(an_) + 2), PJ['cage']['z'], pump_mat, .8)
pcyl('pump_cap_lip', PJ['cap_lip']['d'], PJ['cap_lip']['z'], pump_mat, seg=96); pcyl('pump_cap_top', PJ['cap_top']['d'], PJ['cap_top']['z'], M['alublack'], seg=96)      # キャップ2段(リップ+トッププレート)
pbox('pump_housing_body', PJ['housing_body']['x'], PJ['housing_body']['y'], PJ['housing_body']['z'], pump_mat, 6.0); pbox('pump_elbow', PJ['elbow']['x'], PJ['elbow']['y'], PJ['elbow']['z'], pump_mat, 5.0)      # 筐体本体+エルボ状出口
make_fan('fan_pump_vrm', PJ['vrm_fan']['d'], PJ['vrm_fan']['z'][1] - PJ['vrm_fan']['z'][0], 7, M['dark'], principled('vrm_blade', '#1b1c20', 0, .45), principled('vrm_hub', '#101114', .2, .4), pcx, pcy, cl[2] + PJ['vrm_fan']['z'][0])      # VRMファン(径・中心は未確認 U58)
for k_, sy_ in enumerate(PJ['stub_y']):      # ホース口: 上面から垂直。スイベルナット(Ø20.4)+スタブ(Ø11.1)。y位置は図面の読み取り(左右ミラーは未確認)
    pcyl(f'pump_swivel_{k_}', PJ['nut']['d'], PJ['nut']['z'], M['alublack'], PJ['stub_x'], sy_, 24); pcyl(f'pump_fitting_{k_}', PJ['stub']['d'], PJ['stub']['z'], M['alublack'], PJ['stub_x'], sy_, 24)
for k_, (dx_, dy_) in enumerate(((-27, -45), (27, -45), (-27, 45), (27, 45))):            # AM5取付穴 54×90mm(AM4互換パターン, Noctua等の公開資料)。長辺(90)はポンプのホース出口方向と直交(ARCTIC 2D図面 Bottom View)。バックプレート固定: ばね付きM4 x4(基板を貫通してバックプレートへ)
    z_top_, z_bot_ = cl[2] + 14, bz - 1
    icyl(f'pump_screw{k_}', 2.0, z_top_ - z_bot_, 'z', pcx + dx_, pcy + dy_, (z_top_ + z_bot_) / 2, M['steel'], 16)      # M4軸Ø4(ばねの内径Ø5.5の内側を通る)
    icyl(f'pump_screw_head{k_}', 3.5, 2.0, 'z', pcx + dx_, pcy + dy_, z_top_ + 1.0, M['steel'], 16)      # 頭Ø7
    coil(f'pump_spring{k_}', 3.3, 1.1, 8, 4, (X0 + pcx + dx_, Y0 + pcy + dy_), Z0 - (cl[2] + 4) - 8, M['steel'], axis='z', ends=.5, per_turn=16, seg=6)      # 取付ばね(線径1.1×平均径6.6×有効4巻=典型値, ARCTIC寸法はUNVERIFIED)
for k_, (dx_, dy_) in enumerate(((-27, -45), (27, -45), (-27, 45), (27, 45))):      # VRMヒートシンクのポンプ取付ねじ逃げ(Ø9)
    _c = cyl(f'vrm_notch{k_}', 4.5, 40, 'z', X0 + pcx + dx_, Y0 + pcy + dy_, Z0 - (Z1 + 7), None, 24, body=False); _c.hide_render = True; BODY_OBJS.append(_c)
    _m = _vs.modifiers.new(f'screw_notch{k_}', 'BOOLEAN'); _m.object = _c; _m.operation = 'DIFFERENCE'; _m.solver = 'EXACT'
# ラジエーター(277x120x38) + P12 Pro x2
rx_, ry_, rz_ = lp('radiator')
ibox('rad_core', 120, 253, 38, rx_, ry_ + 12, rz_, M['rad_black'], .8)      # フィン部=全長277-タンク12×2
_cd = [c for c in json.load(open(os.path.join(ROOT, 'model', 'layout.json'))).get('candidates', []) if c['id'] == 'rad_duct'][0]; dx_, dy_, dz_ = _cd['pos']; DW_, DL_, DH_ = _cd['size']           # R10E-001: 吸気分離ダクト(板金t1.0 四方壁)。上端はドーム内面へ(ガスケット未設計)
for nm_, (bx, by, bw, bl) in ({} if not A.with_duct else {'a': (dx_, dy_, 1.0, DL_), 'b': (dx_ + DW_ - 1.0, dy_, 1.0, DL_), 'c': (dx_, dy_, DW_, 1.0), 'd': (dx_, dy_ + DL_ - 1.0, DW_, 1.0)}).items(): ibox('rad_duct_' + nm_, bw, bl, DH_, bx, by, dz_, M['alublack'], .3)
ibox('rad_tank_a', 120, 12, 38, rx_, ry_ - 0, rz_, M['alublack'], 1.5); ibox('rad_tank_b', 120, 12, 38, rx_, ry_ + 265, rz_, M['alublack'], 1.5)
for k in range(2):
    make_fan(f'fan_rad{k}', 120, 28, 7, principled('p12_frame', '#101114', 0, .45), principled('p12_blade', '#1b1c20', 0, .45), principled('p12_hub', '#101114', .2, .4), rx_ + 60, ry_ + 18.5 + 60 + k * 120, rz_ + 38, hub_k=.2375, open_k=.485)      # P12 Pro: ハブØ57(公式2D図面の概算)、開口は枠幅の約97%
def cable(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 6; cu.fill_mode = 'FULL'; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)       # cablemodelのfillet済み折れ線をそのまま使う(曲げ半径はtools/cable_check.pyで検査済)
    for p, q in zip(pts, sp.points): v = V(X0 + p[0], Y0 + p[1], Z0 - p[2]); q.co = (v.x, v.y, v.z, 1.0)
    ob = bpy.data.objects.new(name, cu); cu.materials.append(mat); return link(ob)
# ===== ライザー: LINKUP AVA5 PCIe5.0 (フラットリボン6本): 基板x16スロット -> GPUエッジ =====
def ribbon(name, pts_local, width, thick, mat):
    me = bpy.data.meshes.new(name); bmm = bmesh.new(); ctrl = [Vector(p) for p in pts_local]; n = 24; verts = []
    def bez(t):
        a_, b_, c_, d_ = ctrl; u = 1 - t
        return u ** 3 * a_ + 3 * u * u * t * b_ + 3 * u * t * t * c_ + t ** 3 * d_
    for i in range(n + 1):
        p = bez(i / n); verts.append((bmm.verts.new(V(X0 + p.x, Y0 + p.y - width / 2, Z0 - p.z)), bmm.verts.new(V(X0 + p.x, Y0 + p.y + width / 2, Z0 - p.z))))
    for i in range(n): bmm.faces.new((verts[i][0], verts[i][1], verts[i + 1][1], verts[i + 1][0]))
    bmm.to_mesh(me); bmm.free(); me.materials.append(mat); ob = bpy.data.objects.new(name, me)
    so = ob.modifiers.new('solid', 'SOLIDIFY'); so.thickness = thick; so.offset = 0
    return link(ob)
ry0, rh_ = lp('riser')[1], ls('riser')[1]
ibox('riser_plug', 6, rh_, 12, bx + 158.7, ry0, Z1 + 11, M['dark'], .4)                    # スロットに挿す側のブロック
for k in range(6):
    y0 = ry0 + 7 + k * 15
    ribbon(f'riser{k}', [(bx + 164.7, y0, Z1 + 20), (bx + 178, y0, Z1 + 26), (gx - 8, y0, gz + 16), (gx - 2, y0, gz + 5)], 12, .9, M['rubber'])
ibox('riser_gpu_conn', 6, rh_, 8, gx - 7.5, ry0, gz + 1.5, M['dark'], .4)

# ===== GPU: RTX 5070 Ti 小型2スロット (寸法基準 PNY Slim 290x150x40, 2ファン, 12V-2x6)。縦置き: 長軸=y, 出力ブラケット=下端, ファン=ドーム側 =====
gcol = principled('gpu_shroud', '#17181b', .15, .42); add_bump(gcol, 700, .02)
GW, GL, GT = ls('gpu')            # 幅(x)150 / 長さ(y)290 / 厚み(z)40
ibox('gpu_backplate', GW, GL, 1.6, gx, gy, gz, principled('gpu_backplate', '#1b1c20', .8, .4), .4)
bpc_ = ibox('gpu_bp_cutter', 90, 8, 4, gx + 30, gy + 24, gz - 1, None); bpc_.hide_render = True
ar_ = bpc_.modifiers.new('arr', 'ARRAY'); ar_.count = 16; ar_.use_relative_offset = False; ar_.use_constant_offset = True; ar_.constant_offset_displace = (0, 16, 0)
m_ = bpy.data.objects['gpu_backplate'].modifiers.new('slots', 'BOOLEAN'); m_.object = bpc_; m_.operation = 'DIFFERENCE'; m_.solver = 'MANIFOLD'
gp = os.path.join(TEXDIR, 'pcb_gpu8.png'); pcb_tex(gp, GW - 10, GL - 20, 23, '#0f1114', '#2d3239')
ibox('gpu_pcb', GW - 10, 170, 1.6, gx + 5, gy + 12, gz + 1.6, img_material('pcb_gpu8', gp, rough=.5), uv=True)      # PCB: 約140×170(実機は約170×112程度=Akiba 1件のみ=UNVERIFIED。長辺はブラケット側に寄せ、残りはヒートシンクのみ)
ry0, rh_ = lp('riser')[1], ls('riser')[1]
ibox('gpu_edge', 3, 89, 1.8, gx - 1.2, gy + 16.8, gz + 3.4, M['gold'])                  # PCIeエッジ(金メッキ)
_gfm = principled('gpu_fins', '#bfc3c9', 1.0, .38)
ibox('gpu_heatsink_base', GW - 12, GL - 40, 3, gx + 6, gy + 20, gz + 3.2, _gfm, .5)      # ベース板
for _k in range(52): ibox(f'gpu_fin{_k}', GW - 14, 0.5, 14, gx + 7, gy + 21 + _k * 5.0, gz + 12.5, _gfm, .1)      # フィンはヒートパイプ(Ø6, z6.2〜12.2)の上に載せる(貫通穴の簡略化。穴は未モデル=INTF-03で実形状化)      # フィン52枚(厚0.5・ピッチ5.0・高20)。枚数・形状は公式に無い=UNVERIFIED
for k in range(5): icyl(f'gpu_hpipe{k}', 3, GL - 60, 'y', gx + 22 + k * 25, gy + GL / 2 + 8, gz + 9.3, M['copper'], 20)      # ヒートパイプ(Ø6)をベース上面に接して通す(フィン内に埋めず、フィン高さ内で見える)
shr = ibox('gpu_shroud_body', GW, GL, 13, gx, gy, gz + 27, gcol, 2.0)
fy_list = (gy + GL / 2 - 70, gy + GL / 2 + 70, )
for k, fy_ in enumerate(fy_list):
    shc = cyl(f'gpu_fan_hole{k}', 54, 17, 'z', X0 + gx + GW / 2, Y0 + fy_, Z0 - (gz + 33.5), None, 64, body=False); shc.hide_render = True; BODY_OBJS.append(shc)
    bmx = shr.modifiers.new(f'hole{k}', 'BOOLEAN'); bmx.object = shc; bmx.operation = 'DIFFERENCE'; bmx.solver = 'EXACT'
    make_fan(f'fan_gpu{k}', 110, 8, 11, M['dark'], principled('gpu_blade', '#222428', .2, .45), principled('gpu_hub', '#2a2c31', .3, .4), gx + GW / 2, fy_, gz + 29)
    bpy.data.objects[f'fan_gpu{k}_frame'].hide_render = True
ibox('gpu_trim', GW, 1.6, 13.1, gx, gy + GL / 2, gz + 27, M['silver_trim'])             # 2基のファンの間の銀アクセント
# GPU刻印: PNY品の刻印は未確認(U46)のため描画しない(推測の作り込みを避ける)
ibox('gpu_bracket', GW, 1.5, GT + 2, gx, gy - 1.5, gz - 1, M['steel'], .3)              # 出力ブラケット(下端)
for k, (nm, w_) in enumerate((('hdmi', 15), ('dp', 16), ('dp', 16), ('dp', 16))): ibox(f'gpu_port{k}', w_, 3, 6.5, gx + 20 + k * 28, gy - 3, gz + 7, M['dark'], .3)
for k, (nm, w_) in enumerate((('hdmi', 15), ('dp', 16), ('dp', 16), ('dp', 16))):      # ブラケットのポート開口(コネクタが貫通する穴 +0.3mm/側)
    _c = cutbox(f'gpu_bracket_port{k}_cutter', gx + 20 + k * 28 - 0.3, gy - 4, gz + 7 - 0.3, w_ + 0.6, 5, 7.1)
    _m = bpy.data.objects['gpu_bracket'].modifiers.new(f'port{k}', 'BOOLEAN'); _m.object = _c; _m.operation = 'DIFFERENCE'; _m.solver = 'EXACT'
_cn = cutbox('gpu_conn_notch', gx + GW - 41, gy + GL - 23, gz + 26, 24, 11, 16); _mn = shr.modifiers.new('conn_notch', 'BOOLEAN'); _mn.object = _cn; _mn.operation = 'DIFFERENCE'; _mn.solver = 'EXACT'      # 12V-2x6がシュラウドの切欠きから出る
ibox('gpu_12v2x6', 22, 9, 10, gx + GW - 40, gy + GL - 22, gz + 30, M['dark'], .4)       # 12V-2x6コネクタ(カード上面の端, 位置は想定)

# ===== 電源: Corsair SF1000 (SFX 125x63.5x100)。ファン面を上(ドーム側)、モジュラー端子面を基板側 =====
px_, py_, pz_ = lp('psu')
# PSU本体(MDB-020/021/022): 中実の箱でなく、ファン面(上)に径88の開口を持つ殻+内部の詰め物(電源基板の代用)。ファンは開口内に収め、グリルは上面に接する。
_pb = ibox('psu_body', 125, 100, 63.5, px_, py_, pz_, M['sf_body'], 1.5)
_pc = cyl('psu_fan_opening', 44, 14.0, 'z', X0 + px_ + 62, Y0 + py_ + 50, Z0 - (pz_ + 63.5 - 5.0), None, 64, body=False)      # 開口+ファン収容空間(深さ14: 上面から内へ12mm); _pc.hide_render = True; BODY_OBJS.append(_pc)
_pm = _pb.modifiers.new('fan_opening', 'BOOLEAN'); _pm.object = _pc; _pm.operation = 'DIFFERENCE'; _pm.solver = 'EXACT'
wire = principled('psu_wire', '#2a2c31', .9, .4)
make_fan('fan_psu', 92, 8, 9, M['dark'], principled('psu_blade', '#202226', .2, .45), principled('psu_hub', '#2a2c31', .3, .4), px_ + 62, py_ + 50, pz_ + 55.0)      # ファン(厚8)を開口内に収める(上面63.5まで)
bpy.data.objects['fan_psu_frame'].hide_render = True
for k in range(1, 5): icyl(f'psu_grille_ring{k}', 9.5 * k, .5, 'z', px_ + 62, py_ + 50, pz_ + 63.75, wire, 48)      # グリル=上面に接する(面上0.5mm)
_bm = bmesh.new()
for k in range(6):
    bmesh.ops.create_cube(_bm, size=1.0, matrix=Matrix.Translation(V(X0 + px_ + 62, Y0 + py_ + 50, Z0 - (pz_ + 63.75))) @ Matrix.Rotation(math.radians(k * 30), 4, 'Y') @ Matrix.Diagonal((88, .5, .5, 1)))
_me = bpy.data.meshes.new('psu_grille_spokes'); _bm.to_mesh(_me); _bm.free(); _me.materials.append(wire); link(bpy.data.objects.new('psu_grille_spokes', _me))
ibox('psu_label', 20, 70, .3, px_ + 2, py_ + 14, pz_ + 63.5, M['sf_label'])     # 仕様ラベル: グリル(x16〜108)の外=左端の帯へ移動(内容は未確認のため無地)
# モジュラーソケット(MDB-023/MDC-001): 個数・配置はCorsair公式図が未取得(U59)で確認できない。従来の「2段×5列の10個」は根拠が無く、ATX24(幅約50mm)や12V-2x6(幅約22mm)のプラグが入らない寸法だった。
# ケーブルがつながる4口だけを、プラグ(ATX24 50x10 / EPS 25x18 / 12V-2x6 22x10 / SATA電源 17x6: 各規格の外形)が入る最小寸法で置く。他のソケットは未モデル(UNVERIFIED)。
for _i, (_cx, _w, _h, _zc) in enumerate(((28, 52.0, 11.0, 30.0), (69, 26.0, 19.0, 30.0), (96, 24.0, 11.0, 30.0), (50, 19.0, 7.0, 16.0))):      # (PSU内x, 幅, 高さ(z方向), 中心z)
    ibox(f'psu_socket{_i}', _w, 6, _h, px_ + _cx - _w / 2, py_ - 4, pz_ + _zc - _h / 2, M['rubber'], .4)
# ===== パネル用コントローラ基板(4K eDP, 150x55 横置き。型番未確定) =====
cx_, cy_, cz_ = lp('ctrl_board')
cp = os.path.join(TEXDIR, 'pcb_ctrl.png'); pcb_tex(cp, 55, 150, 41, '#16222b', '#2a3d4c', '4K eDP ctrl')
ibox('ctrl_pcb', ls('ctrl_board')[0], ls('ctrl_board')[1], 1.6, cx_, cy_, cz_, img_material('pcb_ctrl', cp, rough=.5), uv=True)
ibox('ctrl_hdmi', 15, 6.5, 6, cx_ + 8, cy_ + 1, cz_ + 1.6, M['steel']); ibox('ctrl_dp', 17, 6.5, 6, cx_ + 28, cy_ + 1, cz_ + 1.6, M['steel'])
ibox('ctrl_soc', 14, 14, 1.4, cx_ + 20, cy_ + 50, cz_ + 1.6, M['chip']); ibox('ctrl_edp_conn', 20, 4, 4, cx_ + 18, cy_ + ls('ctrl_board')[1] - 8, cz_ + 1.6, M['dark'])
for k in range(3): icyl(f'ctrl_cap{k}', 4, 9, 'z', cx_ + 12 + k * 14, cy_ + 80, cz_ + 1.6 + 4.5, M['cap'], 20)
for k in range(2): ibox(f'ctrl_coil{k}', 9, 9, 7, cx_ + 10 + k * 18, cy_ + 28, cz_ + 1.6, M['alublack'], .5)

# ===== ACインレット(C14, 下辺左。ソケットは下向き=ドーム下辺の開口へ) =====
ibox('ac_inlet_body', 28, 26, 20, ax_, ay_, az_, principled('c14', '#1b1c20', 0, .5), .6); ibox('ac_inlet_flange', 36, 3, 28, ax_ - 4, ay_ - 2, az_ - 4, M['steel'], .3)
ibox('ac_inlet_socket', 22, 1, 15, ax_ + 3, ay_ - 2.5, az_ + 2.5, M['dark'])
# ===== 配線・ホース: model/cables.json(tools/cablemodel.py が生成, tools/cable_check.py で干渉/曲げ/長さ検査済)から描画。各ケーブルは独立オブジェクト =====
CABJ = json.load(open(os.path.join(ROOT, 'model', 'cables.json')))['cables']
CMAT = {'rubber': M['rubber'], 'hose': M['hose'], 'umb': principled('umb', '#c9ced6', 0, .5)}
for c_ in CABJ: cable('cable_' + c_['id'], [tuple(q) for q in c_['path']], c_['od'] / 2, CMAT[c_['mat']])
_PM = {'plug_white': principled('plug_white', '#e9e8e2', 0, .5), 'plug_black': principled('plug_black', '#17181b', 0, .55), 'alublack': M['alublack']}
for pl_ in json.load(open(os.path.join(ROOT, 'model', 'cables.json'))).get('plugs', []):      # ケーブル端のプラグ/ホース口(INTF/MDC-001対応)
    x0_, y0_, z0_, w_, d_, h_ = pl_['box']; nm_ = ('rad_port_' if pl_['id'].startswith('RAD_') else 'cable_plug_') + pl_['id']
    if pl_.get('shape') == 'cyl': icyl(nm_, w_ / 2, h_, 'z', x0_ + w_ / 2, y0_ + d_ / 2, z0_ + h_ / 2, _PM[pl_['color']], 24)
    else: ibox(nm_, w_, d_, h_, x0_, y0_, z0_, _PM[pl_['color']], .8)

exec(open(os.path.join(HERE, 'hardware_v8.py'), encoding='utf-8').read())      # 小部品(ばね/ネジ/ラッチ/ヒンジ機構等)

# ---------------- アセンブリ(部品群)ごとにグルーピング: 各ファン/ポンプ/ラジエーター/GPU/PSU/基板/SSD/ctrl/AC/ケーブル/ヒンジ/スタンド/ドーム/トレイ/表示部を独立した親にする ----------------
ASM = [('ASM_stand_neck', ('stand_arm', 'stand_neck', 'stand_swivel_rotor', 'stand_swivel_bearing_inner', 'stand_swivel_friction', 'stand_swivel_bolt0', 'stand_swivel_bolt1', 'stand_swivel_bolt2', 'stand_swivel_bolt3', 'stand_swivel_bolt4', 'stand_swivel_bolt5', 'stand_swivel_stop_tab', 'pe_braid_swivel', 'hinge_friction', 'spring_die', 'spring_guide', 'spring_seat_bot', 'stand_anchor', 'hinge_stopper_dn', 'hinge_stopper_up')),
       ('ASM_fan_gpu0', ('fan_gpu0',)), ('ASM_fan_gpu1', ('fan_gpu1',)), ('ASM_fan_rad0', ('fan_rad0',)), ('ASM_fan_rad1', ('fan_rad1',)), ('ASM_fan_psu', ('fan_psu',)), ('ASM_fan_pump_vrm', ('fan_pump_vrm',)),
       ('ASM_dome', ('power_button', 'cover_', 'gasket', 'latch_', 'hook_', 'magnet', 'dowel_', 'rf_window', 'antenna')),
       ('ASM_tray', ('tray_', 'hang_', 'standoff_', 'screw_', 'pe_stud', 'pe_nut', 'pe_braid_tray', 'clip_', 'gpu_cradle')),
       ('ASM_gpu', ('gpu_', 'riser')), ('ASM_aio_pump', ('pump_',)), ('ASM_aio_rad', ('rad_',)), ('ASM_psu', ('psu_',)),
       ('ASM_ssd', ('ssd_', 'txt_samsung', 'm2_screw')), ('ASM_ctrl', ('ctrl_',)), ('ASM_ac_inlet', ('ac_inlet',)), ('ASM_cables', ('cable_',)),
       ('ASM_hinge', ('hinge_axle', 'hinge_eclip', 'hinge_block', 'hinge_cheek', 'hinge_cover', 'hinge_backing', 'hinge_doubler', 'hinge_bolt', 'hinge_friction', 'hinge_cam', 'hinge_stopper', 'spring_', 'pe_braid_hinge')),
       ('ASM_stand_fixed', ('stand_', 'hinge_axle', 'hinge_eclip')),
       ('ASM_display', ('slab', 'front_glass', 'display', 'chin_print', 'camera', 'mic')),
       ('ASM_board', ('board_', 'io_', 'vrm_', 'choke', 'cap', 'socket', 'cpu_', 'txt_', 'dimm', 'atx24', 'eps8', 'pcie_', 'chipset', 'm2_', 'am5_'))]
FIXED = ('ASM_stand_fixed', 'ASM_stand_neck')      # ネックは頭部とチルトしないが、首振りでは回る
_asm = {}
for ob in list(COLL.objects):
    if ob.parent is not None or ob.name.startswith('ASM_') or ob.name in ('floor', 'target', 'cam', 'key', 'back_key'): continue
    for an, pre in ASM:
        if ob.name.startswith(pre):
            if an not in _asm:
                e = bpy.data.objects.new(an, None); e.empty_display_type = 'PLAIN_AXES'; e.empty_display_size = 5; link(e, body=(an not in FIXED)); _asm[an] = e
            ob.parent = _asm[an]; break

# ---------------- 分解(Explode)・チルト ----------------
def shift_group(prefix_list, dz_):
    for ob in list(COLL.objects):
        if any(ob.name.startswith(p) for p in prefix_list): ob.location += Vector((0, dz_, 0))
if A.explode > 0:
    e = A.explode
    shift_group(['cover_back', 'cover_filter', 'gasket'], 620 * e); shift_group(['fan_exhaust'], 440 * e); shift_group(['pump', 'hose', 'rad', 'fan_rad', 'txt_arctic', 'txt_ihs'], 330 * e)
    shift_group(['ac_inlet', 'cable_ac'], 260 * e); shift_group(['gpu', 'fan_gpu', 'cable_pcie8', 'txt_gpu', 'riser'], 210 * e); shift_group(['psu', 'fan_psu', 'cable_atx24', 'cable_eps', 'txt_sf', 'txt_plat'], 140 * e)
    shift_group(['ssd', 'txt_samsung', 'm2_screw'], 110 * e); shift_group(['ctrl_', 'cable_ctrl', 'cable_umb'], 80 * e)
    shift_group(['slab', 'front_glass', 'display', 'chin_print', 'camera', 'mic', 'power_button'], -300 * e)      # 前面(ディスプレイ)は前方へ
if A.only:
    _pf = tuple(s_ for s_ in A.only.split(',') if s_)
    for ob in COLL.objects:
        if ob.type in ('MESH', 'CURVE', 'FONT') and not ob.name.startswith(_pf): ob.hide_render = True
if A.open_stand:
    for ob in COLL.objects:
        if ob.name.startswith(('stand_skirt', 'stand_neck_collar', 'stand_neck_shroud', 'stand_neck_cover', 'hinge_cover', 'hinge_boot')) and not ob.name.endswith('_hole'): ob.hide_render = True
if A.cut and A.explode == 0:
    for ob in COLL.objects:
        if ob.name.startswith(('cover_back', 'cover_filter', 'gasket')): ob.hide_render = True
PIV = bpy.data.objects.new('tilt_pivot', None); COLL.objects.link(PIV); PIV.location = V(0, S['hinge']['axis_y'], ZC); bpy.context.view_layer.update()
for ob in COLL.objects:
    if ob in BODY_OBJS and ob.parent is None:
        ob.parent = PIV; ob.matrix_parent_inverse = PIV.matrix_world.inverted()
PIV.rotation_euler = (-math.radians(A.tilt), 0, 0)   # +tiltで上端が後ろへ(Blender +Y=背面): X軸まわり -θ
# 首振り(垂直軸=設計y軸=Blender Z): 頭部(PIV)とネック一式が回る。足・ステータ・軸受は固定。+swivelで画面が右へ向く
SWIV = bpy.data.objects.new('swivel_pivot', None); COLL.objects.link(SWIV); SWIV.location = V(0, -DROP, ZC); bpy.context.view_layer.update()
for o_ in [PIV] + [x for x in COLL.objects if x.name == 'ASM_stand_neck']:
    mw = o_.matrix_world.copy(); o_.parent = SWIV; o_.matrix_world = mw
SWIV.rotation_euler = (0, 0, math.radians(A.swivel))

# ファン回転 (フレーム数指定時はアニメーション)
for k, r in enumerate(rotors):
    r.rotation_euler = (0, A.phase * 2 + k * .6, 0)
    if A.frames > 0:
        scene.frame_start, scene.frame_end = 1, A.frames
        for f, ang in ((1, A.phase * 2), (A.frames + 1, A.phase * 2 + (math.pi * 2) * (1 if 'cpu' in r.name else 1.4))):
            r.rotation_euler[1] = ang + k * .6; r.keyframe_insert('rotation_euler', index=1, frame=f)

if A.debug_keyhole:
    from mathutils.bvhtree import BVHTree
    dg_ = bpy.context.evaluated_depsgraph_get()
    for nm_ in ('tray_plate', 'tray_insulation'):
        ob_ = bpy.data.objects[nm_]; ev_ = ob_.evaluated_get(dg_); me_ = ev_.to_mesh(); me_.transform(ob_.matrix_world)
        tr_ = BVHTree.FromPolygons([v.co.copy() for v in me_.vertices], [tuple(p.vertices) for p in me_.polygons], epsilon=1e-4)
        for (kx_, ky_) in KH:
            for lab_, dy_ in (('頭穴中心', 0.0), ('溝中央', 6.0), ('ピン位置', 12.0), ('溝の外(+20)', 20.0)):
                px_, pz_ = X0 + kx_, Y0 + ky_ + dy_
                hit_ = tr_.ray_cast(Vector((px_, 100.0, pz_)), Vector((0, -1, 0)))      # 設計+z(背面)側から前面方向へ
                print('KHDBG', nm_, (kx_, ky_), lab_, 'hit_y=', None if hit_[0] is None else round(hit_[0].y, 2))
        ev_.to_mesh_clear()
    sys.exit(0)
# ---------------- 実形状の干渉検査(INTF-01): 評価済みメッシュ(モディファイア適用後)のBVH交差 ----------------
if A.check_interference:
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get(); recs = []
    for ob in COLL.objects:
        if ob.type != 'MESH' or ob.hide_render or ob.name.startswith(('floor', 'target')) or ob.name.endswith(('_hole', '_cutter', '_cavity', '_notch', '_opening')) or '_cutter' in ob.name: continue      # ブーリアン用カッターは形状ではないので検査しない
        ev = ob.evaluated_get(dg); me_ = ev.to_mesh(); me_.transform(ob.matrix_world)
        vs = [v.co.copy() for v in me_.vertices]; ps = [tuple(p.vertices) for p in me_.polygons]
        if len(vs) < 3 or not ps: ev.to_mesh_clear(); continue
        xs = [v.x for v in vs]; ys = [v.y for v in vs]; zs = [v.z for v in vs]
        recs.append((ob.name, (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)), BVHTree.FromPolygons(vs, ps, epsilon=1e-4))); ev.to_mesh_clear()
    recs.sort(key=lambda r: r[1][0]); out = []; n_ = len(recs)
    for i in range(n_):
        ni, bi, ti = recs[i]
        for j in range(i + 1, n_):
            nj, bj, tj = recs[j]
            if bj[0] > bi[3]: break
            if bj[1] > bi[4] or bi[1] > bj[4] or bj[2] > bi[5] or bi[2] > bj[5]: continue
            ov = ti.overlap(tj)
            if ov: out.append({'a': ni, 'b': nj, 'tri_pairs': len(ov), 'aabb_overlap_mm': [round(min(bi[3], bj[3]) - max(bi[0], bj[0]), 3), round(min(bi[4], bj[4]) - max(bi[1], bj[1]), 3), round(min(bi[5], bj[5]) - max(bi[2], bj[2]), 3)]})
    json.dump({'objects': n_, 'pairs': sorted(out, key=lambda r: -r['tri_pairs'])}, open(A.check_interference, 'w'), ensure_ascii=False, indent=1)
    print('INTERFERENCE objects', n_, 'overlapping pairs', len(out)); sys.exit(0)
# ---------------- GLB書き出し(床・照明・カメラを足す前。非表示のブール用カッターは除外) ----------------
if A.export:
    bpy.ops.export_scene.gltf(filepath=A.export, export_format='GLB', export_apply=True, use_renderable=True, export_animations=False)


# ---------------- 写実化パス(レンダリング専用。GLB書き出しの後なのでGLBには影響しない) ----------------
def realify():
    for m in bpy.data.materials:
        if not m.use_nodes or m.name in ('floor',) or 'Principled BSDF' not in m.node_tree.nodes: continue
        nt = m.node_tree; b = nt.nodes['Principled BSDF']
        emissive = b.inputs['Emission Strength'].default_value > 0.01 or m.name == 'display'
        if not emissive:      # (1) 微小ベベル: エッジにハイライトが乗り、CGの鋭利さが消える
            bv = nt.nodes.new('ShaderNodeBevel'); bv.samples = 6; bv.inputs['Radius'].default_value = 0.35
            lk = b.inputs['Normal'].links
            if lk and lk[0].from_node.type == 'BUMP': nt.links.new(bv.outputs['Normal'], lk[0].from_node.inputs['Normal'])
            elif not lk: nt.links.new(bv.outputs['Normal'], b.inputs['Normal'])
        if b.inputs['Metallic'].default_value >= 0.6 and not b.inputs['Roughness'].links:      # (2) 金属の粗さムラ(加工痕/指紋の薄いムラ)
            r0 = b.inputs['Roughness'].default_value
            tc = nt.nodes.new('ShaderNodeTexCoord'); no = nt.nodes.new('ShaderNodeTexNoise'); mr = nt.nodes.new('ShaderNodeMapRange')
            no.inputs['Scale'].default_value = 0.06; no.inputs['Detail'].default_value = 5; no.inputs['Roughness'].default_value = 0.6
            mr.inputs['To Min'].default_value = max(0.05, r0 - 0.07); mr.inputs['To Max'].default_value = r0 + 0.09
            nt.links.new(tc.outputs['Object'], no.inputs['Vector']); nt.links.new(no.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
realify() if not A.flat else None

# ---------------- 環境 / カメラ / レンダー ----------------
floor = bpy.data.objects.new('floor', bpy.data.meshes.new('floor'))
bmf = bmesh.new(); bmesh.ops.create_grid(bmf, x_segments=1, y_segments=1, size=6000); bmf.to_mesh(floor.data); bmf.free()
floor.location = V(0, -DROP - 12.0, 0); COLL.objects.link(floor)      # 足底(y=-DROP-12)に接する
if A.flat:
    floor.data.materials.append(principled('floor', '#e9ebef', 0, .9)); floor.is_shadow_catcher = True
else:    # 半光沢の床: 製品の映り込み+接地影。遠方は背景色へ溶け込ませて水平線を消す
    fm = principled('floor', '#e4e6ec', 0, .30); fnt = fm.node_tree; fb = fnt.nodes['Principled BSDF']
    ftc = fnt.nodes.new('ShaderNodeTexCoord'); fvl = fnt.nodes.new('ShaderNodeVectorMath'); fvl.operation = 'LENGTH'; fmr = fnt.nodes.new('ShaderNodeMapRange')
    fmr.inputs['From Min'].default_value = 1300; fmr.inputs['From Max'].default_value = 5200; fmr.interpolation_type = 'SMOOTHSTEP'
    ftr = fnt.nodes.new('ShaderNodeBsdfTransparent'); fms = fnt.nodes.new('ShaderNodeMixShader'); fout = fnt.nodes['Material Output']
    fnt.links.new(ftc.outputs['Object'], fvl.inputs[0]); fnt.links.new(fvl.outputs['Value'], fmr.inputs['Value']); fnt.links.new(fmr.outputs['Result'], fms.inputs['Fac'])
    fnt.links.new(fb.outputs['BSDF'], fms.inputs[1]); fnt.links.new(ftr.outputs['BSDF'], fms.inputs[2]); fnt.links.new(fms.outputs['Shader'], fout.inputs['Surface'])    # 遠方は透明にして背景(world)へ溶け込ませる
    floor.data.materials.append(fm)
wd = bpy.data.worlds.new('studio'); wd.use_nodes = True; wnt = wd.node_tree; bg = wnt.nodes['Background']; scene.world = wd
tcw = wnt.nodes.new('ShaderNodeTexCoord'); spw = wnt.nodes.new('ShaderNodeSeparateXYZ'); cr = wnt.nodes.new('ShaderNodeValToRGB')
wnt.links.new(tcw.outputs['Generated'], spw.inputs['Vector']); wnt.links.new(spw.outputs['Z'], cr.inputs['Fac'])
cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = hexc('#c3c7d1' if A.flat else '#cfd3dc'); cr.color_ramp.elements[1].position = 0.85; cr.color_ramp.elements[1].color = hexc('#ffffff')
e = cr.color_ramp.elements.new(0.5); e.color = hexc('#e6e9f0')
wnt.links.new(cr.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 1.05
def sun(name, rot, energy, color='#fff7ee', angle=4):
    l = bpy.data.lights.new(name, 'SUN'); l.energy = energy; l.angle = math.radians(angle); l.color = hexc(color)[:3]
    o = bpy.data.objects.new(name, l); o.rotation_euler = rot; COLL.objects.link(o)
sun('key', (math.radians(52), 0, math.radians(35)), 2.3); sun('back_key', (math.radians(58), 0, math.radians(215)), 1.8, '#f3f6ff', 6)
def area(name, loc, size, power, color='#ffffff'):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = power; l.size = size; l.color = hexc(color)[:3]
    o = bpy.data.objects.new(name, l); o.location = loc; COLL.objects.link(o)
    tr = o.constraints.new('TRACK_TO'); tr.target = TGT; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
def softbox(name, loc, w, h, strength, color='#ffffff'):      # 発光する大きな面光源: 金属/ガラスにスタジオ風の映り込みを作る。カメラには映らない
    me = bpy.data.meshes.new(name); bm_ = bmesh.new(); bmesh.ops.create_grid(bm_, x_segments=1, y_segments=1, size=0.5); bm_.to_mesh(me); bm_.free()
    o = bpy.data.objects.new(name, me); o.scale = (w, h, 1); o.location = loc; COLL.objects.link(o)
    mt = bpy.data.materials.new(name); mt.use_nodes = True; nb = mt.node_tree.nodes['Principled BSDF']
    nb.inputs['Base Color'].default_value = (0, 0, 0, 1); nb.inputs['Emission Color'].default_value = hexc(color); nb.inputs['Emission Strength'].default_value = strength
    me.materials.append(mt); o.visible_camera = False; o.visible_shadow = False
    tr = o.constraints.new('TRACK_TO'); tr.target = TGT; tr.track_axis = 'TRACK_Z'; tr.up_axis = 'UP_Y'
TGT = bpy.data.objects.new('target', None); TGT.location = V(0, 190, -40); COLL.objects.link(TGT)
cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 70; cam_d.clip_start = 10; cam_d.clip_end = 20000; cam_d.sensor_width = 36
cam = bpy.data.objects.new('cam', cam_d); COLL.objects.link(cam); scene.camera = cam
tt = cam.constraints.new('TRACK_TO'); tt.target = TGT; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
if not A.flat:
    D_ = 2300; ty_ = TGT.location.z      # ソフトボックス(リング配置): 左右の縦長ストリップ、天面の大型、背後のリム
    softbox('sb_top', V(0, 1900, -45), 2200, 1400, 9.0); softbox('sb_l', V(-D_, 420, -300), 520, 1500, 14.0, '#fff4e6'); softbox('sb_r', V(D_, 380, -200), 520, 1500, 11.0, '#eaf1ff')
    softbox('sb_front', V(500, 350, 2300), 1500, 900, 5.0); softbox('sb_back', V(-400, 400, -2400), 1500, 900, 6.0); softbox('sb_rim', V(1700, 700, -1900), 400, 1200, 18.0, '#f2f6ff')
k = 1.0 if A.panel == 24 else 1.18
VIEWS = {'front': ((560, 330, 1900), (0, 205, -30)), 'back': ((-700, 330, -1950), (0, 200, -45)), 'side': ((1900, 270, -80), (0, 190, -45)),
         'inside': ((40, 215, -1380), (0, 205, -45)), 'top': ((0, 1600, -60), (0, 100, -45)), 'closeup': ((-330, 200, -560), (-205, 120, -40)), 'io': ((-820, 120, -430), (-250, 70, -40)),
         'detail_front': ((250, 250, 700), (0, 140, 0)), 'explode': ((-3300, 650, -1500), (0, 150, -330))}
if A.view in ('closeup', 'io'): k = 1.0
vp, vt = VIEWS[A.view]; cam.location = V(vp[0] * k, vp[1] * k, vp[2] * k); TGT.location = V(*vt)
if A.focus:   # 内部座標(x,y,z)を注視し、背面側から az/el で周回(az=0: 真後ろ)
    fx_, fy_, fz_ = [float(v) for v in A.focus.split(',')]; t3 = Vector((X0 + fx_, Y0 + fy_, Z0 - fz_))
    az_, el_ = math.radians(A.az), math.radians(A.el)
    c3 = t3 + Vector((A.dist * math.sin(az_) * math.cos(el_), A.dist * math.sin(el_), -A.dist * math.cos(az_) * math.cos(el_)))
    cam.location = V(c3.x, c3.y, c3.z); TGT.location = V(t3.x, t3.y, t3.z)
cam_d.lens = A.lens
if not A.flat and A.view not in ('inside', 'explode', 'top') and not A.focus:      # 被写界深度(軽め: f/9)でカメラ写真らしく
    cam_d.dof.use_dof = True; cam_d.dof.focus_object = TGT; cam_d.dof.aperture_fstop = 9.0
r = scene.render; r.engine = 'CYCLES'; w_, h_ = [int(x) for x in A.res.split('x')]; r.resolution_x, r.resolution_y, r.resolution_percentage = w_, h_, 100
cy = scene.cycles; cy.device = 'CPU'; cy.samples = A.samples; cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'; cy.max_bounces = 12; cy.glossy_bounces = 8 if hasattr(cy, 'glossy_bounces') else 8; cy.transparent_max_bounces = 16
cy.preview_samples = 16
if A.flat: scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'; scene.view_settings.exposure = -0.35
else:
    try: scene.view_settings.view_transform = 'AgX'
    except Exception: scene.view_settings.view_transform = 'Standard'
    try: scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    scene.view_settings.exposure = -0.6
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGB'
os.makedirs(os.path.dirname(A.out), exist_ok=True)
if A.save_blend: bpy.ops.wm.save_as_mainfile(filepath=A.save_blend)
if A.frames > 0:
    r.image_settings.file_format = 'PNG'; r.filepath = A.out.replace('.png', '_')
    bpy.ops.render.render(animation=True)
else:
    r.filepath = A.out; bpy.ops.render.render(write_still=True)
print('DONE', A.out)
