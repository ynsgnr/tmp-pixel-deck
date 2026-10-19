"""Base block. Change the parameters in Params. Do not change numbers in the steps.

Run: SKILL_DIR=<skill folder> STAGE=1 FreeCADCmd base_part.py
"""
import os
import sys

import FreeCAD as App
import Part
import Sketcher

sys.path.insert(0, os.path.join(os.environ.get("SKILL_DIR", "."), "scripts"))
from fc import *  # noqa: E402,F403

V = App.Vector
doc = App.newDocument("Model")

decide("D1", "Z is up. The origin is at the front-left-bottom corner.",
       "All dimensions start at one corner.")

with step("S1", "Make the parameters.", "All dimensions come from Params."):
    P = doc.addObject("App::VarSet", "Params")
    for name, kind, value, use in [
        ("Width", "App::PropertyLength", "40 mm", "Outer size along X."),
        ("Depth", "App::PropertyLength", "30 mm", "Outer size along Y."),
        ("Height", "App::PropertyLength", "20 mm", "Outer size along Z."),
    ]:
        P.addProperty(kind, name, "Params", use)
        setattr(P, name, value)
W, D, H = P.Width.Value, P.Depth.Value, P.Height.Value

with step("S2", "Sketch the base rectangle on the XY plane.", "The block grows up from Z = 0."):
    body = doc.addObject("PartDesign::Body", "Body")
    xy = next(f for f in body.Origin.OriginFeatures if f.Role == "XY_Plane")
    sk = body.newObject("Sketcher::SketchObject", "BaseSketch")
    if hasattr(sk, "AttachmentSupport"):
        sk.AttachmentSupport = (xy, [""])  # 1.0+
    else:
        sk.Support = (xy, [""])            # 0.21 and older
    sk.MapMode = "FlatFace"
    c = [V(0, 0, 0), V(W, 0, 0), V(W, D, 0), V(0, D, 0)]
    sk.addGeometry([Part.LineSegment(c[i], c[(i + 1) % 4]) for i in range(4)], False)
    sk.addConstraint([Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1) for i in range(4)]
                     + [Sketcher.Constraint("Horizontal", 0), Sketcher.Constraint("Horizontal", 2),
                        Sketcher.Constraint("Vertical", 1), Sketcher.Constraint("Vertical", 3),
                        Sketcher.Constraint("Coincident", 0, 1, -1, 1)])
    for k, (kind, g, name, expr) in enumerate([("DistanceX", 0, "Wd", "Params.Width"),
                                               ("DistanceY", 1, "Dp", "Params.Depth")]):
        i = sk.addConstraint(Sketcher.Constraint(kind, g, 1, g, 2, (W, D)[k]))
        sk.renameConstraint(i, name)
        sk.setExpression(f"Constraints.{name}", expr)
    axes(sk)  # want x=+X y=+Y normal=+Z

with step("S3", "Pad the sketch to Height.", "This makes the block."):
    pad = body.newObject("PartDesign::Pad", "BasePad")
    pad.Profile = sk
    pad.setExpression("Length", "Params.Height")
    expect(body, size=(W, D, H), lo=(0, 0, 0), volume=W * D * H)

checkpoint(doc, os.environ.get("STAGE", "1"), os.environ.get("OUT_DIR", "."),
           script=os.path.basename(globals().get("__file__", "base_part.py")))
