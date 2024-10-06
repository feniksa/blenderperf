import argparse
import time
import subprocess
import shutil
import sys

from analyze import *

def save2file(data, outdir):
    file_name = os.path.join(outdir, 'data.txt')
    with open(file_name, "w") as file:
        for d in data:
            file.write(f"{d}\n")

def get_render_memory(directory):
    file_name = os.path.join(directory, 'memory.txt')

    with open(file_name, "r") as file:
        file_content = file.read()

    return float(file_content)

def get_render_time(directory):
    file_name = os.path.join(directory, 'time.txt')

    with open(file_name, "r") as file:
        file_content = file.readline().strip()
        
    time_parts = file_content.split(":")

    # Extract hours, minutes, seconds, and microseconds
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds, microseconds = map(int, time_parts[2].split("."))

    timestamp = timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
    return timestamp


def check_executable(path: str):
    return os.path.isfile(path) and os.access(path, os.X_OK)

def run_prepare_command(script_path, workdir, outdir):
    command = [sys.executable, script_path, '--workdir', workdir, '--outdir', outdir, '--prepare']
    try:
        result = subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr, universal_newlines=True)
        # print("Command Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)

def get_assets_list(script_path, workdir, outdir) -> list[str]:
    command = [sys.executable, script_path,
               '--workdir', workdir,
               '--outdir', outdir,
               '--print_assets']
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception('no assets to test')

    return result.stdout.splitlines()

def dump_environment(executable_path, script_path, workdir, outdir):
    command = [sys.executable,
               script_path,
               '--executable', executable_path,
               '--workdir', workdir,
               '--outdir', outdir,
               '--dump_environment']
    try:
        result = subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr, universal_newlines=True)
        # print("Command Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)

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
    parser.add_argument('-c', '--clean', default=1, type=int, help='clean outdir')
    parser.add_argument('-x', '--width', type=int, default=3840, help='render image width')
    parser.add_argument('-y', '--height', type=int, default=2160, help='render image height')

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

    if args.clean:
        shutil.rmtree(args.outdir)
        os.makedirs(args.outdir)
        with open(os.path.join(args.outdir, '.keepme'), "w") as file:
            pass

    run_prepare_command(plugin_script_path, args.workdir, args.outdir)
    dump_environment(args.executable, plugin_script_path, args.workdir, args.outdir)

    assets_path = get_assets_list(plugin_script_path, args.workdir, args.outdir)

    for asset in assets_path:
        filename = os.path.splitext(os.path.basename(asset))[0]

        iteration = 0
        
        render_times = []
        render_memories = []

        while iteration < args.repeats:
            iteration += 1

            start_time = time.time()

            outdir = os.path.join(args.outdir, filename, 'frame_' + str(iteration))
            os.makedirs(outdir, exist_ok=True)
       
            command = [sys.executable, plugin_script_path, 
                       '--workdir', args.workdir, 
                       '--outdir', outdir, 
                       '--executable', args.executable,
                       '--samples', str(args.samples),
                       '--asset', asset,
                       '--gpu', str(args.gpu),
                       '--width', str(args.width),
                       '--height', str(args.height),
                       ]

            # try to run program
            try:
                result = subprocess.run(command, stdout=sys.stdout, stderr=sys.stderr)
                retcode = result.returncode
            except subprocess.CalledProcessError as e:
                retcode = 1
                print(e)

            # if program failed, we copy to frame_0 to errors/frame_0 for futher investigation

            if retcode != 0:
                errordir = os.path.join(args.outdir, filename, 'errors', 'frame_' + str(iteration))
                os.makedirs(errordir, exist_ok=True)
                shutil.copytree(outdir, errordir, dirs_exist_ok=True)

                # retry to run command
                try:
                    result = subprocess.run(command, stdout=sys.stdout, stderr=sys.stderr)
                    retcode = result.returncode
                except subprocess.CalledProcessError as e:
                    retcode = 1
                    print(e)


            # command failed second time, give up
            if retcode != 0:
                raise Exception(f"can't run program" + " ".join(command))

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time} seconds")

            # read render timings for frame
            render_time = get_render_time(outdir)
            render_times.append(render_time.total_seconds())

            # read render vram usage for frame
            render_memory = get_render_memory(outdir)
            render_memories.append(render_memory)

        # analyze render times for all frames
        outdir = os.path.join(args.outdir, filename, 'render')
        os.makedirs(outdir, exist_ok=True)

        save2file(render_times, outdir)
        analyze(render_times, outdir) 


        # analyze vram usage times for all frames
        outdir = os.path.join(args.outdir, filename, 'memory')
        os.makedirs(outdir, exist_ok=True)
        save2file(render_memories, outdir)
        analyze(render_memories, outdir)


if __name__ == "__main__":
    main()
