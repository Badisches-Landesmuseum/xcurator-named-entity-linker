from anytree.importer import JsonImporter
from anytree import RenderTree
import json

class TreeDictRepository:
    def __init__(self, file: str):
        if not file:
            raise ValueError("No Collection name given!")
        self.file = file
        self.tree = TreeDictRepository._load(self,file)

    def _load(self, file):
        with open(file) as json_file:
            tree = json.load(json_file)
        importer = JsonImporter()
        return importer.import_(tree)

    def render_tree(self):
        return RenderTree(self.tree)