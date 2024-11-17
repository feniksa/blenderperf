import os

import requests
import tarfile
from pathlib import Path
from urllib.parse import urljoin
from urllib.parse import urlparse
from hashfile import HashFile


class Storage:
    __directory:str = ''

    def __init__(self, path):
        self.__directory = path
        
        if not os.path.exists(self.__directory):
            errmsg = "work directory {} doesn't exists. Please, create it"
            raise Exception(errmsg.format(self.__directory))

    def unpack(self, file_path, dst_dir = '', server_file_hash = ''):
        dst_dir = os.path.join(self.__directory, dst_dir)

        hash_file = HashFile(file_path, 'unpack')
        if hash_file.exists():
            if hash_file.value() == server_file_hash:
                print(f"file {file_path} already unpacked, skip")
                return

        print(f'unpack {file_path} to {dst_dir}')

        os.makedirs(dst_dir, exist_ok=True)

        with tarfile.open(file_path) as tar:
            tar.extractall(path=dst_dir)

        if server_file_hash:
            hash_file.create(server_file_hash)


    def search(self, filename, dst_dir = ''):
        start_dir = os.path.join(self.__directory, dst_dir)

        for dirpath, dirnames, filenames in os.walk(start_dir):
            if filename in filenames:
                return os.path.join(dirpath, filename)
        return None

    def download(self, url, dst_dir = '', server_file_hash = ''):
        resolved_file_path = self.resolve_file_path(url, dst_dir)

        hash_file = HashFile(resolved_file_path)
        if hash_file.exists():
            if hash_file.value() == server_file_hash:
                print(f"file {resolved_file_path} cached, skip")
                return resolved_file_path

        print(f'download {url} to {resolved_file_path}')

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
    
            file_length = int(r.headers['Content-Length'])
            downloaded = 0
    
            with open(resolved_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    print('{}/{}'.format(downloaded, file_length), end="\x1b[1G")
                print('')

        if server_file_hash:
            hash_file.create(server_file_hash)

        return resolved_file_path


    def resolve_file_path(self, url, dst_dir):
        parsed_url = urlparse(url)
        path = parsed_url.path
        path_dir = os.path.dirname(parsed_url.path)
        file_name = os.path.basename(path)

        resolved_directory = os.path.join(self.__directory, dst_dir) + path_dir
        os.makedirs(resolved_directory, exist_ok=True)

        resolved_file_path = os.path.join(resolved_directory, file_name)

        return resolved_file_path

