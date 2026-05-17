"""
top.py

Outputs:
    top.step
    top.stl
"""

from build123d import *
from common import *

# Parameters:

draw_text=False

face_hole_dia=33

face_glass_dia=37.4
face_glass_height=1.85

face_cyl_1_dia = body_dia
face_cyl_1_height = 1.0
face_cyl_2_dia = 39.0
face_cyl_2_height = 1.4

face_mount_base=0.6

face_height=face_cyl_1_height+face_cyl_2_height

text_off=face_cyl_2_dia/2 - (face_cyl_2_dia-face_hole_dia)/4 + 0.5
text_height = face_height - face_glass_height-0.4
text_size=3.0

# Extra function, not in common.py:
def ConeWrap(d1, d2, h):
    if h <= 1e-5: return None
    if abs(d1-d2) < 1e-6:
        return Cyl(d=d1, h=h)
    
    with BuildPart() as p:
        Cone(bottom_radius=d1/2, top_radius=d2/2, height=h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return p.part

# Build functions:

# 1. Face base:
def face_base():
    c1 = ConeWrap(d1=body_dia, d2=face_cyl_1_dia, h=face_cyl_1_height)
    c2 = Translate([0,0,face_cyl_1_height], ConeWrap(d1=face_cyl_1_dia, d2=face_cyl_2_dia, h=face_cyl_2_height))
    return Union(c1, c2)

# 2. Face Mount:
def face_mount(for_top=True, base_h=face_mount_base):

    with BuildPart() as p:
        with BuildSketch(Plane.XY) as s:

            with Locations((-face_mount_w/2, -face_mount_d/2)):
                Rectangle(face_mount_w, face_mount_d, align=(Align.MIN, Align.MIN))
            
            fillet(s.vertices(), radius=body_radius)

            if for_top:

                with BuildSketch(Plane.XY,  mode=Mode.PRIVATE) as body_sketch:
                    with Locations((mount_dist_w/2, mount_dist_h/2)):
                        Circle(body_dia/2)

                    with Locations((face_mount_w/2+25, -face_mount_d/2-1+25)):
                        Rectangle(50,50,mode=Mode.SUBTRACT)
                    with Locations((-50-face_mount_w/2+25, -face_mount_d/2-1+25)):
                        Rectangle(50,50,mode=Mode.SUBTRACT)
                    with Locations((0, face_mount_d/2+25)):
                        Rectangle(50,50,mode=Mode.SUBTRACT)
                
                add(body_sketch.sketch)
                make_hull()

        extrude(amount=base_h)

    res = p.part
    if for_top:
        s_cut = Translate([0,0,base_h], screw())
        res = Difference(res, s_cut)

    return res

# 3. Face mounts:
def face_mounts(for_top=True, base_h=face_mount_base):
    m1 = Translate([-mount_dist_w/2, -mount_dist_h/2, 0], face_mount(for_top, base_h))
    m2 = Translate([mount_dist_w/2, -mount_dist_h/2, 0], Scale([-1,1,1], face_mount(for_top, base_h)))
    m3 = Translate([-mount_dist_w/2, mount_dist_h/2, 0], Scale([1,-1,1], face_mount(for_top, base_h)))
    m4 = Translate([mount_dist_w/2, mount_dist_h/2, 0], Scale([-1,-1,1], face_mount(for_top, base_h)))
    return Union(m1, m2, m3, m4)

# 4. Face whole:
def face_whole():
    u_obj=Union(face_base(), face_mounts())

    s_locs = [
        (mount_dist_w/2, mount_dist_h/2),
        (-mount_dist_w/2, mount_dist_h/2),
        (mount_dist_w/2, -mount_dist_h/2),
        (-mount_dist_w/2, -mount_dist_h/2),
    ]
    cuts= [Translate([x, y, face_mount_base], screw()) for x, y in s_locs]

    return Difference(u_obj, *cuts)

# 5. Text rotated:
def text_rotated(s, angle):
    with BuildPart() as p:
        with BuildSketch():
            Text(s, font_size=text_size, font_style=FontStyle.BOLD, align=(Align.CENTER, Align.CENTER))
        extrude(amount=text_height+0.1)

    res = Rotate([0,0,angle], p.part)
    res = Translate([0, -text_off, 0], res)
    res = Rotate([0,0,-angle], res)
    return res

# 6. Face:
def face():
    base_obj = face_whole()

    c1 = usb_flatten(face_height)
    c2 = Translate([0,0,-1], Cyl(d=face_hole_dia, h=face_height+2))
    c3 = Translate([0,0,-1], Cyl(d=face_glass_dia, h=face_glass_height+1))

    cuts = [c1,c2,c3]

    if draw_text:
        angles = [button_angle_r, button_angle_1, button_angle_2, button_angle_3]
        labels = ["R","1","2","3"]
        txt_objs = [text_rotated(l, a) for l, a in zip(labels, angles)]
        cuts.append(Translate([0,0, face_height-text_height], Union(*txt_objs)))

    return Difference(base_obj, *cuts)

from ocp_vscode import show

# Build the part:
face_model = face()

# Visualize:
show(face_model)

# Exports:
export_step(face_model, "top.step")
export_stl(face_model, "top.stl")