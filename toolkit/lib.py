import bpy, bmesh, math, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

FPS = 24
def F(t): return int(round(t * FPS))

def reset(end_t):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS; sc.frame_start = 0; sc.frame_end = F(end_t)
    return sc

def mat(name, col, rough=0.8, noise=0.0, scale=40, alpha=1.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = m.node_tree.nodes; l = m.node_tree.links; b = n['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough
    if noise > 0:
        tex = n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = scale / 3; tex.inputs['Detail'].default_value = 2
        tco = n.new('ShaderNodeTexCoord'); l.new(tco.outputs['Object'], tex.inputs['Vector'])
        r = n.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].color = (*[c * (1 - noise) for c in col], 1)
        r.color_ramp.elements[1].color = (*[min(1, c * (1 + noise)) for c in col], 1)
        l.new(tex.outputs['Fac'], r.inputs['Fac']); l.new(r.outputs['Color'], b.inputs['Base Color'])
    if emit > 0:
        b.inputs['Emission Color'].default_value = (*col, 1); b.inputs['Emission Strength'].default_value = emit
    if alpha < 1: b.inputs['Alpha'].default_value = alpha
    return m

def stone(name, lo, hi, scale):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = m.node_tree.nodes; l = m.node_tree.links; b = n['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.9
    v = n.new('ShaderNodeTexVoronoi'); v.inputs['Scale'].default_value = scale
    tc = n.new('ShaderNodeTexCoord'); l.new(tc.outputs['Object'], v.inputs['Vector'])
    r = n.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (*lo, 1); r.color_ramp.elements[1].color = (*hi, 1)
    sep = n.new('ShaderNodeSeparateColor'); l.new(v.outputs['Color'], sep.inputs['Color']); l.new(sep.outputs[0], r.inputs['Fac'])
    l.new(r.outputs['Color'], b.inputs['Base Color'])
    mr = n.new('ShaderNodeMath'); mr.operation = 'POWER'; mr.inputs[1].default_value = 0.5
    l.new(v.outputs['Distance'], mr.inputs[0])
    bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.9; bp.inputs['Distance'].default_value = 0.02
    l.new(mr.outputs[0], bp.inputs['Height']); l.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def link(ob): bpy.context.scene.collection.objects.link(ob); return ob

def prism(name, poly, y0, y1, m):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    front = [bm.verts.new((x, y0, z)) for x, z in poly]
    back = [bm.verts.new((x, y1, z)) for x, z in poly]
    n = len(poly); bm.faces.new(front[::-1]); bm.faces.new(back)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((front[i], front[j], back[j], back[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(m); return ob

def cube(name, x0, x1, y0, y1, z0, z1, m, origin_bottom=False):
    ob = prism(name, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1, m)
    if origin_bottom:
        for v in ob.data.vertices: v.co.z -= z0
        ob.location.z = z0
    return ob

def bevel(ob, w=0.01, seg=2):
    md = ob.modifiers.new('bv', 'BEVEL'); md.width = w; md.segments = seg

def _const(ob):
    ad = ob.animation_data
    if ad and ad.action:
        fcs = getattr(ad.action, 'fcurves', None)
        if fcs is None:
            try:
                fcs = [fc for layer in ad.action.layers for strip in layer.strips for cb in strip.channelbags for fc in cb.fcurves]
            except Exception: fcs = []
        for fc in fcs:
            if fc.data_path.startswith('hide'):
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

def set_vis(ob, keys):
    for t, v in keys:
        ob.hide_render = not v; ob.keyframe_insert('hide_render', frame=F(t))
        ob.hide_viewport = not v; ob.keyframe_insert('hide_viewport', frame=F(t))
    _const(ob)

def kf(ob, path, t, val, idx=None):
    if idx is None: setattr(ob, path, val); ob.keyframe_insert(path, frame=F(t))
    else: getattr(ob, path)[idx] = val; ob.keyframe_insert(path, index=idx, frame=F(t))

def empty(name, loc):
    e = bpy.data.objects.new(name, None); e.location = loc; return link(e)

def setup_render(sc, cams):
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.022, 0.028, 1)
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.2; sun.angle = math.radians(8)
    so = link(bpy.data.objects.new('sun', sun)); so.rotation_euler = (math.radians(50), math.radians(-25), math.radians(-35))
    fill = bpy.data.lights.new('fill', 'AREA'); fill.energy = 450; fill.size = 5
    fo = link(bpy.data.objects.new('fill', fill)); fo.location = (-1.5, -4.5, 3.0); fo.rotation_euler = (math.radians(60), 0, math.radians(-20))
    cd = bpy.data.cameras.new('cam'); cd.lens = 30
    cam = link(bpy.data.objects.new('cam', cd)); sc.camera = cam
    tgt = empty('tgt', (0, 0, 0))
    tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    for t, cl, tl in cams:
        cam.location = cl; cam.keyframe_insert('location', frame=F(t))
        tgt.location = tl; tgt.keyframe_insert('location', frame=F(t))
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 5
    sc.render.use_persistent_data = True
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
    sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'; sc.cycles.max_bounces = 3
    sc.render.resolution_x = 720; sc.render.resolution_y = 1280
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    return cam

def run(sc, cam, anchors, outdir):
    import sys
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['test', '1']
    mode = args[0]
    if mode == 'anchors':
        out = {}
        for f in range(sc.frame_start, sc.frame_end + 1):
            sc.frame_set(f)
            out[f] = {k: list(world_to_camera_view(sc, cam, Vector(p))[:2]) for k, p in anchors.items()}
        json.dump(out, open(outdir + '/anchors.json', 'w'))
    elif mode == 'test':
        for t in [float(x) for x in args[1].split(',')]:
            sc.frame_set(F(t)); sc.render.resolution_percentage = int(args[2]) if len(args) > 2 else 50
            sc.render.filepath = f'{outdir}/test_{t:05.1f}.png'; bpy.ops.render.render(write_still=True)
    elif mode == 'render':
        sc.frame_start = int(args[1]); sc.frame_end = int(args[2]); sc.frame_step = 2
        sc.render.filepath = outdir + '/frames/f_'; bpy.ops.render.render(animation=True)
