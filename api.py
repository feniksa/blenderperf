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
    
    __key_api:str = 'api_key'
    __ping_counter = 0

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def get_url(self, path):
        return urljoin(self.url, path)
       
    def ping(self):
        url = self.get_url('automatron/nodeapi/ping')

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
    
    #def get_node_jobs(self):
    #    url = self.get_url('automatron/nodeapi/jobs')
    #    data = {
    #        self.__key_api: self.api_key
    #    }
    #    response = requests.post(url, json.dumps(data))
    #    response.raise_for_status()

    #    if response.status_code == 200:
    #        return response.json().get("jobs")
    #    else:
    #        print("Failed:", response.status_code, response.message)
    #        raise Exception(response.message)

    def task_change_status(self, task_id, status):
        url = self.get_url('automatron/nodeapi/task/status/change')
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

    def get_node_task(self):
        url = self.get_url('automatron/nodeapi/task')
        data = {
            self.__key_api: self.api_key,
        }
        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json().get('task')
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)

    def post_task_data(self, task_id, metric, data, data_type='text'):
        url = self.get_url('automatron/nodeapi/task/postdata')
        data = {
            self.__key_api: self.api_key,
            'task_id': task_id, 
            'metric': metric,
            'data':  data,
            'data_type': data_type,
        }
        response = requests.post(url, json.dumps(data))
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()
        else:
            print("Failed:", response.status_code, response.message)
            raise Exception(response.message)


    #def get_node_tasks(self, node_job_id):
    #    url = self.get_url('automatron/nodeapi/tasks')
    #    data = {
    #        self.__key_api: self.api_key,
    #        'node_job_id': node_job_id,
    #    }
    #    response = requests.post(url, json.dumps(data))
    #    response.raise_for_status()

    #    if response.status_code == 200:
    #        return response.json().get('tasks')
    #    else:
    #        print("Failed:", response.status_code, response.message)
    #        raise Exception(response.message)


#    def create_report(self, application:str):
#        url = urljoin(self.url, 'automatron/api/report/create')
#
#        data = {
#            'api_key': self.api_key,
#            'application': application,
#            'application_hash': self.get_application_hash(application),
#        }
#
#        # Send the POST request and capture the response
#        response = requests.post(url, json.dumps(data))
#        response.raise_for_status()
#
#        # Check if the request was successful
#        if response.status_code == 200:
#            return response.json()['report_id']
#        else:
#            print("Failed:", response.status_code, response.message)
#            raise Exception(response.message)
#        pass

#def api_create_report(url, api_key, application, application_hash):
#    url = urljoin(url, 'automatron/api/report/create')
#
#    data = {
#        'api_key' : api_key,
#        'application': application,
#        'application_hash': application_hash,
#    }
#
#    # Send the POST request and capture the response
#    response = requests.post(url, json.dumps(data))
#    response.raise_for_status()
#    
#    # Check if the request was successful
#    if response.status_code == 200:
#        return response.json()['report_id']
#    else:
#        print("Failed:", response.status_code, response.message)
#        raise Exception(response.message)
#
#def api_create_gpu_report(url, api_key, report_id, asset_hash):
#    url = urljoin(url, 'automatron/api/report/gpu/create')
#
#    gpu_name = ''
#    median_time = 23.3
#    median_vram = 24.3
#
#    # foreach test asset
#    render_times = [ 1, 2, 3, 4 ]
#    vram_usage = [ 1.2, 1.3, 1.4 ]
#
#    data = {
#        'api_key' : api_key, 
#        'report_id': report_id,
#        'gpu' : gpu_name,
#        'asset_hash' : asset_hash,
#        'render_times' : render_times,
#        'vram_usage' : vram_usage,
#        'median_time': median_time,
#        'median_vram' : median_vram
#    }
#
#    # Send the POST request and capture the response
#    response = requests.post(url, json.dumps(data))
#
#    # Check if the request was successful
#    if response.status_code == 200:
#        return response.json()['report_id']
#    else:
#        print("Failed:", response.status_code, response.message)
#        raise Exception(response.message)
#

