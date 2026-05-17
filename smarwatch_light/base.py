"""
base.py

Outputs:
    base.step
    base.stl
"""

from build123d import *
from common import *

# Parameters:

base_bottom=1.5
base_wall=4.0
base_screw_len_add=0.4+0.3

base_bat_dia=35.5
base_bat_cut_w=22
base_bat_cut_h=3+1.5
base_bat_cut_off=0.9-1.5

use_printed_strap=False

base_strap_h=7.8
base_strap_d=5.2+base_strap_add_l
base_strap_cyl=3
base_strap_warp=1
base_strap_cut=0.1
base_strap_off=body_radius

fstrap_width=20
fstrap_dist=fstrap_width+0.2
fstrap_hole=1.1
fstrap_depth=1.9
fstrap_add=1.5
fstrap_h=base_strap_h-2
fstrap_warp=base_strap_warp-1

base_height = base_bottom + base_wall

# Build:

# 1. Base Bat:
def base_bat(h):
    c1 = Cyl(d=base_bat_dia, h=h)
    cut1 = Translate([-base_bat_dia/2, -base_bat_dia+base_bat_cut_off, -1], Cube([base_bat_dia, base_bat_dia/2, h+2]))
    add1 = Translate([-base_bat_cut_w/2, -base_bat_dia/2+base_bat_cut_off, 0], Cube([base_bat_cut_w, base_bat_cut_h, h]))
    return Union(Difference(c1, cut1), add1)

# 2. Base strap:
def base_strap():
    h_obj = StrapHull(base_strap_w, base_strap_d, base_strap_cyl, base_strap_h, base_strap_warp)
    s_cut = Translate([-1, base_strap_d-strap_d/2, base_strap_h/2+base_strap_warp], Rotate([0,90,0], screw(True, True)))
    c_cut = Translate([-0.1, -0.1, -base_strap_off+base_height], Cube([base_strap_w+0.2, base_strap_cut+0.1, base_strap_h]))
    return Translate([-base_strap_w/2, 0, 0], Difference(h_obj, s_cut, c_cut))

# 3. Fstrap piece:
def fstrap_piece(w,s_hole):
    h_obj = FStrapHull(w, fstrap_add, base_strap_d, base_strap_cyl, fstrap_h, fstrap_warp)
    cyl_cut = Translate([-1, base_strap_d-strap_d/2, fstrap_h/2+fstrap_warp], Rotate([0,90,0], Cyl(d=s_hole, h=w+2)))
    c_cut = Translate([-0.1, -0.1-fstrap_add, -base_strap_off+base_height], Cube([w+0.2, base_strap_cut+0.1+fstrap_add, fstrap_h]))
    return Translate([-w/2,0,0], Difference(h_obj, cyl_cut, c_cut))

# 4. fstrap:
def fstrap():
    parts=[]
    for i in [-1,1]:
        piece = fstrap_piece(fstrap_depth, fstrap_hole)
        piece = Translate([(fstrap_dist+fstrap_depth)/2,0,0], piece)
        piece = Scale([i,1,1], piece)
        parts.append(piece)
    return Union(*parts)

# 5. Base:
def base():
    u_parts=[]
    u_parts.append(body(base_bottom, True))
    u_parts.append(Translate([0,0,base_bottom], body(base_wall, False)))

    if use_printed_strap:
        for i in [-1,1]:
            s = Translate([0, body_dia/2+base_mount_off, base_strap_off], base_strap())
            s = Scale([1,i,1], s)
            u_parts.append(s)
    else:
        for i in [-1,1]:
            fs = Translate([0, body_dia/2+base_mount_off, base_strap_off], fstrap())
            fs = Scale([1,i,1], fs)
            u_parts.append(fs)

    u_obj = Union(*u_parts)

    cut1 = Translate([0,0,base_bottom-0.01], base_bat(base_wall+1.01))
    cut2 = Translate([0,0,base_bottom-base_screw_len_add], base_screws())
    cut3 = usb_flatten(base_height)

    return Difference(u_obj, cut1, cut2, cut3)

from ocp_vscode import show

# Create the part:
base_model = base()

# Visualize:
show(base_model)

# Export:
export_step(base_model, "base.step")
export_stl(base_model, "base.stl")