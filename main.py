import argparse
import os
import time
import subprocess
import sys

def check_executable(path: str):
    return os.path.isfile(path) and os.access(path, os.X_OK)

def main():
    default_outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outdir')
    default_workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workdir')

    parser = argparse.ArgumentParser(
        prog='main.py',
        description='run performance test for application',
        epilog='for more information: https://github.com/feniksa/blenderperf')

    parser.add_argument('-s', '--samples', default=200, type=int, help='number of samples')
    parser.add_argument('-r', '--repeats', default=100, type=int, help='number of repeats')
    parser.add_argument('-e', '--executable', type=str, required=True, help='executable name to run')
    parser.add_argument('-o', '--outdir', default = default_outdir, type=str, help='output directory. Must exist')
    parser.add_argument('-w', '--workdir', default = default_workdir, type=str, help='working directory for assets and temporary files')
    parser.add_argument('-p', '--plugin', default='blender', type=str, help='plugin to load')
    parser.add_argument('-g', '--gpu', default=0, type=int, help='gpu to render on')


    args = parser.parse_args()

    if not os.path.isdir(args.workdir):
        raise Exception('working directory does not exist')

    if not os.path.isdir(args.outdir):
        raise Exception('output directory does not exist')

    if not check_executable(args.executable):
        raise Exception('executable not found')

    plugin_script_path = os.path.dirname(os.path.abspath(__file__)) + '/plugins/' + args.plugin + '.py'
    if not os.path.exists(plugin_script_path):
        raise Exception('plugin not found: ' + plugin_script_path)

    command = ["python", plugin_script_path, '--workdir', args.workdir, '--outdir', args.outdir, '--prepare']
    try:
        result = subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr, universal_newlines=True)
        #print("Command Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr) 

    command = ["python", plugin_script_path, 
               '--workdir', args.workdir, 
               '--outdir', args.outdir, 
               '--print_assets']
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception('no assets to test')

    output_str = result.stdout
    for asset in output_str.splitlines():
        filename = os.path.splitext(os.path.basename(asset))[0]

        iteration = 0
        while iteration < args.repeats:
            iteration += 1

            start_time = time.time()

            outdir = os.path.join(args.outdir, filename, 'frame_' + str(iteration))
            os.makedirs(outdir, exist_ok=True)
        
            command = ["python", plugin_script_path, 
                       '--workdir', args.workdir, 
                       '--outdir', outdir, 
                       '--executable', args.executable,
                       '--samples', str(args.samples),
                       '--asset', asset,
                       '--gpu', str(args.gpu)
                       ]
            result = subprocess.run(command, stdout=sys.stdout, stderr=sys.stderr)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time} seconds")

        pass


if __name__ == "__main__":
    main()
