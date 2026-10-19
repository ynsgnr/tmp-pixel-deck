"""Compact FreeCAD model checks. Prints only what matters; last line is OK or ISSUES.

    from fc_check import report, stress
    report(doc)                                   # after every stage
    report(doc, pairs=[(LidBody, BaseBody, 0.2)]) # fit check, clearance in mm
    stress(doc, Params, ["Width", "WallThickness"])
"""
import fc_spatial as sp


def report(doc, pairs=()):
    doc.recompute()  # returns a count; does not raise on broken features
    ok = True
    for o in doc.Objects:
        if not o.isValid():
            ok = False
            print("INVALID", o.Name, o.getStatusString())
        if o.TypeId == "Sketcher::SketchObject":
            issues = {k: v for k in ("ConflictingConstraints", "RedundantConstraints",
                                     "MalformedConstraints")
                      if (v := list(getattr(o, k, [])))}
            full = getattr(o, "FullyConstrained", True)  # property since 0.20
            if not full or issues:
                ok = False
                print("SKETCH", o.Name, "fully_constrained", full, issues or "")
    for b in doc.findObjects("PartDesign::Body"):
        s = sp.gshape(b)
        if s.isNull():
            print(f"BODY {b.Label}: empty")
            continue
        bb = sp.bbox(s)
        line = (f"BODY {b.Label}: solids={len(s.Solids)} vol={s.Volume:.1f} "
                f"bbox={bb.XLength:.2f}x{bb.YLength:.2f}x{bb.ZLength:.2f}")
        if len(s.Solids) != 1:
            ok = False
            line += " EXPECTED_1_SOLID"
        try:
            s.check()  # raises with a description of the fault
        except Exception as e:  # noqa: BLE001 - OCC raises several types
            ok = False
            line += f" SHAPE_CHECK_FAILED {e}"
        print(line)
    for a, b, clearance in pairs:
        sp.fits(a, b, clearance)
    if sp.FAILS:
        ok = False
        print(f"SPEC failures since last report: {', '.join(sp.FAILS)}")
        sp.FAILS.clear()
    print("OK" if ok else "ISSUES")
    return ok


def stress(doc, params, names, factor=1.5):
    """Scale each parameter, recompute, report what breaks, restore."""
    for n in names:
        old = getattr(params, n)
        setattr(params, n, int(old * factor) if isinstance(old, int) else old * factor)
        doc.recompute()
        bad = [o.Name for o in doc.Objects if not o.isValid()]
        print(f"STRESS {n} x{factor}: {'ok' if not bad else 'BREAKS ' + ','.join(bad)}")
        setattr(params, n, old)
        doc.recompute()
