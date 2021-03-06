import sys
import os
import bpy
from mathutils import Vector, Matrix
import math
from math import pi
import imp

Testing = False

#Controller_Radius = bpy.context.scene.controller_radius

Rim_Center = (0, 0, 0)
#Rim_Radius = bpy.context.scene.rim_radius
#Rim_Minor_Radius = 0.005


Hub_Center = (0, 0, 0) #TODO: Probably don't need this
#Hub_Thickness = 0.0015

#Spinner_Hub_Radius = 0.04
#Spinner_Radius = Rim_Radius
Spinner_Radius = 0.25
#Spinner_Number = 12
#Spinner_Start_Angle = math.radians(0)

#TODO: Need spoke_offset?
#Spoke_Offset = 0.02
#Spoke_Len = Spinner_Radius - Spoke_Offset
#Spoke_Number = 2
#Spoke_Start_Angle = math.radians(0)

#Linkage_Male_Len = 0.12
#Linkage_Female_Len = 0.12
#Linkage_Incidence = math.radians(60)
#Linkage_Offset = bpy.context.scene.spinner_hub_radius / 2

def add_controller():
    bpy.ops.mesh.primitive_circle_add(radius=bpy.context.scene.controller_radius, fill_type='NGON', location=(bpy.context.scene.rim_radius+bpy.context.scene.controller_radius+0.10, 0, 0))
    controller = bpy.context.object
    controller.name = 'controller'
    controller.location = (1, 0, 0) #TODO: ???
    return controller

def add_rim():
    bpy.ops.mesh.primitive_torus_add(mode='MAJOR_MINOR', major_radius=bpy.context.scene.rim_radius, minor_radius=bpy.context.scene.rim_minor_radius, view_align=False, location=Rim_Center, rotation=(0.0, 0.0, 0.0), layers=bpy.context.scene.layers)
    rim = bpy.context.object
    rim.name = 'rim'
    bpy.ops.object.editmode_toggle()
    bpy.ops.transform.shrink_fatten(value=bpy.context.scene.rim_minor_radius)
    bpy.ops.object.editmode_toggle()
    return rim

def add_spinners(rim):
    spinners = []
    controller = add_controller()
    prev_hub = controller
    for spinner_num in range(bpy.context.scene.spinner_number):
        angle = spinner_num * 2 * math.pi/bpy.context.scene.spinner_number + bpy.context.scene.spinner_start_angle
        spinner = add_spinner_to_rim(rim, angle, spinner_num % 2)
        spinners.append(spinner)
        hub = spinner['hub']
        cns = hub.constraints.new('COPY_ROTATION')
        cns.target = prev_hub
        if controller == prev_hub:
            cns.target_space = 'WORLD'            
        else:
            cns.target_space = 'LOCAL'
        cns.owner_space = 'LOCAL'
        cns.use_x = False
        cns.use_y = False
        prev_hub = hub
    return spinners
    
def add_spinner_to_rim(rim, angle, spinner_type = 0):
    spinner = add_spinner(spinner_type)
    hub = spinner['hub']
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    hub_empty = bpy.context.object
    hub_empty.name = 'hub_empty'
    hub_empty.empty_draw_size = 0.02
    spinner['hub_empty'] = hub_empty
    trans_to_rim = Matrix.Translation(Vector((bpy.context.scene.rim_radius, 0, 0)))
    rot_on_rim = Matrix.Rotation(angle, 4, 'Z')
    rot_perp_to_rim = Matrix.Rotation(pi/2, 4, 'X')
    m = rot_on_rim * trans_to_rim * rot_perp_to_rim 
    hub_empty.rotation_euler = m.to_euler()
    hub_empty.location = m.to_translation()
    hub.parent = hub_empty
    hub_empty.parent = rim
    return spinner
    
def add_spinner(spinner_type):
    hub = add_hub()
    male_linkage = add_male_linkage()
    male_linkage.parent = hub
    female_linkage = add_female_linkage()
    female_linkage.parent = hub
    spokes = add_spokes(hub, spinner_type)
    result = {'hub': hub, 'male_linkage': male_linkage, 'female_linkage': female_linkage}
    return result

def add_hub():
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=bpy.context.scene.spinner_hub_radius, depth=bpy.context.scene.hub_thickness  , end_fill_type='NGON', calc_uvs=False, view_align=False, enter_editmode=False, location=Hub_Center, layers=bpy.context.scene.layers)
    hub = bpy.context.object
    hub.name = 'hub'
    return hub

