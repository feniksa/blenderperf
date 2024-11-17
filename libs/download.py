import argparse
import time
import subprocess
import shutil
import sys
import os
import json

from api import Api

def main():
    parser = argparse.ArgumentParser(
        prog='hello.py',
        description='test application',
        epilog='for more information: https://github.com/feniksa/blenderperf')

    parser.add_argument('-p', '--params',  help='')
    parser.add_argument('-i', '--inputs',  help='')
    parser.add_argument('-a', '--apikey',  type=str, help='api token')
    parser.add_argument('-u', '--url', type=str, help='url for upload')
    parser.add_argument('-w', '--workdir', type=str, help='default workdir')
    parser.add_argument('-c', '--cachedir', type=str, help='default cache dir')

    args = parser.parse_args()

    api = Api(args.url, args.apikey, args.workdir, args.cachedir)

    server_file_name = ''
    server_file_url = ''
    server_file_hash = ''

    inputs = json.loads(args.inputs) 
    params = json.loads(args.params) 

    for _input in inputs:
        match _input['name']:
            case 'exe':
                server_file_name = _input['value']['name']
                server_file_url = _input['value']['url']
                server_file_hash = _input['value']['hash']

    if server_file_name == '' or server_file_hash == '' or server_file_url == '':
        raise Exception('no required parameter')
            
    arch = api.download_file(server_file_name, server_file_url, server_file_hash)
    api.unpack(arch)

if __name__ == "__main__":
    main()



