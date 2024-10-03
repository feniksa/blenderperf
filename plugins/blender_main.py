from pathlib import Path
import bpy
import sys
import argparse
import time

def enable_gpu():
    bpy.context.scene.cycles.device = "GPU"

def enable_hip():
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = 'HIP'

def enable_cuda():
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = 'CUDA'

def is_nvidia_gpu(gpu_name):
    if gpu_name.startswith('NVIDIA'):
        return True
    else:
        return False

def is_amd_gpu(gpu_name):
    if gpu_name.startswith('AMD Radeon'):
        return True
    else:
        return False

def process_device(device):
    device["use"] = 0

    if is_nvidia_gpu(device['name']):
        print('Enable GPU {} with CUDA'.format(device['name']))

        device['use'] = True
        enable_cuda()

        return

    if is_amd_gpu(device['name']):
        print('Enable GPU {} with HIP'.format(device['name']))

        device['use'] = True
        enable_hip()
        return


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # get all args after "--"

    parser = argparse.ArgumentParser(prog='blender_main.py', 
            description='Performance tester')

    parser.add_argument('-scene', '-c')
    parser.add_argument('-samples', '-s')
    parser.add_argument('-out', '-o')
    #parser.add_argument('-device_type', '-t')
    parser.add_argument('-gpu', '-g')

    args = parser.parse_args(argv[0].split(' '))
    print(args)

    # open blend file
    bpy.ops.wm.open_mainfile(filepath=args.scene)

    # open scene and set params
    for scene in bpy.data.scenes:
        scene.cycles.samples = int(args.samples)
        scene.render.engine = 'CYCLES'
        scene.cycles.use_denoising = False
        scene.cycles.use_adaptive_sampling = False
        
    enable_gpu()

    # get_devices() to let Blender detects GPU device
    bpy.context.preferences.addons["cycles"].preferences.get_devices()

    # enable GPU device
    for device in bpy.context.preferences.addons["cycles"].preferences.devices:
        process_device(device)
    

    # set render output and format 
    bpy.context.scene.render.filepath = str(Path(args.out).resolve() / 'render.png')
    scene.render.image_settings.file_format = 'PNG'

    # render
    bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    main()

