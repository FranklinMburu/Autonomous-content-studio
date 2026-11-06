"""Earth film: a photoreal sunrise over the Earth's limb for the Candela hero (replaces the dotted globe's look).

Rendered with Blender (free, GPL; the rendered pictures are ours) on Kaggle's free T4, from NASA public-domain maps
(Blue Marble day, Black Marble night lights, clouds; a CC BY 4.0 fallback is credited if NASA's links fail).
The camera is ORTHOGRAPHIC and placed with the exact same maths as web/src/lib/earth.js (radius 860 px, centre
(720, 1370) in a 1440x900 frame, the same turn and tilt, the same sun path), so the website can put its live story
lights and cards on top of the film in exactly the right places.
One clip, frame i = scroll progress t = i/(N-1): the sun rises along the limb and the globe turns 4 degrees.
Outputs: earth.mp4 (H.264, a keyframe every 4 frames so scrolling can scrub it), earth.webm (VP9), poster.jpg,
end.jpg, credits.txt, log.txt.
"""
import json, math, os, shutil, subprocess, sys, time, traceback, urllib.request

OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
W, H, N = int(os.environ.get("EF_W", 1920)), int(os.environ.get("EF_H", 1200)), int(os.environ.get("EF_N", 72))
SAMPLES = int(os.environ.get("EF_SAMPLES", 96))
WORK = "/kaggle/working/ef"; os.makedirs(f"{WORK}/frames", exist_ok=True); os.makedirs(f"{WORK}/tex", exist_ok=True)

# ---------- textures (NASA first; a CC BY 4.0 fallback that is credited) ----------
SOURCES = {
    "day": [("https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73751/world.topo.bathy.200407.3x5400x2700.jpg", "NASA Blue Marble Next Generation (public domain)"),
            ("https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74092/world.200407.3x5400x2700.jpg", "NASA Blue Marble Next Generation (public domain)"),
            ("https://www.solarsystemscope.com/textures/download/8k_earth_daymap.jpg", "Solar System Scope, CC BY 4.0")],
    "night": [("https://eoimages.gsfc.nasa.gov/images/imagerecords/144000/144898/BlackMarble_2016_3km.jpg", "NASA Black Marble 2016 (public domain)"),
              ("https://eoimages.gsfc.nasa.gov/images/imagerecords/144000/144898/BlackMarble_2016_01deg.jpg", "NASA Black Marble 2016 (public domain)"),
              ("https://www.solarsystemscope.com/textures/download/8k_earth_nightmap.jpg", "Solar System Scope, CC BY 4.0")],
    "clouds": [("https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57747/cloud_combined_8192.jpg", "NASA Blue Marble clouds (public domain)"),
               ("https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57747/cloud_combined_2048.jpg", "NASA Blue Marble clouds (public domain)"),
               ("https://www.solarsystemscope.com/textures/download/8k_earth_clouds.jpg", "Solar System Scope, CC BY 4.0")],
}
credits = []
for kind, cands in SOURCES.items():
    for url, who in cands:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "candela-studio-lab"})
            data = urllib.request.urlopen(req, timeout=120).read()
            if len(data) < 100_000:
                raise RuntimeError(f"too small ({len(data)} bytes)")
            open(f"{WORK}/tex/{kind}.jpg", "wb").write(data)
            credits.append(f"{kind}: {who}: {url}"); log(f"texture {kind}: {len(data) // 1024} KB from {url}")
            break
        except Exception as e:
            log(f"texture {kind}: {url} failed: {str(e)[:120]}")
    else:
        log(f"NO {kind} TEXTURE"); credits.append(f"{kind}: none")
open(f"{OUT}/credits.txt", "w").write("\n".join(credits) + "\nRendered with Blender (blender.org).\n")
log(f"textures {time.time() - t0:.0f}s")

# ---------- Blender ----------
BL = "https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz"
subprocess.run("apt-get install -y -qq libxi6 libxrender1 libxkbcommon0 libsm6 libgl1 libxxf86vm1 libxfixes3 > /dev/null 2>&1",
               shell=True)
if not os.path.exists("/kaggle/working/blender/blender"):
    subprocess.run(f"wget -q -O /kaggle/working/bl.tar.xz {BL} && mkdir -p /kaggle/working/blender && "
                   "tar -xf /kaggle/working/bl.tar.xz -C /kaggle/working/blender --strip-components=1", shell=True, check=True)
log(f"blender ready {time.time() - t0:.0f}s")

