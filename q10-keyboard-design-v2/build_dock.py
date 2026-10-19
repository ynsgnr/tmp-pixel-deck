"""Pixel 10 Pro + BBQ10 (Q10) keyboard dock, v2. Change values in Params only.

Parts: PhoneMount (plate, ColL, ColR), MagnetCap (print 2), Keyboard (BBQ10
bottom case with a dock bar that carries PostL/PostR, and two magnet pads under
the bottom corners). Phone and MetalPin bodies are references. Magnets slide
into closed slots; only the cap centre magnet goes in from the bottom.
Positions: 1 keyboard docked below the phone on the posts; 2 keyboard keys-up
on the phone, pads on the caps; 3 keyboard leaning from the plate to the caps.

Run: SKILL_DIR=<repo root> FreeCADCmd build_dock.py
Outputs go to OUT_DIR (default: ./out next to this script).
"""
import math
import os
import re
import sys

import FreeCAD as App
import MeshPart
import Part
import Sketcher

HERE = os.environ.get("DOCK_DIR") or os.path.dirname(
    os.path.abspath(globals().get("__file__", "build_dock.py")))
SKILL_DIR = os.environ.get("SKILL_DIR", os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from fc import *  # noqa: E402,F403
import fc_spatial as sp  # noqa: E402

V = App.Vector
OUT = os.path.abspath(os.environ.get("OUT_DIR", os.path.join(HERE, "out")))
os.makedirs(OUT, exist_ok=True)
CASE_STEP = os.path.join(HERE, "ref", "Q10_Keyboard_bottom_case.STEP")
App.ParamGet("User parameter:BaseApp/Preferences/Document").SetBool("CreateBackupFiles", False)
doc = App.newDocument("Q10Dock")

# ---------------------------------------------------------------- helpers
PV = {}
ENV = {"tan": lambda a: math.tan(math.radians(a)), "sin": lambda a: math.sin(math.radians(a)),
       "cos": lambda a: math.cos(math.radians(a)), "abs": abs, "pi": math.pi, "sqrt": math.sqrt,
       "asin": lambda v: math.degrees(math.asin(v)), "atan": lambda v: math.degrees(math.atan(v))}


def ev(expr):
    """Value of a Params expression, for initial geometry and predictions."""
    return float(eval(re.sub(r"\bmm\b", "", str(expr).replace("Params.", "")), dict(ENV), PV))


def mm(e):
    """A bare 0 has no unit. FreeCAD rejects 0 - length."""
    return "0 mm" if e == "0" else e


def plane(body, role):
    return next(f for f in body.Origin.OriginFeatures if f.Role == role)


def sketch(body, name, role="XY_Plane", x=None, y=None, z=None, tilt=None):
    """Sketch on a Body origin plane. x, y, z: offset in plane axes. tilt: about plane x."""
    sk = body.newObject("Sketcher::SketchObject", name)
    sk.AttachmentSupport = (plane(body, role), [""])
    sk.MapMode = "FlatFace"
    base, exprs = [0.0, 0.0, 0.0], {}
    for i, (k, e) in enumerate((("x", x), ("y", y), ("z", z))):
        if e is not None:
            base[i] = ev(e)
            exprs[f".AttachmentOffset.Base.{k}"] = e
    rot = App.Rotation()
    if tilt is not None:
        rot = App.Rotation(V(1, 0, 0), ev(tilt))
        exprs[".AttachmentOffset.Rotation.Angle"] = tilt
    sk.AttachmentOffset = App.Placement(V(*base), rot)
    for k, e in exprs.items():
        sk.setExpression(k, e)
    return Sk(sk)


class Sk:
    """Adds fully constrained geometry. Every dimension is an expression."""

    def __init__(self, sk):
        self.sk = sk

    def dim(self, args, expr):
        i = self.sk.addConstraint(Sketcher.Constraint(*args, ev(expr)))
        self.sk.renameConstraint(i, f"dim{i}")
        self.sk.setExpression(f"Constraints.dim{i}", expr)

    def fix(self, g, pos, xe, ye):
        for e, kind, axis in ((xe, "DistanceX", -2), (ye, "DistanceY", -1)):
            if e == "0":
                self.sk.addConstraint(Sketcher.Constraint("PointOnObject", g, pos, axis))
            else:
                self.dim((kind, -1, 1, g, pos), e)

    def circle(self, cx, cy, d):
        g = self.sk.addGeometry(Part.Circle(V(ev(cx), ev(cy), 0), V(0, 0, 1), ev(d) / 2), False)
        self.fix(g, 3, cx, cy)
        self.dim(("Diameter", g), d)
        return g

    def profile(self, pts, segs=None):
        """Closed loop. segs[i] joins pts[i] to pts[i+1]: None = line,
        ("a", cx, cy, r, ccw) = arc tangent to its neighbours.
        An arc has a fixed centre, so the solver cannot flip it after a parameter change."""
        n = len(pts)
        segs = segs or [None] * n
        p = [V(ev(x), ev(y), 0) for x, y in pts]
        geo = []
        for i in range(n):
            a, b, s = p[i], p[(i + 1) % n], segs[i]
            if s is None:
                geo.append((self.sk.addGeometry(Part.LineSegment(a, b), False), 1, 2, None))
                continue
            c, r, ccw = V(ev(s[1]), ev(s[2]), 0), ev(s[3]), s[4]
            aa, ab = math.atan2(a.y - c.y, a.x - c.x), math.atan2(b.y - c.y, b.x - c.x)
            lo, hi = (aa, ab) if ccw else (ab, aa)
            while hi <= lo:
                hi += 2 * math.pi
            g = self.sk.addGeometry(Part.ArcOfCircle(Part.Circle(c, V(0, 0, 1), r), lo, hi), False)
            geo.append((g, 1, 2, s) if ccw else (g, 2, 1, s))
        for i in range(n):
            g, _, e, sa = geo[i - 1]
            g2, s2, _, sb = geo[i]
            if sa or sb:  # endpoint tangency includes coincidence
                self.sk.addConstraint(Sketcher.Constraint("Tangent", g, e, g2, s2))
            else:
                self.sk.addConstraint(Sketcher.Constraint("Coincident", g, e, g2, s2))
                self.fix(g2, s2, *pts[i])
        for g, _, _, s in geo:
            if s:
                self.fix(g, 3, mm(s[1]) if s[1] != "0" else "0", mm(s[2]) if s[2] != "0" else "0")
                self.dim(("Radius", g), s[3])

    def rrect(self, cx, cy, w, h, r):
        cx, cy = mm(cx), mm(cy)
        x0, x1 = f"({cx}) - ({w}) / 2", f"({cx}) + ({w}) / 2"
        y0, y1 = f"({cy}) - ({h}) / 2", f"({cy}) + ({h}) / 2"
        pts = [(x1, f"{y0} + {r}"), (x1, f"{y1} - {r}"), (f"{x1} - {r}", y1), (f"{x0} + {r}", y1),
               (x0, f"{y1} - {r}"), (x0, f"{y0} + {r}"), (f"{x0} + {r}", y0), (f"{x1} - {r}", y0)]
        xa, xb, ya, yb = f"{x1} - {r}", f"{x0} + {r}", f"{y1} - {r}", f"{y0} + {r}"
        self.profile(pts, [None, ("a", xa, ya, r, True), None, ("a", xb, ya, r, True),
                           None, ("a", xb, yb, r, True), None, ("a", xa, yb, r, True)])

    def rect(self, x0, y0, x1, y1):
        self.profile([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

    def slot(self, cx, cy, axis, sign, face):
        """Magnet slot: a disc at (cx, cy) and a channel out through the side face.
        axis "x" or "y", sign +1 or -1 = exit direction. The entry is SlotLip narrower per side."""
        cx, cy = mm(cx), mm(cy)
        fl = f"({sign}) * (({face}) - ({cx if axis == 'x' else cy}))"
        r, rl = "Params.PocketD / 2", "(Params.PocketD / 2 - Params.SlotLip)"
        al, ae = f"{fl} - Params.SlotLipL", f"{fl} + 1 mm"
        loc = [("0 mm", r), ("0 mm", f"-{r}"), (al, f"-{r}"), (al, f"-{rl}"),
               (ae, f"-{rl}"), (ae, rl), (al, rl), (al, r)]

        def to_sketch(a, b):  # rotations only, so the loop stays counter-clockwise
            if axis == "x":
                return f"({cx}) + ({sign}) * ({a})", f"({cy}) + ({sign}) * ({b})"
            if sign > 0:
                return f"({cx}) - ({b})", f"({cy}) + ({a})"
            return f"({cx}) + ({b})", f"({cy}) - ({a})"

        self.profile([to_sketch(a, b) for a, b in loc], [("a", cx, cy, r, True)] + [None] * 7)


def pad(body, name, sk, length, reverse=False, symmetric=False):
    f = body.newObject("PartDesign::Pad", name)
    f.Profile = sk.sk
    f.setExpression("Length", length)
    f.Reversed = reverse
    if symmetric:
        if hasattr(f, "SideType"):
            f.SideType = "Symmetric"
        else:
            f.Midplane = True
    return f


def pocket(body, name, sk, length=None, reverse=False, symmetric=False):
    f = body.newObject("PartDesign::Pocket", name)
    f.Profile = sk.sk
    if length is None:
        f.Type = "ThroughAll"
    else:
        f.setExpression("Length", length)
    f.Reversed = reverse
    if symmetric:
        if hasattr(f, "SideType"):
            f.SideType = "Symmetric"
        else:
            f.Midplane = True
    return f


def place(obj, x="0", y="0", z="0", rot_z=None):
    obj.Placement = App.Placement(V(ev(x), ev(y), ev(z)),
                                  App.Rotation(V(0, 0, 1), rot_z or 0))
    for k, e in (("x", x), ("y", y), ("z", z)):
        if e != "0":
            obj.setExpression(f".Placement.Base.{k}", e)


def rr_area(w, h, r):
    return w * h - (4 - math.pi) * r * r


def circ(d):
    return math.pi * d * d / 4


def vol(x):
    return sp.gshape(x).Volume


# ---------------------------------------------------------------- stage 1
decide("D1", "Z is up and normal to the screen. Origin: X on the phone centre line, "
       "Y on the line through the ColL and ColR axes, Z on the plate top face.",
       "The column axes are the mating datum for the keyboard posts.")
decide("D2", "The phone extends to -Y. In position 1 the keyboard extends to +Y.",
       "Position 1 is the keyboard continuous with the screen.")
decide("D3", "Clearance is 0.2 mm per side. No press fits.",
       "User: FDM printer, 0.2 mm per side, parts are assembled.")
decide("D4", "Method: one VarSet, one Body per part in one Std Part. No master sketch.",
       "All interfaces are Params expressions, so a master sketch adds no data.")
decide("D5", "The keyboard Body starts from the BBQ10 bottom case STEP (MIT licence).",
       "The user STL is not a closed solid. The STEP is the same case without the old posts.")
decide("D6", "Magnets are 5 mm diameter x 2 mm, poles on the flat faces, in a 3x3 array.",
       "User measurements. Magnet size drives the cap, column and ear size.")
decide("D7", "Metal pin: 2 mm banana male. Its spring is 3.5 mm at rest, in the middle of the "
       "contact. The base is not measured: PinHeadD, PinHeadL and PinShankL are assumptions.",
       "User: 2 mm plug, 3.5 mm where it flexes, base not in the measurement.")

with step("S1", "Make the parameters.", "All dimensions come from Params."):
    asm = doc.addObject("App::Part", "Dock")
    P = doc.addObject("App::VarSet", "Params")
    LEN, DST, ANG = "App::PropertyLength", "App::PropertyDistance", "App::PropertyAngle"

    def param(name, kind, value, use):
        P.addProperty(kind, name, "Params", use)
        if isinstance(value, str):
            P.setExpression(name, value)
            PV[name] = ev(value)
        else:
            setattr(P, name, value)
            PV[name] = float(value)

    for name, kind, value, use in [
        ("Clearance", LEN, 0.2, "Gap per side between mating printed parts."),
        ("PhoneL", LEN, 157.0, "Phone in Pixelsnap case, length."),
        ("PhoneW", LEN, 77.0, "Phone in Pixelsnap case, width."),
        ("PhoneT", LEN, 10.0, "Phone in Pixelsnap case, thickness."),
        ("PhoneR", LEN, 10.0, "Phone corner radius in plan."),
        ("PlateT", LEN, 4.4, "Mount plate thickness."),
        ("PlateCornerR", LEN, 3.0, "Plate corner radius at the column end."),
        ("LipT", LEN, 2.0, "Corner lip wall thickness."),
        ("LipH", LEN, 3.0, "Corner lip height above the plate."),
        ("LipLen", LEN, 15.0, "Corner lip length along each phone edge from the corner."),
        ("RingID", LEN, 46.0, "MagSafe steel ring inner diameter."),
        ("RingOD", LEN, 54.0, "MagSafe steel ring outer diameter."),
        ("RingDepth", LEN, 1.0, "Ring recess depth in the plate top."),
        ("RingOffset", DST, 0.0, "Ring centre offset from the phone centre along +Y."),
        ("MagD", LEN, 5.0, "Magnet diameter."),
        ("MagT", LEN, 2.0, "Magnet thickness."),
        ("MagWeb", LEN, 1.0, "Wall between two magnet pockets."),
        ("MagEdge", LEN, 1.4, "Wall between a magnet pocket and the cap side."),
        ("CapH", LEN, 5.8, "Magnet cap height on the flat part."),
        ("ScreenGap", LEN, 0.5, "Cap top above the screen surface."),
        ("PinD", LEN, 2.0, "Metal pin nominal diameter (2 mm banana). The post bore grips it."),
        ("PinSpringD", LEN, 3.5, "Metal pin spring diameter at rest, in the middle of the contact."),
        ("PinShankL", LEN, 6.0, "Assumed: metal pin contact length below the base."),
        ("PinHeadD", LEN, 5.0, "Assumed: metal pin base diameter."),
        ("PinHeadL", LEN, 1.5, "Assumed: metal pin base length."),
        ("PostOD", LEN, 8.0, "Keyboard post outer diameter."),
        ("PostBoreD", LEN, 3.6, "Measured from the fitted test post: bore for the banana plug."),
        ("PostLobeD", LEN, 3.28, "Measured from the fitted test post: diameter across the 3 lobes."),
        ("PostReliefD", LEN, 4.14, "Measured from the fitted test post: relief between the lobes."),
        ("PostLobeL", LEN, 2.0, "Measured from the fitted test post: lobe length at the bore mouth."),
        ("LobeR", LEN, 0.5, "Radius of each lobe rib."),
        ("SocketDepth", LEN, 6.0, "Column socket depth from the plate bottom."),
        ("PostTipGap", LEN, 0.3, "Gap between the post tip and the socket ceiling."),
        ("SlitW", LEN, 0.8, "Width of the two slits in each post."),
        ("SlitBottom", LEN, 1.0, "Uncut post length above the ear."),
        ("PostFillet", LEN, 0.6, "Fillet radius at the post base."),
        ("PostChamfer", LEN, 0.4, "Chamfer at the post tip."),
        ("MouthChamfer", LEN, 0.8, "Chamfer at the socket mouth."),
        ("EdgeR", LEN, 2.0, "Corner radius of columns, caps and ears in plan."),
        ("SkinT", LEN, 0.6, "Skin between a magnet and the mating face."),
        ("SlotLip", LEN, 0.3, "Slot entry is this much narrower per side; the magnet snaps past it."),
        ("SlotLipL", LEN, 1.0, "Length of the narrow slot entry."),
        ("CheekT", LEN, 3.0, "Dock bar cheek thickness outside each case side wall."),
        ("CheekL", LEN, 20.0, "Cheek length down each case side wall."),
        ("CheekIn", LEN, 0.3, "Cheek overlap into the side wall."),
        ("BaseIn", LEN, 0.6, "Base slab overlap under the top wall."),
        ("TongueL", LEN, 20.0, "Tongue length past the ears. It bears on the plate bottom in position 1."),
        ("KbW", LEN, 71.81, "Measured: BBQ10 bottom case width."),
        ("KbH", LEN, 7.0, "Measured: BBQ10 bottom case height."),
        ("KbFloorZ", LEN, 1.2, "Measured: top wall openings start above this height."),
        ("KbDepth", LEN, 50.58, "Measured: case depth from the top wall face to the bottom edge."),
        ("KbCornerR", LEN, 12.35, "Measured: case bottom corner radius in plan."),
        ("KbScrewX", LEN, 31.05, "Measured: bottom screw hole distance from the centre line."),
        ("KbScrewY", DST, -42.38, "Measured: bottom screw hole Y."),
        ("KbScrewHeadD", LEN, 4.2, "Measured: bottom screw countersink diameter."),
        ("KbTabY", LEN, 1.0, "Measured: top-edge tabs protrude this far past the wall."),
        ("KbTabZ", LEN, 2.0, "Measured: tab bottom above the case floor face."),
        ("Pitch", LEN, "Params.MagD + 2 * Params.Clearance + Params.MagWeb",
         "Derived. Magnet pitch."),
        ("PocketD", LEN, "Params.MagD + 2 * Params.Clearance", "Derived. Magnet pocket diameter."),
        ("PocketDepth", LEN, "Params.MagT + Params.Clearance", "Derived. Magnet pocket depth."),
        ("CapW", LEN, "2 * Params.Pitch + Params.PocketD + 2 * Params.MagEdge",
         "Derived. Square size of cap, column and ear."),
        ("ColTop", LEN, "Params.PhoneT + Params.ScreenGap - Params.CapH",
         "Derived. Column top above the plate top."),
        ("PostX", LEN, "Params.KbW / 2 - Params.CapW / 2",
         "Derived. Column and post axis distance from the centre line."),
        ("SocketD", LEN, "Params.PostOD + 2 * Params.Clearance", "Derived. Socket diameter."),
        ("PinBoreD", LEN, "Params.PinSpringD + 2 * Params.Clearance",
         "Derived. Column pin bore. The spring passes it freely."),
        ("HeadBoreD", LEN, "Params.PinHeadD + 2 * Params.Clearance",
         "Derived. Collar counterbore diameter."),
        ("HeadBoreDepth", LEN, "Params.PinHeadL + Params.Clearance",
         "Derived. Collar counterbore depth."),
        ("PostL", LEN, "Params.SocketDepth - Params.PostTipGap", "Derived. Post length above the ear."),
        ("EarT", LEN, "Params.KbH", "Derived. Dock bar height, equal to the case height."),
        ("BarY", LEN, "Params.KbTabY + Params.Clearance", "Derived. Dock bar face near the case."),
        ("EarY", LEN, "Params.BarY + Params.CapW / 2",
         "Derived. Post axis distance from the keyboard top wall."),
        ("PhoneTopY", DST, "-Params.CapW / 2 - Params.LipT - Params.Clearance",
         "Derived. Y of the phone edge near the columns."),
        ("RingY", DST, "Params.PhoneTopY - Params.PhoneL / 2 + Params.RingOffset",
         "Derived. Y of the ring centre."),
        ("PlateW", LEN, "Params.PhoneW + 2 * Params.Clearance + 2 * Params.LipT",
         "Derived. Plate width."),
        ("PadT", LEN, "Params.SkinT + Params.PocketDepth", "Derived. Magnet pad thickness."),
        ("PadY", DST, "-Params.KbDepth + Params.CapW / 2", "Derived. Magnet pad centre Y."),
        ("ScrewHoleD", LEN, "Params.KbScrewHeadD + 2 * Params.Clearance",
         "Derived. Screw access hole through the pad."),
        ("KbLen", LEN, "Params.KbDepth + Params.BarY + Params.CapW + Params.TongueL",
         "Derived. Keyboard end-to-end length."),
        ("KinkAngle", ANG, "asin((Params.PhoneT + Params.ScreenGap) / sqrt(Params.KbLen * Params.KbLen"
         " + Params.PadT * Params.PadT)) + atan(Params.PadT / Params.KbLen)",
         "Derived. Position 3: right triangle of keyboard length and column height."),
        ("KinkY", DST, "-Params.Pitch / 2", "Derived. Kink line Y on the cap."),
        ("KinkRowY", DST, "Params.KinkY - (Params.MagEdge + Params.PocketD / 2) * cos(Params.KinkAngle)",
         "Derived. Kink magnet row Y: under the pad edge row in position 3."),
    ]:
        param(name, kind, value, use)
    doc.recompute()
    spec("params evaluate", abs(P.CapW.Value - PV["CapW"]) < 1e-6, f"CapW {P.CapW} vs {PV['CapW']}")

g = dict(PV)  # short names for predictions
# Pad magnets (i outward, j toward the keyboard top). The screw hole and the
# rounded case corner take (1, 0) and (1, -1); the centre has no free side.
PAD_MAGNETS = [(-1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
Clr, CapW, R = g["Clearance"], g["CapW"], g["EdgeR"]
decide("D8", f"Cap and column are {CapW:.2f} mm square.",
       "This is the smallest square that holds the 3x3 magnet array.")

with step("S2", "Check the interface stack from the parameters.",
          "Wall and engagement sizes must be printable before modelling."):
    tip = g["ColTop"] - g["HeadBoreDepth"] - g["PinShankL"]
    web = (g["ColTop"] - g["HeadBoreDepth"]) - (-g["PlateT"] + g["SocketDepth"])
    post_top = -g["PlateT"] - Clr + g["PostL"]
    spec("pin tip recessed 0.5 mm or more", tip >= -g["PlateT"] + 0.5, f"tip Z {tip:.2f}")
    spec("pin reaches 1 mm into the socket", tip <= -g["PlateT"] + g["SocketDepth"] - 1,
         f"tip Z {tip:.2f}")
    spec("web between socket and collar >= 1.2 mm", web >= 1.2, f"web {web:.2f}")
    spec("pin enters the post bore >= 2 mm", post_top - tip >= 2, f"{post_top - tip:.2f}")
    spec("post wall >= 1.2 mm", (g["PostOD"] - g["PostReliefD"]) / 2 >= 1.2)
    spec("lobes stay inside the post", g["PostLobeD"] / 2 + 2 * g["LobeR"] < g["PostOD"] / 2 - 1)
    spring = g["ColTop"] - g["HeadBoreDepth"] - g["PinShankL"] / 2
    spec("pin spring is >= 1 mm inside the post bore", post_top - spring >= 1.0,
         f"spring Z {spring:.2f}, post top Z {post_top:.2f}")
    spec("spring is squeezed by the post lobes", g["PinSpringD"] > g["PostLobeD"])
    spec("slot lip leaves a channel", 0 < g["SlotLip"] < g["PocketD"] / 2 - 1)
    for i, j in PAD_MAGNETS:
        d = math.hypot(i * g["Pitch"] - (g["KbScrewX"] - g["PostX"]),
                       j * g["Pitch"] - (g["KbScrewY"] - g["PadY"]))
        spec(f"pad magnet ({i},{j}) clear of the screw hole by 0.6 mm",
             d >= g["PocketD"] / 2 + g["ScrewHoleD"] / 2 + 0.6, f"{d:.2f}")
        mx, my = g["PostX"] + i * g["Pitch"], g["PadY"] + j * g["Pitch"]
        cx, cy = g["KbW"] / 2 - g["KbCornerR"], -g["KbDepth"] + g["KbCornerR"]
        d = math.hypot(mx - cx, my - cy)
        spec(f"pad magnet ({i},{j}) inside the case corner by 0.6 mm",
             mx <= cx or my >= cy or d + g["PocketD"] / 2 <= g["KbCornerR"] - 0.6, f"{d:.2f}")
    spec("edge-row channel clear of the screw hole by 0.4 mm",
         g["KbScrewX"] - g["ScrewHoleD"] / 2 - (g["PostX"] + g["PocketD"] / 2) >= 0.4)
    spec("column wall around socket >= 2 mm", (CapW - g["SocketD"]) / 2 >= 2)
    spec("post fillet stays inside the socket chamfer",
         g["PostOD"] / 2 + g["PostFillet"] <= g["SocketD"] / 2 + g["MouthChamfer"] - Clr)
    kk = math.radians(g["KinkAngle"])
    surf = g["CapH"] - (g["KinkY"] - g["KinkRowY"]) * math.tan(kk)
    deep = g["SkinT"] + g["PocketDepth"]
    inner = g["KinkRowY"] + g["PocketD"] / 2 * math.cos(kk) + deep * math.sin(kk)
    spec("kink slot wall to centre row >= 0.8 mm", -g["PocketD"] / 2 - inner >= 0.8,
         f"wall {-g['PocketD'] / 2 - inner:.2f}")
    v_exit = (-CapW / 2 - g["KinkRowY"] - deep * math.sin(kk)) / math.cos(kk)
    floor = surf + v_exit * math.sin(kk) - deep * math.cos(kk)
    spec("kink slot floor at the cap side >= 0.5 mm", floor >= 0.5, f"floor {floor:.2f}")
    spec("flat slots clear the centre magnet",
         g["CapH"] - g["SkinT"] - g["PocketDepth"] >= g["PocketDepth"] + 0.6)
    print(f"STACK pin tip Z={tip:.2f} web={web:.2f} post top Z={post_top:.2f} "
          f"kink slot floor={floor:.2f}")

# ---------------------------------------------------------------- stage 3
with step("S3", "Pad the plate down from Z = 0.", "The phone back rests on Z = 0."):
    mount = doc.addObject("PartDesign::Body", "PhoneMount")
    asm.addObject(mount)
    sk = sketch(mount, "PlateSketch")
    W2, YE, RC = "Params.PlateW / 2", "Params.CapW / 2", "Params.PlateCornerR"
    sk.profile([(W2, "Params.RingY"), (W2, f"{YE} - {RC}"), (f"{W2} - {RC}", YE),
                (f"-{W2} + {RC}", YE), (f"-{W2}", f"{YE} - {RC}"), (f"-{W2}", "Params.RingY")],
               [None, ("a", f"{W2} - {RC}", f"{YE} - {RC}", RC, True), None,
                ("a", f"-{W2} + {RC}", f"{YE} - {RC}", RC, True), None,
                ("a", "0", "Params.RingY", W2, True)])
    plate = pad(mount, "Plate", sk, "Params.PlateT", reverse=True)
    pw, rc = g["PlateW"], g["PlateCornerR"]
    a_plate = pw * (CapW / 2 - g["RingY"]) - 2 * (1 - math.pi / 4) * rc * rc + math.pi * pw * pw / 8
    expect(mount, size=(pw, CapW / 2 - g["RingY"] + pw / 2, g["PlateT"]),
           lo=(-pw / 2, g["RingY"] - pw / 2, -g["PlateT"]), volume=a_plate * g["PlateT"])
    v_mount = a_plate * g["PlateT"]

with step("S4", "Pad ColL and ColR up from the plate.", "Columns stand outside the phone, at +Y."):
    sk = sketch(mount, "ColumnSketch")
    for sx in ("-", ""):
        sk.rrect(f"{sx}Params.PostX", "0", "Params.CapW", "Params.CapW", "Params.EdgeR")
    pad(mount, "Columns", sk, "Params.ColTop")
    v_mount += 2 * rr_area(CapW, CapW, R) * g["ColTop"]
    expect(mount, hi=(None, CapW / 2, g["ColTop"]), volume=v_mount)

with step("S5", "Pad the two corner lips.", "The lips locate the phone corners (R = PhoneR)."):
    sk = sketch(mount, "LipSketch")
    for s in (1, -1):
        sx = "" if s > 0 else "-"
        cx = f"{sx}(Params.PhoneW / 2 - Params.PhoneR)"
        cy = "Params.PhoneTopY - Params.PhoneR"
        xi = f"{sx}(Params.PhoneW / 2 + Params.Clearance)"
        xo = f"{sx}(Params.PhoneW / 2 + Params.Clearance + Params.LipT)"
        xs = f"{sx}(Params.PhoneW / 2 - Params.LipLen)"
        yi, yo = "Params.PhoneTopY + Params.Clearance", "Params.PhoneTopY + Params.Clearance + Params.LipT"
        yb = "Params.PhoneTopY - Params.LipLen"
        ri, ro = "Params.PhoneR + Params.Clearance", "Params.PhoneR + Params.Clearance + Params.LipT"
        pts = [(xs, yi), (cx, yi), (xi, cy), (xi, yb), (xo, yb), (xo, cy), (cx, yo), (xs, yo)]
        segs = [None, ("a", cx, cy, ri, s < 0), None, None, None, ("a", cx, cy, ro, s > 0),
                None, None]  # the mirror flips the arc sense
        sk.profile(pts, segs)
    pad(mount, "Lips", sk, "Params.LipH")
    ri_, ro_ = g["PhoneR"] + Clr, g["PhoneR"] + Clr + g["LipT"]
    a_lip = 2 * (g["LipLen"] - g["PhoneR"]) * g["LipT"] + math.pi / 4 * (ro_ ** 2 - ri_ ** 2)
    v_mount += 2 * a_lip * g["LipH"]
    expect(mount, hi=(None, None, g["ColTop"]), volume=v_mount)

with step("S6", "Cut the ring recess in the plate top.", "A stick-on MagSafe ring holds the phone."):
    sk = sketch(mount, "RingSketch")
    sk.circle("0", "Params.RingY", "Params.RingOD + 2 * Params.Clearance")
    sk.circle("0", "Params.RingY", "Params.RingID - 2 * Params.Clearance")
    pocket(mount, "RingRecess", sk, "Params.RingDepth")
    v_mount -= (circ(g["RingOD"] + 2 * Clr) - circ(g["RingID"] - 2 * Clr)) * g["RingDepth"]
    expect(mount, volume=v_mount)
    solid_at(mount, V(0, g["RingY"] + (g["RingID"] + g["RingOD"]) / 4, -g["RingDepth"] / 2), solid=False)

with step("S7", "Cut the post sockets up from the plate bottom.", "Posts enter from below the mount."):
    sk = sketch(mount, "SocketSketch", z="-Params.PlateT")
    for sx in ("-", ""):
        sk.circle(f"{sx}Params.PostX", "0", "Params.SocketD")
    pocket(mount, "Sockets", sk, "Params.SocketDepth", reverse=True)
    v_mount -= 2 * circ(g["SocketD"]) * g["SocketDepth"]
    expect(mount, volume=v_mount)
    solid_at(mount, V(g["PostX"], 0, -g["PlateT"] + g["SocketDepth"] - 0.1), solid=False)
    solid_at(mount, V(g["PostX"], 0, -g["PlateT"] + g["SocketDepth"] + 0.1))

with step("S8", "Cut the pin bores and collar counterbores from the column top.",
          "The pin goes in from the top. Bore = PinSpringD + 2 x Clearance."):
    sk = sketch(mount, "PinBoreSketch", z="Params.ColTop")
    for sx in ("-", ""):
        sk.circle(f"{sx}Params.PostX", "0", "Params.PinBoreD")
    pocket(mount, "PinBores", sk)
    sk = sketch(mount, "HeadBoreSketch", z="Params.ColTop")
    for sx in ("-", ""):
        sk.circle(f"{sx}Params.PostX", "0", "Params.HeadBoreD")
    pocket(mount, "HeadBores", sk, "Params.HeadBoreDepth")
    v_mount -= 2 * circ(g["PinBoreD"]) * (g["ColTop"] + g["PlateT"] - g["SocketDepth"])
    v_mount -= 2 * (circ(g["HeadBoreD"]) - circ(g["PinBoreD"])) * g["HeadBoreDepth"]
    expect(mount, volume=v_mount)
    solid_at(mount, V(-g["PostX"] + g["PinSpringD"] / 2 + Clr / 2, 0, 0), solid=False)

# Magnet caps: identical Bodies, origin on the axis at the cap bottom.
caps = []
for side, sx in (("L", "-"), ("R", "")):
    with step(f"S9{side}", f"Pad the MagnetCap{side} block.", "The cap covers the column top."):
        cap = doc.addObject("PartDesign::Body", f"MagnetCap{side}")
        asm.addObject(cap)
        sk = sketch(cap, "CapSketch")
        sk.rrect("0", "0", "Params.CapW", "Params.CapW", "Params.EdgeR")
        pad(cap, "Block", sk, "Params.CapH")
        place(cap, x=f"{sx}Params.PostX", z="Params.ColTop")
        v_cap = rr_area(CapW, CapW, R) * g["CapH"]
        xc = -g["PostX"] if sx else g["PostX"]
        expect(cap, size=(CapW, CapW, g["CapH"]), lo=(xc - CapW / 2, -CapW / 2, g["ColTop"]),
               volume=v_cap)

    with step(f"S10{side}", f"Cut the kink bevel on the -Y side of MagnetCap{side}.",
              "The keyboard rests on the bevel at KinkAngle in the landscape position."):
        sk = sketch(cap, "BevelSketch", role="YZ_Plane")
        far = "(-Params.CapW / 2 - 1 mm)"
        sk.profile([("Params.KinkY", "Params.CapH"),
                    (far, f"Params.CapH - (Params.KinkY - {far}) * tan(Params.KinkAngle)"),
                    (far, "Params.CapH + 1 mm"), ("Params.KinkY", "Params.CapH + 1 mm")])
        pocket(cap, "Bevel", sk, symmetric=True)
        # Wedge volume over the rounded footprint, from the parameters.
        n, y0, y1 = 400, -CapW / 2, g["KinkY"]
        wedge = 0.0
        for i in range(n):
            y = y0 + (i + 0.5) * (y1 - y0) / n
            dy = y - (-CapW / 2 + R)
            width = CapW - 2 * R + (2 * math.sqrt(max(R * R - dy * dy, 0)) if dy < 0 else 2 * R)
            wedge += width * (y1 - y) * math.tan(kk) * (y1 - y0) / n
        v_cap -= wedge
        expect(cap, volume=v_cap)
        solid_at(cap, V(cap.Placement.Base.x, -CapW / 2 + 0.3,
                        g["ColTop"] + g["CapH"] - 0.3), solid=False)

    with step(f"S11{side}", f"Cut eight magnet slots and the centre pocket in MagnetCap{side}.",
              "Each magnet slides in from the nearest side, under a skin. The kink row exits at -Y."):
        top, mid = g["ColTop"] + g["CapH"] - g["SkinT"], g["PocketDepth"] / 2
        sk = sketch(cap, "FlatSlotSketch", z="Params.CapH - Params.SkinT")
        for cx in ("-Params.Pitch", "0", "Params.Pitch"):
            sk.slot(cx, "Params.Pitch", "y", 1, "Params.CapW / 2")
        sk.slot("Params.Pitch", "0", "x", 1, "Params.CapW / 2")
        sk.slot("-Params.Pitch", "0", "x", -1, "-Params.CapW / 2")
        pocket(cap, "FlatSlots", sk, "Params.PocketDepth")
        # The centre magnet goes in from the bottom. The column top closes the pocket.
        sk = sketch(cap, "CentrePocketSketch")
        sk.circle("0", "0", "Params.PocketD")
        pocket(cap, "CentrePocket", sk, "Params.PocketDepth", reverse=True)
        sk = sketch(cap, "KinkSlotSketch",
                    y="Params.KinkRowY + Params.SkinT * sin(Params.KinkAngle)",
                    z="Params.CapH - (Params.KinkY - Params.KinkRowY) * tan(Params.KinkAngle)"
                      " - Params.SkinT * cos(Params.KinkAngle)",
                    tilt="Params.KinkAngle")
        face = ("(-Params.CapW / 2 - Params.KinkRowY - Params.SkinT * sin(Params.KinkAngle))"
                " / cos(Params.KinkAngle)")
        for cx in ("-Params.Pitch", "0", "Params.Pitch"):
            sk.slot(cx, "0", "y", -1, face)
        pocket(cap, "KinkSlots", sk, "Params.PocketDepth")
        if side == "L":
            axes(sk.sk)  # want normal=(0,-sin K,cos K)
        for dx in (-g["Pitch"], 0, g["Pitch"]):
            solid_at(cap, V(xc + dx, g["Pitch"], top - mid), solid=False)
            solid_at(cap, V(xc + dx, g["Pitch"], top + g["SkinT"] / 2))
            solid_at(cap, V(xc + dx, CapW / 2 - 0.2, top - mid), solid=False)
        for dx in (-g["Pitch"], g["Pitch"]):
            solid_at(cap, V(xc + dx, 0, top - mid), solid=False)
        solid_at(cap, V(xc, 0, g["ColTop"] + mid), solid=False)
        solid_at(cap, V(xc, 0, g["ColTop"] + g["PocketDepth"] + 0.3))
        d = g["SkinT"] + mid
        kz = g["ColTop"] + surf - d * math.cos(kk)
        for dx in (-g["Pitch"], 0, g["Pitch"]):
            solid_at(cap, V(xc + dx, g["KinkRowY"] + d * math.sin(kk), kz), solid=False)
            solid_at(cap, V(xc + dx, g["KinkRowY"] + g["SkinT"] / 2 * math.sin(kk),
                            g["ColTop"] + surf - g["SkinT"] / 2 * math.cos(kk)))
        caps.append(cap)

# Keyboard: case placed in the keyboard frame KB, then ears, posts and ribs.
with step("S12", "Load the BBQ10 bottom case into the keyboard frame KB.",
          "KB: floor face at z = 0, keys at +z, top wall face at y = 0, centred on x."):
    # A BaseFeature ignores shape placements, so move the geometry itself.
    case = Part.read(CASE_STEP)
    case.transformShape(App.Rotation(V(0, 1, 0), 180).toMatrix(), True)  # floor is on top in the STEP
    cb = case.BoundBox
    case.transformShape(App.Placement(V(-(cb.XMin + cb.XMax) / 2, 0, -cb.ZMin),
                                      App.Rotation()).toMatrix(), True)
    wall_y = max(w.BoundBox.YMax for w in case.slice(V(0, 0, 1), 1.0))  # below the tabs
    case.transformShape(App.Placement(V(0, -wall_y, 0), App.Rotation()).toMatrix(), True)
    spec("case geometry carries no placement", case.Placement.isIdentity())
    ref = doc.addObject("Part::Feature", "KbCaseRef")
    ref.Shape = case
    ref.Visibility = False
    asm.addObject(ref)
    kb = doc.addObject("PartDesign::Body", "Keyboard")
    asm.addObject(kb)
    kb.BaseFeature = ref
    doc.recompute()
    cb = case.BoundBox
    spec("case width matches KbW", abs(cb.XLength - g["KbW"]) < 0.05, f"{cb.XLength:.2f}")
    spec("tabs protrude KbTabY", abs(cb.YMax - g["KbTabY"]) < 0.05, f"{cb.YMax:.2f}")
    tabs = [w.BoundBox for w in case.slice(V(0, 1, 0), 0.5 * g["KbTabY"])
            if w.BoundBox.ZMin > 0.5]
    spec("tabs start at or above KbTabZ", bool(tabs) and all(t.ZMin >= g["KbTabZ"] for t in tabs),
         str([(round(t.XMin, 2), round(t.XMax, 2), round(t.ZMin, 2)) for t in tabs]))
    print("TABS x ranges", [(round(t.XMin, 2), round(t.XMax, 2)) for t in tabs])
    v_kb = case.Volume

with step("S13", "Pad the base slab, then the dock bar with cheeks and tongue.",
          "Phone torque goes through a full-height bar into both case side walls."):
    XB, XI = "Params.KbW / 2 + Params.CheekT", "Params.KbW / 2 - Params.CheekIn"
    YE, XT = "Params.EarY + Params.CapW / 2", "Params.PostX - Params.CapW / 2"
    YT = f"{YE} + Params.TongueL"
    # Slab first: a Body keeps one solid, so each new pad must touch the case.
    sk = sketch(kb, "BaseSlabSketch")
    sk.rect(f"-({XI})", "-Params.BaseIn", XI, "Params.BarY + 1 mm")
    pad(kb, "BaseSlab", sk, "Params.KbFloorZ - Params.Clearance")
    sk = sketch(kb, "DockBarSketch")
    sk.profile([(f"-({XB})", "-Params.CheekL"), (f"-({XI})", "-Params.CheekL"),
                (f"-({XI})", "Params.BarY"), (XI, "Params.BarY"), (XI, "-Params.CheekL"),
                (XB, "-Params.CheekL"), (XB, YE), (XT, YE), (XT, YT), (f"-({XT})", YT),
                (f"-({XT})", YE), (f"-({XB})", YE)])
    pad(kb, "DockBar", sk, "Params.EarT")
    xb, xt = g["KbW"] / 2 + g["CheekT"], g["PostX"] - CapW / 2
    yt = g["EarY"] + CapW / 2 + g["TongueL"]
    expect(kb, lo=(-xb, None, 0), hi=(xb, yt, g["KbH"]))
    solid_at(kb, V(g["PostX"], g["EarY"], g["EarT"] / 2))
    solid_at(kb, V(0, yt - 0.5, g["EarT"] / 2))
    solid_at(kb, V(xb - 0.5, -g["CheekL"] + 0.5, g["EarT"] / 2))
    for t in tabs:  # the bar keeps Clearance to the tabs and the wall openings
        solid_at(kb, V((t.XMin + t.XMax) / 2, g["KbTabY"] + Clr / 2, g["KbTabZ"] + 1), solid=False)
    solid_at(kb, V(g["PostX"] - g["Pitch"], 0.5, (g["KbFloorZ"] + g["KbTabZ"]) / 2), solid=False)

with step("S15", "Pad the posts and cut the pin bore through post and ear.",
          "Bore sizes copy the test post that fits the banana plug."):
    sk = sketch(kb, "PostSketch", z="Params.EarT")
    for sx in ("-", ""):
        sk.circle(f"{sx}Params.PostX", "Params.EarY", "Params.PostOD")
    pad(kb, "Posts", sk, "Params.PostL")
    sk = sketch(kb, "PostBoreSketch", z="Params.EarT + Params.PostL")
    for sx in ("-", ""):
        sk.circle(f"{sx}Params.PostX", "Params.EarY", "Params.PostBoreD")
    pocket(kb, "PostBores", sk)
    # The bore mouth copies the fitted test post: a relief with three lobes.
    sk = sketch(kb, "ReliefSketch", z="Params.EarT + Params.PostL")
    for sx in ("-", ""):
        sk.circle(f"{sx}Params.PostX", "Params.EarY", "Params.PostReliefD")
    pocket(kb, "Relief", sk, "Params.PostLobeL")
    sk = sketch(kb, "LobeSketch", z="Params.EarT + Params.PostL")
    rl = "(Params.PostLobeD / 2 + Params.LobeR)"
    for sx in ("-", ""):
        for cs, sn in ((0, 1), (-0.8660254, -0.5), (0.8660254, -0.5)):  # 90, 210, 330 deg
            sk.circle(f"{sx}Params.PostX + ({cs}) * {rl}", f"Params.EarY + ({sn}) * {rl}",
                      "2 * Params.LobeR")
    pad(kb, "Lobes", sk, "Params.PostLobeL", reverse=True)
    expect(kb, hi=(None, None, max(g["EarT"] + g["PostL"], 7.0)))
    top = g["EarT"] + g["PostL"]
    solid_at(kb, V(g["PostX"], g["EarY"], g["EarT"] / 2), solid=False)
    solid_at(kb, V(g["PostX"] + g["PostOD"] / 2 - 0.4, g["EarY"], top / 2 + g["EarT"] / 2))
    solid_at(kb, V(g["PostX"], g["EarY"] + g["PostLobeD"] / 2 + 0.1, top - 0.5))
    solid_at(kb, V(g["PostX"], g["EarY"] - g["PostReliefD"] / 2 + 0.1, top - 0.5), solid=False)
    solid_at(kb, V(g["PostX"], g["EarY"] + g["PostBoreD"] / 2 - 0.1, top - g["PostLobeL"] - 0.5),
             solid=False)

with step("S16", "Cut two slits across each post.", "The slits let the post flex to fit the socket."):
    sk = sketch(kb, "SlitSketch", z="Params.EarT + Params.PostL")
    for sx in ("-", ""):
        sk.rect(f"{sx}Params.PostX - Params.PostOD / 2 - 1 mm", "Params.EarY - Params.SlitW / 2",
                f"{sx}Params.PostX + Params.PostOD / 2 + 1 mm", "Params.EarY + Params.SlitW / 2")
    pocket(kb, "Slits", sk, "Params.PostL - Params.SlitBottom")
    solid_at(kb, V(g["PostX"] + g["PostOD"] / 2 - 0.4, g["EarY"], g["EarT"] + g["PostL"] - 0.5),
             solid=False)
    solid_at(kb, V(g["PostX"] + g["PostOD"] / 2 - 0.4, g["EarY"], g["EarT"] + g["SlitBottom"] / 2))

with step("S17", "Pad two magnet pads under the bottom corners and cut the screw access holes.",
          "Pads meet the caps in position 2 and the kink row in position 3."):
    yb, yt = "-Params.KbDepth", "-Params.KbDepth + Params.CapW"
    ya = "-Params.KbDepth + Params.KbCornerR"
    sk = sketch(kb, "PadSketch")
    for s_, sx in ((1, ""), (-1, "-")):
        x0 = f"{sx}(Params.PostX - Params.CapW / 2)"
        xa, xr = f"{sx}(Params.KbW / 2 - Params.KbCornerR)", f"{sx}(Params.KbW / 2)"
        sk.profile([(x0, yb), (xa, yb), (xr, ya), (xr, yt), (x0, yt)],
                   [None, ("a", xa, ya, "Params.KbCornerR", s_ > 0), None, None, None])
    pad(kb, "Pads", sk, "Params.PadT", reverse=True)
    sk = sketch(kb, "ScrewAccessSketch")
    for sx in ("-", ""):
        sk.circle(f"{sx}Params.KbScrewX", "Params.KbScrewY", "Params.ScrewHoleD")
    pocket(kb, "ScrewAccess", sk, "Params.PadT")
    solid_at(kb, V(g["PostX"] - 3, g["PadY"], -g["PadT"] / 2))
    solid_at(kb, V(g["KbScrewX"], g["KbScrewY"], -g["PadT"] / 2), solid=False)
    expect(kb, lo=(None, -g["KbDepth"], -g["PadT"]))

with step("S18a", "Cut six magnet slots in each pad, under a skin on the pad bottom.",
          "Each magnet slides in from a pad side and snaps past the lip."):
    sk = sketch(kb, "PadSlotSketch", z="-Params.PadT + Params.SkinT")
    for s_, sx in ((1, ""), (-1, "-")):
        for i, j in PAD_MAGNETS:
            cx = f"{sx}Params.PostX + ({s_ * i}) * Params.Pitch"
            cy = f"Params.PadY + ({j}) * Params.Pitch"
            if j < 0:
                sk.slot(cx, cy, "y", -1, yb)
            elif j > 0:
                sk.slot(cx, cy, "y", 1, yt)
            else:
                sk.slot(cx, cy, "x", -s_, f"{sx}(Params.PostX - Params.CapW / 2)")
    pocket(kb, "PadSlots", sk, "Params.PocketDepth", reverse=True)
    zm = -g["PadT"] + g["SkinT"] + g["PocketDepth"] / 2
    for i, j in PAD_MAGNETS:
        solid_at(kb, V(g["PostX"] + i * g["Pitch"], g["PadY"] + j * g["Pitch"], zm), solid=False)
        solid_at(kb, V(g["PostX"] + i * g["Pitch"], g["PadY"] + j * g["Pitch"],
                       -g["PadT"] + g["SkinT"] / 2))
    solid_at(kb, V(g["PostX"], g["PadY"], zm))

with step("S18", "Place the keyboard in position 1 and add the reference bodies.",
          "Phone and metal pins are bought parts, for fit checks only."):
    place(kb, y="Params.EarY", z="-Params.PlateT - Params.Clearance - Params.EarT", rot_z=180)
    phone = doc.addObject("PartDesign::Body", "Phone")
    asm.addObject(phone)
    sk = sketch(phone, "PhoneSketch")
    sk.rrect("0", "-Params.PhoneL / 2", "Params.PhoneW", "Params.PhoneL", "Params.PhoneR")
    pad(phone, "PhoneBlock", sk, "Params.PhoneT")
    place(phone, y="Params.PhoneTopY")
    pins = []
    for side, sx in (("L", "-"), ("R", "")):
        pin = doc.addObject("PartDesign::Body", f"MetalPin{side}")
        asm.addObject(pin)
        sk = sketch(pin, "HeadSketch")
        sk.circle("0", "0", "Params.PinHeadD")
        pad(pin, "Head", sk, "Params.PinHeadL")
        sk = sketch(pin, "ShankSketch")
        sk.circle("0", "0", "Params.PinD")
        pad(pin, "Shank", sk, "Params.PinShankL", reverse=True)
        place(pin, x=f"{sx}Params.PostX", z="Params.ColTop - Params.HeadBoreDepth")
        pins.append(pin)
    expect(phone, size=(g["PhoneW"], g["PhoneL"], g["PhoneT"]),
           lo=(-g["PhoneW"] / 2, g["PhoneTopY"] - g["PhoneL"], 0),
           volume=rr_area(g["PhoneW"], g["PhoneL"], g["PhoneR"]) * g["PhoneT"])
    expect(kb, lo=(None, None, -g["PlateT"] - Clr - g["EarT"] - g["PadT"]))


def overlap(a, b):
    return sp.gshape(a).common(sp.gshape(b)).Volume


with step("S19", "Check the fits in position 1.", "Each joint keeps Clearance or touches by design."):
    for pin, cap in zip(pins, caps):
        spec(f"{pin.Label} no overlap with PhoneMount", overlap(pin, mount) < 1e-6)
        solid_at(mount, V(pin.Placement.Base.x + g["PinHeadD"] / 2 + Clr / 2, 0,
                          g["ColTop"] - g["HeadBoreDepth"] + g["PinHeadL"] / 2), solid=False)
        spec(f"{cap.Label} no overlap with PhoneMount", overlap(cap, mount) < 1e-6)
        spec(f"{cap.Label} sits on its column",
             sp.gshape(cap).distToShape(sp.gshape(mount))[0] < 1e-6)
    upper = sp.gshape(mount).common(Part.makeBox(500, 500, 50, V(-250, -250, 0.01)))
    d = sp.gshape(phone).distToShape(upper)[0]
    spec("phone to lips >= Clearance", d >= Clr - 1e-4, f"{d:.3f}")
    spec("phone no overlap with PhoneMount", overlap(phone, mount) < 1e-6)
    # P2 and P3 from the parameters. Both keep the keyboard top edge toward -Y, keys up.
    cap_top = g["ColTop"] + g["CapH"]
    p2_floor = cap_top + g["PadT"]
    spec("P2: keyboard floor clears the screen", p2_floor > g["PhoneT"], f"{p2_floor:.2f}")
    spec("P2: keyboard ends before the phone end", CapW / 2 - g["KbLen"] >= g["PhoneTopY"] - g["PhoneL"],
         f"keyboard to Y={CapW / 2 - g['KbLen']:.1f}")
    th = math.radians(g["KinkAngle"])
    tri = g["KbLen"] * math.sin(th) - g["PadT"] * math.cos(th)
    spec("P3: right triangle of keyboard length and column height", abs(tri - cap_top) < 1e-6,
         f"{tri:.3f} vs {cap_top:.3f}")
    # High end: keyboard bottom edge on the kink line. Low end: tongue tip on the plate.
    y_high = g["KinkY"] - g["PadT"] * math.sin(th)
    y_low = y_high - g["KbLen"] * math.cos(th)
    y_land = g["RingY"] + g["PhoneW"] / 2
    print(f"P3 angle {g['KinkAngle']:.2f} deg; keyboard from Y={y_low:.1f} (plate) to "
          f"Y={y_high:.1f} (cap); landscape phone edge at Y={y_land:.1f}")
    if y_low < y_land + Clr:
        print(f"P3 CONFLICT: the keyboard needs {y_high - y_low:.1f} mm along the plate; "
              f"the gap to the landscape phone is {y_high - y_land:.1f} mm")
    lever = CapW / 2 + g["TongueL"]
    spec("P1: tongue tip under the plate", lever <= -g["RingY"], f"{lever:.1f}")
    print(f"P1 peel lever: tongue tip to post axis {lever:.1f} mm "
          f"(old ear edge {CapW / 2:.1f} mm)")

cap_top = g["ColTop"] + g["CapH"]
decide("D9", "Assembly: slide 8 magnets into the cap side slots past the lips. Put the centre "
       "magnet in from the bottom. Push each metal pin into its column from the top. "
       "Glue each cap on its column; the cap closes the centre pocket and holds the pin.",
       "User: open pockets let magnets jump out. Slots hold each magnet apart under a skin.")
decide("D10", "Magnet poles on the cap top, rows from +Y to -Y: N S N, N S N, N N N. "
       "The N N N row is on the kink bevel. Put each pad magnet to attract the cap magnet "
       "below it in position 2.", "User pattern NSN/NSN/NNN. A pad has 6 magnets: the screw "
       "hole and the case corner take two places, the centre has no free side.")
decide("D11", "Print all three parts as modelled with no supports: slots bridge 5.4 mm under a skin.",
       "The bar and the cap stand on flat bottoms. Posts and columns are vertical.")
decide("D14", "Keyboard side: a full-height dock bar with 3 mm cheeks on both side walls and a "
       "tongue under the plate. No thin neck.",
       "User: the phone hangs on this joint in position 1, so the torque is large.")
decide("D15", "In position 1 the plate bears on the bar and tongue. The banana plugs hold the "
       "posts in the sockets.", "User: the banana plug is good enough for position 1.")
decide("D12", f"Position 2: the keyboard lies keys up on the phone, top edge toward the phone "
       f"top. Its corner pads rest on the caps; the floor is {p2_floor - g['PhoneT']:.1f} mm "
       "above the screen.", "User: the keys must be usable on the phone.")
decide("D13", f"Position 3: KinkAngle = {g['KinkAngle']:.2f} deg from the right triangle of the "
       f"keyboard length ({g['KbLen']:.1f} mm) and the column height ({cap_top:.1f} mm). "
       "The pad edge row lands on the kink row.", "User: the angle comes from this triangle.")
decide("D16", "The post bore copies the fitted test post: 3.6 mm bore, 3 lobes at 3.28 mm over "
       "the last 2 mm, 4.14 mm relief. The post OD stays 8 mm for strength.",
       "User: the test post fits the banana plug with its flex spaces and sizes.")

PAIRS = [(kb, mount, Clr), (pins[0], kb, Clr), (pins[1], kb, Clr),
         (caps[0], pins[0], Clr), (caps[1], pins[1], Clr)]
PX = round(g["PostX"], 2)
checkpoint(doc, 4, OUT, pairs=PAIRS, cuts=[("x", PX), ("y", 0.0)], script="build_dock.py")

# ---------------------------------------------------------------- stage 5
with step("S20", "Chamfer the socket mouths.", "A lead-in guides the post into the socket."):
    base = mount.Tip
    names = edges(base, where=lambda c: abs(c.z + g["PlateT"]) < 1e-3
                  and abs(abs(c.x) - g["PostX"]) < 1e-3 and abs(c.y) < 1e-3)
    ch = mount.newObject("PartDesign::Chamfer", "MouthChamfer")
    ch.Base = (base, names)
    ch.setExpression("Size", "Params.MouthChamfer")
    spec("socket mouth edges found", len(names) >= 2, str(names))

with step("S21", "Fillet the post bases and chamfer the post tips.",
          "The fillet is the post support. The chamfer is a lead-in."):
    base = kb.Tip
    kx, ky = g["PostX"], g["EarY"]
    names = edges(base, where=lambda c: abs(c.z - g["EarT"]) < 1e-3 and abs(abs(c.x) - kx) < 1e-3
                  and abs(c.y - ky) < 1e-3)
    fil = kb.newObject("PartDesign::Fillet", "PostFillet")
    fil.Base = (base, names)
    fil.setExpression("Radius", "Params.PostFillet")
    spec("post base edges found", len(names) >= 2, str(names))
    doc.recompute()
    top = g["EarT"] + g["PostL"]
    shp = fil.Shape
    names = []
    for i, e in enumerate(shp.Edges):
        bb = e.BoundBox
        if (abs(bb.ZMin - top) < 1e-3 and abs(bb.ZMax - top) < 1e-3 and hasattr(e.Curve, "Radius")
                and abs(e.Curve.Radius - g["PostOD"] / 2) < 1e-3):
            names.append(f"Edge{i + 1}")
    print("EDGES post tip outer arcs:", names)
    chm = kb.newObject("PartDesign::Chamfer", "PostChamfer")
    chm.Base = (fil, names)
    chm.setExpression("Size", "Params.PostChamfer")
    spec("post tip arcs found", len(names) == 4, str(names))

doc.recompute()
checkpoint(doc, 5, OUT, pairs=PAIRS, cuts=[("x", PX), ("y", 0.0)], script="build_dock.py")
with step("S22", "Export the printed parts in their own frames.",
          "Print MagnetCap twice."):
    for body, name in ((mount, "PhoneMount"), (caps[0], "MagnetCap_x2"),
                       (kb, "Q10_Keyboard_bottom_case_v2")):
        shp = body.Shape.copy()
        shp.Placement = App.Placement()
        shp.exportStep(os.path.join(OUT, f"{name}.step"))
        mesh = MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.02, AngularDeflection=0.2,
                                      Relative=False)
        mesh.write(os.path.join(OUT, f"{name}.stl"))
        mb, sb = mesh.BoundBox, shp.BoundBox
        spec(f"{name} STL matches the solid", max(abs(mb.XLength - sb.XLength),
             abs(mb.YLength - sb.YLength), abs(mb.ZLength - sb.ZLength)) < 0.05)
        print(f"STL {name}: closed={mesh.isSolid()} non-manifold={mesh.hasNonManifolds()}")
        print(f"EXPORT {name}: bbox {shp.BoundBox.XLength:.2f}x{shp.BoundBox.YLength:.2f}"
              f"x{shp.BoundBox.ZLength:.2f} vol {shp.Volume:.1f}")
before = {b.Label: b.Shape.Volume for b in (mount, caps[0], kb)}
stress(doc, P, ["PhoneW", "PostOD", "MagD", "TongueL", "SocketDepth"])

for b in (mount, caps[0], kb):
    spec(f"{b.Label} restored after stress", abs(b.Shape.Volume - before[b.Label]) < 1e-3,
         f"{b.Shape.Volume:.3f} vs {before[b.Label]:.3f}")
write_trace(doc, os.path.join(OUT, "TRACE.md"), "build_dock.py")
report(doc)
