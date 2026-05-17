"""
mid.py

Outputs:
    mid.step
    mid.stl
"""

from build123d import *
from common import *

# Parameters:

use_single_piece_buttons = False

lcd_parts_height=4.3
electronics_height=lcd_parts_height+pcb_h

mid_base=0.8
electronics_dia=37.3
cut_w=7.0
cut_h=38.0
cut_tw=14.5
cut_th=4.5
cut_off=1

top_cut_w=14.6
top_cut_l=3.0
top_cut_off=1.6
bot_cut_w=15.8
bot_cut_l=4.2
bot_cut_off=2.3
bot_cut_wall_h=pcb_h+0.2
bot_cut_wall_w=1.2

usb_w=8.3
usb_h=3.8
usb_cut=8.5
usb_cut_off=0.7
usb_cut_len=1.6

mid_strap_cut_w=10
mid_strap_cut_h=5
mid_strap_cut_d=mid_strap_cut_h-1
mid_strap_cut_off_y=1.1
mid_strap_cut_off_z=0.5

mid_button_width=4.3-0.3
mid_button_height=3.0
mid_button_depth=4.0
mid_button_gap_width=2.6
mid_button_gap_wall=1.6
mid_button_off=0
mid_button_holder_width=5.4
mid_button_holder_depth=1.4

button_height=2.2
button_length=5.0
button_width=3.7
button_radius=0.5
button_wing=0.5
button_wing_len=1.0

mid_snap_dia=2+0.2
mid_snap_off=2.55

mid_threshold=4.0

mid_height=mid_base+electronics_height

# Build functions:

# 1. Mid cutout:
def mid_cutout(h):
    with BuildPart() as p:
        with BuildSketch():
            Rectangle(cut_w, cut_h, align=(Align.MIN, Align.MIN))
            with Locations((-(cut_tw-cut_w)/2, cut_h-cut_th)):
                Rectangle(cut_tw, cut_th, align=(Align.MIN, Align.MIN))
        extrude(amount=h)
    return p.part.moved(Location((-cut_w/2,-cut_h/2,0)))

def mid_button_cut_original():
    c1 = Translate([-mid_button_width/2,-1,0], Cube([mid_button_width, mid_button_depth+2, mid_button_height]))

    y_off_holder = (body_dia - electronics_dia)/2 - mid_button_holder_depth
    c2 = Translate([-mid_button_holder_width/2, y_off_holder,0], Cube([mid_button_holder_width, mid_button_holder_depth+1, mid_button_height]))

    c3 = Translate([-mid_button_gap_width/2, mid_button_gap_wall, mid_button_height-1], Cube([mid_button_gap_width, mid_button_depth-mid_button_gap_wall+1, mid_height]))
    return Union(c1,c2,c3)

def mid_button_original():
    rb = roundedcube(button_width, button_height, button_length, button_radius, round_bot=True)
    t1 = Translate([button_width+button_wing,0,button_length], Rotate([0,180,0], rb))

    c1 = Cube([button_wing+button_radius, button_height, button_wing_len])

    c2 = Translate([button_width, 0, 0], Cube([button_wing+button_radius, button_height, button_wing_len]))
    return Union(t1, c1, c2)

# Mid Buttons:
def mid_buttons_original():
    parts=[]
    for i in [button_angle_r, button_angle_1, button_angle_2, button_angle_3]:
        b = mid_button_original()
        t1 = Rotate([90,0,0], b)
        y_loc= -body_dia/2+button_length-button_wing_len
        t2 = Translate([-button_width/2-button_wing, y_loc, button_height], t1)
        parts.append(Rotate([0,0,i], t2))
    return Union(*parts)

# Button cutouts:
def buttons_cutouts():
    if use_single_piece_buttons:
        return None
    return mid_button_cut_original()

# Buttons assembly:
def buttons_assembly():
    if use_single_piece_buttons:
        return None
    return mid_buttons_original()

# Mid body cut 2:
def mid_body_cut_2():
    return Translate([-mid_strap_cut_w/2, -body_dia/2-7, mid_height-5], Rotate([45,0,45], Cube([5,10,1])))

# Mid body cut main:
def mid_body_cut():
    p1 = Translate([-mid_strap_cut_w/2, -body_dia/2+mid_strap_cut_off_y, mid_height + mid_strap_cut_off_z], Rotate([180,0,0], prism(mid_strap_cut_w, mid_strap_cut_d, mid_strap_cut_h)))

    c2 = mid_body_cut_2()
    c3 = Scale([-1,1,1], mid_body_cut_2())
    return Union(p1, c2, c3)

# Mid body:
def mid_body():
    b = body(mid_height)
    cut1 = mid_body_cut()
    cut2 = Scale([1,-1,1], mid_body_cut())

    main_body = Difference(b, cut1, cut2)
    top_cyl = Translate([0,0,mid_height-1], Cyl(d=body_dia, h=1))
    return Union(main_body, top_cyl)

# Build mid part:
def mid():
    m_body = mid_body()

    cuts = []
    cuts.append(Rotate([0,0,180], Translate([0,-cut_off,-1], mid_cutout(mid_base+2))))
    cuts.append(Translate([-body_dia/2-1, -usb_w/2, mid_base], Cube([body_dia/2, usb_w, usb_h])))

    x_usb_2 = -usb_cut_len-body_dia/2+(body_dia-electronics_dia)/2+usb_cut_off
    cuts.append(Translate([x_usb_2, -usb_cut/2, mid_base], Cube([usb_cut_len, usb_cut, mid_height])))

    cuts.append(usb_flatten(mid_height))

    for i in [button_angle_r, button_angle_1, button_angle_2, button_angle_3]:
        b_cut = Translate([0,-body_dia/2, mid_base+mid_button_off], buttons_cutouts())
        cuts.append(Rotate([0,0,i], b_cut))

    cuts.append(Translate([0,0,-1], base_screws(nut=False, bottom=True)))

    elec_cyl = Translate([0,0,mid_base], Cyl(d=electronics_dia, h=mid_height-mid_base+1))
    top_cut = Translate([-top_cut_w/2, electronics_dia/2-top_cut_off, mid_base], Cube([top_cut_w, top_cut_l, mid_height-mid_base+1]))

    bot_box = Cube([bot_cut_w, bot_cut_l, mid_height-mid_base+1])
    bot_wall_sub = Translate([-1,-1,-1], Cube([bot_cut_w+2, bot_cut_wall_w+1, mid_height-mid_base-bot_cut_wall_h+1]))
    bot_final = Translate([-bot_cut_w/2, -electronics_dia/2-bot_cut_off, mid_base], Difference(bot_box, bot_wall_sub))

    mid_final_base = Difference(m_body, *cuts, elec_cyl, top_cut, bot_final)

    snaps = []
    snap_angles = [-135-10, -45+10, 135+10, 45-10]
    for angle in snap_angles:
        s = Translate([0,-body_dia/2+mid_snap_off, mid_base], Cyl(d=mid_snap_dia, h=mid_height-mid_base))
        snaps.append(Rotate([0,0,angle], s))

    return Union(mid_final_base, *snaps)

# Mid assembly with the main body and the buttons:
def mid_assembly():
    m = mid()
    return Union(m, buttons_assembly())

# Create the part:
mid_model = mid_assembly()

# Visualize:
from ocp_vscode import show
show(mid_model)

# Exports:
m = mid()
export_step(m, "mid.step")
export_stl(m, "mid.stl")