SCENE = r'''
import bpy, math, json, os, sys
from mathutils import Matrix, Vector
P = json.loads(os.environ["EF_PARAMS"])
W, H, N, SAMPLES, WORK = P["W"], P["H"], P["N"], P["SAMPLES"], P["WORK"]
# --- the same constants as web/src/lib/earth.js ---
SUN_FROM, SUN_TO, RISE_FROM, RISE_TO, LON_FROM, LON_TO, LAT0 = -0.55, 0.12, 0.8, 1.0, -10, -6, -6
R_PX, CY_PX, REF_W = 860.0, 1370.0, 1440.0
lerp = lambda a, b, t: a + (b - a) * t

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
for dev in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = dev; prefs.get_devices()
        if any(d.type == dev for d in prefs.devices):
            for d in prefs.devices: d.use = d.type == dev
            print("GPU:", dev, [d.name for d in prefs.devices if d.use]); break
    except Exception as e:
        print("no", dev, e)
sc.cycles.device = "GPU"
sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.image_settings.file_format = "PNG"; sc.render.film_transparent = False
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Punchy"
except Exception as e: print("look:", e)
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0, 0, 0)

def img(name):
    p = f"{WORK}/tex/{name}.jpg"
    return bpy.data.images.load(p) if os.path.exists(p) else None

def latlon_uv(nt):
    """object position -> equirectangular UV (lon 0 at +X, north +Z), exactly like the JS globe's lat/lon"""
    tc = nt.nodes.new("ShaderNodeTexCoord"); nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Object"], nrm.inputs[0])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nrm.outputs[0], sep.inputs[0])
    at = nt.nodes.new("ShaderNodeMath"); at.operation = "ARCTAN2"; nt.links.new(sep.outputs["Y"], at.inputs[0]); nt.links.new(sep.outputs["X"], at.inputs[1])
    u = nt.nodes.new("ShaderNodeMath"); u.operation = "MULTIPLY_ADD"; u.inputs[1].default_value = 1 / (2 * math.pi); u.inputs[2].default_value = 0.5
    nt.links.new(at.outputs[0], u.inputs[0])
    asn = nt.nodes.new("ShaderNodeMath"); asn.operation = "ARCSINE"; nt.links.new(sep.outputs["Z"], asn.inputs[0])
    v = nt.nodes.new("ShaderNodeMath"); v.operation = "MULTIPLY_ADD"; v.inputs[1].default_value = 1 / math.pi; v.inputs[2].default_value = 0.5
    nt.links.new(asn.outputs[0], v.inputs[0])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u.outputs[0], cmb.inputs[0]); nt.links.new(v.outputs[0], cmb.inputs[1])
    return cmb.outputs[0]

def sun_factor(nt, lo, hi, invert=False):
    """smooth 0..1 of how much the sun lights this point (dot of the surface normal with the sun direction);
    invert=True gives 1 in the dark instead"""
    geo = nt.nodes.new("ShaderNodeNewGeometry"); d = nt.nodes.new("ShaderNodeVectorMath"); d.operation = "DOT_PRODUCT"
    nt.links.new(geo.outputs["Normal"], d.inputs[0]); d.name = "sundot"
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = lo, hi
    if invert:
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0
    nt.links.new(d.outputs["Value"], mr.inputs["Value"])
    return d, mr.outputs["Result"]

SUNDOTS = []
def sphere(name, r, seg=256):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r)
    o = bpy.context.object; o.name = name; bpy.ops.object.shade_smooth(); return o

# Earth: day map lit by the sun + city lights on the night side
earth = sphere("earth", 1.0); m = bpy.data.materials.new("earth"); m.use_nodes = True; nt = m.node_tree
bsdf = nt.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.55
uv = latlon_uv(nt)
if img("day"):
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img("day"); t.interpolation = "Cubic"; nt.links.new(uv, t.inputs[0])
    nt.links.new(t.outputs[0], bsdf.inputs["Base Color"])
if img("night"):
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img("night"); tn.interpolation = "Cubic"; nt.links.new(uv, tn.inputs[0])
    d, night = sun_factor(nt, -0.25, 0.08, invert=True); SUNDOTS.append(d)   # 1 on the night side, 0 in daylight
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 1.6
    nt.links.new(night, mul.inputs[0])
    nt.links.new(tn.outputs[0], bsdf.inputs["Emission Color"]); nt.links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
earth.data.materials.append(m)

# Clouds: white, lit by the sun, transparent elsewhere
if img("clouds"):
    cl = sphere("clouds", 1.006); m = bpy.data.materials.new("clouds"); m.use_nodes = True; nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]; bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1); bsdf.inputs["Roughness"].default_value = 0.9
    tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = img("clouds"); tc.image.colorspace_settings.name = "Non-Color"
    nt.links.new(latlon_uv(nt), tc.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mix = nt.nodes.new("ShaderNodeMixShader")
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "MULTIPLY"; pw.inputs[1].default_value = 0.9
    nt.links.new(tc.outputs[0], pw.inputs[0]); nt.links.new(pw.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(bsdf.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    cl.data.materials.append(m)

# Atmosphere: a thin glowing shell, brightest at the limb (fresnel) and on the sunlit side: blue, warm near the sun
at = sphere("air", 1.012); m = bpy.data.materials.new("air"); m.use_nodes = True; nt = m.node_tree
for n in list(nt.nodes):
    if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 3.0; nt.links.new(lw.outputs["Facing"], pw.inputs[0])
d, lit = sun_factor(nt, -0.25, 0.3); SUNDOTS.append(d)
ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
cr.elements[0].position, cr.elements[0].color = 0.0, (0.03, 0.08, 0.25, 1)    # far from the sun: faint deep blue
cr.elements[1].position, cr.elements[1].color = 1.0, (1.0, 0.97, 0.9, 1)      # at the sun: white
e = cr.elements.new(0.55); e.color = (0.25, 0.5, 1.0, 1)                       # sky blue
e = cr.elements.new(0.85); e.color = (1.0, 0.6, 0.3, 1)                        # warm where sunlight grazes the air
nt.links.new(lit, ramp.inputs[0])
k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; nt.links.new(pw.outputs[0], k.inputs[0])
k2 = nt.nodes.new("ShaderNodeMath"); k2.operation = "MULTIPLY_ADD"; k2.inputs[1].default_value = 6.0; k2.inputs[2].default_value = 0.06
nt.links.new(lit, k2.inputs[0]); nt.links.new(k2.outputs[0], k.inputs[1])
em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(ramp.outputs[0], em.inputs["Color"]); nt.links.new(k.outputs[0], em.inputs["Strength"])
tr = nt.nodes.new("ShaderNodeBsdfTransparent"); add = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(em.outputs[0], add.inputs[0]); nt.links.new(tr.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
at.data.materials.append(m)

# Stars: a plane far behind the Earth (an orthographic camera can't see the world background as a sky)
bpy.ops.mesh.primitive_plane_add(size=12); stars = bpy.context.object; stars.name = "stars"
m = bpy.data.materials.new("stars"); m.use_nodes = True; nt = m.node_tree
for n in list(nt.nodes):
    if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
tc = nt.nodes.new("ShaderNodeTexCoord"); vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 260
nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.0, 0.035
mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0
nt.links.new(vo.outputs["Distance"], mr.inputs["Value"])
nz = nt.nodes.new("ShaderNodeTexWhiteNoise"); nt.links.new(vo.outputs["Position"], nz.inputs["Vector"])
pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 6; nt.links.new(nz.outputs["Value"], pw.inputs[0])
mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; nt.links.new(mr.outputs["Result"], mu.inputs[0]); nt.links.new(pw.outputs[0], mu.inputs[1])
mu2 = nt.nodes.new("ShaderNodeMath"); mu2.operation = "MULTIPLY"; mu2.inputs[1].default_value = 1.6; nt.links.new(mu.outputs[0], mu2.inputs[0])
em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mu2.outputs[0], em.inputs["Strength"])
nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"]); stars.data.materials.append(m)

# The sun: a lamp for the lighting + a small, very bright disc on the limb for the camera (it makes the glare)
lamp = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(lamp)
lamp.data.energy = 6.0; lamp.data.angle = math.radians(0.6)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.011); disc = bpy.context.object; disc.name = "disc"
m = bpy.data.materials.new("disc"); m.use_nodes = True; nt = m.node_tree
for n in list(nt.nodes):
    if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.93, 0.82, 1); em.inputs["Strength"].default_value = 400
nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"]); disc.data.materials.append(m)
for o in (disc,):
    o.visible_shadow = False

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.sensor_fit = "HORIZONTAL"; cam.data.ortho_scale = REF_W / R_PX
cam.data.clip_start, cam.data.clip_end = 0.01, 100

# compositor: the glow and the rays a real camera makes when it looks at the sun
sc.use_nodes = True; ct = sc.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers"); comp = ct.nodes.new("CompositorNodeComposite")
g1 = ct.nodes.new("CompositorNodeGlare"); g1.glare_type = "FOG_GLOW"; g1.quality = "HIGH"; g1.threshold = 1.0; g1.size = 9; g1.mix = -0.25
g2 = ct.nodes.new("CompositorNodeGlare"); g2.glare_type = "STREAKS"; g2.quality = "HIGH"; g2.threshold = 3.0; g2.streaks = 8
g2.angle_offset = math.radians(12); g2.fade = 0.93; g2.mix = -0.55
ct.links.new(rl.outputs["Image"], g1.inputs["Image"]); ct.links.new(g1.outputs["Image"], g2.inputs["Image"])
ct.links.new(g2.outputs["Image"], comp.inputs["Image"])

def js_to_bl(v):   # earth.js world (x east-ish, y north, z towards lon 0) -> Blender (X towards lon 0, Y east, Z north)
    return Vector((v[2], v[0], v[1]))

for i in range(N):
    t = i / (N - 1) if N > 1 else 0.0
    lo, la = math.radians(-lerp(LON_FROM, LON_TO, t)), math.radians(LAT0)
    cl, sl, ca, sa_ = math.cos(lo), math.sin(lo), math.cos(la), math.sin(la)
    # earth.js rotation(): view = M * world, with M = tilt(LAT0) * turn(-lon)
    turn = Matrix(((cl, 0, sl), (0, 1, 0), (-sl, 0, cl)))
    tilt = Matrix(((1, 0, 0), (0, ca, -sa_), (0, sa_, ca)))
    M = tilt @ turn; Mt = M.transposed()   # view -> world (JS axes)
    right, up, back = (js_to_bl(Mt @ Vector(a)) for a in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    shift = (CY_PX - 450.0) / R_PX          # the Earth's centre is 920 px below the middle of the 1440x900 frame
    cam.matrix_world = Matrix((
        (right.x, up.x, back.x, 0), (right.y, up.y, back.y, 0), (right.z, up.z, back.z, 0), (0, 0, 0, 1)))
    cam.location = up * shift + back * 20
    sa = lerp(SUN_FROM, SUN_TO, t); rise = lerp(RISE_FROM, RISE_TO, t)
    # light comes from BEHIND the planet (like the TradingView shot): the face we see is night (city lights),
    # only a thin crescent along the limb near the sun is in daylight
    sv = Vector((0.32 * math.sin(sa), 0.32 * math.cos(sa), -1.0)).normalized()
    sun_w = js_to_bl(Mt @ sv)
    lamp.rotation_euler = (-sun_w).to_track_quat("-Z", "Y").to_euler(); lamp.data.energy = 6.0 * rise
    sd = 1.0 + lerp(-6, 9, t) / R_PX
    disc.location = js_to_bl(Mt @ Vector((sd * math.sin(sa), sd * math.cos(sa), -0.02)))
    disc.active_material.node_tree.nodes["Emission"].inputs["Strength"].default_value = 400 * rise
    stars.matrix_world = cam.matrix_world.copy(); stars.location = up * shift - back * 30
    for dn in SUNDOTS:
        dn.inputs[1].default_value = sun_w
    for o in ("clouds",):
        if o in bpy.data.objects:
            bpy.data.objects[o].rotation_euler[2] = math.radians(0.6 * t)   # clouds drift a little
    sc.render.filepath = f"{WORK}/frames/f{i:04d}.png"
    bpy.ops.render.render(write_still=True)
    print(f"frame {i + 1}/{N}", flush=True)
print("render done")
'''
open(f"{WORK}/scene.py", "w").write(SCENE)
params = json.dumps({"W": W, "H": H, "N": N, "SAMPLES": SAMPLES, "WORK": WORK})
t1 = time.time()
p = subprocess.run(["/kaggle/working/blender/blender", "-b", "--factory-startup", "-P", f"{WORK}/scene.py"],
                   env={**os.environ, "EF_PARAMS": params}, capture_output=True, text=True)
