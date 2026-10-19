"""Detail views of the printed parts and the docked joint. Run after build_dock.py.

Run: FreeCADCmd render_details.py
"""
import sys, os; HERE=os.environ.get('DOCK_DIR') or os.path.dirname(os.path.abspath(globals().get('__file__','render_details.py')))
sys.path.insert(0,os.path.join(os.environ.get('SKILL_DIR',os.path.dirname(HERE)),'scripts'))
import FreeCAD as App, Part
import fc_spatial as sp
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
V=App.Vector
OUT=os.path.join(HERE,'out')+os.sep
doc=App.openDocument(OUT+'stage5.FCStd'); doc.recompute()
P=doc.getObject('Params'); px=P.PostX.Value
def shade(ax, shp, color, el, az):
    v,f=shp.tessellate(0.05)
    v=np.array([[p.x,p.y,p.z] for p in v]); f=np.array(f); t=v[f]
    n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12
    L=np.array([0.4,-0.6,0.7]); L/=np.linalg.norm(L)
    s=0.35+0.65*np.clip(n@L,0,1)
    c=np.array(matplotlib.colors.to_rgb(color))
    ax.add_collection3d(Poly3DCollection(t,facecolors=np.clip(c[None,:]*s[:,None]+0.15,0,1),edgecolor='none'))
    return v
def views(shapes, title, path, views=((35,-60),(-35,-60),(30,120),(90,-90))):
    fig=plt.figure(figsize=(14,11))
    for k,(el,az) in enumerate(views):
        ax=fig.add_subplot(2,2,k+1,projection='3d')
        pts=np.vstack([shade(ax,s,c,el,az) for s,c in shapes])
        lo,hi=pts.min(0),pts.max(0); cc=(lo+hi)/2; r=(hi-lo).max()/2
        ax.set_xlim(cc[0]-r,cc[0]+r); ax.set_ylim(cc[1]-r,cc[1]+r); ax.set_zlim(cc[2]-r,cc[2]+r)
        ax.view_init(el,az); ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z'); ax.set_title(f'elev {el}, azim {az}')
    fig.suptitle(title); fig.tight_layout(); fig.savefig(path,dpi=75); plt.close(fig); print('IMG',path)
g=lambda n: sp.gshape(doc.getObject(n))
cap=doc.getObject('MagnetCapL').Shape.copy(); cap.Placement=App.Placement()
views([(cap,'#DD8452')],'MagnetCap (local frame, print as modelled)',OUT+'detail_magnetcap.png')
kb=doc.getObject('Keyboard').Shape.copy(); kb.Placement=App.Placement()
box=Part.makeBox(32,48,16,V(px-16,-22,-1))
views([(kb.common(box),'#C44E52')],'Keyboard ear PostR (KB frame: floor z=0, keys +z)',OUT+'detail_keyboard_ear.png',
      views=((35,-120),(-40,-120),(30,60),(90,-90)))
views([(kb,'#C44E52')],'Q10 keyboard bottom case v2 (KB frame)',OUT+'detail_keyboard.png')
m=doc.getObject('PhoneMount').Shape
views([(m.common(Part.makeBox(30,30,20,V(px-15,-18,-6))),'#4C72B0')],'PhoneMount ColR (cut-out view)',OUT+'detail_column.png',
      views=((35,-60),(-35,-60),(30,120),(90,-90)))
# zoomed sections through the right post axis
fig,axs=plt.subplots(1,2,figsize=(16,7))
cols={'PhoneMount':'#4C72B0','MagnetCapR':'#55A868','Keyboard':'#C44E52','MetalPinR':'#DD8452','Phone':'#8172B2'}
for ax,(axis,at,ix,iy,xl,lim) in zip(axs,[('x',px,1,2,'Y',(-35,30)),('y',0.0,0,2,'X',(px-14,px+14))]):
    n=V(1,0,0) if axis=='x' else V(0,1,0)
    for name,c in cols.items():
        s=g(name)
        for w in s.slice(n,at):
            pts=np.array([[p.x,p.y,p.z] for p in w.discretize(Deflection=0.01)])
            ax.fill(pts[:,ix],pts[:,iy],color=c,alpha=0.35,lw=0); ax.plot(pts[:,ix],pts[:,iy],color=c,lw=1)
        ax.plot([],[],color=c,label=name)
    ax.set_xlim(*lim); ax.set_ylim(-13,12); ax.set_aspect('equal'); ax.grid(alpha=.3)
    ax.set_xlabel(xl+' (mm)'); ax.set_ylabel('Z (mm)'); ax.set_title(f'Section {axis.upper()}={at:.2f}, position 1 (docked)')
    ax.axhline(10,color='#8172B2',ls=':',lw=1); ax.text(lim[0]+0.5,10.2,'screen Z=10',fontsize=8,color='#8172B2')
axs[0].legend(loc='lower left',fontsize=8)
fig.tight_layout(); fig.savefig(OUT+'detail_dock_sections.png',dpi=80); print('IMG sections')
