"""
assembly.py

Output:
    assembly.step
"""

from build123d import *
from common import *

# Import other functions nedeed that comes from the other files:
from base import base, base_height
from mid import mid, mid_height, mid_buttons_original
from top import face
from strap import strap, strap_piece_body_h

# Assembly variables:
view_assembly = True

assembly_dist = 0
print_dist = 5
assembly_strap_angle = 16.5
assembly_strap_off = 1.3 + base_strap_add_l

# Create the assembly:
def assembly():
    parts_list=[]

    # 1. Face (Top) part:
    z_face = base_height + mid_height + assembly_dist*2
    face_part = Translate([0,0,z_face], face())
    parts_list.append((face_part, "Face", "green"))

    # 2. Buttons parts:
    z_buttons = base_height + assembly_dist
    buttons_part = Translate([0,0,z_buttons], mid_buttons_original())
    parts_list.append((buttons_part, "Buttons", "red"))

    # 3. Mid body part:
    z_mid = base_height + assembly_dist
    mid_part = Translate([0,0,z_mid], mid())
    parts_list.append((mid_part, "Mid", "blue"))

    # 4. Base part:
    base_part = base()
    parts_list.append((base_part, "Base", "orange"))

    # 5. Straps:
    s_top_list = strap(assembled=True, rows=1, angle=assembly_strap_angle)

    strap_top_final = Translate([strap_piece_body_h/2, body_dia/2 + assembly_strap_off, 0],
                                Rotate([0,0,90], s_top_list))
    parts_list.append((strap_top_final, "Strap_Top", "cyan"))

    strap_bot_final = Translate([-strap_piece_body_h/2, -body_dia/2 - assembly_strap_off, 0],
                                Rotate([0,0,-90], s_top_list))
    parts_list.append((strap_bot_final, "Strap_Bot", "cyan"))

    return parts_list

# Print the layout:
def print_layout():
    parts_list=[]
    parts_list.append((face(), "Face", "green"))
    parts_list.append((Translate([body_dia+print_dist,0,0], mid()), "Mid", "blue"))
    parts_list.append((Translate([(body_dia+print_dist)*2,0,0], base()), "Base", "orange"))

    strap_print = Translate([-body_dia/2+print_dist, body_dia/2+print_dist*2, 0],
                            strap(assembled=False))
    parts_list.append((strap_print, "Strap_Layout", "cyan"))

    return parts_list

# Visualize:
from ocp_vscode import show

if view_assembly:
    assy_data=assembly()

    final_objs=[]
    final_names=[]
    final_colors=[]
    objs_to_export=[]

    for obj, name, color in assy_data:

        if isinstance(obj, list):
            for i, sub_obj in enumerate(obj):
                rotated = Rotate([0,0,90], sub_obj)
                final_objs.append(rotated)
                final_names.append(f"{name}_{i}")
                final_colors.append(color)
                objs_to_export.append(sub_obj)
        else:
            rotated = Rotate([0,0,90], obj)
            final_objs.append(rotated)
            final_names.append(name)
            final_colors.append(color)
            objs_to_export.append(obj)

    show(*final_objs, names=final_names, colors=final_colors)


    # Final export:
    watch_export = Compound(objs_to_export).moved(Rotation((0,0,90)))
    export_step(watch_export, "smartwatch_assembly.step")
    export_stl(watch_export, "smartwatch_assembly.stl")

else:
    layout_data = print_layout()

    flat_layout=[]
    flat_names=[]
    flat_colors=[]
    for obj, name, color in layout_data:
        if isinstance(obj, list):
            flat_layout.extend(obj)
            flat_names.extend([f"{name}_{i}" for i in range(len(obj))])
            flat_colors.extend([color] * len(obj))
        else:
            flat_layout.append(obj)
            flat_names.extend(name)
            flat_colors.extend(color)
    
    show(*flat_layout, names=flat_names, colors=flat_colors)