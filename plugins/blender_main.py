from pathlib import Path
import bpy
import sys
import argparse
import time

def enable_gpu():
    bpy.context.scene.cycles.device = "GPU"

def enable_cpu():
    bpy.context.scene.cycles.device = "CPU"

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

def enable_device(device):
    device["use"] = False

    if is_nvidia_gpu(device['name']):
        print('Enable GPU {} with CUDA'.format(device['name']))

        device['use'] = True
        enable_gpu()
        enable_cuda()

        return

    if is_amd_gpu(device['name']):
        print('Enable GPU {} with HIP'.format(device['name']))

        device['use'] = True
        enable_gpu()
        enable_hip()
        return

    # fallback to CPU
    enable_cpu()
    device['use'] = True


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # get all args after "--"

    parser = argparse.ArgumentParser(prog='blender_main.py', 
            description='Performance tester')

    parser.add_argument('-scene', '-c')
    parser.add_argument('-samples', '-s')
    parser.add_argument('-out', '-o')
    parser.add_argument('-gpu', '-g', type=int)
    parser.add_argument('-resolution_x', '-x', type=int, default=1024)
    parser.add_argument('-resolution_y', '-y', type=int, default=768)

    args = parser.parse_args(argv[0].split(' '))

    # open blend file
    bpy.ops.wm.open_mainfile(filepath=args.scene)

    # open scene and set params
    for scene in bpy.data.scenes:
        scene.cycles.samples = int(args.samples)
        scene.render.engine = 'CYCLES'
        scene.render.resolution_x = args.resolution_x
        scene.render.resolution_y = args.resolution_y
        scene.cycles.use_denoising = False
        scene.cycles.use_adaptive_sampling = False
        scene.render.image_settings.file_format = 'PNG'

    # enable gpu acceleration
    enable_gpu()

    # get_devices() to let Blender detects GPU device
    bpy.context.preferences.addons["cycles"].preferences.get_devices()

    devices = bpy.context.preferences.addons["cycles"].preferences.devices
    if args.gpu > len(devices):
        raise Exception(f'bad device index {args.gpu}')

    # disable all devices first (rewrite scene preferences
    for device in bpy.context.preferences.addons["cycles"].preferences.devices:
        device['use'] = False

    enable_device(devices[args.gpu])

    # set render output and format 
    bpy.context.scene.render.filepath = str(Path(args.out).resolve() / 'render.png')

    # render
    bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    main()

