
bl_info = {
    "name" : "Object Adder",
    "author" : "s1d_fx",
    "version" : (1, 0),
    "blender" : (5, 2, 0),    
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Add Mesh",
    
}








import bpy

class TestPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "TestPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Add Objects'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text= "Click to add objects", icon = 'FILE_3D')
        row = layout.row()
        row.operator("mesh.primitive_plane_add")
        row = layout.row()
        row.operator("mesh.primitive_cube_add")
        row = layout.row()
        row.operator("mesh.primitive_uv_sphere_add")
        row = layout.row()
        row.operator("mesh.primitive_cylinder_add")
        row = layout.row()
        row.operator("mesh.primitive_torus_add")
        row = layout.row()
        row.operator("mesh.primitive_monkey_add")

def register():
    bpy.utils.register_class(TestPanel)

def unregister():
    bpy.utils.unregister_class(TestPanel)

if __name__ == "__main__":
    register()

