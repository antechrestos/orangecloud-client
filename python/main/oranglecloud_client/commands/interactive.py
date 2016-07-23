import sys

_currrent_folder_id = None

def shell(client):
    ask_exit = False
    sync()
    while not ask_exit:
        command_line = sys.stdin.readline()
        command_line = command_line.rstrip('\r\n').lstrip(' \t')




def ls(entity_id=None):
    pass


def mkdir(name):
    pass


def upload(file_path):
    pass


def download(name, destination_path):
    pass


def freespace():
    pass

def sync():
    pass