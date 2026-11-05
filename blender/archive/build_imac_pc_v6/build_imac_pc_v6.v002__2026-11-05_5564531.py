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
ap.add_argument('--cut', action='store_true'); ap.add_argument('--tilt', type=float, default=0)
ap.add_argument('--explode', type=float, default=0); ap.add_argument('--phase', type=float, default=0.3)
ap.add_argument('--panel', type=int, default=S['panel_size']); ap.add_argument('--save-blend', default='')
ap.add_argument('--export', default=''); ap.add_argument('--focus', default=''); ap.add_argument('--dist', type=float, default=500); ap.add_argument('--az', type=float, default=0); ap.add_argument('--el', type=float, default=20); ap.add_argument('--lens', type=float, default=70); ap.add_argument('--frames', type=int, default=0)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
A = ap.parse_args(argv)

# ---------------- 寸法 ----------------
PW, PH = S['panels'][str(A.panel)]['w'], S['panels'][str(A.panel)]['h']
BEZ, CHIN, SLAB = (S['bezel'] if A.panel == 27 else 10), S['chin'], S['slab_t']
W = S['body_w'] if A.panel == 27 else 547.0
H = PH + BEZ + CHIN
POD_T, POD_H, WALL = S['pod']['total_t'], S['pod']['h'], S['pod']['wall']
POD_W = W - S['pod']['side_margin']
IN_W, IN_D = POD_W - 2 * WALL, POD_T - SLAB - WALL
ST_W, DROP, FOOT = S['stand']['w'], S['stand']['drop'], S['stand']['foot_depth']
ZC = -(SLAB + POD_T) / 2
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

def smooth(ob, bevel=0.0, seg=2, curved=False):
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
    w, h = 2560, 1440
    img = Image.new('RGB', (w, h)); px = img.load()
    c0, c1 = [tuple(int(x[i:i + 2], 16) for i in (1, 3, 5)) for x in (light, base)]
    c0 = tuple(min(255, int(v * 1.12 + 10)) for v in c1); c1 = tuple(int(v * .55) for v in c1)
    for y in range(h):
        for x in range(0, w, 1):
            t = (x / w * .55 + y / h * .45); px[x, y] = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(over)
    for i in range(9):
        cx = 150 + i * 300; d.rounded_rectangle((cx - 120, -300, cx + 120, h + 300), 120, fill=(255, 255, 255, 70 if i % 2 else 30))
    over = over.rotate(-12, resample=Image.BICUBIC, center=(w / 2, h / 2)).filter(ImageFilter.GaussianBlur(26))
    img = Image.alpha_composite(img.convert('RGBA'), over).convert('RGB'); d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle((0, 0, w, 34), fill=(255, 255, 255, 120)); d.rounded_rectangle((w / 2 - 340, h - 120, w / 2 + 340, h - 36), 36, fill=(255, 255, 255, 110))
    for i in range(9): d.rounded_rectangle((w / 2 - 310 + i * 72, h - 108, w / 2 - 258 + i * 72, h - 56), 12, fill=(255, 255, 255, 180))
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
M['chin'] = principled('painted_chin', chin_c, 0.0, 0.28, coat=1.0, coat_rough=0.04)
M['glass'] = principled('front_glass', '#EDEEF0', 0.0, 0.06, coat=1.0, coat_rough=0.02)
M['screen'] = img_material('display', wp, emission=True, strength=0.65)
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
box('slab', W, H, SLAB, -W / 2, 0, -SLAB, M['body'], bevel=2.5)
box('front_glass', W - 0.6, H - 0.6, 1.2, -W / 2 + .3, .3, -0.6, M['glass'], bevel=0.5)
box('display', PW, PH, 0.2, -PW / 2, CHIN, 0.62, M['screen'], uv=True)
box('chin_paint', W - 5, CHIN - 4, 0.2, -W / 2 + 2.5, 2, 0.62, M['chin'])
cyl('camera', 1.8, 0.4, 'z', 0, H - 5, 0.75, M['black'], 24)
for sx in (-1, 1): cyl('mic', 0.55, 0.3, 'z', sx * 70, H - 5, 0.72, M['black'], 12)