tail = "\n".join(l for l in (p.stdout + p.stderr).splitlines() if not l.startswith("Fra:"))[-4000:]
log(tail)
frames = sorted(f for f in os.listdir(f"{WORK}/frames") if f.endswith(".png"))
log(f"rendered {len(frames)}/{N} frames in {time.time() - t1:.0f}s ({(time.time() - t1) / max(1, len(frames)):.1f}s each)")
if frames:
    shutil.copy(f"{WORK}/frames/{frames[0]}", f"{OUT}/first.png"); shutil.copy(f"{WORK}/frames/{frames[-1]}", f"{OUT}/last.png")
    ff = shutil.which("ffmpeg") or "ffmpeg"
    def enc(*a):
        r = subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-framerate", "24", "-i", f"{WORK}/frames/f%04d.png", *a],
                           capture_output=True, text=True)
        if r.returncode: log("ffmpeg:", r.stderr[-500:])
    enc("-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "slow", "-g", "4", "-movflags", "+faststart", f"{OUT}/earth.mp4")
    enc("-c:v", "libvpx-vp9", "-pix_fmt", "yuv420p", "-crf", "34", "-b:v", "0", "-g", "4", "-row-mt", "1", f"{OUT}/earth.webm")
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", f"{WORK}/frames/{frames[0]}", "-q:v", "3", f"{OUT}/poster.jpg"])
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", f"{WORK}/frames/{frames[-1]}", "-q:v", "3", f"{OUT}/end.jpg"])
    for f in ("earth.mp4", "earth.webm", "poster.jpg"):
        if os.path.exists(f"{OUT}/{f}"): log(f"{f}: {os.path.getsize(f'{OUT}/{f}') // 1024} KB")
log(f"total {time.time() - t0:.0f}s")
