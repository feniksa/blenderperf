import argparse
import os
import json
import subprocess
import shutil
import sys

import requests
import tarfile
from pathlib import Path
from urllib.parse import urljoin
from api import Api
from storage import Storage


def main():
    parser = argparse.ArgumentParser(
        prog='submit.py',
        description='test for application',
        epilog='for more information: https://github.com/feniksa/blenderperf')

    default_url = 'http://localhost:8000'
    default_outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outdir')
    default_cachedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cachedir')
    default_workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workdir')

    parser.add_argument('-p', '--ping', action='store_true', dest='ping', help='ping server')
    parser.add_argument('-u', '--url', default=default_url, type=str, help='url for upload')
    parser.add_argument('-a', '--apikey', default='qqq', type=str, help='api token')
    parser.add_argument('-o', '--outdir', default=default_outdir, type=str, help='default outdir with metrics')
    parser.add_argument('-w', '--workdir', default=default_workdir, type=str, help='default workdir')
    parser.add_argument('-c', '--cachedir', default=default_cachedir, type=str, help='default cache dir')

    args = parser.parse_args()

    cache = Storage(args.cachedir)
    workdir = Storage(args.workdir)

    api = Api(args.url, args.apikey)

    if args.ping:
        reply = api.ping()
        print(reply)
        return 0


    jobs = api.get_node_jobs()
    for job in jobs:
        print("job {} {}".format(job.get('job_id'), job.get('name')))

        node_job_id = job.get("id")

        #TODO: use getnodetask in loop.
        tasks = api.get_node_tasks(node_job_id)
        for task in tasks:
            api.task_change_status(task.get('id'), 'in_progress')

            action = task.get('action', '')
            match action:
                case 'download':
                    server_file_path = task.get('file_url')
                    server_file_name = task.get('file_name')
                    server_file_hash = task.get('file_hash')

                    print(f"download asset {server_file_path}")

                    asset_file = cache.download(api.get_url(server_file_path), 'downloads', server_file_hash)
                    print(f"saved to {asset_file}")

                    api.task_change_status(task.get('id'), 'success')

                case 'unpack':
                    server_file_path = task.get('file_url')
                    server_file_name = task.get('file_name')
                    server_file_hash = task.get('file_hash')

                    file_path = cache.resolve_file_path(server_file_path, 'downloads')

                    try:
                        cache.unpack(file_path, 'assets', server_file_hash)
                        api.task_change_status(task.get('id'), 'success')
                    except Exception as e:
                        api.task_change_status(task.get('id'), 'failed')

                case 'execute':
                    server_file_path = task.get('file_url')
                    server_file_name = task.get('file_name')
                    server_file_hash = task.get('file_hash')

                    file_path = cache.resolve_file_path(server_file_path, 'downloads')

                    inputs = job.get('inputs')
                    task_params = task.get('task_params')

                    command = [ sys.executable, file_path,
                               '--url', args.url,
                               '--apikey', args.apikey,
                               '--cachedir', args.cachedir,
                               '--workdir', args.workdir,
                               '--inputs', json.dumps(inputs),
                               '--params', json.dumps(task_params) ]

                    env = os.environ.copy()
                    env["PYTHONPATH"] = os.path.dirname(os.path.realpath(__file__))

                    try:
                        result = subprocess.run(                                
                                command,
                                env=env,
                                stdout=sys.stdout, 
                                stderr=sys.stderr)

                        if result.returncode == 0:
                            api.task_change_status(task.get('id'), 'success')
                    except subprocess.CalledProcessError as e:
                        print(e)
                        #api.task_change_status(task.get('id'), 'failed')


    #report_id = api_create_report(args.url, args.apikey, 'blender', '123')
    #print(report_id)

    #gpu_report_id = api_create_gpu_report(args.url, report_id)
    
    
if __name__ == "__main__":
    main()