def add_spokes(hub, spinner_type):
    spokes = []
    if spinner_type == 0:
        for spoke_num in range(bpy.context.scene.spoke_number):
            spoke = add_spoke(hub, spoke_num * 2 * pi / bpy.context.scene.spoke_number + bpy.context.scene.spoke_start_angle)
            vane_src = bpy.context.scene.objects[bpy.context.scene.vane_1]
            me = vane_src.data
            vane = bpy.data.objects.new(bpy.context.scene.vane_1, me)
            vane.location = (0,0,0)
            bpy.context.scene.objects.link(vane)
            rot_perp = Matrix.Rotation(-pi/2, 4, 'Y')
            x = 1
            if spoke_num % 2:
                x = -1
            rot_perp2 = Matrix.Rotation(x * pi/2, 4, 'X')
            rot3 = Matrix.Rotation(0, 4, 'Z')
            trans = Matrix.Translation(Vector((0, 0, bpy.context.scene.spoke_len/2)))
            m = trans * rot_perp * rot_perp2 * rot3
            vane.rotation_euler = m.to_euler()
            vane.location = m.to_translation()
            vane.parent = spoke
            spokes.append(spoke)
    elif spinner_type == 1:
        for spoke_num in range(bpy.context.scene.spoke_number):
            spoke = add_spoke(hub, spoke_num * 2 * pi / bpy.context.scene.spoke_number + bpy.context.scene.spoke_start_angle+pi/2)
            vane_src = bpy.context.scene.objects[bpy.context.scene.vane_2]
            me = vane_src.data
            vane = bpy.data.objects.new(bpy.context.scene.vane_2, me)
            vane.location = (0,0,0)
            bpy.context.scene.objects.link(vane)
            rot_perp = Matrix.Rotation(-pi/2, 4, 'Y')
            rot_perp2 = Matrix.Rotation(pi/2, 4, 'X')
            trans = Matrix.Translation(Vector((0, 0, -0.03)))
            m = trans * rot_perp * rot_perp2
            vane.rotation_euler = m.to_euler()
            vane.location = m.to_translation()
            vane.parent = spoke
            spokes.append(spoke)
        return spokes

def add_spoke(hub, angle = 0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0015, depth=bpy.context.scene.spoke_len  , end_fill_type='NGON', calc_uvs=False, view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0.0, 0.0, 0.0), layers=bpy.context.scene.layers)
    spoke = bpy.context.object
    spoke.name = 'spoke'
    spoke.parent = hub
    bpy.context.scene.cursor_location = Vector((0,0,0))
    trans = Matrix.Translation(Vector((bpy.context.scene.spoke_offset + bpy.context.scene.spoke_len/2, 0, 0)))
    rot = Matrix.Rotation(angle, 4, 'Z')
    rot_perp = Matrix.Rotation(pi/2, 4, 'Y')
    m = rot * trans * rot_perp 
    spoke.rotation_euler = m.to_euler()
    spoke.location = m.to_translation()
    return spoke

def add_male_linkage():
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0015, depth=bpy.context.scene.linkage_male_len  , end_fill_type='NGON', calc_uvs=False, view_align=False, enter_editmode=False, location=(0, 0, bpy.context.scene.linkage_male_len/2), rotation=(0.0, 0.0, 0.0), layers=bpy.context.scene.layers)
    linkage = bpy.context.object
    linkage.name = 'male linkage'
    bpy.context.scene.cursor_location = Vector((0,0,0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.transform.rotate(value=bpy.context.scene.linkage_incidence-math.radians(90), axis=(1,0,0))
    bpy.ops.transform.translate(value=(0, bpy.context.scene.linkage_offset, 0))
    return linkage

def add_female_linkage():
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.0015, depth=bpy.context.scene.linkage_female_len  , end_fill_type='NGON', calc_uvs=False, view_align=False, enter_editmode=False, location=(0, 0, bpy.context.scene.linkage_female_len/2), rotation=(0.0, 0.0, 0.0), layers=bpy.context.scene.layers)
    linkage = bpy.context.object
    linkage.name = 'female linkage'
    bpy.context.scene.cursor_location = Vector((0,0,0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.transform.rotate(value= -bpy.context.scene.linkage_incidence-math.radians(90), axis=(1,0,0))
    bpy.ops.transform.translate(value=(0, bpy.context.scene.linkage_offset, 0))
    return linkage

def append_obj(blend_file_name, obj_name):
    import wind_spinner
    wind_spinner_file = wind_spinner.__file__
    file = os.path.dirname(wind_spinner.__file__)+"/"+blend_file_name
    section = '/Object/'
    filepath = file + section + obj_name
    directory = file + section
    filename = obj_name
    prior_objects = [object for object in bpy.context.scene.objects]
    bpy.ops.wm.append(filepath=file, filename=filename, directory=directory, autoselect=True)
    current_objects = [object for object in bpy.context.scene.objects]
    new_objects = set(current_objects) - set(prior_objects)
    return new_objects.pop()

def delete_all():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def test2():
    pass
        
def test():
    hub = add_hub()
    spoke_num = 0
    spoke = add_spoke(hub, spoke_num * 2 * pi / bpy.context.scene.spoke_number + bpy.context.scene.spoke_start_angle+pi/2)
    vane = append_obj('vane2.blend', 'Large Disk')
    vane.scale = vane.scale * 0.5
    rot_perp = Matrix.Rotation(-pi/2, 4, 'Y')
    rot_perp2 = Matrix.Rotation(pi/2, 4, 'X')
    trans = Matrix.Translation(Vector((0, 0, -0.03)))
    m = trans * rot_perp * rot_perp2
    vane.rotation_euler = m.to_euler()
    vane.location = m.to_translation()
    vane.parent = spoke

def reload_me():
    imp.reload(sys.modules[__name__])

def run():
    delete_all()
    if Testing:
        test()
    else:
        rim = add_rim()
        spinners = add_spinners(rim)
    
if __name__ == "__main__":
    run()