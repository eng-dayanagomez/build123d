"""
strap.py

Outputs:
    strap.step
    strap.stl
"""

from build123d import *
from common import *

# Parameters:

strap_piece_body_w=5
strap_piece_body_h=20
strap_latch_l=6.8
strap_latch_gap=2*0.2
strap_radius=1.0

# base_strap_w comes from common.py
strap_latch_w_body= base_strap_w + strap_latch_gap

strap_piece_w = strap_piece_body_w + 2*strap_latch_l
strap_latch_dist = strap_latch_wl + strap_latch_gap

strap_rows = 2
strap_cols = 6
strap_piece_dist = 5

# Create a fixed rounded cube function only for this case:
def fixed_roundedcube(x,y,z,r):
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(x,y,align=(Align.MIN, Align.MIN))
            fillet(p.vertices(), radius=r)
        extrude(amount=z)

        edges = p.edges().filter_by(Axis.Z, reverse=True)
        fillet(edges, radius=r*0.99)
    return p.part

# Build functions:

# 1. Strap latch:
def strap_latch(long=False, latch_id=0):
    w = strap_latch_wl if long else strap_latch_ws
    h_dia =nut_dia if long else screw_dia

    p1 = Translate([strap_latch_l-strap_radius,0,0],
                   fixed_roundedcube(strap_d/2+strap_radius, w, strap_d, strap_radius))
    
    u1 = Translate([strap_d/2-strap_radius,0,0],
                   fixed_roundedcube(strap_latch_l-strap_d/2+strap_radius*2, w, strap_d, strap_radius))
    
    u2 = Translate([strap_d/2,0,strap_d/2],
                   Rotate([-90,0,0], roundedcylinder(strap_d, w, strap_radius, True)))
    
    hole = Translate([strap_d/2, -1, strap_d/2],
                     Rotate([-90,0,0], Cyl(d=h_dia, h=w+2)))
    
    latch_full = Union(p1, Difference(Union(u1, u2), hole))

    if not long and visualize_screws:
        s_off = strap_d/2+screw_visual_off
        if latch_id == 1:
            latch_full = Union(latch_full, Translate([strap_d//2, 0, s_off], Rotate([90,0,0], screw(False, False, screw_len_strap))))
        elif latch_id == 2:
            latch_full = Union(latch_full, Translate([strap_d//2, w, s_off], Rotate([-90,0,0], screw(False, False, screw_len_strap))))

    return latch_full

# 2. Strap piece:
def strap_piece(latch_dist=strap_latch_dist):
    y_off = (strap_piece_body_h-latch_dist)//2 - strap_latch_ws
    l1 = Translate([0, y_off, 0], strap_latch(False, 1))
    l2 = Translate([0, y_off+strap_latch_ws+latch_dist, 0], strap_latch(False, 2))

    # Central body:
    c_body = Translate([strap_latch_l,0,0],
                       fixed_roundedcube(strap_piece_body_w, strap_piece_body_h, strap_d, strap_radius))
    
    lx = strap_latch_l*2+strap_piece_body_w
    ly = strap_latch_wl/2+strap_piece_body_h/2
    l_long= Translate([lx,ly,0], Rotate([0,0,180], strap_latch(True)))

    return Union(l1,l2,c_body,l_long)

# 3. Strap:
def strap(assembled=True, rows=strap_rows, angle=0):
    all_solids=[]
    for y in range(rows):
        y_pos = y * (strap_piece_body_h + strap_piece_dist)

        # Base piece:
        p_base = strap_piece(strap_latch_w_body)
        p_off = strap_piece_w-strap_d/2
        p0 = Translate([0,y_pos,0], Translate([p_off, 0, strap_d/2], Rotate([0, angle, 0], Translate([-p_off,0,-strap_d/2], p_base))))
        all_solids.append(p0)

        if strap_cols > 1:
            for x in range(1, strap_cols):
                dist_x = (strap_piece_w-strap_d) if assembled else (strap_piece_w + strap_piece_dist)
                all_solids.append(Translate([x*dist_x, y_pos, 0], strap_piece()))

    return all_solids


# Create the parts:
pieces = strap(assembled=False)

# Visualize:
from ocp_vscode import show
show(*pieces, names=[f"Piece_{i+1}" for i in range(len(pieces))], colors=["orange"]*len(pieces))

# Exports:
export_step(Compound(children=pieces), "strap.step")
export_stl(Compound(children=pieces), "strap.stl")