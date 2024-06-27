from pathlib import Path
import bpy
import sys
import argparse
import time

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

parser = argparse.ArgumentParser(prog='blender_script.py', 
        description='Performance tester')

parser.add_argument('-scene', '-c')
parser.add_argument('-samples', '-s')
parser.add_argument('-out', '-o')
parser.add_argument('-device_type', '-t')

args = parser.parse_args(argv[0].split(' '))
print(args)

# open blend file
bpy.ops.wm.open_mainfile(filepath=args.scene)

# open scene and set params
for scene in bpy.data.scenes:
    scene.cycles.samples = int(args.samples)
    scene.render.engine = 'CYCLES'
    scene.cycles.use_denoising = False

#bpy.context.scene.render.engine = 'CYCLES'

#bpy.context.user_preferences.addons['cycles'].preferences.devices[0].use = True
#bpy.context.user_preferences.addons['cycles'].preferences.compute_device_type = "HIP"


# Set the device_type
bpy.context.preferences.addons[
    "cycles"
].preferences.compute_device_type = args.device_type

# Set the device and feature set
bpy.context.scene.cycles.device = "GPU"

# get_devices() to let Blender detects GPU device
bpy.context.preferences.addons["cycles"].preferences.get_devices()
print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
for d in bpy.context.preferences.addons["cycles"].preferences.devices:
    d["use"] = 0
    if d["name"].startswith('AMD Radeon') or d["name"].startswith('NVIDIA') :
        d["use"] = 1
    print(d["name"], d["use"])


bpy.context.scene.render.filepath = str(Path(args.out).resolve() / 'render.png')

print('----------------  START -----------------')
time_start = time.time()

scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(write_still=True)

#bpy.data.images['Render Result'].save_render(bpy.context.scene.render.filepath)

#exec_time = time.time() - time_start
#with open(Path(args.out).resolve() / 'render_time.txt', "w") as text_file:
#    text_file.write("%s\n" % exec_time)

print('----------------  DONE -----------------')