# ---------------- 内部部品 ----------------
rotors = []
def make_fan(name, size, depth, n, frame_mat, blade_mat, hub_mat, cx, cy, czl):
    """内部座標 (cx,cy,czl)=ファン底面中心。軸=背面方向(+z local)。"""
    wc = Vector((X0 + cx, Y0 + cy, Z0 - czl - depth / 2))     # 設計図座標での体積中心
    fr = box(name + '_frame', size, size, depth, wc.x - size / 2, wc.y - size / 2, wc.z - depth / 2, frame_mat, bevel=1.2)
    cut = cyl(name + '_hole', size * .46, depth + 2, 'z', wc.x, wc.y, wc.z, None, 64, body=False); cut.hide_render = True; BODY_OBJS.append(cut)
    bm = fr.modifiers.new('hole', 'BOOLEAN'); bm.object = cut; bm.operation = 'DIFFERENCE'; bm.solver = 'EXACT'
    rotor = bpy.data.objects.new(name + '_rotor', None); rotor.location = V(wc.x, wc.y, wc.z); link(rotor)
    hub = cyl(name + '_hub', size * .19, depth * .7, 'z', wc.x, wc.y, wc.z, hub_mat, 48); hub.parent = rotor; hub.location = (0, 0, 0)
    hub.rotation_euler = (math.pi / 2, 0, 0)
    L = size * .46 - size * .17 - 1; R0 = size * .17
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
def dome_shell():
    cx, cy = DOME_X0 + DOME_W / 2, DOME_Y0 + DOME_H / 2
    a0, b0, r0 = DOME_W / 2, DOME_H / 2, DM['corner_r']
    me = bpy.data.meshes.new('cover_back'); bm = bmesh.new(); rings = []
    insets = [0, 0] + [DM['run'] * (k / 12) for k in range(1, 13)]
    for i, ins in enumerate(insets):
        dep = 0 if i == 0 else d_inner(ins) + WALL
        rr = max(r0 - ins * 0.85, 6)
        ring = [bm.verts.new(V(cx + px, cy + py, -SLAB - dep)) for (px, py) in rrect(a0 - ins, b0 - ins, rr)]
        rings.append(ring)
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for j in range(n):
            k = (j + 1) % n; bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('cover_back', me); me.materials.append(M['body'])
    so = ob.modifiers.new('wall', 'SOLIDIFY'); so.thickness = WALL * 0.8; so.offset = 1
    for p in me.polygons: p.use_smooth = len(p.vertices) == 4      # 平坦部(ngon)はフラット
    link(ob)
    # 法線が背面(-設計z = Blender +Y)を向くことを保証
    if sum(p.normal.y for p in me.polygons) < 0:
        for p in me.polygons: p.flip()
        me.update()
    return ob
