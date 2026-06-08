#!/usr/bin/env python3
"""
Round the corners of every system logo in assets/images/systems/*.png.

Each logo is a 256x256 image with an OPAQUE background filling the canvas, so we
mask the opaque content's bounding box with a rounded rectangle. Box-style logos
(the whole set as of this writing) round cleanly; truly transparent/centered-icon
logos would get their content bbox rounded instead (could clip) -- run with --check
first to confirm they're all box-style before committing.

Modifies files IN PLACE. Originals live in ../../dii-ess-aye-main (OG)/.
Requires: pillow, numpy
Usage:
  python round_logos.py --check        # report box-style vs irregular, change nothing
  python round_logos.py --radius 0.12  # round all at 12% of the content's short side
"""
from PIL import Image, ImageDraw
import numpy as np, os, sys

D = os.path.join(os.path.dirname(__file__), "..", "assets","images","systems")
RADIUS_FRAC = 0.12
CHECK = "--check" in sys.argv
if "--radius" in sys.argv:
    RADIUS_FRAC = float(sys.argv[sys.argv.index("--radius")+1])

files=[f for f in os.listdir(D) if f.lower().endswith(".png") and not f.startswith("._")]
box=0; irregular=[]
for f in files:
    p=os.path.join(D,f)
    im=Image.open(p).convert("RGBA"); W,H=im.size
    a=np.array(im); op=a[:,:,3]>30
    if op.sum()==0: irregular.append((f,"empty")); continue
    ys,xs=np.where(op); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    bw,bh=x1-x0+1,y1-y0+1
    fill=op.sum()/(bw*bh); cov=(bw*bh)/(W*H)
    if not (fill>0.92 and cov>0.55):
        irregular.append((f,round(fill,2),round(cov,2)))
        if CHECK: continue
    box+=1
    if CHECK: continue
    rad=int(min(bw,bh)*RADIUS_FRAC)
    mask=Image.new("L",(W,H),0)
    ImageDraw.Draw(mask).rounded_rectangle([x0,y0,x1,y1],radius=rad,fill=255)
    im.putalpha(Image.composite(im.getchannel("A"),Image.new("L",(W,H),0),mask))
    im.save(p)

print(f"{len(files)} logos | box-style={box if not CHECK else len(files)-len(irregular)} "
      f"| irregular={len(irregular)} | radius={RADIUS_FRAC:.0%}")
for r in irregular: print("  IRREGULAR:", r)
if not CHECK: print("rounded in place.")
