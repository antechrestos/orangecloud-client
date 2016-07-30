import sys
from os import path


def add_project_root_to_path():
    root = path.join(path.dirname(__file__), '..', '..')
    print root
    sys.path.append(root)