dome = dome_shell()
# 吸排気の六角配列穴(ドーム平坦部〜傾斜部)。ゾーンは内部座標(x0,y0,x1,y1): 水冷ラジエーター上、ケースファン上、GPUファン上
def vent_cutter(name, zones, step=7.0, hr=2.1, margin=22):
    bmc = bmesh.new()
    for (zx0, zy0, zx1, zy1) in zones:
        zx0, zy0 = max(zx0, margin), max(zy0, margin); zx1, zy1 = min(zx1, IW_ - margin), min(zy1, IH_ - margin)
        row = 0; y_ = zy0
        while y_ <= zy1:
            x_ = zx0 + (step / 2 if row % 2 else 0)
            while x_ <= zx1:
                bmesh.ops.create_cone(bmc, cap_ends=True, segments=10, radius1=hr, radius2=hr, depth=DOME_DEPTH + 10,
                                      matrix=Matrix.Translation(V(X0 + x_, Y0 + y_, Z0 - DOME_DEPTH / 2)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
                x_ += step
            y_ += step * .87; row += 1
    me = bpy.data.meshes.new(name); bmc.to_mesh(me); bmc.free()
    ob = bpy.data.objects.new(name, me); ob.hide_render = True; link(ob); return ob
LAY = {i['id']: i for i in json.load(open(os.path.join(ROOT, 'model', 'layout.json')))['items']}
def lp(k): return LAY[k]['pos']
def ls(k): return LAY[k]['size']
rx, ry, _ = lp('radiator'); fx, fy, _ = lp('fan'); gx, gy, gz = lp('gpu')
vc = vent_cutter('cover_vents', [(rx + 4, ry + 4, rx + 116, ry + 273), (fx + 4, fy + 4, fx + 116, fy + 116), (gx + 20, gy + 15, gx + 100, gy + 215)])
# 外周のI/O・GPU出力の開口(ドーム傾斜壁を貫通)
bx, by, bz = lp('board')
def cutbox(name, x0, y0, z0, w, h, d):
    c = ibox(name, w, h, d, x0, y0, z0, None); c.hide_render = True; BODY_OBJS.append(c); return c
c_io = cutbox('cover_io_cutter', bx + 12, -20, 2, 120, bz + 60 + 40, 52)
c_gpu = cutbox('cover_gpu_cutter', gx + 4, -20, 2, 112, gy + 6 + 20, 52)
for nm, c in (('vents', vc), ('io', c_io), ('gpu', c_gpu)):
    m_ = dome.modifiers.new(nm, 'BOOLEAN'); m_.object = c; m_.operation = 'DIFFERENCE'; m_.solver = 'MANIFOLD'
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
# スタンド
box('stand_arm', ST_W, DROP - 6, 8, -ST_W / 2, -DROP, ZC - 4, M['stand'], bevel=2)
box('stand_foot', ST_W, 6, FOOT, -ST_W / 2, -DROP - 6, ZC - FOOT / 2, M['stand'], bevel=2.2, body=False)
cyl('hinge', 11, ST_W + 2, 'x', 0, -14, ZC, M['steel'], 64, body=False)
box('stand_power_recess', 12, 26, 0.5, -6, -DROP * .55 - 13, ZC + 3.9, M['dark'], bevel=3)
ARM_OBJ = bpy.data.objects['stand_arm']; BODY_OBJS.remove(ARM_OBJ)

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

# ---- サービストレイ(A5052 t2.0, 角丸) + キーホール吊りピン + 拘束ネジ ----
def tray():
    cx, cy = X0 + IW_ / 2, Y0 + IH_ / 2; me = bpy.data.meshes.new('tray'); bm = bmesh.new()
    pts = rrect(IW_ / 2 - 2, IH_ / 2 - 2, 18, 8)
    f = bm.faces.new([bm.verts.new(V(cx + px, cy + py, Z0 - 1.0)) for (px, py) in pts]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('tray_plate', me); me.materials.append(principled('tray_alu', '#8d9198', 1.0, 0.42))
    so = ob.modifiers.new('t', 'SOLIDIFY'); so.thickness = 2.0; so.offset = 1
    return link(ob)
tray()
for k, (px_, py_) in enumerate([(60, 60), (555, 60), (60, 210), (555, 310)]):
    icyl(f'keyhole_pin{k}', 1.75, 8, 'z', px_, py_, 0.5, M['steel'], 20); icyl(f'keyhole_head{k}', 3.5, 1.2, 'z', px_, py_, 0.6, M['steel'], 24)
    icyl(f'keyhole_slot{k}', 5.0, .3, 'z', px_, py_, 3.15, M['rubber'], 24)
for k, sx_ in enumerate((-60, 60)):
    icyl(f'tray_screw{k}', 3.2, 3.0, 'z', IW_ / 2 + sx_, 14, 3.0 + 1.5, M['alublack'], 24); icyl(f'tray_screw_hex{k}', 1.6, .3, 'z', IW_ / 2 + sx_, 14, 6.1, M['rubber'], 6)
def standoff(x, y, h=3): icyl(f'standoff_{int(x)}_{int(y)}', 2.7, h, 'z', x, y, 3 - h / 2 + 1.5 if False else 3.0 + h / 2 - h, M['alu'], 6)

# ===== Mini-ITX 基板: ASUS ROG STRIX X870-I GAMING WIFI (170x170、レイアウトは公式マニュアル図の実測) =====
BL = json.load(open(os.path.join(ROOT, 'model', 'x870i_layout.json')))
pcbp = os.path.join(TEXDIR, 'pcb_x870i.png'); pcb_tex(pcbp, 170, 170, 9, '#0b0c0e', '#1c1f24', '')
ibox('board_pcb', 170, 170, 1.6, bx, by, bz, img_material('pcb_x870i', pcbp, rough=.45), uv=True)
for (hx, hy) in ((4, 4), (166, 4), (4, 166), (166, 166)): icyl(f'board_screw_{hx}_{hy}', 2.9, 1.2, 'z', bx + hx + 2 - 2, by + hy, bz + 1.6 + .6, M['steel'], 6)
Z1 = bz + 1.6          # 基板上面
IOX = BL['io_x_ranges']
# 後部I/O(下向き): 公式図でx範囲確定、ブロック内の並びは未確認(代表的な構成で配置)
io_x0, io_x1 = IOX['HDMI_U10G34'][0] - 2, IOX['M2_WIFI'][1] + 2
ibox('io_shield', io_x1 - io_x0, 26, 44.45, bx + io_x0, by - 2, Z1, M['steel'])
def port(name, xc, zc, w, h, inner=None):
    ibox(name + '_shell', w, 1.4, h, bx + xc - w / 2, by - 3.4, Z1 + zc - h / 2, M['steel'], .2)
    ibox(name + '_hole', w - 3, 1.5, h - 3, bx + xc - (w - 3) / 2, by - 3.5, Z1 + zc - (h - 3) / 2, inner or M['dark'])
mid = lambda k: (IOX[k][0] + IOX[k][1]) / 2
port('io_hdmi', mid('HDMI_U10G34'), 10, 15, 6.5); port('io_usb_a1', mid('HDMI_U10G34'), 24, 14.5, 7, principled('usb_blue', '#2a6df0', 0, .5)); port('io_usb_a2', mid('HDMI_U10G34'), 36, 14.5, 7)
port('io_usb4_a', mid('U40G_EC1_U10G11'), 10, 9, 3.6); port('io_usb4_b', mid('U40G_EC1_U10G11'), 24, 9, 3.6); port('io_usb_a3', mid('U40G_EC1_U10G11'), 36, 14.5, 7)
port('io_usb4_c', mid('U40G_EC2'), 12, 9, 3.6); port('io_rj45', mid('LAN_U10G_C7'), 12, 16, 13.5, M['alu']); port('io_usbc2', mid('LAN_U10G_C7'), 30, 9, 3.6)
for k, xs in enumerate((bx + 115.5, bx + 119.5)): icyl(f'io_sma{k}', 3.2, 5, 'y', xs, by - 5, Z1 + 38, M['gold'], 20)
# VRMヒートシンク(ファン付)・I/Oカバー: 高さは公式資料で未確認(仮置き、docs/unverified-tracker.md)
ibox('vrm_shroud', 98, 36, 22, bx + 8, by + 24, Z1, M['shroud'], 1.5)
ibox('vrm_trim', 98, 1.2, 22.1, bx + 8, by + 24, Z1, M['silver_trim'])
label('ROG', 9, bx + 28, by + 42, Z1 + 22.15, M['print_w'], name='txt_rog'); label('STRIX', 5.5, bx + 62, by + 42, Z1 + 22.15, M['print_w'], name='txt_strix')
label('X870-I GAMING WIFI', 3.6, bx + 74, by + 31, Z1 + 22.15, M['silver_trim'], name='txt_model')
icyl('vrm_fan_ring', 12, 1.0, 'z', bx + 96, by + 42, Z1 + 22.5, M['alublack'], 32)
# チョーク・コンデンサ・MOSFET(CPUソケット周り): 公式写真の一般配置(個数は未確認)
for i in range(8): ibox(f'choke{i}', 7, 7, 4.5, bx + 14 + i * 9.6, by + 62, Z1, M['cap'], .5)
for i in range(6): icyl(f'cap{i}', 3.2, 9, 'z', bx + 22 + i * 9.6, by + 74, Z1 + 4.5, M['cap'], 20)
# AM5ソケット + 9800X3D (IHS 'AMD RYZEN 7 9800X3D')
sx_, sy_ = BL['socket_center']
ibox('socket', 60, 60, 4, bx + sx_ - 30, by + sy_ - 30, Z1, principled('socket', '#2a2c31', 0, .5))
ibox('cpu_ihs', 40, 40, 2.6, bx + sx_ - 20, by + sy_ - 20, Z1 + 4, principled('ihs', '#9da3ab', 1.0, .28), .6)
label('AMD', 4, bx + sx_ - 8, by + sy_ + 12, Z1 + 6.65, M['print_w'], name='txt_ihs_amd', ext=.02); label('RYZEN 7', 3, bx + sx_ - 8, by + sy_ + 6, Z1 + 6.65, M['print_w'], name='txt_ihs_ryzen', ext=.02); label('9800X3D', 3, bx + sx_ - 8, by + sy_ + 1, Z1 + 6.65, M['print_w'], name='txt_ihs_model', ext=.02)
# チップセット(ヒートシンク) / PCIe x16 / ATX24 / EPS / M.2 ドーターカード
ibox('chipset_sink', 21, 19, 9, bx + 129, by + 47, Z1, M['alublack'], .6)
ibox('pcie_x16', 8.6, 89, 11, bx + 157.4, by + 43, Z1, M['dark'], .3); ibox('pcie_gold', 2, 60, .4, bx + 160.7, by + 57, Z1 + 11.0, M['gold'])
ibox('atx24', 50.1, 10, 15, bx + 13.4, by + 159, Z1, M['white'], .4); ibox('eps8', 11.8, 18.1, 11, bx + 1.6, by + 2.4, Z1, M['dark'], .3)
ibox('m2_daughter', 25, 59, 1.6, bx + 130, by + 79, Z1 + 12, M['pcb_black'])      # 高さ未確認(仮置き)
for i in range(2): ibox(f'dimm_slot{i}', 155, BL['dimm_slots']['y'][i][1] - BL['dimm_slots']['y'][i][0], 8, bx + BL['dimm_slots']['x'][0], by + BL['dimm_slots']['y'][i][0], Z1, M['plastic'], .3)
# DDR5 DIMM x2 (大手品・型番未定: ブランドロゴは入れず仕様ステッカーのみ)
for i in range(2):
    y0_, y1_ = BL['dimm_slots']['y'][i]
    ibox(f'dimm{i}_body', 133.35, y1_ - y0_ - 0.6, 36, bx + 8, by + y0_ + .3, Z1 + 8, principled('dimm_spreader', '#1b1c20', .8, .35), .6)
    ibox(f'dimm{i}_sticker', 60, .2, 10, bx + 40, by + y1_ - .6 if i == 0 else by + y0_ + .1, Z1 + 24, M['sf_label'])
# ===== M.2 SSD: Samsung 990 PRO with Heatsink (80.15x25x8.88, 黒ヒートシンク+赤スリット) =====
sd = lp('ssd')
ibox('ssd_body', 80.15, 25, 8.88, sd[0], sd[1], sd[2], principled('ssd_sink', '#101113', .7, .4), .5)
for k in range(6): ibox(f'ssd_slit{k}', 1.2, 22, .3, sd[0] + 14 + k * 8, sd[1] + 1.5, sd[2] + 8.88, M['print_red'])
label('SAMSUNG', 4.2, sd[0] + 62, sd[1] + 12.5, sd[2] + 9.0, M['print_w'], name='txt_samsung'); label('990 PRO', 3, sd[0] + 62, sd[1] + 6, sd[2] + 9.0, M['print_w'], name='txt_990')

# ===== CPU水冷 ARCTIC Liquid Freezer III Pro 240: ポンプブロック =====
cl = lp('cooler'); cs = ls('cooler'); pcx, pcy = cl[0] + cs[0] / 2, cl[1] + cs[1] / 2
pump_mat = principled('arctic_pump', '#18191c', 0.4, 0.4)
icyl('pump_body', 45.5, 34, 'z', pcx, pcy, cl[2] + 17, pump_mat, 64)
icyl('pump_cap', 40, 6, 'z', pcx, pcy, cl[2] + 34 + 3, M['alublack'], 64)
icyl('pump_vrmfan_ring', 30, 28.5, 'z', pcx, pcy - 22, cl[2] + 40 + 14.25 - 6, M['dark'], 40)
label('ARCTIC', 7, pcx, pcy + 12, cl[2] + 40.1, M['print_w'], name='txt_arctic_pump')
for sgn, nm in ((1, 'a'), (-1, 'b')):
    ibox(f'pump_port_{nm}', 14, 20, 14, pcx + sgn * 40 - 7, pcy + cs[1] / 2 - 25, cl[2] + 10, pump_mat, 2)   # ホース出口(側面)
# ラジエーター(277x120x38) + P12 Pro x2
rx_, ry_, rz_ = lp('radiator')
ibox('rad_core', 120, 277, 38, rx_, ry_, rz_, M['rad_black'], .8)
ibox('rad_tank_a', 120, 12, 38, rx_, ry_ - 0, rz_, M['alublack'], 1.5); ibox('rad_tank_b', 120, 12, 38, rx_, ry_ + 265, rz_, M['alublack'], 1.5)
label('ARCTIC', 6, rx_ + 60, ry_ + 138, rz_ + 38.05, M['print_w'], rot=90, name='txt_arctic_rad')
for k in range(2):
    make_fan(f'fan_rad{k}', 120, 25, 11, principled('p12_frame', '#101114', 0, .45), principled('p12_blade', '#1b1c20', 0, .45), principled('p12_hub', '#101114', .2, .4), rx_ + 60, ry_ + 18.5 + 60 + k * 120, rz_ + 38)
# ホース(OD約12): ポンプ側面 -> ラジエーターtank。GPU端(y<53)の下を通す
def hose(name, pts): return cable(name, pts, 6.0, M['hose'])
# ケーブル関数はここで必要なので先に定義
def cable(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 6; cu.fill_mode = 'FULL'; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, bp in zip(pts, sp.bezier_points): bp.co = V(X0 + p[0], Y0 + p[1], Z0 - p[2]); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name, cu); cu.materials.append(mat); return link(ob)
hose('hose_a', [(pcx + 40, pcy + 28, cl[2] + 17), (pcx + 70, pcy - 40, cl[2] + 20), (330, 40, 40), (440, 36, 34), (rx_ + 40, ry_ + 6, rz_ + 19)])
hose('hose_b', [(pcx - 40, pcy + 28, cl[2] + 17), (pcx - 30, pcy - 70, cl[2] + 15), (330, 24, 28), (460, 22, 30), (rx_ + 80, ry_ + 6, rz_ + 19)])
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

# ===== GPU: ASUS Dual GeForce RTX 5060 Ti 16GB OC (229x120x50, 2.5スロット, ファン2基, 8ピン1本) =====
gcol = principled('gpu_shroud', '#17181b', .15, .42); add_bump(gcol, 700, .02)
ibox('gpu_backplate', 120, 229, 1.6, gx, gy, gz, principled('gpu_backplate', '#1b1c20', .8, .4), .4)
bpc_ = ibox('gpu_bp_cutter', 70, 8, 4, gx + 25, gy + 24, gz - 1, None); bpc_.hide_render = True
ar_ = bpc_.modifiers.new('arr', 'ARRAY'); ar_.count = 12; ar_.use_relative_offset = False; ar_.use_constant_offset = True; ar_.constant_offset_displace = (0, 16, 0)
m_ = bpy.data.objects['gpu_backplate'].modifiers.new('slots', 'BOOLEAN'); m_.object = bpc_; m_.operation = 'DIFFERENCE'; m_.solver = 'MANIFOLD'
gp = os.path.join(TEXDIR, 'pcb_gpu6.png'); pcb_tex(gp, 111, 215, 23, '#0f1114', '#2d3239')
ibox('gpu_pcb', 111, 215, 1.6, gx + 4, gy + 12, gz + 1.6, img_material('pcb_gpu6', gp, rough=.5), uv=True)
ibox('gpu_edge', 3, 89, 1.8, gx - 1.2, ry0, gz + 3.4, M['gold'])
ibox('gpu_heatsink', 108, 200, 28, gx + 6, gy + 18, gz + 3.2, principled('gpu_fins', '#bfc3c9', 1.0, .38), .5)
for k in range(5): icyl(f'gpu_hpipe{k}', 3, 200, 'y', gx + 18 + k * 20, gy + 118, gz + 8 + 3, M['copper'], 20)
shr = ibox('gpu_shroud_body', 120, 229, 18, gx, gy, gz + 32, gcol, 2.0)
for k, fy_ in enumerate((gy + 70, gy + 160)):
    shc = cyl(f'gpu_fan_hole{k}', 43, 22, 'z', X0 + gx + 60, Y0 + fy_, Z0 - (gz + 41), None, 64, body=False); shc.hide_render = True; BODY_OBJS.append(shc)
    bmx = shr.modifiers.new(f'hole{k}', 'BOOLEAN'); bmx.object = shc; bmx.operation = 'DIFFERENCE'; bmx.solver = 'EXACT'
    make_fan(f'fan_gpu{k}', 90, 10, 11, M['dark'], principled('gpu_blade', '#222428', .2, .45), principled('gpu_hub', '#2a2c31', .3, .4), gx + 60, fy_, gz + 34)
    bpy.data.objects[f'fan_gpu{k}_frame'].hide_render = True
ibox('gpu_trim', 120, 1.6, 18.1, gx, gy + 112, gz + 32, M['silver_trim'])      # 2基のファンの間の細いアクセントライン(銀)
label('DUAL', 6, gx + 108, gy + 30, gz + 50.05, M['print_w'], rot=90, name='txt_gpu_dual', ext=.03)
label('GEFORCE RTX', 3.6, gx + 108, gy + 200, gz + 50.05, M['print_w'], rot=90, name='txt_gpu_geforce', ext=.03)
ibox('gpu_bracket', 120, 1.5, 50, gx, gy - 1.5, gz, M['steel'], .3)              # 出力ブラケット(下端 y側)
for k, (nm, w_) in enumerate((('hdmi', 15), ('dp', 16), ('dp', 16), ('dp', 16))): ibox(f'gpu_port{k}', w_, 3, 6.5, gx + 14 + k * 26, gy - 3, gz + 7, M['dark'], .3)
ibox('gpu_12v8pin', 20.6, 11.5, 10, gx + 95, gy + 210, gz + 36, M['dark'], .4)

# ===== 電源: Corsair SF750 (SFX 125x63.5x100)。ファン面を上(ドーム側)、モジュラー端子面を基板側 =====
px_, py_, pz_ = lp('psu')
ibox('psu_body', 125, 100, 63.5, px_, py_, pz_, M['sf_body'], 1.5)
wire = principled('psu_wire', '#2a2c31', .9, .4)
ibox('psu_grille_plate', 100, 92, .4, px_ + 12, py_ + 4, pz_ + 63.5, M['dark'])
make_fan('fan_psu', 92, 8, 9, M['dark'], principled('psu_blade', '#202226', .2, .45), principled('psu_hub', '#2a2c31', .3, .4), px_ + 62, py_ + 50, pz_ + 54)
bpy.data.objects['fan_psu_frame'].hide_render = True
for k in range(1, 5): icyl(f'psu_grille_ring{k}', 9.5 * k, .5, 'z', px_ + 62, py_ + 50, pz_ + 64.2, wire, 48)
_bm = bmesh.new()
for k in range(6):
    bmesh.ops.create_cube(_bm, size=1.0, matrix=Matrix.Translation(V(X0 + px_ + 62, Y0 + py_ + 50, Z0 - (pz_ + 64.2))) @ Matrix.Rotation(math.radians(k * 30), 4, 'Y') @ Matrix.Diagonal((92, .5, .5, 1)))
_me = bpy.data.meshes.new('psu_grille_spokes'); _bm.to_mesh(_me); _bm.free(); _me.materials.append(wire); link(bpy.data.objects.new('psu_grille_spokes', _me))
label('SF750', 7, px_ + 62, py_ + 85, pz_ + 63.95, M['print_w'], name='txt_sf750', ext=.03)
label('PLATINUM', 3.5, px_ + 62, py_ + 15, pz_ + 63.95, M['print_w'], name='txt_platinum', ext=.03)
ibox('psu_label', 70, 38, .3, px_ + 28, py_ + 30, pz_ + 63.5, M['sf_label'])     # 仕様ラベル(内容は未確認のため無地)
for i in range(6): ibox(f'psu_socket{i}', 13, 5, 9, px_ + 8 + i * 19, py_ - 4, pz_ + 25, M['rubber'], .4)

# ===== ケースファン: Noctua NF-A12x25 PWM (120x120x25) =====
fz_ = lp('fan')[2]
make_fan('fan_exhaust', 120, 25, 9, M['noctua_beige'], M['noctua_brown'], M['noctua_brown'], fx + 60, fy + 60, fz_)

# ===== パネル用コントローラ基板(4K eDP, 150x55 横置き。型番未確定) =====
cx_, cy_, cz_ = lp('ctrl_board')
cp = os.path.join(TEXDIR, 'pcb_ctrl6.png'); pcb_tex(cp, 150, 55, 41, '#16222b', '#2a3d4c', '4K eDP ctrl')
ibox('ctrl_pcb', 150, 55, 1.6, cx_, cy_, cz_, img_material('pcb_ctrl6', cp, rough=.5), uv=True)
ibox('ctrl_hdmi', 15, 6.5, 6, cx_ + 8, cy_ + 1, cz_ + 1.6, M['steel']); ibox('ctrl_dp', 17, 6.5, 6, cx_ + 28, cy_ + 1, cz_ + 1.6, M['steel'])
ibox('ctrl_soc', 14, 14, 1.4, cx_ + 70, cy_ + 20, cz_ + 1.6, M['chip']); ibox('ctrl_edp_conn', 4, 20, 4, cx_ + 144, cy_ + 18, cz_ + 1.6, M['dark'])
for k in range(3): icyl(f'ctrl_cap{k}', 4, 9, 'z', cx_ + 100 + k * 14, cy_ + 12, cz_ + 1.6 + 4.5, M['cap'], 20)
for k in range(2): ibox(f'ctrl_coil{k}', 9, 9, 7, cx_ + 100 + k * 18, cy_ + 34, cz_ + 1.6, M['alublack'], .5)

# ===== ケーブル(PSUのモジュラー端子 -> 各機器)。トレイ上のクリップ点を通る =====
cable('cable_atx24', [(px_ + 20, py_ - 6, pz_ + 25), (px_ + 8, py_ - 20, pz_ + 30), (bx + 36, by + 176, Z1 + 20), (bx + 38, by + 164, Z1 + 12)], 4.8, M['rubber'])
cable('cable_eps', [(px_ + 38, py_ - 6, pz_ + 25), (px_ + 30, py_ - 16, 30), (bx - 6, 190, 26), (bx - 6, by + 40, 18), (bx + 6, by + 12, Z1 + 8)], 2.8, M['rubber'])
cable('cable_pcie8', [(px_ + 76, py_ - 6, pz_ + 25), (px_ + 100, py_ - 20, 40), (300, 198, 58), (gx + 102, gy + 205, 58), (gx + 102, gy + 212, gz + 42)], 3.2, M['rubber'])
cable('cable_ctrl_12v', [(px_ + 100, py_ + 100, pz_ + 20), (cx_ + 20, cy_ - 4, 14), (cx_ + 20, cy_ + 6, cz_ + 4)], 2.2, M['rubber'])
cable('cable_umbilical', [(cx_ + 146, cy_ + 28, cz_ + 5), (cx_ + 146, cy_ + 50, 10), (cx_ + 120, IH_ - 8, 6), (cx_ + 120, IH_ + 2, 1)], 3.0, principled('umb', '#c9ced6', 0, .5))
# ---------------- 分解(Explode)・チルト ----------------
def shift_group(prefix_list, dz_):
    for ob in list(COLL.objects):
        if any(ob.name.startswith(p) for p in prefix_list): ob.location += Vector((0, dz_, 0))
if A.explode > 0:
    e = A.explode
    shift_group(['cover_back', 'gasket'], 230 * e); shift_group(['pump', 'hose', 'rad', 'fan_rad', 'txt_arctic'], 110 * e)
    shift_group(['gpu', 'fan_gpu', 'cable_pcie8', 'txt_gpu'], 70 * e); shift_group(['psu', 'cable_atx24', 'cable_eps', 'txt_sf', 'txt_plat'], 45 * e); shift_group(['fan_exhaust'], 85 * e); shift_group(['ctrl_', 'cable_ctrl', 'cable_umb'], 30 * e)
if A.cut and A.explode == 0:
    for ob in COLL.objects:
        if ob.name.startswith(('cover_back', 'gasket')): ob.hide_render = True
PIV = bpy.data.objects.new('tilt_pivot', None); COLL.objects.link(PIV); PIV.location = V(0, 0, ZC); bpy.context.view_layer.update()
for ob in COLL.objects:
    if ob in BODY_OBJS and ob.parent is None:
        ob.parent = PIV; ob.matrix_parent_inverse = PIV.matrix_world.inverted()
PIV.rotation_euler = (math.radians(A.tilt), 0, 0)   # +で上端が後ろへ(Blender +Y=背面)

# ファン回転 (フレーム数指定時はアニメーション)
for k, r in enumerate(rotors):
    r.rotation_euler = (0, A.phase * 2 + k * .6, 0)
    if A.frames > 0:
        scene.frame_start, scene.frame_end = 1, A.frames
        for f, ang in ((1, A.phase * 2), (A.frames + 1, A.phase * 2 + (math.pi * 2) * (1 if 'cpu' in r.name else 1.4))):
            r.rotation_euler[1] = ang + k * .6; r.keyframe_insert('rotation_euler', index=1, frame=f)

# ---------------- GLB書き出し(床・照明・カメラを足す前。非表示のブール用カッターは除外) ----------------
if A.export:
    bpy.ops.export_scene.gltf(filepath=A.export, export_format='GLB', export_apply=True, use_renderable=True, export_animations=False)

# ---------------- 環境 / カメラ / レンダー ----------------
floor = bpy.data.objects.new('floor', bpy.data.meshes.new('floor'))
bmf = bmesh.new(); bmesh.ops.create_grid(bmf, x_segments=1, y_segments=1, size=6000); bmf.to_mesh(floor.data); bmf.free()
floor.location = V(0, -DROP - 6.2, 0); floor.data.materials.append(principled('floor', '#e9ebef', 0, .9)); COLL.objects.link(floor); floor.is_shadow_catcher = True
wd = bpy.data.worlds.new('studio'); wd.use_nodes = True; wnt = wd.node_tree; bg = wnt.nodes['Background']; scene.world = wd
tcw = wnt.nodes.new('ShaderNodeTexCoord'); spw = wnt.nodes.new('ShaderNodeSeparateXYZ'); cr = wnt.nodes.new('ShaderNodeValToRGB')
wnt.links.new(tcw.outputs['Generated'], spw.inputs['Vector']); wnt.links.new(spw.outputs['Z'], cr.inputs['Fac'])
cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = hexc('#c8ccd6'); cr.color_ramp.elements[1].position = 0.85; cr.color_ramp.elements[1].color = hexc('#ffffff')
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
TGT = bpy.data.objects.new('target', None); TGT.location = V(0, 190, -40); COLL.objects.link(TGT)
cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 70; cam_d.clip_start = 10; cam_d.clip_end = 20000; cam_d.sensor_width = 36
cam = bpy.data.objects.new('cam', cam_d); COLL.objects.link(cam); scene.camera = cam
tt = cam.constraints.new('TRACK_TO'); tt.target = TGT; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
k = 1.0 if A.panel == 24 else 1.18
VIEWS = {'front': ((560, 330, 1900), (0, 205, -30)), 'back': ((-700, 330, -1950), (0, 200, -45)), 'side': ((1900, 270, -80), (0, 190, -45)),
         'inside': ((40, 215, -1380), (0, 205, -45)), 'top': ((0, 1600, -60), (0, 100, -45)), 'closeup': ((-330, 200, -560), (-205, 120, -40)), 'io': ((-820, 120, -430), (-250, 70, -40)),
         'detail_front': ((250, 250, 700), (0, 140, 0)), 'explode': ((-1000, 460, -2050), (0, 130, -120))}
if A.view in ('closeup', 'io'): k = 1.0
vp, vt = VIEWS[A.view]; cam.location = V(vp[0] * k, vp[1] * k, vp[2] * k); TGT.location = V(*vt)
if A.focus:   # 内部座標(x,y,z)を注視し、背面側から az/el で周回(az=0: 真後ろ)
    fx_, fy_, fz_ = [float(v) for v in A.focus.split(',')]; t3 = Vector((X0 + fx_, Y0 + fy_, Z0 - fz_))
    az_, el_ = math.radians(A.az), math.radians(A.el)
    c3 = t3 + Vector((A.dist * math.sin(az_) * math.cos(el_), A.dist * math.sin(el_), -A.dist * math.cos(az_) * math.cos(el_)))
    cam.location = V(c3.x, c3.y, c3.z); TGT.location = V(t3.x, t3.y, t3.z)
cam_d.lens = A.lens
r = scene.render; r.engine = 'CYCLES'; w_, h_ = [int(x) for x in A.res.split('x')]; r.resolution_x, r.resolution_y, r.resolution_percentage = w_, h_, 100
cy = scene.cycles; cy.device = 'CPU'; cy.samples = A.samples; cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'; cy.max_bounces = 8; cy.transparent_max_bounces = 16
cy.preview_samples = 16
scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'; scene.view_settings.exposure = -0.35
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGB'
os.makedirs(os.path.dirname(A.out), exist_ok=True)
if A.save_blend: bpy.ops.wm.save_as_mainfile(filepath=A.save_blend)
if A.frames > 0:
    r.image_settings.file_format = 'PNG'; r.filepath = A.out.replace('.png', '_')
    bpy.ops.render.render(animation=True)
else:
    r.filepath = A.out; bpy.ops.render.render(write_still=True)
print('DONE', A.out)
