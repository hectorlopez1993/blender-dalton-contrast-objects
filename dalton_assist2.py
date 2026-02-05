bl_info = {
    "name": "Dalton-Contrast V10 (Respectful)",
    "author": "Héctor López Martínez",
    "version": (10, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Accesibilidad",
    "description": "Calcula colores de alto contraste por proximidad para artistas daltónicos.",
    "category": "Interface",
}

import bpy
import mathutils
from bpy.app.handlers import persistent
import traceback

# --- DICCIONARIO DE TRADUCCIONES ---
en_translation = {
    ("*", "CÁLCULO AUTOMÁTICO"): "AUTOMATIC CALCULATION",
    ("*", "Mantiene los colores calculados en segundo plano"): "Keeps calculated colors updated in the background",
    ("*", "Tipo"): "Type",
    ("*", "Deuteranopía (Azul/Amarillo)"): "Deuteranopia (Blue/Yellow)",
    ("*", "Protanopía (Azul/Amarillo)"): "Protanopia (Blue/Yellow)",
    ("*", "Tritanopía (Rojo/Turquesa)"): "Tritanopia (Red/Cyan)",
    ("*", "Acromatopsia (Grises)"): "Achromatopsia (Grayscale)",
    ("*", "Alternar Visualización"): "Toggle Visualization",
    ("*", "Vista: Original"): "View: Original",
    ("*", "Vista: Daltonismo"): "View: Colorblind",
    ("*", "Accesibilidad V10 (Control Total)"): "Accessibility V10 (Full Control)",
    ("*", "1. Cálculo de Color:"): "1. Color Calculation:",
    ("*", "Calculando (ON)"): "Calculating (ON)",
    ("*", "Activar Cálculo"): "Enable Calculation",
    ("*", "Alternar Vista (Ojo)"): "Toggle View (Eye)",
    ("*", "Usa 'Alternar Vista' para"): "Use 'Toggle View' to",
    ("*", "ver texturas o atributos."): "see textures or attributes.",
    ("*", "Accesibilidad"): "Accessibility",
}

translations = {
    "en_US": en_translation,
    "en_GB": en_translation,
    "es_ES": {
        ("*", "CÁLCULO AUTOMÁTICO"): "CÁLCULO AUTOMÁTICO",
        ("*", "Mantiene los colores calculados en segundo plano"): "Mantiene los colores calculados en segundo plano",
        ("*", "Tipo"): "Tipo",
        ("*", "Deuteranopía (Azul/Amarillo)"): "Deuteranopía (Azul/Amarillo)",
        ("*", "Protanopía (Azul/Amarillo)"): "Protanopía (Azul/Amarillo)",
        ("*", "Tritanopía (Rojo/Turquesa)"): "Tritanopía (Rojo/Turquesa)",
        ("*", "Acromatopsia (Grises)"): "Acromatopsia (Grises)",
        ("*", "Alternar Visualización"): "Alternar Visualización",
        ("*", "Vista: Original"): "Vista: Original",
        ("*", "Vista: Daltonismo"): "Vista: Daltonismo",
        ("*", "Accesibilidad V10 (Control Total)"): "Accesibilidad V10 (Control Total)",
        ("*", "1. Cálculo de Color:"): "1. Cálculo de Color:",
        ("*", "Calculando (ON)"): "Calculando (ON)",
        ("*", "Activar Cálculo"): "Activar Cálculo",
        ("*", "Alternar Vista (Ojo)"): "Alternar Vista (Ojo)",
        ("*", "Usa 'Alternar Vista' para"): "Usa 'Alternar Vista' para",
        ("*", "ver texturas o atributos."): "ver texturas o atributos.",
        ("*", "Accesibilidad"): "Accesibilidad",
    }
}

# --- LÓGICA DE TRADUCCIÓN AUXILIAR ---
def _(text):
    return bpy.app.translations.pgettext(text, "*")

# --- PALETAS ---
PALETTE_RED_GREEN = [(0.0, 0.1, 0.8, 1.0), (1.0, 0.8, 0.0, 1.0), (0.4, 0.7, 1.0, 1.0), (0.4, 0.2, 0.0, 1.0), (0.0, 0.0, 0.4, 1.0), (1.0, 0.9, 0.6, 1.0), (0.2, 0.5, 0.8, 1.0), (0.8, 0.6, 0.0, 1.0), (0.7, 0.8, 0.9, 1.0), (0.2, 0.15, 0.0, 1.0), (0.5, 0.5, 0.6, 1.0), (0.9, 0.7, 0.2, 1.0)]
PALETTE_BLUE_YELLOW = [(0.0, 0.8, 0.8, 1.0), (0.8, 0.0, 0.0, 1.0), (0.6, 1.0, 1.0, 1.0), (0.4, 0.0, 0.0, 1.0), (0.0, 0.3, 0.3, 1.0), (1.0, 0.6, 0.6, 1.0), (0.8, 0.9, 0.9, 1.0), (0.6, 0.2, 0.2, 1.0), (0.2, 0.6, 0.6, 1.0), (1.0, 0.8, 0.9, 1.0), (0.0, 0.1, 0.1, 1.0), (1.0, 0.2, 0.4, 1.0)]
PALETTE_MONO = [(1.0, 1.0, 1.0, 1.0), (0.0, 0.0, 0.0, 1.0), (0.7, 0.7, 0.7, 1.0), (0.3, 0.3, 0.3, 1.0), (0.9, 0.9, 0.9, 1.0), (0.1, 0.1, 0.1, 1.0), (0.5, 0.5, 0.5, 1.0), (0.8, 0.8, 0.8, 1.0)]

_is_processing = False

class DaltonProperties(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="CÁLCULO AUTOMÁTICO",
        description="Mantiene los colores calculados en segundo plano",
        default=False,
        update=lambda self, context: update_depsgraph(self, context)
    )
    dalton_type: bpy.props.EnumProperty(
        name="Tipo",
        items=[
            ('DEUTAN', "Deuteranopía (Azul/Amarillo)", ""),
            ('PROTAN', "Protanopía (Azul/Amarillo)", ""),
            ('TRITAN', "Tritanopía (Rojo/Turquesa)", ""),
            ('MONO', "Acromatopsia (Grises)", ""),
        ],
        default='DEUTAN',
        update=lambda self, context: force_update(context)
    )

def get_center_x(obj):
    if obj.bound_box:
        return (obj.matrix_world @ mathutils.Vector(obj.bound_box[0])).x
    return obj.location.x

def apply_colors_logic():
    global _is_processing
    if _is_processing: return
    _is_processing = True
    try:
        context = bpy.context
        props = context.scene.dalton_props
        palette = PALETTE_RED_GREEN if props.dalton_type in ['DEUTAN', 'PROTAN'] else PALETTE_BLUE_YELLOW if props.dalton_type == 'TRITAN' else PALETTE_MONO
        objects = sorted([o for o in context.view_layer.objects if o.type == 'MESH' and not o.hide_viewport], key=get_center_x)
        for i, obj in enumerate(objects):
            new_color = palette[i % len(palette)]
            if obj.color != new_color: obj.color = new_color
    except: traceback.print_exc()
    finally: _is_processing = False

@persistent
def depsgraph_handler(scene):
    if bpy.context.scene.dalton_props.active: apply_colors_logic()

def update_depsgraph(self, context):
    if self.active:
        if depsgraph_handler not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)
        apply_colors_logic()
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type, space.shading.color_type = 'SOLID', 'OBJECT'
    else:
        if depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)

