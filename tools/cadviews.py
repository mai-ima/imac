#!/usr/bin/env python3
"""cadquery の HLR(隠線処理)で実形状から正投影の線画(見える線/隠れ線)を取り出し、A3図面SVGへ配置する共通部品。
使い方: P = project(shape, view_dir, x_dir) → {'vis': [[(x,y),...]], 'hid': [...], 'bbox': (x0,y0,x1,y1)} (単位mm, 投影面座標: x=右, y=上)。
place(P, ox, oy, scale) → SVG <g>(見える線=実線0.35 / 隠れ線=破線0.18、y反転は内部で処理)。寸法線は drawlib の dim_h/dim_v に place と同じ変換で渡す。"""
import math
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
import cadquery as cq

def _edges(compound):
    out = []
    if compound is None or compound.IsNull(): return out
    ex = TopExp_Explorer(compound, TopAbs_EDGE)
    while ex.More(): out.append(TopoDS.Edge_s(ex.Current())); ex.Next()
    return out

def _poly(edge, defl=0.05):
    c = BRepAdaptor_Curve(edge); pts = GCPnts_QuasiUniformDeflection(c, defl, c.FirstParameter(), c.LastParameter())
    if not pts.IsDone(): return []
    return [(pts.Value(i + 1).X(), pts.Value(i + 1).Y()) for i in range(pts.NbPoints())]

def project(shape, view_dir, x_dir):
    """shape: cq.Workplane/Shape。view_dir=視線の向き(カメラ→物体)の逆=カメラ位置方向、x_dir=画面右方向。"""
    sh = shape.val() if hasattr(shape, 'val') else shape
    hlr = HLRBRep_Algo(); hlr.Add(sh.wrapped)
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(), gp_Dir(*view_dir), gp_Dir(*x_dir)))); hlr.Update(); hlr.Hide()
    t = HLRBRep_HLRToShape(hlr)
    vis = []; hid = []
    for comp in (t.VCompound(), t.Rg1LineVCompound(), t.OutLineVCompound()): vis += [p for p in (_poly(e) for e in _edges(comp)) if len(p) > 1]
    for comp in (t.HCompound(), t.Rg1LineHCompound(), t.OutLineHCompound()): hid += [p for p in (_poly(e) for e in _edges(comp)) if len(p) > 1]
    xs = [q[0] for p in vis for q in p] or [0]; ys = [q[1] for p in vis for q in p] or [0]
    return {'vis': vis, 'hid': hid, 'bbox': (min(xs), min(ys), max(xs), max(ys))}

def place(P, ox, oy, s, hidden=True, vis_w=.35, hid_w=.18):
    """投影図を図面座標へ: 図面x = ox + s*x, 図面y = oy - s*y(SVGは下向き)。ox,oy は投影原点(0,0)の図面位置。"""
    f = lambda p: f"{ox + s * p[0]:.2f},{oy - s * p[1]:.2f}"
    o = ['<g fill="none" stroke-linejoin="round" stroke-linecap="round">']
    if hidden and P['hid']: o.append(f'<g stroke="#000" stroke-width="{hid_w}" stroke-dasharray="2.2 1.2">' + ''.join('<polyline points="' + ' '.join(f(p) for p in pl) + '"/>' for pl in P['hid']) + '</g>')
    o.append(f'<g stroke="#000" stroke-width="{vis_w}">' + ''.join('<polyline points="' + ' '.join(f(p) for p in pl) + '"/>' for pl in P['vis']) + '</g></g>')
    return '\n'.join(o)

# ---------------- 断面(ハッチング付き): 機構の内部図用 ----------------
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.TopAbs import TopAbs_REVERSED

def _wire_pts(wire, defl=0.03):
    """ワイヤを向き付きで順に標本化(点列)。"""
    pts = []; ex = BRepTools_WireExplorer(wire.wrapped)
    while ex.More():
        e = ex.Current(); c = BRepAdaptor_Curve(e); q = GCPnts_QuasiUniformDeflection(c, defl, c.FirstParameter(), c.LastParameter())
        seg = [(q.Value(i + 1).X(), q.Value(i + 1).Y(), q.Value(i + 1).Z()) for i in range(q.NbPoints())] if q.IsDone() else []
        if e.Orientation() == TopAbs_REVERSED: seg.reverse()
        pts += seg if not pts else seg[1:]
        ex.Next()
    return pts

def cut_half(shape, origin, normal, xdir):
    """面(origin,normal)で切り、normal 側(手前)を除去した半割り形状と、切断面の多角形リスト [(外周, [内周...])](投影面座標 u=p·xdir, v=p·(normal×xdir))を返す。"""
    sh = shape.val() if hasattr(shape, 'val') else shape
    n = cq.Vector(*normal).normalized(); xd = cq.Vector(*xdir).normalized(); yd = n.cross(xd)
    pl = cq.Plane(origin=origin, xDir=tuple(xd), normal=tuple(n))
    cutter = cq.Workplane(pl).rect(4000, 4000).extrude(2000).val()
    half = sh.cut(cutter)
    polys = []
    for f in half.Faces():
        if f.geomType() != 'PLANE': continue
        if abs((f.Center() - cq.Vector(*origin)).dot(n)) > 1e-3 or abs(f.normalAt().dot(n)) < 0.999: continue
        P = lambda pts: [(cq.Vector(*p).dot(xd), cq.Vector(*p).dot(yd)) for p in pts]
        polys.append((P(_wire_pts(f.outerWire())), [P(_wire_pts(w)) for w in f.innerWires()]))
    return half, polys, (xd, yd)

def hatch_defs(specs):
    """specs: {id: (角度deg, 間隔mm, 線幅)} → <defs>。ISO 128-50: 隣接部品は角度/間隔を変える。"""
    o = ['<defs>']
    for k, (ang, sp, w) in specs.items():
        o.append(f'<pattern id="{k}" patternUnits="userSpaceOnUse" width="{sp}" height="{sp}" patternTransform="rotate({ang})"><line x1="0" y1="0" x2="0" y2="{sp}" stroke="#000" stroke-width="{w}"/></pattern>')
    o.append('</defs>'); return '\n'.join(o)

def place_section(polys, ox, oy, s, hid, sw=.5):
    """切断面を塗りハッチで描画(外周・内周とも evenodd)。hid=パターンid。"""
    f = lambda p: f"{ox + s * p[0]:.2f},{oy - s * p[1]:.2f}"
    d = ''
    for outer, inners in polys:
        for loop in [outer] + inners: d += 'M' + ' L'.join(f(p) for p in loop) + ' Z '
    return f'<path d="{d}" fill="url(#{hid})" fill-rule="evenodd" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>'
