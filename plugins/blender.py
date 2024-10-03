import argparse
import os
import time
import subprocess
import sys
from pathlib import Path
import glob
import tarfile
import re 
from datetime import datetime, timedelta


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
    
    command = [sys.executable, plugin_script_path, '-u', url, '-d', assets_dir]
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

def create_timestamp(minutes, seconds, milliseconds):
    # Create a timedelta object
    delta = timedelta(minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    # Create a reference datetime object (e.g., epoch time)
    #reference_time = datetime(1970, 1, 1)

    # Add the timedelta to the reference time
    #timestamp = reference_time + delta

    #return timestamp
    return delta

# analyze blender stdout and generate summary csv file
def analyze_blender_output(stdout_file_name):
    parse_regexp = '^.*\|\sTime:([0-9]+):([0-9]+)\.([0-9]+)\s\|\sMem:([0-9.]+)M,\sPeak:([0-9.]+)M\s\|.*Sample ([0-9]+)\/([0-9]+)$'
   
    results = []
    with open(stdout_file_name, "r") as file:
        for line in file:
            dta = re.findall(parse_regexp, line)
            if not dta:
                continue

            indata = list(dta[0])
            results.append({
                'gpu_m' : indata[0], 
                'gpu_s' : indata[1], 
                'gpu_ms' : indata[2], 
                'gpu_mem_mb' : indata[3], 
                'gpu_peak_mem_mb' : indata[4],
                'sample': int(indata[5]),
                'samples': int(indata[6]),
                'timestamp': create_timestamp(int(indata[0]), int(indata[1]), int(indata[2])),
                'memory' : float(indata[3]),
                'memory_peak' : float(indata[4]),
                })

    if len(results) < 2:
        raise Exception('results are empty')

    # check that first sample are rendered
    if results[0]['sample'] != 0:
        raise Exception('Not rendered first sample')

    # check that all samples are rendered and present in output
    if results[0]['samples'] != results[len(results) - 1]['sample']:
        raise Exception('Not all samples rendered')

    # get overall render time
    render_time = results[len(results) - 1]['timestamp'] - results[0]['timestamp']
    memory = results[len(results) - 1]['memory']

    return render_time, memory

    
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
    parser.add_argument('-g', '--gpu', default=0, type=int, help='gpu to render on')


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


    # script executed inside blender
    blender_main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blender_main.py')

    # this options goes directly to plugins/blender_main.py
    script_options = [
                '-scene', args.asset, 
                '-samples', str(args.samples),
                '-gpu', str(args.gpu),
                '-out', args.outdir]

    # this options goes to blender executable
    command = [args.executable, 
               '--background', 
               '--factory-startup', 
               '-noaudio', 
               '--enable-autoexec', 
               '--python', blender_main_script, 
               '--',' '.join(script_options)]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    stdout_file = os.path.join(args.outdir, 'stdout.log')
    stderr_file = os.path.join(args.outdir, 'stderr.log')

    with open(stdout_file, 'w') as file:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

            file.write(line)
        
    with open(stderr_file, 'w') as file:
        for line in process.stderr:
            sys.stderr.write(line)
            sys.stderr.flush()

            file.write(line)

    timestamp, memory = analyze_blender_output(stdout_file)

    file_name = os.path.join(args.outdir, "time.txt")
    with open(file_name, "w") as file:
        file.write(f"{timestamp}\n")

    file_name = os.path.join(args.outdir, "memory.txt")
    with open(file_name, "w") as file:
        file.write(f"{memory}\n")


if __name__ == "__main__":
    main()
