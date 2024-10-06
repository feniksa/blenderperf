import os
from pathlib import Path
import bpy
import sys
import argparse

def enable_gpu():
    bpy.context.scene.cycles.device = "GPU"

def dump_device(device, outdir):
    device_name = device['name']

    file_name = os.path.join(outdir, "gpu.txt")
    with open(file_name, "w") as file:
        file.write(f"{device_name}\n")

def dump_blender_version(outdir):
    
    blender_version = bpy.app.version_string
    blender_hash = bpy.app.build_hash
    blender_build_date = bpy.app.build_date

    file_name = os.path.join(outdir, "version.txt")
    with open(file_name, "w") as file:
        file.write(f"{blender_version}\n")
        file.write(f"{blender_hash}\n")
        file.write(f"{blender_build_date}\n")


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # get all args after "--"

    parser = argparse.ArgumentParser(prog='blender_main.py', 
            description='Performance tester')

    parser.add_argument('-out', '-o')
    parser.add_argument('-gpu', '-g', type=int)

    args = parser.parse_args(argv[0].split(' '))

    # open scene and set params
    for scene in bpy.data.scenes:
        scene.render.engine = 'CYCLES'

    # enable gpu acceleration
    enable_gpu()

    # get_devices() to let Blender detects GPU device
    bpy.context.preferences.addons["cycles"].preferences.get_devices()

    devices = bpy.context.preferences.addons["cycles"].preferences.devices
    if args.gpu > len(devices):
        raise Exception("No GPU devices found")

    dump_device(devices[args.gpu], args.out)
    dump_blender_version(args.out)
    

if __name__ == "__main__":
    main()

