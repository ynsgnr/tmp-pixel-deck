"""Spatial checks: measure instead of picturing. Each call prints one line.
Failed checks are collected; fc_check.report() lists them and ends in ISSUES.

    from fc_spatial import (axes, expect, faces, edges, on_top, centred, fits,
                            solid_at, spec, placements)

Objects (Bodies, Std Parts) are measured in global coordinates. PartDesign
features and plain shapes are measured as they are (the Body's frame).
"""
import math

import FreeCAD as App
import Part

TOL = 1e-4  # mm for positional checks; booleans leave ~1e-7..1e-5 mm of noise
FAILS = []
_AX = {"+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0),
       "-Y": (0, -1, 0), "+Z": (0, 0, 1), "-Z": (0, 0, -1)}


def _f(x):  # float from number or Quantity
    return float(getattr(x, "Value", x))


def _v(t):  # Vector from Vector, (x, y, z) or "+Z"/"-x"
    if isinstance(t, str):
        t = t.upper() if t[0] in "+-" else "+" + t.upper()
        return App.Vector(*_AX[t])
    if isinstance(t, (tuple, list)):
        return App.Vector(*map(_f, t))
    return t


def _dir(v):
    v = App.Vector(v).normalize()
    for k, a in _AX.items():
        if (v - App.Vector(*a)).Length < 1e-6:
            return k
    return f"({v.x:.3f},{v.y:.3f},{v.z:.3f})"


def _pt(p):
    return f"({p.x:.3f},{p.y:.3f},{p.z:.3f})"


def _label(x):
    if isinstance(x, (tuple, list, App.Vector)):
        return _pt(_v(x))
    return getattr(x, "Label", type(x).__name__)


def gshape(x):
    """Shape of x; Bodies and Std Parts in global coordinates."""
    if not hasattr(x, "TypeId"):
        return x  # already a Part.Shape
    _fresh(x)
    s = Part.getShape(x)
    if x.TypeId in ("PartDesign::Body", "App::Part") and hasattr(x, "getGlobalPlacement"):
        s.Placement = x.getGlobalPlacement()  # includes parent Std Part placements
    return s


def _fresh(x):  # recompute so checks inside a step() see current geometry
    doc = getattr(x, "Document", None)
    if doc is not None:
        doc.recompute()


def bbox(s):
    """Tight bounding box (optimalBoundingBox on 0.20+)."""
    f = getattr(s, "optimalBoundingBox", None)  # tight on curved faces; 0.20+
    return f() if f else s.BoundBox


def spec(name, ok, detail=""):
    """Record and print one check. Details are printed only on failure."""
    if not ok:
        FAILS.append(name)
    print(f"SPEC {name}: {'ok' if ok else 'FAIL ' + detail}")
    return ok


def axes(obj):
    """Where a sketch or datum really points, in global axes."""
    _fresh(obj)
    pl =obj.getGlobalPlacement() if hasattr(obj, "getGlobalPlacement") else obj.Placement
    r = pl.Rotation
    print(f"AXES {obj.Label}: x={_dir(r.multVec(App.Vector(1, 0, 0)))} "
          f"y={_dir(r.multVec(App.Vector(0, 1, 0)))} "
          f"normal={_dir(r.multVec(App.Vector(0, 0, 1)))} origin={_pt(pl.Base)}")


def expect(x, size=None, lo=None, hi=None, volume=None, tol=0.01, vol_rel=1e-3):
    """Compare a result with a prediction written from the parameters.
    size/lo/hi are (x, y, z) with None to skip an axis; volume in mm^3."""
    s = gshape(x)
    bb = bbox(s)
    got = {"size": (bb.XLength, bb.YLength, bb.ZLength),
           "lo": (bb.XMin, bb.YMin, bb.ZMin), "hi": (bb.XMax, bb.YMax, bb.ZMax)}
    bad = []
    for key, want in (("size", size), ("lo", lo), ("hi", hi)):
        for a, w, g in zip("xyz", want or (), got[key]):
            if w is not None and abs(g - _f(w)) > tol:
                bad.append(f"{key}.{a}={g:.3f} want {_f(w):.3f}")
    if volume is not None and abs(s.Volume - _f(volume)) > max(abs(_f(volume)) * vol_rel, 1e-6):
        bad.append(f"vol={s.Volume:.2f} want {_f(volume):.2f}")
    return spec(f"expect {_label(x)}", not bad, "; ".join(bad))


def _centre(x):
    if isinstance(x, (tuple, list, App.Vector)):
        return _v(x)
    return bbox(gshape(x)).Center


