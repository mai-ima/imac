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
X0, Y0, Z0 = -POD_W / 2 + WALL, WALL, -SLAB      # 内部座標の原点(設計図座標)

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

# ポッド(左右壁・上下の吸排気スリット壁)
PD = POD_T - SLAB; zmid = -SLAB - PD / 2
box('pod_left', WALL, POD_H, PD, -POD_W / 2, 0, -SLAB - PD, M['body'], bevel=0.6)
box('pod_right', WALL, POD_H, PD, POD_W / 2 - WALL, 0, -SLAB - PD, M['body'], bevel=0.6)
def slotted_wall(name, y):
    w = box(name, POD_W, WALL, PD, -POD_W / 2, y, -SLAB - PD, M['body'], bevel=0.5)
    cut = box(name + '_cutter', 3.2, WALL + 2, PD - 14, -POD_W / 2 + 28, y - 1, -SLAB - PD + 7, None, body=False)
    ar = cut.modifiers.new('arr', 'ARRAY'); ar.count = 29; ar.use_relative_offset = False; ar.use_constant_offset = True; ar.constant_offset_displace = ((POD_W - 56) / 28, 0, 0)
    bm = w.modifiers.new('slots', 'BOOLEAN'); bm.object = cut; bm.operation = 'DIFFERENCE'; bm.solver = 'MANIFOLD'
    cut.hide_render = True; BODY_OBJS.append(cut)
