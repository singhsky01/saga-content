import sys; sys.path.insert(0, '/home/claude/work')
from lib import *
import random, math
random.seed(5)
END = 50.0
sc = reset(END)
M = {
 'soil': mat('soil', (0.20, 0.10, 0.045), 0.9, 0.35, 18),
 'base': stone('base', (0.14, 0.14, 0.14), (0.42, 0.41, 0.40), 45),
 'bed': mat('bed', (0.45, 0.36, 0.23), 0.95, 0.3, 120),
 'paver': mat('paver', (0.22, 0.20, 0.18), 0.7, 0.2, 14),
 'paver2': mat('paver2', (0.16, 0.145, 0.13), 0.7, 0.2, 14),
 'conc': mat('conc', (0.40, 0.40, 0.38), 0.8, 0.2, 30),
 'siding': mat('siding', (0.62, 0.58, 0.50), 0.7, 0.05, 10),
 'trim': mat('trim', (0.85, 0.85, 0.82), 0.5),
 'spout': mat('spout', (0.80, 0.80, 0.78), 0.4),
 'pipe': mat('pipe', (0.05, 0.05, 0.05), 0.4),
 'wet': mat('wet', (0.05, 0.22, 0.55), 0.2, alpha=0.55),
 'pud': mat('pud', (0.03, 0.07, 0.12), 0.04, alpha=0.8),
 'drop': mat('drop', (0.35, 0.65, 1.0), 0.1, emit=1.5),
 'arrow': mat('arrow', (0.9, 0.12, 0.1), 0.5, emit=1.2),
 'fabric': mat('fabric', (0.55, 0.55, 0.52), 0.9),
 'edge': mat('edge', (0.015, 0.015, 0.015), 0.5),
 'plate': mat('plate', (0.85, 0.55, 0.05), 0.4),
 'grass': mat('grass', (0.025, 0.11, 0.015), 0.85, 0.3, 160),
 'cover': mat('cover', (0.20, 0.10, 0.045), 0.9, 0.35, 18),
 'garrow': mat('garrow', (0.10, 0.75, 0.30), 0.5, emit=1.2),
}
D = 2.4; XE = 2.6
# house
cube('found', -0.35, 0.0, 0, D, -1.0, 0.25, M['conc'])
sid = cube('siding', -0.3, -0.02, 0, D, 0.25, 1.7, M['siding'])
for k in range(14):
    cube(f'lap_{k}', -0.02, 0.0, 0, D, 0.27 + k * 0.1, 0.285 + k * 0.1, M['trim'])
cube('soil', 0, XE, 0, D, -1.0, -0.32, M['soil'])
# downspout on wall face at y 0.35..0.45
SPY0, SPY1 = 0.03, 0.15
cube('spout_v', 0.0, 0.1, SPY0, SPY1, 0.25, 1.7, M['spout'])
spout_out = cube('spout_elbow', 0.0, 0.32, SPY0, SPY1, 0.12, 0.25, M['spout'])

# ---------- failure set ----------
fail = []
def sprof(x): return -0.095 * max(0.0, 1 - x / 1.3)
xs = [i * 0.05 for i in range(int(XE / 0.05) + 1)]
fbase = prism('f_base', [(0, -0.32), (XE, -0.32)] + [(x, -0.08) for x in reversed(xs)], 0, D, M['base']); fail.append(fbase)
fbase.shape_key_add(name='Basis'); kb = fbase.shape_key_add(name='sunk')
for v in kb.data:
    if v.co.z > -0.1: v.co.z += sprof(v.co.x)
fbed = prism('f_bed', [(x, -0.08) for x in xs] + [(x, -0.06) for x in reversed(xs)], 0, D, M['bed']); fail.append(fbed)
fbed.shape_key_add(name='Basis'); kb2 = fbed.shape_key_add(name='sunk')
for v in kb2.data: v.co.z += sprof(v.co.x)
P, J = 0.32, 0.005; NC = 8; NR = 7
fp = []
for i in range(NC):
    col = []
    for j in range(NR):
        x0 = 0.005 + i * (P + J); y0 = 0.005 + j * (P + J)
        p = cube(f'fp_{i}_{j}', x0, x0 + P, y0, y0 + P, -0.06, 0.0, M['paver' if (i + j) % 3 else 'paver2']); bevel(p, 0.006)
        col.append(p); fail.append(p)
    fp.append(col)
