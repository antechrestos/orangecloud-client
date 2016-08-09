import logging
import os
import stat
import sys

_logger = logging.getLogger(__name__)

_root = None

_current_folder = None


class _Folder(object):
    def __init__(self, folder_id, parent, name):
        self.folder_id = folder_id
        self.parent = parent
        self.name = name
        self.sub_folders = []
        self.files = None


def cd(_, *args):
    global _current_folder
    global _root
    if len(args) != 1 or len(args[0]) == 0:
        sys.stderr.write('cd <sub folder name or ..>\n')
        return
    else:
        path = args[0]
        path_walked = []
        if path[0] == '/':
            _current_folder = _root
            path = path[1:]
            path_walked.append('')
        for sub_path in path.split('/'):
            if len(sub_path) > 0:
                if sub_path == '..' and _current_folder.parent is not None:
                    _current_folder = _current_folder.parent
                elif sub_path != '.':
                    found = False
                    for sub_folder in _current_folder.sub_folders:
                        if sub_path == sub_folder.name:
                            _current_folder = sub_folder
                            found = True
                            break
                    if not found:
                        sys.stderr.write('cd: Folder not found: %s\n' % '/'.join(path_walked))
            path_walked.append(sub_path)


def ls(client, *args):
    global _current_folder
    if len(args) >= 2:
        sys.stderr.write('cd [subfolder of subfile]\n')
        return

    def print_folder(folder):
        for entity in folder.sub_folders:
            print '%s/' % entity.name
        for entity in folder.files:
            print '%s' % entity.name

    _load_files_if_necessary(client, _current_folder)
    if len(args) == 0:
        print_folder(_current_folder)
    else:
        entity_name = args[0]
        for sub_folder in _current_folder.sub_folders:
            if sub_folder.name == entity_name:
                _load_files_if_necessary(client, sub_folder)
                print_folder(sub_folder)
                return
        for sub_file in _current_folder.files:
            if sub_file.name == entity_name:
                print '%s - %s - %d' % (sub_file.name, sub_file.creationDate, sub_file.size)
                return
        sys.stderr.write('ls: File/Folder not found: %s\n' % entity_name)


def mkdir(client, *args):
    global _current_folder
    if len(args) != 1:
        sys.stderr.write('mkdir <name>\n')
        return
    else:
        f = client.folders.create(args[1], _current_folder.folder_id)
        _current_folder.sub_folders.append(_Folder(f.id, _current_folder, f.name))


def upload(client, *args):
    global _current_folder
    if len(args) != 1:
        sys.stderr.write('upload <filesytem path>\n')
        return
    elif os.path.isfile(args[0]):
        client.files.upload(args[0], _current_folder.folder_id)
        _load_files_if_necessary(client, True)
    elif os.path.isdir(args[0]):
        folders_created = _upload_directory(client, args[0], _current_folder)
        _current_folder.sub_folders.append(folders_created)
    else:
        sys.stderr.write('upload: Bad system file, must be either a directory or a file: %s\n' % args[0])
        return


def download(client, *args):
    global _current_folder
    if len(args) != 1:
        sys.stderr.write('download <subfile name> <destination file path>\n')
        return
    elif not os.path.isdir(args[1]):
        sys.stderr.write('download: invalid directory\n' % args[1])
        return
    elif args[0] == '.':
        _download_directory(client, _current_folder, args[1])
    else:
        _load_files_if_necessary(client, _current_folder)
        entity_name = args[0]
        for sub_file in _current_folder.files:
            if sub_file.name == entity_name:
                client.files.download(sub_file.downloadUrl, os.path.join(args[1], sub_file.name))
                return

        for sub_directory in _current_folder.sub_folders:
            if sub_directory.name == entity_name:
                destination_path = os.path.join(args[1], sub_directory.name)
                if not os.path.exists(destination_path):
                    _create_local_directory(destination_path)
                elif not os.path.isdir(destination_path) or not os.access(destination_path, os.W_OK):
                    sys.stderr.write('download: %s exist and is not a writable directory\n' % destination_path)
                    return
                else:
                    _download_directory(client, sub_directory, destination_path)
                    return
        sys.stderr.write('download: File/Folder not found: %s\n' % args[0])


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


def reload_cache(client, *args):
    global _root
    global _current_folder
    flat_hierarchy = client.folders.get(flat=True)
    root = _Folder(flat_hierarchy.id, None, flat_hierarchy.name)
    folders_by_id = {f.id: _Folder(f.id, None, f.name) for f in flat_hierarchy.subfolders}
    folders_by_id[root.folder_id] = root
    for f in flat_hierarchy.subfolders:
        if f.parentId not in folders_by_id:
            sys.stderr.write('%s not in list. Available: \n%s\n' % (f.parentId, '\n'.join(folders_by_id.keys())))
        parent = folders_by_id[f.parentId]
        folder = folders_by_id[f.id]
        folder.parent = parent
        parent.sub_folders.append(folder)

    _root = root
    if _current_folder is None:
        _current_folder = root
    else:
        while _current_folder is not None and _current_folder.folder_id not in folders_by_id:
            _current_folder = _current_folder.parent
        if _current_folder is None:
            _current_folder = root


def pwd(*args):
    print get_path()


def get_path():
    global _current_folder
    result = []
    visitor = _current_folder
    while visitor is not None:
        result.append(visitor.name)
        visitor = visitor.parent
    result.reverse()
    return '/%s' % '/'.join(result)


def _upload_directory(client, directory_path, current_directory):
    sub_folders = []
    for sub_entity in os.listdir(directory_path):
        full_path = os.path.join(directory_path, sub_entity)
        if os.path.isfile(full_path):
            client.files.upload(full_path, current_directory.folder_id)
        elif os.path.isdir(full_path):
            f = client.folders.create(sub_entity, current_directory.folder_id)
            new_folder = _Folder(f.id, current_directory, f.name)
            sub_folders.append(new_folder)
            new_folder.sub_folders.append(_upload_directory(full_path, new_folder))
    _load_files_if_necessary(client, current_directory, True)
    return sub_folders


def _create_local_directory(destination_path):
    os.mkdir(destination_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def _download_directory(client, folder, destination_path):
    _load_files_if_necessary(folder)
    for sub_file in folder.files:
        client.files.download(sub_file.downloadUrl, os.path.join(destination_path, sub_file.name))
    for sub_folder in folder.sub_folders:
        sub_folder_path = os.path.join(destination_path, sub_folder.name)
        if not os.path.exists(sub_folder_path):
            _create_local_directory(sub_folder_path)
        elif not os.path.isdir(sub_folder_path) or not os.access(sub_folder_path, os.W_OK):
            sys.stderr.write('download: %s exist and is not a writable directory\n' % sub_folder_path)
            return
        else:
            _download_directory(client, sub_folder, sub_folder_path)


def _load_files_if_necessary(client, folder, force=False):
    if folder.files is None or force:
        folder.files = client.folders.get(folder.folder_id).files
