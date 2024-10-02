import argparse
import os
import time
import subprocess
import sys
from pathlib import Path
import glob
import tarfile


def get_assets_dir(workdir):
    assets_dir = os.path.join(workdir, 'assets')

    return assets_dir

def unpack_assets(workdir):
    directory = get_assets_dir(workdir)

    tar_bz2_files = glob.glob(os.path.join(directory, "*.tar.bz2"))

    for tar_bz2_file in tar_bz2_files:
        timestamp_file = tar_bz2_file + '.unpk'
        if os.path.exists(timestamp_file):
            continue
            
        print(f'unpack {tar_bz2_file}')
        with tarfile.open(tar_bz2_file, "r:bz2") as tar:
            tar.extractall(path=directory)

        with open(timestamp_file, 'w') as file:
            pass


def download_assets(workdir):
    url = 'https://200volts.com/blenderperf/assets'

    assets_dir = get_assets_dir(workdir)

    os.makedirs(assets_dir, exist_ok=True)

    plugin_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'download_assets.py')
    
    command = ["python", plugin_script_path, '-u', url, '-d', assets_dir]
    result = subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr, universal_newlines=True)
    if result.returncode != 0:
        raise Exception(f"can't download {url}")


def prepare_assets(workdir):
    download_assets(workdir)
    unpack_assets(workdir)

def print_assets(workdir):
    directory = get_assets_dir(workdir)

    subdirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    for subdir in subdirs:
        blend_files = glob.glob(os.path.join(directory, subdir, "*.blend"))

        # Print the list of .blend files
        for blend_file in blend_files:
            print(blend_file)


def main():
    parser = argparse.ArgumentParser(
        prog='blender.py',
        description='run performance test for application',
        epilog='for more information: https://github.com/feniksa/blenderperf')

    parser.add_argument('-s', '--samples', default=200, type=int, help='number of samples')
    parser.add_argument('-o', '--outdir', required=True, type=str, help='output directory. Must exist')
    parser.add_argument('-a', '--asset', required=False, type=str, help='asset to render')
    parser.add_argument('-w', '--workdir', required=True, type=str,
                        help='working directory for assets and temporary files')
    parser.add_argument('-p', '--prepare', action='store_true', help='download testing assets and exit')
    parser.add_argument('-i', '--print_assets', action='store_true', help='get list of testing assets')
    parser.add_argument('-e', '--executable', type=str, required=False, help='executable name to run')

    args = parser.parse_args()

    if not os.path.isdir(args.workdir):
        raise Exception('working directory does not exist')

    if not os.path.isdir(args.outdir):
        raise Exception('output directory does not exist')

    if args.prepare:
        prepare_assets(args.workdir)
        exit(0)

    if args.print_assets:
        print_assets(args.workdir) 
        exit(0)


    device_type = 'HIP'
    blender_main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blender_main.py')

    command = [args.executable, '--background', '--factory-startup', '-noaudio', '--enable-autoexec', 
               '--python', blender_main_script, 
               '--', '-scene', args.asset, '-samples', str(args.samples),
               '-device_type', device_type, '-out', args.outdir]


    with open(os.path.join(args.outdir, 'output.log'), 'w') as file:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

            file.write(line)


        #$BLENDER_EXE --background --factory-startup -noaudio --enable-autoexec --python "$SCRIPT_DIR/blender_main.py" \
	#-- "-scene $SCENE_FILE -samples $SAMPLES -device_type "$DEVICE_TYPE" -out $OUTDIR" | \
	#tee "$OUTDIR/log.txt" 


if __name__ == "__main__":
    main()
