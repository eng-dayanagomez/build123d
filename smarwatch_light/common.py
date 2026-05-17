"""
common.py

In this file are the global variables and the global functions
"""

from build123d import *

# Global variables/parameters:

pcb_h=1.6
body_dia=43.7
body_radius=1.5
mount_dist_w=18.0
mount_dist_h=41.0
face_mount_w=6.0
face_mount_d=face_mount_w
base_mount_w=mount_dist_w + face_mount_d
base_mount_d=10.0
base_mount_off=1.65
nut_dia=1.9
screw_dia=2.3
screw_gap=screw_dia-nut_dia
screw_head_dia=5.0
screw_head_height=2.3
usb_flat=0.7
button_angle_off=32.5
button_angle_r=+90+button_angle_off
button_angle_1=+90-button_angle_off
button_angle_2=-90+button_angle_off
button_angle_3=-90-button_angle_off
strap_d=5.0
strap_latch_ws=3.3
strap_latch_wl=8.4
base_strap_w=strap_latch_wl
base_strap_add_l=0.3

visualize_screws=False
screw_visual_off=5.0
screw_len_body=12.0
screw_len_strap=7.5

# Global functions:

# 1. Cube:
def Cube(size):
    if isinstance(size, (int, float)): size = [size, size, size]
    if size[0] <= 1e-5 or size[1] <= 1e-5 or size[2] <= 1e-5: return None
    return Box(size[0], size[1], size[2], align=(Align.MIN, Align.MIN, Align.MIN))

# 2. Cylinder:
def Cyl(d=None, h=None):
    if h <= 1e-5 or d <= 1e-5: return None
    return Cylinder(radius=d/2, height=h, align=(Align.CENTER, Align.CENTER, Align.MIN))

# 3. Sphere:
def Sph(r=None):
    if r <= 1e-5: return None
    return Sphere(radius=r)

# 4. Torus:
def Tor(r1, r2):
    if r1 <= 1e-5 or r2 <= 1e-5: return None
    return Torus(major_radius=r1, minor_radius=r2, align=(Align.CENTER, Align.CENTER, Align.CENTER))

# 5. Translate:
def Translate(vec, obj):
    if obj is None: return None
    if isinstance(obj, list): return [o.moved(Location((vec[0], vec[1], vec[2]))) for o in obj if o is not None]
    return obj.moved(Location((vec[0], vec[1], vec[2])))

# 6. Rotate:
def Rotate(vec, obj):
    if obj is None: return None
    if isinstance(obj, list): return [o.moved(Rotation((vec[0], vec[1], vec[2]))) for o in obj if o is not None]
    return obj.moved(Rotation((vec[0], vec[1], vec[2])))

# 7. Scale:
def Scale(vec, obj):
    if obj is None: return None
    def _scale_single(o):
        res = o
        if vec[0] < 0: res = mirror(res, about=Plane.YZ)
        if vec[1] < 0: res = mirror(res, about=Plane.XZ)
        if vec[2] < 0: res = mirror(res, about=Plane.XY)
        # Reconstruct normal solids post-mirror:
        with BuildPart() as p:
            add(res)
        return p.part
    if isinstance(obj, list): return [_scale_single(o) for o in obj if o is not None]
    return _scale_single(obj)

# 8. Union:
def Union(*objs):
    valid_objs= []
    for o in objs:
        if isinstance(o, list): valid_objs.extend([x for x in o if x is not None])
        elif o is not None: valid_objs.append(o)
    if not valid_objs: return None
    with BuildPart() as p:
        for o in valid_objs: add(o)
    return p.part

# 9. Difference:
def Difference(base, *subs):
    if base is None: return None
    valid_subs = []
    for s in subs:
        if isinstance(s, list): valid_subs.extend([x for x in s if x is not None])
        elif s is not None: valid_subs.append(s)
    with BuildPart() as p:
        add(base)
        for s in valid_subs: add(s, mode=Mode.SUBTRACT)
    return p.part


# Figures that will be used later in many occasions:

# 1. Prism:
def prism(l, w, h):
    if l <= 1e-5 or w <= 1e-5 or h <= 1e-5: return None
    with BuildPart() as p:
        with BuildSketch(Plane.YZ):
            Polygon([(0,0),(w,0),(w,h)])
        extrude(amount=l)
    return p.part

# 2. Usb_flatten:
def usb_flatten(h):
    return Translate([-body_dia/2,-body_dia/2,-1], Cube([usb_flat, body_dia, h+1.1]))

# 3. Rounded cylinder:
def roundedcylinder(d, h, r, top=False):
    parts=[]
    if top:
        parts.append(Cyl(d=d-2*r,h=h))
        parts.append(Translate([0,0,r], Cyl(d=d, h=h-2*r)))
        parts.append(Translate([0,0,r], Tor(d/2-r, r)))
        parts.append(Translate([0,0,h-r], Tor(d/2-r, r)))
    else:
        parts.append(Cyl(d=d-2*r,h=h))
        parts.append(Translate([0,0,r], Cyl(d=d, h=h-r)))
        parts.append(Translate([0,0,r], Tor(d/2-r, r)))
    return Union(*parts)

