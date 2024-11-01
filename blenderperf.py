import argparse
import os
import json

import requests
from urllib.parse import urljoin

def get_scene_report(scene_dir):
    pass

class Api:
    url:str = ''
    api_key:str = ''

    __key_api:str = 'api_key'
    __ping_counter = 0

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def ping(self):
        url = urljoin(self.url, 'gpuperf/nodeapi/ping')

        self.__ping_counter = self.__ping_counter + 1

        data = {
            self.__key_api: self.api_key,
            'counter': self.__ping_counter,
        }

        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)
    
    def get_node_jobs(self):
        url = urljoin(self.url, 'gpuperf/nodeapi/jobs')
        data = {
            self.__key_api: self.api_key
        }
        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json().get("jobs")
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)

    def get_node_tasks(self, job_id):
        url = urljoin(self.url, 'gpuperf/nodeapi/tasks')
        data = {
            self.__key_api: self.api_key,
            'job_id': job_id,
        }
        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json().get('tasks')
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)



    def download_file(self, file_path, filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
    
            file_length = int(r.headers['Content-Length'])
            downloaded = 0
    
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    print('{}/{}'.format(downloaded, file_length), end="\x1b[1G")
                print('')



    def get_application_hash(self, application_name:str):
        return ''

    def create_report(self, application:str):
        url = urljoin(self.url, 'gpuperf/api/report/create')

        data = {
            'api_key': self.api_key,
            'application': application,
            'application_hash': self.get_application_hash(application),
        }

        # Send the POST request and capture the response
        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()['report_id']
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)
        pass

    def create_gpu_report(self, report_id:str):
        pass

def api_create_report(url, api_key, application, application_hash):
    url = urljoin(url, 'gpuperf/api/report/create')

    data = {
        'api_key' : api_key,
        'application': application,
        'application_hash': application_hash,
    }

    # Send the POST request and capture the response
    response = requests.post(url, json.dumps(data))
    response.raise_for_status()
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()['report_id']
    else:
        print("Failed:", response.status_code, response.message)
        raise Exception(response.message)

def api_create_gpu_report(url, api_key, report_id, asset_hash):
    url = urljoin(url, 'gpuperf/api/report/gpu/create')

    gpu_name = ''
    median_time = 23.3
    median_vram = 24.3

    # foreach test asset
    render_times = [ 1, 2, 3, 4 ]
    vram_usage = [ 1.2, 1.3, 1.4 ]

    data = {
        'api_key' : api_key, 
        'report_id': report_id,
        'gpu' : gpu_name,
        'asset_hash' : asset_hash,
        'render_times' : render_times,
        'vram_usage' : vram_usage,
        'median_time': median_time,
        'median_vram' : median_vram
    }

    # Send the POST request and capture the response
    response = requests.post(url, json.dumps(data))

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()['report_id']
    else:
        print("Failed:", response.status_code, response.message)
        raise Exception(response.message)



def main():
    parser = argparse.ArgumentParser(
        prog='submit.py',
        description='test for application',
        epilog='for more information: https://github.com/feniksa/blenderperf')

    default_url = 'http://localhost:8000'
    default_outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outdir')

    parser.add_argument('-p', '--ping', action='store_true', dest='ping', help='ping server')
    parser.add_argument('-u', '--url', default=default_url, type=str, help='url for upload')
    parser.add_argument('-a', '--apikey', default='qqq', type=str, help='api token')
    parser.add_argument('-o', '--outdir', default=default_outdir, type=str, help='default outdir with metrics')

    args = parser.parse_args()

    #get_assets_list(args.outdir)

    api = Api(args.url, args.apikey)

    if args.ping:
        reply = api.ping()
        print(reply)
        return 0

    jobs = api.get_node_jobs()
    for job in jobs:
        print(job)
        job_id = job.get("id")
        tasks = api.get_node_tasks(job_id)
        for task in tasks:
            print(task)
            print('\n')
    

    #report_id = api_create_report(args.url, args.apikey, 'blender', '123')
    #print(report_id)

    #gpu_report_id = api_create_gpu_report(args.url, report_id)
    
    
if __name__ == "__main__":
    main()
