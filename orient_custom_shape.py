# <pep8 compliant>
#
# orient_custom_shape.py
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Orient Custom Shape",
    "author": "Gilles Pagia & Ron Tarrant",
    "version": (0,1),
    "blender": (2, 6, 3),
    "api": 46487,
    "location": "Properties > Bone > Orient Custom Shape (visible in pose mode only)",
    "description": "Rotates, scales and translates a custom bone shape to match rotation, scale and translation of its bone",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"}

"""
Orient Custom Shape
This script orients the translation, rotation and scale of a bone's custom shape
to match the rotation, translation and scaling of the bone itself. Once orientation
is matched, editing the mesh to put the bone 'handle' where it's needed is far
easier.
This script takes the opposite approach to that of Auto Custom Shape. Auto
Custom Shape creates a new mesh object each time. Orient Custom Shape uses
whatever pre-built mesh object you'd care to use.

Usage:
1) Install and activate the script in the Add-Ons tab of User Preferences,
2) build a rig,
3) load or build a set of custom shape meshes,
4) go to Pose Mode,
5) for each bone that will have a Custom Shape, set the custom shape using
   the drop-down menu in Bone Properties -> Display,
6) click on the Orient Bone Shape button,
7) Select the shape mesh (the mesh assigned to the bone in Step 5),
8) switch to Edit Mode,
9) select all vertices, and
10) reposition/rotation/whatever until you're happy with the placement.

The "Orient Bone Shape" panel and button will only be visible in pose mode.

Version history:
v0.1 - Initial revision.
"""

import bpy
from mathutils import *

class BONE_OT_orient_custom_shape(bpy.types.Operator):
    '''Matches the bone's selected custom shape to the bone's orientation'''
    bl_idname = "object.orient_custom_shape"
    bl_label = "Orient custom shape"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armatureName = bpy.context.active_object.name
        armature = bpy.data.objects[armatureName]

        activePoseBone = bpy.context.active_pose_bone
        boneName = bpy.context.active_pose_bone.name
        bone = armature.data.bones[boneName]

        objectName = activePoseBone.custom_shape.name
        shapeObject = bpy.data.objects[objectName]

        # Rotate shape object to match bone local rotation in the armature.
        shapeObject.rotation_euler = (0.0, 0.0, 0.0)
        boneChain = bone.parent_recursive
        boneChain.insert(0, bone)

        bone.show_wire = True

        for boneRotation in boneChain:
            rotationMatrix = Matrix((boneRotation.x_axis, boneRotation.y_axis, boneRotation.z_axis)).transposed()
            shapeObject.rotation_euler.rotate(rotationMatrix)

        # Same with translation and scaling.
        shapeObject.location = bone.head_local
        shapeObject.scale = bone.length * Vector((1.0, 1.0, 1.0))

        # Move object to armature coordinates system (except scaling, see below).
        rotationMatrix = armature.rotation_euler
        shapeObject.rotation_euler.rotate(rotationMatrix)
        shapeObject.location.rotate(rotationMatrix)
        shapeObject.location += armature.location

        # Display warning message if the armature has scaling different to one.
        scale = armature.scale

        if(scale.x != 1) or (scale.y != 1) or (scale.z != 1):
            self.report({'Warning'}, "Armature should have a scale factor of 1.0 to match bone shape properly")

        return {'FINISHED'}


class BONE_PT_orient_custom_shape(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    bl_label = "Orient the custom shape to match the bone"

    @classmethod
    def poll(cls, context):
        if context.edit_bone:
            return True

        ob = context.object
        return ob and ob.mode == 'POSE' and context.bone

    def draw(self, context):
        layout = self.layout
        bone = context.bone
        if not bone:
            bone = context.edit_bone

        row = layout.row()
        row.operator("object.orient_custom_shape", text="Orient Custom Shape", icon='BONE_DATA')


def register():
    bpy.utils.register_class(BONE_OT_orient_custom_shape)
    bpy.utils.register_class(BONE_PT_orient_custom_shape)


def unregister():
    bpy.utils.unregister_class(BONE_OT_orient_custom_shape)
    bpy.utils.unregister_class(BONE_PT_orient_custom_shape)


if __name__ == "__main__":
    register()
