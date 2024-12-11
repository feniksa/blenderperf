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
import tempfile
import time


def execute_task(args, api, task):
    procedure = task.get('procedure_name')
    code = task.get('procedure_code')

    inputs = task.get('inputs')

    print(f"execute \"{procedure}\" procedure")

    with tempfile.NamedTemporaryFile(delete=True, mode='w') as temp_file:
        temp_file.write(code)
        temp_file.flush()

        command = [ sys.executable, temp_file.name,
                               '--url', args.url,
                               '--apikey', args.apikey,
                               '--cachedir', args.cachedir,
                               '--workdir', args.workdir,
                               '--taskid', str(task.get('id')),
                               '--inputs', str(json.dumps(inputs)),
                               ]

        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.realpath(__file__))

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, universal_newlines=True)

            # Read stdout and stderr
            stdout, stderr = process.communicate()

            # Decode and print outputs
            #stdout = stdout.decode('utf-8')
            #stderr = stderr.decode('utf-8')

            print(stdout)
            print(stderr)
                        
            api.post_task_data(task.get('id'), 'stdout', stdout)
            api.post_task_data(task.get('id'), 'stderr', stderr)

            if process.returncode == 0:
                api.task_change_status(task.get('id'), 'success')
            else:
                api.task_change_status(task.get('id'), 'failed')

            api.post_task_data(task.get('id'), 'returncode', str(process.returncode), 'int')

        except subprocess.CalledProcessError as e:
            api.post_task_data(task.get('id'), 'stderr', str(e))
            api.task_change_status(task.get('id'), 'failed')


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

    while True:
        start_time = time.time()  

        try: 
            print('get task from server')
            task = api.get_node_task()
            if task:
                execute_task(args, api, task)
        except KeyboardInterrupt:
            return 0
        except requests.exceptions.ConnectionError:
            print('connection error. Retry')
            pass

        execution_time = time.time() - start_time  # Measure execution time

        sleep_time = max(0, 1 - execution_time)
        time.sleep(sleep_time)
        
    return 0
    
    
if __name__ == "__main__":
    main()
