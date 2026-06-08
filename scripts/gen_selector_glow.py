#!/usr/bin/env python3
"""
Generate the golden glassmorphism selector frame PNG for the dsi-puh-lus carousel.

Output: assets/images/common/selector_glow_gold.png  (square PNG, scaled by the theme)

The frame has 3 baked layers (ES theme images can't do gradients/blur at runtime):
  1. translucent golden gradient BODY  (diagonal light->amber, low alpha = glass)
  2. gradient gold BORDER ring          (champagne -> gold -> amber, diagonal)
  3. soft outer+inner GLOW bloom         (gaussian-blurred copies of the ring)

Tuning knobs are at the top. Re-run, then deploy with deploy.py (or see the guide).
Requires: pillow, numpy   ->   pip install pillow numpy
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os

# ---- knobs -----------------------------------------------------------------
S          = 300          # PNG size in px (square). Scaled to the element box by ES.
RADIUS     = 74           # corner radius (~25% of S = rounded square)
BORDER     = 6            # border core thickness in px
BODY_A0    = 55           # body alpha at the light corner (top-left)
BODY_A1    = 125          # body alpha at the deep corner (bottom-right); 0 = invisible body
# body gold gradient stops (RGB): light -> mid -> deep
BODY = (np.array([255,236,170]), np.array([245,196,90]), np.array([200,140,30]))
# border gold gradient stops (RGB)
BORD = (np.array([255,250,225]), np.array([255,205,70]), np.array([214,150,28]))
GLOW = [(18,0.5),(10,0.7),(5,0.9)]   # (blur_radius, intensity) passes for the bloom
OUT  = os.path.join(os.path.dirname(__file__), "..",
                    "assets","images","common","selector_glow_gold.png")
# ----------------------------------------------------------------------------

def rrect(w,h,rad,aa=4):
    b=Image.new('L',(w*aa,h*aa),0)
    ImageDraw.Draw(b).rounded_rectangle([0,0,w*aa-1,h*aa-1],radius=rad*aa,fill=255)
    return b.resize((w,h),Image.LANCZOS)

def lerp3(stops,t):
    a,b,c=stops
    return np.where(t[...,None]<0.5, a+(b-a)*(t[...,None]/0.5),
                                     b+(c-b)*((t[...,None]-0.5)/0.5))

W=H=S
base=Image.new('RGBA',(W,H),(0,0,0,0))
outer=rrect(W,H,RADIUS)
yy,xx=np.mgrid[0:H,0:W]; t=(xx/W+yy/H)/2.0          # diagonal 0(TL)->1(BR)

# 1. body
col=lerp3(BODY,t).astype(np.uint8)
alpha=(BODY_A0+t*(BODY_A1-BODY_A0)).astype(np.uint8)
body=Image.new('RGBA',(W,H),(0,0,0,0))
body.paste(Image.fromarray(np.dstack([col,alpha]),'RGBA'),mask=outer)
base=Image.alpha_composite(base,body)
# top sheen
sh=np.zeros((H,W,4),np.uint8)
for y in range(H//3):
    sh[y,:]=[255,250,225,int(60*(1-y/(H/3))**1.5)]
s=Image.new('RGBA',(W,H),(0,0,0,0)); s.paste(Image.fromarray(sh,'RGBA'),mask=outer)
base=Image.alpha_composite(base,s)

# 2. border ring
inner=Image.new('L',(W,H),0); inner.paste(rrect(W-2*BORDER,H-2*BORDER,max(RADIUS-BORDER,6)),(BORDER,BORDER))
ring=np.clip(np.array(outer).astype(int)-np.array(inner).astype(int),0,255).astype(np.uint8)
grad=lerp3(BORD,t).astype(np.uint8)
ring_img=Image.new('RGBA',(W,H),(0,0,0,0))
ring_img.paste(Image.fromarray(np.dstack([grad,np.full((H,W),255,np.uint8)]),'RGBA'),
               mask=Image.fromarray(ring,'L'))

# 3. glow bloom (under the crisp ring)
glow=Image.new('RGBA',(W,H),(0,0,0,0))
for r,it in GLOW:
    g=np.array(ring_img.filter(ImageFilter.GaussianBlur(r))).astype(float); g[:,:,3]*=it
    glow=Image.alpha_composite(glow,Image.fromarray(g.astype(np.uint8),'RGBA'))
base=Image.alpha_composite(base,glow)
base=Image.alpha_composite(base,ring_img)

base.save(OUT)
print("wrote", os.path.normpath(OUT), f"({S}x{S})")