def on_top(a, b, tol=TOL):
    """a rests on b along +Z: touching faces and overlapping footprints."""
    A, B = bbox(gshape(a)), bbox(gshape(b))
    dz = A.ZMin - B.ZMax
    xy = A.XMin < B.XMax and B.XMin < A.XMax and A.YMin < B.YMax and B.YMin < A.YMax
    return spec(f"{_label(a)} on {_label(b)}", abs(dz) < tol and xy,
                f"dz={dz:.4f} footprints_overlap={xy}")


def centred(a, b, along="xy", tol=TOL):
    """Bounding-box centres (or given points) coincide on the named axes."""
    ca, cb = _centre(a), _centre(b)
    off = {k: getattr(ca, k) - getattr(cb, k) for k in along.lower()}
    return spec(f"{_label(a)} centred on {_label(b)} in {along}",
                all(abs(d) < tol for d in off.values()),
                " ".join(f"d{k}={d:.4f}" for k, d in off.items()))


def fits(a, b, clearance, tol=TOL):
    """No overlap and at least `clearance` mm between a and b."""
    A, B = gshape(a), gshape(b)
    gap = A.distToShape(B)[0]
    overlap = A.common(B).Volume
    c = _f(clearance)
    return spec(f"{_label(a)}/{_label(b)} fit", overlap < 1e-6 and gap >= c - tol,
                f"gap={gap:.3f} want>={c:.3f} overlap={overlap:.4f}")


def solid_at(x, point, solid=True, tol=TOL):
    """Point is inside material (solid=True) or empty space, e.g. a hole or channel."""
    p = _v(point)
    inside = gshape(x).isInside(p, tol, True)
    return spec(f"{_label(x)} {'solid' if solid else 'empty'} at {_pt(p)}", inside == solid)


def _shape_local(x):
    _fresh(x)
    return x.Shape if hasattr(x, "Shape") else x  # names must match the feature


def faces(x, normal=None, extreme=None, where=None, angle=1.0):
    """Face names picked by normal ("+Z"), extreme ("max"/"min" along it) and a
    predicate on the centre. Pass the feature being dressed up (pad)."""
    n = _v(normal) if normal else None
    picks = []
    for i, f in enumerate(_shape_local(x).Faces, 1):
        u0, u1, v0, v1 = f.ParameterRange
        fn = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
        if n is not None and fn.getAngle(n) > math.radians(angle):
            continue
        c = f.CenterOfMass
        if where and not where(c):
            continue
        picks.append((i, f, fn, c))
    if extreme and n is not None and picks:
        pos = [p[3].dot(n) for p in picks]
        target = max(pos) if extreme == "max" else min(pos)
        picks = [p for p, d in zip(picks, pos) if abs(d - target) < TOL]
    for i, f, fn, c in picks:
        print(f"FACE Face{i} centre={_pt(c)} normal={_dir(fn)} area={f.Area:.2f}")
    if not picks:
        print("FACE none matched")
    return [f"Face{i}" for i, *_ in picks]


def edges(x, direction=None, length=None, where=None, angle=1.0, tol=0.01):
    """Edge names picked by direction (straight edges only), length and a
    predicate on the centre, e.g. where=lambda c: c.z > 19.9."""
    d = _v(direction) if direction else None
    picks = []
    for i, e in enumerate(_shape_local(x).Edges, 1):
        if length is not None and abs(e.Length - _f(length)) > tol:
            continue
        line = e.Curve.TypeId == "Part::GeomLine"
        t = e.tangentAt(e.FirstParameter)
        if d is not None:
            if not line or min(t.getAngle(d), t.getAngle(d * -1)) > math.radians(angle):
                continue
        c = e.CenterOfMass
        if where and not where(c):
            continue
        picks.append(i)
        kind = f"dir={_dir(t)}" if line else e.Curve.TypeId.split("::")[-1]
        print(f"EDGE Edge{i} centre={_pt(c)} length={e.Length:.2f} {kind}")
    if not picks:
        print("EDGE none matched")
    return [f"Edge{i}" for i in picks]


def placements(doc):
    """Markdown table of each Body/Std Part: global placement and bounding box."""
    rows = ["| part | base | yaw,pitch,roll | bbox min | bbox max |", "|---|---|---|---|---|"]
    for o in doc.Objects:
        if o.TypeId not in ("PartDesign::Body", "App::Part"):
            continue
        pl = o.getGlobalPlacement() if hasattr(o, "getGlobalPlacement") else o.Placement
        ypr = ",".join(f"{a:.1f}" for a in pl.Rotation.getYawPitchRoll())
        s = gshape(o)
        lo = hi = "-"
        if not s.isNull():
            bb = bbox(s)
            lo, hi = _pt(App.Vector(bb.XMin, bb.YMin, bb.ZMin)), _pt(App.Vector(bb.XMax, bb.YMax, bb.ZMax))
        rows.append(f"| {o.Label} | {_pt(pl.Base)} | {ypr} | {lo} | {hi} |")
    print("\n".join(rows))
