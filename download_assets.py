import os
import argparse
import json
import requests

parser = argparse.ArgumentParser(prog='download_assets.py', description='Download test assets')

parser.add_argument('-url', '-', required=True)
parser.add_argument('-directory', '-d', required=True)

args = parser.parse_args()

def get_timestamp_filename(name):
    return args.directory + '/' + name + '.tms'

def get_asset_filename(name):
    return args.directory + '/' + name 

def same_timestamp(filename, mtime) -> bool:
    cached_mtime = ''

    if not os.path.exists(filename):
        return False

    with open(filename, 'r') as file:
        cached_mtime = file.readline().strip()

    return cached_mtime == mtime

def same_filesize(filename, msize):
    file_size = os.path.getsize(filename)
    return msize == file_size

def save_file_mtime_size(filename, mtime):
    with open(filename, 'w') as file:
        file.write('{}\n'.format(mtime))

def download_file(url, filename):
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

if not os.path.exists(args.directory):
    print("directory {} doesn't exists".format(args.directory))
    exit(2)

print('send request to ' + args.url)

response = requests.get(args.url)
if response.status_code == 200:
    print('server reply 200')

    data = response.json()
    print('present {} assets '.format(len(data)))

    for remote_info in data:
        #print(remote_info['name'])
        #print(remote_info['type'])
        #print(remote_info['mtime'])
        #print(remote_info['size'])
        timestamp_filename = get_timestamp_filename(remote_info['name'])
        asset_filename = get_asset_filename(remote_info['name'])

        if same_timestamp(timestamp_filename, remote_info['mtime']):
            if same_filesize(asset_filename, remote_info['size']):
                print('asset {} cached. skip'.format(remote_info['name']))
                continue
       
        download_url = args.url + '/' + remote_info['name']

        print('download {} and save to {}'.format(download_url, asset_filename))
        download_file(download_url, asset_filename)
        print('done')

        print('save timestamp of file')        
        save_file_mtime_size(timestamp_filename, remote_info['mtime'])
        print('done')
else:
    print(f"Failed to retrieve data: {response.status_code}")
    exit(1)