wetz = cube('f_wet', 0.0, 1.0, -0.004, D, -0.6, -0.06, M['wet'], origin_bottom=True); fail.append(wetz)
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.55, depth=0.002, location=(0.3, 0.75, -0.056))
pud = bpy.context.active_object; pud.data.materials.append(M['pud']); pud.scale = (1, 1.3, 1); fail.append(pud)
# arrows toward house (red) on patio surface
def arrow(name, m, length=0.45):
    a = empty(name, (0, 0, 0))
    sh = bpy.data.meshes.new('as'); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.04, radius2=0.04, depth=length); bm.to_mesh(sh); bm.free()
    o1 = link(bpy.data.objects.new(name + 's', sh)); o1.data.materials.append(m); o1.rotation_euler = (0, math.radians(90), 0); o1.location = (length / 2, 0, 0); o1.parent = a
    hd = bpy.data.meshes.new('ah'); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.09, radius2=0, depth=0.14); bm.to_mesh(hd); bm.free()
    o2 = link(bpy.data.objects.new(name + 'h', hd)); o2.data.materials.append(m); o2.rotation_euler = (0, math.radians(-90), 0); o2.location = (-0.07, 0, 0); o2.parent = a
    return a, [o1, o2]
red = []
for k, y in enumerate([0.35, 1.0, 1.65]):
    a, parts = arrow(f'ra{k}', M['arrow']); a.location = (0.75, y, 0.12); a.rotation_euler = (0, math.radians(-6), 0); red.append((a, parts))


# ---------- correct set (full layer build) ----------
good = []
SL = 0.05 / XE
def top(x): return -0.08 - SL * x
FAB = -0.315
fab = prism('g_fab', [(0, -0.32), (XE, -0.32), (XE, FAB), (0, FAB)], -0.005, D, M['fabric']); good.append(fab)
lifts = []
for k in range(3):
    lo = lambda x, k=k: FAB + (top(x) - FAB) * k / 3
    hi = lambda x, k=k: FAB + (top(x) - FAB) * (k + 1) / 3
    l = prism(f'g_lift{k}', [(0, lo(0)), (XE, lo(XE)), (XE, hi(XE)), (0, hi(0))], 0, D, M['base']); good.append(l); lifts.append(l)
gbed = prism('g_bed', [(0, -0.08), (XE, top(XE)), (XE, top(XE) + 0.02), (0, -0.06)], 0, D, M['bed']); good.append(gbed)
gp = []
for i in range(NC):
    for j in range(NR):
        x0 = 0.005 + i * (P + J); y0 = 0.005 + j * (P + J)
        p = cube(f'gp_{i}_{j}', x0, x0 + P, y0, y0 + P, -0.06, 0.0, M['paver' if (i + j) % 3 else 'paver2']); bevel(p, 0.006)
        p.rotation_euler[1] = math.atan(SL); p.location.z += -SL * (x0 + P / 2)
        good.append(p); gp.append((p, i))
edge = cube('g_edge', XE, XE + 0.035, 0, D, top(XE) - 0.005, top(XE) + 0.045, M['edge']); good.append(edge)
gpd = cube('g_pipe_down', 0.02, 0.10, -0.05, 0.05, -0.5, 0.12, M['pipe']); good.append(gpd)
gph = cube('g_pipe_h', 0.02, XE + 0.6, -0.05, 0.05, -0.58, -0.5, M['pipe']); good.append(gph)
garrow, gparts = arrow('ga', M['garrow'], 0.55); garrow.rotation_euler = (0, 0, math.pi); garrow.location = (1.3, 0.9, 0.1)
# lawn beyond the patio edge (always there)
cube('lawn_soil', XE + 0.035, XE + 0.6, 0, D, -1.0, -0.1, M['soil'])
cube('lawn_grass', XE + 0.035, XE + 0.6, 0, D, -0.1, -0.065, M['grass'])
cube('pit_soil', XE, XE + 0.035, 0, D, -1.0, top(XE) - 0.005, M['soil'])
# cover hiding the cross-section until the reveal
cover = cube('cover', -0.36, XE + 0.62, -0.075, -0.055, -1.02, 0.02, M['cover'])
set_vis(cover, [(0, False), (4.0, True), (12.6, False)])
kf(cover, 'location', 11.9, (0, 0, 0)); kf(cover, 'location', 12.5, (0, 0, -1.6))

