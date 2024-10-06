import argparse
import os
import subprocess
import sys

import re 
from datetime import timedelta
import platform
import psutil

from blender_assets import prepare_assets, print_assets


def dump_environment(blender_exe, workdir, outdir):
    envdir = os.path.join(outdir, 'environment')
    os.makedirs(envdir, exist_ok=True)

    # Gather system information
    cpu_info = platform.processor()
    ram_info = str(round(psutil.virtual_memory().total / (1024 ** 3))) + " GB"
    os_info = platform.system() + " " + platform.release()

    filename = os.path.join(envdir, "cpu.txt")
    with open(filename, "w") as file:
        file.write(f"{cpu_info}\n")

    filename = os.path.join(envdir, "ram.txt")
    with open(filename, "w") as file:
        file.write(f"{ram_info}\n")

    filename = os.path.join(envdir, "os.txt")
    with open(filename, "w") as file:
        file.write(f"{os_info}\n")

    script_args = [
       '-gpu', str(0),
       '-out', envdir
    ]

    blender_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blender_env.py')
    command = [blender_exe,
               '--background',
               '--factory-startup',
               '-noaudio',
               '--python', blender_script,
               '--', ' '.join(script_args)]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
        return_code = process.returncode
        if return_code != 0:
            raise Exception(stderr)

    except subprocess.CalledProcessError as e:
        print("can't get blender info")
        raise


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
    parser.add_argument('-d', '--dump_environment', required=False, action='store_true', help='dump os system vers, cpu, etc')

    args = parser.parse_args()

    if not os.path.isdir(args.workdir):
        raise Exception('working directory does not exist')

    if not os.path.isdir(args.outdir):
        raise Exception('output directory does not exist')

    if args.prepare:
        prepare_assets(args.workdir)
        exit(0)

    if args.dump_environment:
        dump_environment(args.executable, args.workdir, args.outdir)
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
