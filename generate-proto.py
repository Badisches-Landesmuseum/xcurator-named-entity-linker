import os
from os import listdir
from os.path import isfile, join
from typing import Iterable

import yaml

'''
Python Script to perform Code-Generation for Google Proto files.

By convention the *.proto files have to be stored inside the 'proto' folder in the root-
The generated Proto Classes will be stored at [source_coot/proto]

Requirements: 
- protobuf (Google Protobuf Library) 
- betterproto[compiler] (pip)
'''

PROTO_FILE_DIR = 'proto-files'


def get_proto_files(source_directory: str) -> Iterable[str]:
    return [file for file in listdir(source_directory) if isfile(join(source_directory, file))]


def build_generate_shell_command(proto_source_dir: str, proto_file: str, source_root) -> Iterable[str]:
    if not os.path.exists(source_root + "/proto/"):
        os.makedirs(source_root + "/proto/")
    return ['protoc', '--proto_path', proto_source_dir, '--python_betterproto_out', source_root + "/proto/", proto_file]


def source_dir():
    child_dirs = next(os.walk('.'))[1]
    directories = list(filter(lambda k: '.' not in k and 'proto' not in k and 'test' not in k, child_dirs))
    if len(directories) == 1:
        return directories[0]
    else:
        with open(r'environment.yml') as file:
            environmentFile = yaml.load(file, Loader=yaml.FullLoader)
            directory = str(environmentFile['name']).strip()
            if "-" in directory or "_" in directory:
                directory = directory.replace("-", "_")
            return directory


def get_source_root_folder():
    project_root_absolute = os.path.dirname(__file__)
    project_root = os.path.basename(os.path.normpath(project_root_absolute))

    if "-" in project_root or "_" in project_root:
        source_root = project_root.replace("-", "_")
    else:
        source_root = source_dir()

    if not os.path.isdir(source_root):
        return source_dir()
    if not os.path.isdir(source_root):
        raise EnvironmentError(
            f"Can't locate python source root. Tryed: ({source_root})Do you follow the project structure conventions?")
    if not os.path.isdir(f'{source_root}/proto'):
        os.mkdir(f'{source_root}/proto')
    return source_root


proto_files = get_proto_files(PROTO_FILE_DIR)
print(proto_files)
source_root = get_source_root_folder()
os.system(
    'protoc proto-files/*.proto --python_betterproto_out ' + source_root + "/proto --python_out " + source_root + "/proto")
