import json
import logging
import os
import pickle
from pathlib import Path

import wget


class ResourcesManager:

    def __init__(self, resources_config: dict = None):
        self.resources_config = resources_config

    @staticmethod
    def print_banner():
        print(open(os.path.join(os.path.dirname(__file__), "banner.txt")).read())

    # File manager
    @staticmethod
    def load_json_file(json_file_path):
        path = os.path.join(os.path.dirname(__file__), json_file_path)
        json_file = open(path, "r", encoding="utf-8")
        return json.load(json_file)

    @staticmethod
    def create_folder_if_none(folder_path) -> Path:
        output_dir = Path(os.path.join(os.path.dirname(__file__), folder_path))
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_model_path(self, file_name=None) -> Path:
        output_dir = ResourcesManager.create_folder_if_none(self.resources_config['models'])
        if file_name:
            return Path(os.path.join(output_dir, file_name))
        return output_dir

    def get_custom_training_path(self, file_name: str):
        output_dir = ResourcesManager.create_folder_if_none(self.resources_config['custom-training-files'])
        return Path(output_dir / file_name)



    @staticmethod
    def get_resource_file(file_path: str):
        return os.path.join(os.path.dirname(__file__), file_path)

    @staticmethod
    def download_file(url, output_dir, file_name):
        logging.info("File doesn't exits => Downloading file: " + file_name)
        wget.download(url, str(output_dir))

    # PKL Reader and writer
    @staticmethod
    def get_pkl_file_data(filepath):
        with open(filepath, "rb") as fp:
            loaded_data = pickle.load(fp)
        return loaded_data

    @staticmethod
    def save_pkl_file_data(data, filepath):
        with open(filepath, 'wb') as filehandler:
            # store the data list as binary data stream
            pickle.dump(data, filehandler)
