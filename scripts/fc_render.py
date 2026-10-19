"""Headless previews, global coordinates, labelled axes.

    from fc_render import render, section
    render(doc, "stage3.png")                  # top, front, right, iso
    section(doc, "stage3_z12.png", "z", 12.0)  # cut through an interface

Needs matplotlib in FreeCAD's Python. Without it, render writes an STL next to
the requested path and says so.
"""
import FreeCAD as App

from fc_spatial import bbox, gshape

COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]
# FreeCAD view names: front looks along +Y, right along -X, top along -Z
VIEWS = [("top (XY)", 90, -90), ("front (XZ)", 0, -90), ("right (YZ)", 0, 0), ("iso", 30, -60)]


def _bodies(doc):
    return [(b.Label, gshape(b)) for b in doc.findObjects("PartDesign::Body")
            if not b.Shape.isNull()]


def _plt():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        return None


def render(doc, path, tol=0.2):
    bodies = _bodies(doc)
    plt = _plt()
    if plt is None:
        import Mesh
        stl = path.rsplit(".", 1)[0] + ".stl"
        Mesh.export(doc.findObjects("PartDesign::Body"), stl)
        print(f"RENDER no matplotlib; wrote {stl}")
        return stl
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    meshes, pts = [], []
    for i, (label, s) in enumerate(bodies):
        v, f = s.tessellate(tol)
        meshes.append(([[tuple(v[k]) for k in t] for t in f], COLORS[i % len(COLORS)], label))
        pts.extend(tuple(p) for p in v)
    if not pts:
        print("RENDER nothing to draw")
        return None
    lo = [min(p[k] for p in pts) for k in range(3)]
    hi = [max(p[k] for p in pts) for k in range(3)]
    span = max(h - l for h, l in zip(hi, lo)) or 1
    mid = [(h + l) / 2 for h, l in zip(hi, lo)]

    fig = plt.figure(figsize=(8, 8))
    for n, (name, elev, azim) in enumerate(VIEWS, 1):
        ax = fig.add_subplot(2, 2, n, projection="3d")
        for tris, c, _ in meshes:
            ax.add_collection3d(Poly3DCollection(tris, facecolor=c, edgecolor="k",
                                                 linewidths=0.1, alpha=0.85))
        for k, set_lim in enumerate((ax.set_xlim, ax.set_ylim, ax.set_zlim)):
            set_lim(mid[k] - span / 2, mid[k] + span / 2)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        if name != "iso":
            ax.set_proj_type("ortho")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(name, fontsize=9)
        ax.tick_params(labelsize=6)
    legend = "  ".join(f"{lbl}={c}" for _, c, lbl in meshes) if len(meshes) > 1 else ""
    fig.suptitle(f"overall {hi[0]-lo[0]:.2f} x {hi[1]-lo[1]:.2f} x {hi[2]-lo[2]:.2f} mm  {legend}",
                 fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"RENDER {path} ({len(bodies)} bodies)")
    return path


def section(doc, path, axis="z", at=None):
    """Cut every Body with the plane axis=at (global) and plot the outlines."""
    plt = _plt()
    k = "xyz".index(axis.lower())
    u, v = [i for i in range(3) if i != k]
    normal = App.Vector(*[1 if i == k else 0 for i in range(3)])
    bodies = _bodies(doc)
    if at is None:
        bbs = [bbox(s) for _, s in bodies]
        lo = min((bb.XMin, bb.YMin, bb.ZMin)[k] for bb in bbs)
        hi = max((bb.XMax, bb.YMax, bb.ZMax)[k] for bb in bbs)
        at = (lo + hi) / 2
    if plt is None:
        print("SECTION needs matplotlib")
        return None
    fig, ax = plt.subplots(figsize=(6, 6))
    for i, (label, s) in enumerate(bodies):
        for j, w in enumerate(s.slice(normal, float(at))):
            p = w.discretize(Deflection=0.02)
            ax.plot([q[u] for q in p], [q[v] for q in p], color=COLORS[i % len(COLORS)],
                    lw=0.8, label=None if j else label)
    ax.set_aspect("equal")
    ax.set_xlabel("XYZ"[u])
    ax.set_ylabel("XYZ"[v])
    ax.set_title(f"section {axis.upper()}={at:.2f} mm", fontsize=9)
    ax.grid(lw=0.3)
    if len(bodies) > 1:
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"SECTION {path} {axis.upper()}={at:.2f}")
    return path