slotted_wall('pod_top', POD_H - WALL); slotted_wall('pod_bottom', 0)
# 背面カバー(吸気メッシュ: 透過マスク)
vents = [(WALL + 196 + 60, WALL + 18 + 72, 48), (WALL + 405 + 60, WALL + 20 + 60, 56)]
# 背面カバー: 吸気メッシュは実形状の穴(ブール演算)
cover = box('cover_back', POD_W, POD_H, WALL, -POD_W / 2, 0, -POD_T, M['body'], bevel=0.5)
bmc = bmesh.new(); step = 7.0
for cx_, cy_, R_ in vents:
    row = 0; yy = -R_
    while yy <= R_:
        xx = -R_
        while xx <= R_:
            x_ = xx + (step / 2 if row % 2 else 0)
            if math.hypot(x_, yy) < R_ - 3:
                bmesh.ops.create_cone(bmc, cap_ends=True, segments=10, radius1=2.1, radius2=2.1, depth=WALL + 2,
                                      matrix=Matrix.Translation(V(-POD_W / 2 + cx_ + x_, cy_ + yy, -POD_T + WALL / 2)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
            xx += step
        yy += step * .87; row += 1
mec = bpy.data.meshes.new('cover_holes'); bmc.to_mesh(mec); bmc.free()
cut = bpy.data.objects.new('cover_holes', mec); cut.hide_render = True; link(cut)
bmo = cover.modifiers.new('mesh', 'BOOLEAN'); bmo.object = cut; bmo.operation = 'DIFFERENCE'; bmo.solver = 'MANIFOLD'
for i in range(4): box(f'usbc_slot_{i}', 4, 12, 0.6, -POD_W / 2 + 45 + i * 14, 28, -POD_T - 0.3, M['dark'], bevel=1.5)
# 内部の床(前面スラブ背面)
box('inner_floor', IN_W, POD_H - 2 * WALL, 0.3, X0, Y0, -SLAB - 0.3, M['inner'])

# スタンド
box('stand_arm', ST_W, DROP - 6, 8, -ST_W / 2, -DROP, ZC - 4, M['stand'], bevel=2)
box('stand_foot', ST_W, 6, FOOT, -ST_W / 2, -DROP - 6, ZC - FOOT / 2, M['stand'], bevel=2.2, body=False)
cyl('hinge', 11, ST_W + 2, 'x', 0, -14, ZC, M['steel'], 64, body=False)
box('stand_power_recess', 12, 26, 0.5, -6, -DROP * .55 - 13, ZC + 3.9, M['dark'], bevel=3)
ARM_OBJ = bpy.data.objects['stand_arm']; BODY_OBJS.remove(ARM_OBJ)

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

# ===== 内部部品(すべて市販品。寸法は model/parts.json / 配置は model/layout.json) =====
LAY = {i['id']: i for i in json.load(open(os.path.join(ROOT, 'model', 'layout.json')))['items']}
PARTS = json.load(open(os.path.join(ROOT, 'model', 'parts.json')))
def lp(k): return LAY[k]['pos']

# --- Mini-ITX 基板: GIGABYTE B650I AX (170x170) ---
bx, by, bz = lp('board')
pcbp = os.path.join(TEXDIR, 'pcb_board.png'); pcb_tex(pcbp, 170, 170, 7, '#15171b', '#2c3038', 'B650I AX  mini-ITX 170x170')
mpcb = img_material('pcb_board', pcbp, rough=.5)
ibox('board_pcb', 170, 170, 1.6, bx, by, bz, mpcb, uv=True)
def smd_cloud(name, n, x0, y0, w, h, zl, seed, avoid):
    rr = random.Random(seed); me = bpy.data.meshes.new(name); bmm = bmesh.new(); k = 0
    for _ in range(n * 3):
        if k >= n: break
        x, y = x0 + rr.random() * w, y0 + rr.random() * h
        if any(a[0] < x < a[0] + a[2] and a[1] < y < a[1] + a[3] for a in avoid): continue
        r = bmesh.ops.create_cube(bmm, size=1.0); vs = r['verts']
        sx, sy = (1.6, .8) if rr.random() < .5 else (.8, 1.6)
        bmesh.ops.scale(bmm, vec=(sx, sy, .5), verts=vs); bmesh.ops.translate(bmm, vec=(x, y, zl + .25), verts=vs); k += 1
    bmm.to_mesh(me); bmm.free(); ob = bpy.data.objects.new(name, me); me.materials.append(M['smd'])
    for v in me.vertices: v.co = V(X0 + v.co.x, Y0 + v.co.y, Z0 - v.co.z)
    return link(ob)
smd_cloud('board_smd', 700, bx + 2, by + 2, 166, 166, bz + 1.6, 11, [(bx, by, 24, 170), (bx + 30, by + 36, 110, 104), (bx + 10, by + 140, 150, 28)])
# 後部I/O(左壁面に向く)
ibox('io_shield', 16, 158, 44, bx - 1.5, by + 6, bz + 1.6, M['steel'])
port_defs = [('dp', 12, 34, 17, 8), ('hdmi', 32, 34, 15, 6.5), ('usbc', 52, 34, 9, 3.6), ('usba', 68, 38, 14.5, 7), ('usba', 88, 38, 14.5, 7),
             ('usba', 68, 26, 14.5, 7), ('usba', 88, 26, 14.5, 7), ('rj45', 112, 28, 16, 13.5), ('sma', 142, 38, 7, 7), ('sma', 142, 24, 7, 7),
             ('audio', 20, 15, 7, 7), ('audio', 34, 15, 7, 7), ('audio', 48, 15, 7, 7)]
mblue = principled('usb_blue', '#2a6df0', 0, .5); mred = principled('usb_red', '#d11a2a', 0, .5)
for i, (k, y, z, w, h) in enumerate(port_defs):
    px = -WALL - 0.3      # 左壁の外面
    zc_ = bz + 1.6 + z
    if k == 'sma': icyl(f'io_sma{i}', 3.2, 5, 'x', px - 2, by + 6 + y, zc_, M['gold'], 20); continue
    if k == 'audio': icyl(f'io_audio{i}', 3.4, 2, 'x', px - 1, by + 6 + y, zc_, M['rubber'], 24); icyl(f'io_audio_in{i}', 1.7, 2.2, 'x', px - 1.1, by + 6 + y, zc_, M['dark'], 16); continue
    ibox(f'io_{k}{i}_shell', 1.4, w, h, px - 1.4, by + 6 + y - w / 2, zc_ - h / 2, M['steel'], .2)
    inner = {'usba': mred if (k == 'usba' and y > 80 and z > 30) else mblue, 'rj45': M['alu'], 'hdmi': M['dark'], 'dp': M['dark'], 'usbc': M['dark']}[k]
    ibox(f'io_{k}{i}_hole', 1.5, w - 3, h - 3, px - 1.5, by + 6 + y - (w - 3) / 2, zc_ - (h - 3) / 2, inner)
# VRM(ソケットとI/Oの間。低背: 9mm)
ibox('vrm_base', 12, 94, 2.5, 20, by + 38, bz + 1.6, M['alublack'], .3)
for i in range(14): ibox(f'vrm_fin{i}', 12, 3.6, 6, 20, by + 38 + i * 6.8, bz + 4.1, M['alublack'], .3)
for i in range(5): ibox(f'choke{i}', 7, 7, 5, 34, by + 42 + i * 18, bz + 1.6, M['cap'], .4)
for i in range(4): icyl(f'cap{i}', 3.15, 8, 'z', 148, by + 50 + i * 17, bz + 1.6 + 4, M['steel'], 20)
# AM5 ソケット+CPU(Ryzen 5 9600X)。クーラー中心の直下
cl = lp('cooler'); ccx, ccy = cl[0] + 95 / 2, cl[1] + 94.5 / 2
ibox('socket', 60, 66, 4, ccx - 30, ccy - 33, bz + 1.6, principled('socket', '#2a2c31', 0, .5))
ibox('cpu_ihs', 41, 41, 2.6, ccx - 20.5, ccy - 20.5, bz + 1.6 + 4, principled('ihs', '#9da3ab', 1.0, .28), .6)
# CPUクーラー: Thermalright AXP90-X47 (95 x 94.5 x 47。基準=CPU上面)
cz0 = cl[2]
ibox('cooler_base', 42, 42, 4, ccx - 21, ccy - 21, cz0, M['copper'], .5)
fin = ibox('cooler_fin', 95, .35, 26, cl[0], cl[1] + 1, cz0 + 6, principled('fin', '#c7c9ce', 1.0, .32))
ar = fin.modifiers.new('fins', 'ARRAY'); ar.count = 62; ar.use_relative_offset = False; ar.use_constant_offset = True; ar.constant_offset_displace = (0, 0, 92.5 / 62)
for k, yy in enumerate([-18, -9, 0, 9, 18]): icyl(f'heatpipe{k}', 3, 95, 'x', cl[0] + 47.5, ccy + yy, cz0 + 5, M['copper'], 24)
make_fan('fan_cpu', 92, 15, 9, principled('tl_frame', '#1a1b1e', 0, .5), principled('tl_blade', '#202226', 0, .45), principled('tl_hub', '#202226', .2, .4), ccx, ccy, cz0 + 32)
# DDR5 DIMM x2 (1枚実装 / 1枚は増設用に空き)
rm = lp('ram')
for i, fill in ((0, True), (1, False)):
    yy = by + 138 + i * 9.5
    ibox(f'dimm_slot{i}', 133, 5.5, 8, bx + 22, yy, bz + 1.6, M['plastic'], .3)
    ibox(f'dimm_latch{i}a', 4, 5.8, 3, bx + 19, yy - .15, bz + 1.6, M['dark']); ibox(f'dimm_latch{i}b', 4, 5.8, 3, bx + 155, yy - .15, bz + 1.6, M['dark'])
    if fill:
        ibox('dimm_pcb', 133.35, 1.27, 31.25, bx + 22, yy + 2.1, bz + 9.6, principled('dimm_pcb', '#17251a', 0, .5))
        for k in range(8): ibox(f'dimm_chip{k}', 11, .9, 8, bx + 28 + k * 14.2, yy + 3.4, bz + 14, M['chip'])
        ibox('dimm_label', 90, .2, 12, bx + 40, yy + 4.3, bz + 24, principled('dimm_label', '#d6d8dc', 0, .6))
# M.2 NVMe SSD: Samsung 990 EVO Plus 1TB (80.15 x 22.15 x 2.38)
sd = lp('ssd')
ibox('m2_slot', 10, 6, 3, sd[0] - 6, sd[1] + 8, bz + 1.6, M['dark'])
ibox('m2_pcb', 80.15, 22.15, 1.0, sd[0], sd[1], sd[2], principled('m2_pcb', '#1f2a22', 0, .5))
ibox('m2_label', 60, 18, .2, sd[0] + 14, sd[1] + 2, sd[2] + 1.0, principled('m2_label', '#d6d8dc', 0, .6))
ibox('m2_nand', 14, 13, 1.2, sd[0] + 68, sd[1] + 4.5, sd[2] + 1.0, M['chip']); ibox('m2_ctrl', 12, 12, 1.2, sd[0] + 4, sd[1] + 5, sd[2] + 1.0, M['chip'])
# チップセット・電池・コネクタ
ibox('chipset_base', 28, 28, 8, bx + 128, by + 22, bz + 1.6, M['alublack'], .4)
for i in range(6): ibox(f'chipset_fin{i}', 28, 2.2, 4, bx + 128, by + 24 + i * 4, bz + 9.6, M['alublack'], .2)
icyl('cmos', 10, 3.2, 'z', bx + 140, by + 96, bz + 3.2, M['steel'], 32)
ibox('atx24', 50, 10, 15, bx + 100, by + 160, bz + 1.6, M['white'], .4); ibox('eps8', 20, 8.5, 11, bx + 30, by + 160, bz + 1.6, M['dark'], .3)
ibox('pcie_x16', 8, 89, 11, bx + 160, by + 40, bz + 1.6, M['dark'], .3); ibox('pcie_gold', 2, 56, .4, bx + 162.5, by + 56, bz + 12.7, M['gold'])
ibox('led_power', 2, 2, 1, bx + 10, by + 160, bz + 1.6, M['led'])

# --- GPU: MSI GeForce RTX 5060 8G INSPIRE ITX OC (145 x 120 x 45, 単ファン, 8ピン) ---
gx, gy, gz = lp('gpu')
ibox('gpu_backplate', 120, 145, 1.5, gx, gy, gz, M['steel'], .4)
gp = os.path.join(TEXDIR, 'pcb_gpu.png'); pcb_tex(gp, 111, 139, 23, '#0f1114', '#2d3239')
ibox('gpu_pcb', 111, 139, 1.6, gx + 5, gy + 3, gz + 1.5, img_material('pcb_gpu', gp, rough=.5), uv=True)
ibox('gpu_edge', 5.5, 89, 1.8, gx - 1, gy + 16, gz + 1.6, M['gold'])
ibox('gpu_heatsink', 114, 136, 28, gx + 3, gy + 4.5, gz + 3.1, M['alublack'])
hsf = ibox('gpu_fin', 114, .5, 28, gx + 3, gy + 6, gz + 3.1, M['alu']); a = hsf.modifiers.new('fins', 'ARRAY'); a.count = 34; a.use_relative_offset = False; a.use_constant_offset = True; a.constant_offset_displace = (0, 0, 3.9)
shroud = ibox('gpu_shroud', 120, 145, 14, gx, gy, gz + 31, principled('gpu_shroud', '#1b1d21', .35, .4), 1.5)
shc = cyl('gpu_shroud_hole', 45, 18, 'z', X0 + gx + 60, Y0 + gy + 72, Z0 - (gz + 38), None, 64, body=False); shc.hide_render = True; BODY_OBJS.append(shc)
bmx = shroud.modifiers.new('hole', 'BOOLEAN'); bmx.object = shc; bmx.operation = 'DIFFERENCE'; bmx.solver = 'EXACT'
ibox('gpu_led_strip', 2, 145, .8, gx + 118, gy, gz + 44.2, M['led_blue'])
make_fan('fan_gpu', 100, 10, 9, M['dark'], principled('gpu_blade', '#2a2c31', .2, .45), principled('gpu_hub', '#2a2c31', .3, .4), gx + 60, gy + 72, gz + 33)
bpy.data.objects['fan_gpu_frame'].hide_render = True
ibox('gpu_8pin', 20.6, 11.5, 10, gx + 96, gy + 120, gz + 33, M['dark'], .4)
for k, (kk, x_) in enumerate([('hdmi', 20), ('dp', 44), ('dp', 68), ('dp', 92)]): ibox(f'gpu_port{k}', 14 if kk == 'hdmi' else 16, .6, 6, gx + x_, gy - 1.5, gz + 7, M['dark'])

# --- PCIeライザー: LINKUP AVA5 (フラット配線)。基板のx16スロット -> GPUエッジ ---
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
for k in range(6):
    y0 = by + 44 + k * 13
    ribbon(f'riser{k}', [(bx + 164, y0, bz + 16), (bx + 180, y0, bz + 26), (gx - 4, y0, bz + 12), (gx - 1, y0, gz + 2.4)], 12, .9, M['rubber'])

# --- 電源: SilverStone FX500-G (Flex ATX 500W, 150 x 81.5 x 40.5)。縦置き ---
px_, py_, pz_ = lp('psu')
psu = ibox('psu_body', 81.5, 150, 40.5, px_, py_, pz_, principled('psu_paint', '#1c1d20', .6, .45), 1.5)
ibox('psu_label', 60, 90, .3, px_ + 10, py_ + 30, pz_ + 40.5, principled('psu_label', '#8e949c', 0, .6))
ibox('psu_vent', 70, 36, .4, px_ + 6, py_ + 108, pz_ + 40.4, M['dark'])
icyl('psu_fan_hole', 18, .5, 'z', px_ + 40.7, py_ + 126, pz_ + 40.55, M['dark'], 32)
ibox('psu_ac_inlet', 27.5, 5, 19.5, px_ + 27, py_ - 5, pz_ + 10, M['rubber'], .5)           # IEC C14: 下端(下壁へ貫通)
for i in range(6): ibox(f'psu_cable{i}', 3.2, 12, 3.2, px_ + 12 + i * 11, py_ + 150, pz_ + 12, [M['yellow'], M['red'], M['rubber'], M['rubber'], M['rubber'], M['rubber']][i])

# --- ケース用ファン: Noctua NF-A12x15 PWM (120x120x15)。ベージュ枠+茶ブレード ---
fx, fy, fz = lp('fan')
make_fan('fan_exhaust', 120, 15, 9, principled('noctua_frame', '#cdb994', 0, .55), principled('noctua_blade', '#6b4a31', 0, .5), principled('noctua_hub', '#6b4a31', 0, .5), fx + 60, fy + 60, fz)

# --- パネル用コントローラ基板(4K eDP / 縦長 55x150x15 の予約空間) ---
cx_, cy_, cz_ = lp('ctrl_board')
cp = os.path.join(TEXDIR, 'pcb_ctrl.png'); pcb_tex(cp, 55, 150, 41, '#16222b', '#2a3d4c', '4K eDP ctrl')
ibox('ctrl_pcb', 55, 150, 1.6, cx_, cy_, cz_, img_material('pcb_ctrl', cp, rough=.5), uv=True)
ibox('ctrl_hdmi', 15, 6.5, 6, cx_ + 8, cy_ + 1, cz_ + 1.6, M['steel']); ibox('ctrl_dp', 17, 6.5, 6, cx_ + 28, cy_ + 1, cz_ + 1.6, M['steel'])
ibox('ctrl_soc', 14, 14, 1.4, cx_ + 20, cy_ + 70, cz_ + 1.6, M['chip']); ibox('ctrl_edp_conn', 20, 4, 4, cx_ + 18, cy_ + 142, cz_ + 1.6, M['dark'])
for k in range(3): icyl(f'ctrl_cap{k}', 4, 9, 'z', cx_ + 12 + k * 14, cy_ + 110, cz_ + 1.6 + 4.5, M['cap'], 20)
for k in range(2): ibox(f'ctrl_coil{k}', 9, 9, 7, cx_ + 10 + k * 18, cy_ + 40, cz_ + 1.6, M['alublack'], .5)

# --- ケーブル(PSUから) ---
def cable(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 6; cu.fill_mode = 'FULL'; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, bp in zip(pts, sp.bezier_points): bp.co = V(X0 + p[0], Y0 + p[1], Z0 - p[2]); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name, cu); cu.materials.append(mat); return link(ob)
cable('cable_atx24', [(px_ + 20, py_ + 150, pz_ + 12), (px_ + 10, 168, pz_ + 24), (bx + 125, 170, bz + 20), (bx + 125, by + 164, bz + 10)], 4.5, M['rubber'])
cable('cable_eps', [(px_ + 30, py_ + 150, pz_ + 12), (px_ + 30, 172, pz_ + 30), (bx + 40, 172, bz + 30), (bx + 40, by + 164, bz + 10)], 2.6, M['yellow'])
cable('cable_pcie8', [(px_ + 40, py_ + 150, pz_ + 12), (px_ + 40, 168, pz_ + 28), (gx + 106, gy + 148, gz + 28), (gx + 106, gy + 126, gz + 34)], 3.2, M['red'])
cable('cable_ctrl_12v', [(px_ + 50, py_ + 150, pz_ + 12), (px_ + 52, 166, pz_ + 20), (cx_ + 30, cy_ + 156, cz_ + 8), (cx_ + 30, cy_ + 145, cz_ + 4)], 2.2, M['rubber'])

# ---------------- 分解(Explode)・チルト ----------------
def shift_group(prefix_list, dz_):
    for ob in list(COLL.objects):
        if any(ob.name.startswith(p) for p in prefix_list): ob.location += Vector((0, dz_, 0))
if A.explode > 0:
    e = A.explode
    shift_group(['cover_back', 'usbc_slot'], 220 * e)
    shift_group(['cooler', 'fan_cpu', 'heatpipe'], 90 * e); shift_group(['gpu', 'fan_gpu', 'cable_pcie8'], 60 * e); shift_group(['psu', 'cable_atx24', 'cable_eps', 'cable_ctrl'], 40 * e); shift_group(['fan_exhaust'], 75 * e); shift_group(['ctrl_'], 30 * e)
if A.cut and A.explode == 0:
    for ob in COLL.objects:
        if ob.name.startswith(('cover_back', 'usbc_slot')): ob.hide_render = True
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
VIEWS = {'front': ((520, 300, 1650), (0, 190, -30)), 'back': ((-640, 310, -1750), (0, 175, -45)), 'side': ((1750, 260, -80), (0, 180, -45)),
         'inside': ((60, 120, -950), (0, 95, -45)), 'top': ((0, 1500, -60), (0, 100, -45)), 'closeup': ((-330, 210, -520), (-205, 100, -40)), 'io': ((-820, 170, -430), (-300, 100, -40)),
         'detail_front': ((250, 250, 700), (0, 140, 0)), 'explode': ((-900, 420, -1850), (0, 110, -120))}
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