# ---------- timeline ----------
for o in fail: set_vis(o, [(0, True), (4.0, False), (28.7, True), (32.9, False)])
set_vis(spout_out, [(0, True), (4.0, False), (28.7, True), (32.9, False)])
for a, parts in red:
    for o in parts: set_vis(o, [(0, False), (29.0, True), (32.9, False)])
for o in gparts: set_vis(o, [(0, False), (23.7, True), (26.8, False)])
for i, col in enumerate(fp):
    for p in col: kf(p, 'location', 0, (0, 0, sprof(0.005 + i * (P + J) + P / 2)))
for ob in (fbase, fbed):
    kk = ob.data.shape_keys.key_blocks['sunk']; kk.value = 1.0; kk.keyframe_insert('value', frame=0)
kf(wetz, 'scale', 0, 1.0, 2); kf(pud, 'scale', 0, (1, 1.3, 1))
def build(o, tin):
    set_vis(o, [(0, False), (4.0, True), (11.9, False), (tin, True), (28.7, False), (32.9, True)])
    HOLD.append((o, tin))
HOLD = []
build(gpd, 4.0); build(gph, 4.0)
set_vis(gpd, [(0, False), (4.0, True), (28.7, False), (32.9, True)]); set_vis(gph, [(0, False), (4.0, True), (28.7, False), (32.9, True)])
build(fab, 13.9)
kf(fab, 'location', 0, (0, 0, 0)); kf(fab, 'location', 13.9, (0, 0, 0.35)); kf(fab, 'location', 14.25, (0, 0, 0))
for k, l in enumerate(lifts):
    t = 14.4 + k * 0.6
    build(l, t); kf(l, 'location', 0, (0, 0, 0)); kf(l, 'location', t, (0, 0, 0.45)); kf(l, 'location', t + 0.3, (0, 0, 0))
build(gbed, 16.9); kf(gbed, 'location', 0, (0, 0, 0)); kf(gbed, 'location', 16.9, (0, 0, 0.4)); kf(gbed, 'location', 17.2, (0, 0, 0))
for p, i in gp:
    t = 17.3 + i * 0.14; z = p.location.z; x, y = p.location.x, p.location.y
    build(p, t); kf(p, 'location', 0, (x, y, z)); kf(p, 'location', t, (x, y, z + 0.8)); kf(p, 'location', t + 0.35, (x, y, z))
build(edge, 18.6); kf(edge, 'location', 0, (0, 0, 0)); kf(edge, 'location', 18.6, (0, 0, 0.5)); kf(edge, 'location', 18.9, (0, 0, 0))
for o, tin in HOLD:
    if o.animation_data is None: continue
    sc.frame_set(0); loc = tuple(o.location)
    o.location = loc; o.keyframe_insert('location', frame=F(tin) - 1)
plate = cube('plate', 0, 0.55, 0, 0.5, 0, 0.09, M['plate']); bevel(plate, 0.02)
vis = [(0, False)]
for k in range(3):
    t = 14.75 + k * 0.6; zt = FAB + (top(0) - FAB) * (k + 1) / 3
    vis += [(t, True), (t + 0.5, False)]
    kf(plate, 'location', t, (-0.2, 0.45, zt)); kf(plate, 'location', t + 0.48, (XE - 0.3, 0.45, zt - SL * XE))
set_vis(plate, vis)

