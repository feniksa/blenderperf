import os
from pathlib import Path


class HashFile:
    __hash_file:str = ''

    def __init__(self, file_path, suffix = 'hash'):
        self.__hash_file = "{}.{}".format(file_path, suffix)

    def create(self, hash_value):
        with open(self.__hash_file, "w") as file:
            file.write(hash_value)

    def exists(self):
        if os.path.exists(self.__hash_file):
            return True
        else:
            return False

    def value(self):
        content = ''
        with open(self.__hash_file, "r") as file:
            content = file.read()

        return content


