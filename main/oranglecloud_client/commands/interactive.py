import logging
import sys
import os
import stat

_logger = logging.getLogger(__name__)

_current_folder = None

_hierarchy = None

_path = None


def shell(client):
    ask_exit = False
    sync()
    commands = dict(cd=cd, ls=ls, mkdir=mkdir, upload=upload, download=download, freespace=freespace,
                    sync=sync, pwd=pwd)
    while not ask_exit:
        sys.stdout.write('%s >' % _get_path())
        command_line = sys.stdin.readline()
        command_line = command_line.rstrip('\r\n').lstrip(' \t')
        command_line_splitted = command_line.split(' ')
        command_name = command_line_splitted[0]
        parameters = tuple(command_line_splitted[1:])
        if command_name == 'exit':
            break
        else:
            command = commands.get(command_name)
            if command is None:
                sys.stderr.write('Command not found: %s' % command_name)
            else:
                command(client, *parameters)


def cd(_, *args):
    global _path
    if len(args) != 1:
        sys.stderr.write('cd <sub folder name or ..>\n')
        return
    elif args[0] == '..':
        _path.pop()
    else:
        for sub_folder in _current_folder.subFolders:
            if args[0] == sub_folder.name:
                _path.append(sub_folder.id)
                return
        sys.stderr.write('cd: Folder not found: %s\n' % args[0])


def ls(_, *args):
    global _current_folder
    if len(args) >= 2:
        sys.stderr.write('cd [subfolder of subfile]\n')
        return

    def print_folder(folder):
        for entity in folder.subFolders:
            print '%d/' % entity.name
        for entity in folder.files:
            print '%d' % entity.name

    if len(args) == 0:
        print_folder(_current_folder)
    else:
        for sub_folder in _current_folder.subFolders:
            if sub_folder.name == args[1]:
                print_folder(sub_folder)
                return
        for sub_file in _current_folder.files:
            if sub_file.name == args[1]:
                print '%s - %s - %d' % (sub_file.name, sub_file.creationDate, sub_file.size)
                return
        sys.stderr.write('ls: File/Folder not found: %s\n' % args[1])


def mkdir(client, *args):
    if len(args) != 1:
        sys.stderr.write('mkdir <name>\n')
        return
    else:
        client.folders.create(args[1], _get_current_dir())
        sync(client)


def upload(client, *args):
    if len(args) != 1:
        sys.stderr.write('upload <filesytem path>\n')
        return
    elif os.path.isfile(args[0]):
        client.files.upload(args[0], _get_current_dir())
        sync(client)
    elif os.path.isdir(args[0]):
        _upload_directory(client, args[0], _get_current_dir())
    else:
        sys.stderr.write('upload: Bad system file, must be either a directory or a file: %s\n' % args[0])
        return


def download(client, *args):
    global _current_folder
    if len(args) != 1:
        sys.stderr.write('download <subfile name> <destination file path>\n')
        return
    elif os.path.isdir(args[1]):
        for sub_file in _current_folder.files:
            if sub_file.name == args[0]:
                client.files.download(sub_file.downloadUrl, os.path.join(args[1], sub_file.name))
                return
        for sub_directory in _current_folder.subFolders:
            if sub_directory.name == args[0]:
                destination_path = os.path.join(args[1], sub_directory.name)
                if not os.path.exists(destination_path):
                    _create_local_directory(destination_path)
                elif not os.path.isdir(destination_path) or not os.access(destination_path, os.W_OK):
                    sys.stderr.write('download: %s exist and is not a writable directory\n')
                    return
                else:
                    _download_directory(client, sub_directory, destination_path)
                    return
        sys.stderr.write('download: File/Folder not found: %s\n' % args[0])
    else:
        sys.stderr.write('download: Local Folder not found: %s\n' % args[1])


def freespace(client, *args):
    freespace_in_octet = client.freespace.get().freespace
    one_ko = 1024
    one_mo = 1024 * one_ko
    one_go = 1024 * one_mo
    if freespace_in_octet < one_ko:
        print '%d o' % freespace_in_octet
    elif freespace_in_octet < one_mo:
        print '%0.1f' % ((freespace_in_octet * 10.) / one_mo)
    elif freespace_in_octet < one_go:
        print '%0.1f' % ((one_go * 10.) / one_go)
    else:
        print '%0.1f' % ((freespace_in_octet * 10.) / one_go)


def sync(client, *args):
    global _hierarchy
    global _current_folder
    global _path
    _hierarchy = client.folders.get(flat=True)

    if _current_folder is None:
        _current_folder = _hierarchy
        _path = []
    else:
        _current_folder = _hierarchy
        new_path = []
        for folder_id in _path:
            child_found = False
            for sub_folder in _current_folder.subFolders:
                if folder_id == sub_folder.id:
                    _current_folder = sub_folder
                    child_found = True
                    break
            if child_found:
                new_path.append(folder_id)
            else:
                break
        _path = new_path


def pwd(*args):
    print _get_path()


def _get_path():
    global _path
    global _hierarchy
    result = []
    current_folder = _hierarchy
    for folder_id in _path:
        for sub_folder in current_folder.subFolders:
            if folder_id == sub_folder.id:
                result.append(sub_folder.name)
                current_folder = sub_folder
                break
    return '/%s' % '/'.join(result)


def _get_current_dir():
    global _path
    return None if len(_path) == 0 else _path[len(_path) - 1]


def _upload_directory(client, directory_path, current_directory_id):
    for sub_entity in os.listdir(directory_path):
        full_path = os.path.join(directory_path, sub_entity)
        if os.path.isfile(full_path):
            client.files.upload(full_path, current_directory_id)
        elif os.path.isdir(full_path):
            sub_directory = client.folders.create(sub_entity, current_directory_id)
            _upload_directory(full_path, sub_directory.id)


def _create_local_directory(destination_path):
    os.mkdir(destination_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def _download_directory(client, directory, destination_path):
    for sub_file in directory.files:
        client.files.download(sub_file.downloadUrl, os.path.join(destination_path, sub_file.name))
    for sub_folder in directory.subFolders:
        sub_folder_path = os.path.join(destination_path, sub_folder.name)
        _create_local_directory(sub_folder_path)
        _download_directory(client, sub_folder, sub_folder_path)