import argparse
import os
import json

import requests
import tarfile
from pathlib import Path
from urllib.parse import urljoin


class Api:
    url:str = ''
    api_key:str = ''
    workdir:str = ''
    cachedir:str = ''

    __key_api:str = 'api_key'
    __ping_counter = 0

    def __init__(self, url, api_key, workdir, cachedir):
        self.url = url
        self.api_key = api_key
        self.workdir = workdir
        self.cachedir = cachedir
        
        if not os.path.exists(self.workdir):
            errmsg = "work directory {} doesn't exists. Please, create it"
            raise Exception(errmsg.format(self.workdir))

        if not os.path.exists(self.cachedir):
            errmsg = "cache directory {} doesn't exists. Please, create it"
            raise Exception(errmsg.format(self.cachedir))

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

    def task_change_status(self, task_id, status):
        url = urljoin(self.url, 'gpuperf/nodeapi/task/status/change')
        data = {
            self.__key_api: self.api_key,
            'task_id': task_id, 
            'status': status,
        }

        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json().get("jobs")
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)


    def get_node_tasks(self, node_job_id):
        url = urljoin(self.url, 'gpuperf/nodeapi/tasks')
        data = {
            self.__key_api: self.api_key,
            'node_job_id': node_job_id,
        }
        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json().get('tasks')
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)

    def unpack(self, tar_bz2_file:str, cachedir:bool=False):
        if cachedir:
            directory = self.cachedir
        else:
            directory = self.workdir

        print(f'unpack {tar_bz2_file}')
        with tarfile.open(tar_bz2_file) as tar:
            tar.extractall(path=directory)


    def get_filepath(self, file_path, cachedir=False):
        if cachedir:
            dst_dir = os.path.join(self.cachedir, file_path)
        else:
            dst_dir = os.path.join(self.workdir, file_path)
        
        return dst_dir


    def download_file(self, server_file_name, server_file_path, server_file_hash, cachedir=False):
        local_file_name = os.path.basename(server_file_name)
        local_file_path = os.path.dirname(server_file_name)

        dst_dir = self.get_filepath(local_file_path, cachedir)

        os.makedirs(dst_dir, exist_ok=True)

        dst_file = os.path.join(dst_dir, local_file_name)

        # check if file already downloaded and has same hash
        local_file_hash = self.__get_file_hash(dst_file)
        if local_file_hash == server_file_hash:
            return dst_file

        # download file
        self.__download_file(server_file_path, dst_file)
    
        # save file hash
        self.__save_hash(dst_file, server_file_hash)

        return dst_file

    def __save_hash(self, file_path, file_hash):
        hash_file = "{}.{}".format(file_path, 'hash')
        with open(hash_file, "w") as file:
            file.write(file_hash)

    def __get_file_hash(self, file_path):
        hash_file = "{}.{}".format(file_path, 'hash')
        if not os.path.exists(hash_file):
            return ''

        content = ''
        with open(hash_file, "r") as file:
            content = file.read()

        return content

    def __download_file(self, file_path, filename):
        url = urljoin(self.url, file_path)
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