dropme = bpy.data.meshes.new('drop'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.014); bm.to_mesh(dropme); bm.free()
n = [0]
def mk(t0, t1, path):
    o = link(bpy.data.objects.new(f'd{n[0]}', dropme)); n[0] += 1
    if not o.data.materials: o.data.materials.append(M['drop'])
    o.scale = (1, 1, 2.2); set_vis(o, [(0, False), (t0, True), (t1, False)])
    for tt, p in path: kf(o, 'location', tt, p)
# hook rain + downspout into the dip (0-4)
for i in range(50):
    t = random.uniform(0, 3.4); x = random.uniform(0.1, XE); y = random.uniform(0, D)
    mk(t, t + 0.5, [(t, (x, y, 2.2)), (t + 0.48, (x, y, 0.0))])
for i in range(28):
    t = i * 0.13; y = random.uniform(SPY0 + 0.02, SPY1 - 0.02)
    mk(t, t + 0.5, [(t, (0.31, y, 0.13)), (t + 0.15, (0.36, y, 0.05)), (t + 0.3, (0.38, y, 0.0)), (t + 0.48, (0.45, y + 0.2, -0.05))])
# good: rain runs off the far edge into the lawn (21.3-27.5)
for i in range(90):
    t = random.uniform(21.3, 27.0); x = random.uniform(0.2, XE - 0.2); y = random.uniform(0, D); z = -SL * x
    mk(t, t + 1.5, [(t, (x, y, 2.2)), (t + 0.45, (x, y, z + 0.01)), (t + 1.1, (XE + 0.05, y, -SL * XE)), (t + 1.45, (XE + 0.15, y, -0.07))])
# downspout into pipe and out to daylight (25.7-28.6)
for i in range(22):
    t = 25.7 + i * 0.13
    mk(t, t + 2.0, [(t, (0.06, -0.065, 0.6)), (t + 0.5, (0.06, -0.065, -0.54)), (t + 1.6, (XE + 0.55, -0.065, -0.54)), (t + 1.95, (XE + 0.62, -0.065, -0.9))])
# fail: storm runs toward the house and down the foundation (28.8-32.8)
for i in range(60):
    t = random.uniform(28.8, 31.6); x = random.uniform(0.6, XE); y = random.uniform(0, D)
    mk(t, t + 1.4, [(t, (x, y, 2.2)), (t + 0.45, (x, y, 0.01)), (t + 1.0, (0.03, y, -0.06)), (t + 1.35, (0.03, y, -0.6))])

cams = [
 (0.0, (3.5, -2.6, 2.3), (1.1, 1.1, -0.1)),
 (3.5, (3.3, -2.4, 2.15), (1.1, 1.1, -0.1)),
 (4.2, (1.55, -4.0, 0.35), (1.45, 0.3, -0.33)),
 (19.8, (1.5, -3.7, 0.38), (1.45, 0.3, -0.33)),
 (20.5, (3.4, -2.7, 2.1), (1.1, 0.9, -0.1)),
 (32.4, (3.6, -2.8, 2.2), (1.1, 0.9, -0.1)),
 (33.2, (4.3, -1.9, 1.9), (1.2, 1.2, -0.12)),
 (43.6, (4.5, 2.6, 2.0), (1.2, 1.2, -0.12)),
 (44.4, (3.4, -2.7, 2.2), (1.1, 1.0, -0.1)),
 (50.0, (3.8, -2.3, 2.4), (1.1, 1.0, -0.1)),
]
cam = setup_render(sc, cams)
cam.data.lens = 24

anch = {'dip': (0.2, 0.0, -0.05), 'depth': (0.15, 0.0, -0.2), 'fab': (0.9, 0.0, -0.318), 'base': (1.6, 0.0, -0.2),
        'bed': (1.0, 0.0, -0.075), 'edge': (XE + 0.017, 0.0, -0.1), 'pitch': (1.5, 0.0, -0.03), 'pipe': (1.9, 0.0, -0.54),
        'found': (-0.15, 0.0, -0.4), 'spout': (0.3, SPY0, 0.12), 'patio': (1.3, 1.2, 0.0)}
run(sc, cam, anch, '/home/claude/work/check')
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/check/scene.blend')
