cd /home/claude/work/check
for i in 1 2 3 4 5 6; do
  /opt/blender/blender -b scene.blend --python-expr "import bpy;s=bpy.context.scene;s.render.use_overwrite=False;s.render.use_placeholder=True;s.cycles.samples=5;s.render.resolution_x=720;s.render.resolution_y=1280;s.render.resolution_percentage=100;s.render.engine='CYCLES';s.frame_start=0;s.frame_end=1200;s.frame_step=2;s.render.filepath='/home/claude/work/check/frames/f_';bpy.ops.render.render(animation=True)" > render.log 2>&1
  n=$(ls frames | wc -l); [ "$n" -ge 601 ] && break
done
