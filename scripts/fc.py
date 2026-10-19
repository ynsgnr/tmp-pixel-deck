"""One import for model scripts: from fc import *"""
import os

from fc_check import report, stress
from fc_render import render, section
from fc_spatial import (axes, bbox, centred, edges, expect, faces, fits, gshape, on_top,
                        placements, solid_at, spec)
from fc_trace import decide, step, write_trace

__all__ = ["axes", "bbox", "centred", "checkpoint", "decide", "edges", "expect", "faces",
           "fits", "gshape", "on_top", "placements", "render", "report", "section",
           "solid_at", "spec", "step", "stress", "write_trace"]


def checkpoint(doc, stage, out=".", pairs=(), cuts=(), script=None):
    """End a stage: report, views, sections, placements, TRACE.md, stageN.FCStd.
    pairs: [(a, b, clearance)] fit checks. cuts: [("z", 12.0)] section planes.
    Returns True if report printed OK."""
    def path(name):
        return os.path.abspath(os.path.join(out, name))
    ok = report(doc, pairs)
    render(doc, path(f"stage{stage}.png"))
    for axis, at in cuts:
        section(doc, path(f"stage{stage}_{axis}{at:g}.png"), axis, at)
    if len(doc.findObjects("PartDesign::Body")) > 1:
        placements(doc)
    write_trace(doc, path("TRACE.md"), script)
    doc.saveAs(path(f"stage{stage}.FCStd"))
    return ok
