import glob
import os
import sys
import tarfile
import subprocess

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