# 4. Rounded cube side:
def roundedcube_side(x,y,z,r):
    return Union(
        Translate([r,r,0], Cube([x-r*2, y-r*2, z])),
        Translate([r,0,0], Cube([x-r*2, y, z])),
        Translate([0,r,0], Cube([x, y-r*2, z])),
        Translate([r,r,0], Cyl(d=r*2, h=z)),
        Translate([x-r,r,0], Cyl(d=r*2, h=z)),
        Translate([r,y-r,0], Cyl(d=r*2, h=z)),
        Translate([x-r,y-r,0], Cyl(d=r*2, h=z)),
    )

# 5. Rounded cube bottom half:
def roundedcube_bot_half(x, y, z, r):
    return Union(
        Translate([0,0,r], Cube([x, y, z-r])),
        Translate([r,0,0], Cube([x-r*2, y, r])),
        Translate([r,0,r], Rotate([-90,0,0], Cyl(d=r*2, h=y))),
        Translate([x-r,0,r], Rotate([-90,0,0], Cyl(d=r*2, h=y))),
    )

# 6. Rounded cube side bottom:
def roundedcube_side_bot(x,y,z,r):
    return Union(
        Translate([0,r,0], roundedcube_bot_half(x, y-r*2, z, r)),
        Translate([x-r,0,0], Rotate([0,0,90], roundedcube_bot_half(y, x-r*2, z, r))),
        Translate([r,r,r], Sph(r)),
        Translate([x-r,r,r], Sph(r)),
        Translate([r,y-r,r], Sph(r)),
        Translate([x-r,y-r,r], Sph(r)),
        Translate([0,0,r], roundedcube_side(x,y,z-r,r)),
    )

# 7. Rounded cube:
def roundedcube(x,y,z,r, round_bot=False, round_top=False):
    if not round_bot:
        return roundedcube_side(x,y,z,r)
    else:
        if round_top:
            return Union(
                roundedcube_side_bot(x,y,z/2,r),
                Rotate([180,0,0], Translate([0,y,z], roundedcube_side_bot(x,y,z/2,r)))
            )
        else:
            return roundedcube_side_bot(x,y,z,r)
        
# 8. Screw part:
def screw_part(add_val, height=0):
    if height == 0:
        return Union(Cyl(d=screw_head_dia, h=10), Translate([0,0,-20], Cyl(d=screw_dia+add_val, h=21)))
    else:
        return Union(Cyl(d=screw_head_dia, h=screw_head_height), Translate([0,0,-height], Cyl(d=screw_dia+add_val, h=height+1)))
    
# 9. Screw:
def screw(nut=False, bottom=False, height=20):
    add_val = -screw_gap if nut else 0
    part = screw_part(add_val, height)
    if bottom: return Translate([0,0,height], part)
    return part

# 10. Base screws:
def base_screws(nut=True, bottom=True):
    parts=[]
    for i in [1, -1]:
        for j in [1, -1]:
            parts.append(Translate([i*mount_dist_w/2, j*mount_dist_h/2,0], screw(nut, bottom)))
    return Union(*parts)

# 11. Body:
def body(h, rounded=False):
    parts=[]
    if rounded: parts.append(roundedcylinder(body_dia, h, body_radius))
    else: parts.append(Cyl(d=body_dia,h=h))

    rc = roundedcube(base_mount_w, base_mount_d, h, body_radius, rounded)
    parts.append(Translate([-base_mount_w/2, -body_dia/2 - base_mount_off, 0], rc))
    parts.append(Scale([1,-1,1], Translate([-base_mount_w/2, -body_dia/2-base_mount_off, 0], rc)))

    return Union(*parts)

# 12. Strap hull:
def StrapHull(w,d,cyl_d,h,warp):
    if w <= 1e-5: return None
    with BuildPart() as p:
        with BuildSketch(Plane.YZ):
            Rectangle(0.1, h, align=(Align.MIN, Align.MIN))
            with Locations((d-0.1-cyl_d/2, h/2-0.05+warp)):
                Circle(cyl_d/2)
            make_hull()
        extrude(amount=w)
    return p.part

# 13. FStrap hull:
def FStrapHull(w,add_val,d,cyl_d,h,warp):
    if w <= 1e-5: return None
    with BuildPart() as p:
        with BuildSketch(Plane.YZ):
            with Locations((-add_val,0)):
                Rectangle(0.1+add_val, h, align=(Align.MIN, Align.MIN))
            with Locations((d-0.1-cyl_d/2, h/2-0.05+warp)):
                Circle(cyl_d/2)
            make_hull()
        extrude(amount=w)
    return p.part