def force_update(context):
    apply_colors_logic()
    for window in context.window_manager.windows:
        for area in window.screen.areas: area.tag_redraw()

class VIEW3D_OT_toggle_view_mode(bpy.types.Operator):
    bl_idname = "view3d.toggle_dalton_view_mode"
    bl_label = "Alternar Visualización"
    
    def execute(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if space.shading.type == 'SOLID' and space.shading.color_type == 'OBJECT':
                            space.shading.color_type = 'MATERIAL'
                            self.report({'INFO'}, _("Vista: Original"))
                        else:
                            space.shading.type, space.shading.color_type = 'SOLID', 'OBJECT'
                            self.report({'INFO'}, _("Vista: Daltonismo"))
        return {'FINISHED'}

class VIEW3D_PT_dalton_panel(bpy.types.Panel):
    bl_label = "Accesibilidad V10 (Control Total)"
    bl_idname = "VIEW3D_PT_dalton_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Accesibilidad'

    def draw(self, context):
        layout, props = self.layout, context.scene.dalton_props
        
        box = layout.box()
        box.label(text=_("1. Cálculo de Color:"), icon='PREFERENCES')
        box.prop(props, "dalton_type", text="")
        
        row = box.row()
        label_btn = _("Calculando (ON)") if props.active else _("Activar Cálculo")
        icon_btn = 'PAUSE' if props.active else 'PLAY'
        row.prop(props, "active", text=label_btn, icon=icon_btn, toggle=True)
        
        col = layout.column()
        col.scale_y = 1.6
        # Aquí forzamos la traducción del texto del botón
        col.operator("view3d.toggle_dalton_view_mode", icon='VIS_SEL_11', text=_("Alternar Vista (Ojo)"))
        
        layout.label(text=_("Usa 'Alternar Vista' para"), icon='INFO')
        layout.label(text=_("ver texturas o atributos."), icon='BLANK1')

classes = (DaltonProperties, VIEW3D_PT_dalton_panel, VIEW3D_OT_toggle_view_mode)

def register():
    bpy.app.translations.register(__name__, translations)
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.dalton_props = bpy.props.PointerProperty(type=DaltonProperties)

def unregister():
    bpy.app.translations.unregister(__name__)
    if depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
    del bpy.types.Scene.dalton_props
    for cls in classes: bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()