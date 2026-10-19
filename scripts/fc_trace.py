"""Trace: each build step prints one line and goes into TRACE.md.

    from fc_trace import step, decide, write_trace
    decide("D1", "Clearance is 0.2 mm per side.", "FDM printer, 0.4 mm nozzle.")
    with step("S3", "Cut the cable hole in the rear wall.", "The cable exits at +Y."):
        ...features, expect(), spatial checks...
    write_trace(doc, "TRACE.md")
"""
from contextlib import contextmanager

import FreeCAD as App

import fc_spatial as sp

STEPS, DECISIONS = [], []


def decide(did, what, why=""):
    """Record an assumption or a choice."""
    DECISIONS.append((did, what, why))
    print(f"{did} {what}" + (f" Reason: {why}" if why else ""))


def _state(doc):
    out = {}
    for b in doc.findObjects("PartDesign::Body"):
        s = sp.gshape(b)
        if s.isNull():
            continue
        bb = sp.bbox(s)
        out[b.Label] = (s.Volume, (bb.XLength, bb.YLength, bb.ZLength))
    return out


@contextmanager
def step(sid, what, why="", doc=None):
    """Run one build step. On exit: recompute, then record the change and failures."""
    doc = doc or App.ActiveDocument
    before = _state(doc)
    n_fail = len(sp.FAILS)
    try:
        yield
    except Exception as e:
        _record(sid, what, why, f"ERROR {type(e).__name__}: {e}")
        raise
    doc.recompute()
    parts = []
    for label, (vol, size) in _state(doc).items():
        old = before.get(label)
        if old != (vol, size):
            dv = vol - (old[0] if old else 0)
            parts.append(f"{label} vol {dv:+.1f} mm3, size "
                         + "x".join(f"{v:.2f}" for v in size))
    invalid = [o.Name for o in doc.Objects if not o.isValid()]
    if invalid:
        parts.append("INVALID " + ",".join(invalid))
    if len(sp.FAILS) > n_fail:
        parts.append("FAIL " + ",".join(sp.FAILS[n_fail:]))
    _record(sid, what, why, "; ".join(parts) or "no geometry change")


def _record(sid, what, why, result):
    STEPS.append((sid, what, why, result))
    print(f"{sid} {what} -> {result}")


def _cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def write_trace(doc, path="TRACE.md", script=None):
    """Write parameters, decisions and steps as Markdown tables."""
    ver = ".".join(App.Version()[:3])
    lines = [f"# {doc.Label}", "",
             f"FreeCAD {ver}. Units: mm, degrees."
             + (f" Rebuild: `FreeCADCmd {script}`." if script else ""), ""]
    for vs in doc.findObjects("App::VarSet"):
        lines += ["## Parameters", "", "| Name | Value | Use |", "|---|---|---|"]
        for n in vs.PropertiesList:
            if vs.getGroupOfProperty(n) != "Params":
                continue
            v = getattr(vs, n)
            lines.append(f"| {n} | {_cell(getattr(v, 'UserString', v))} | "
                         f"{_cell(vs.getDocumentationOfProperty(n))} |")
        lines.append("")
    if DECISIONS:
        lines += ["## Decisions", "", "| ID | Decision | Reason |", "|---|---|---|"]
        lines += [f"| {d} | {_cell(w)} | {_cell(r)} |" for d, w, r in DECISIONS]
        lines.append("")
    lines += ["## Steps", "", "| ID | Action | Reason | Result |", "|---|---|---|---|"]
    lines += [f"| {s} | {_cell(w)} | {_cell(r)} | {_cell(res)} |" for s, w, r, res in STEPS]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"TRACE {path} ({len(STEPS)} steps, {len(DECISIONS)} decisions)")
