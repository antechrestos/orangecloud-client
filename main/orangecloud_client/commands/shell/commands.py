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


def cd(path):
    global _current_folder
    global _root
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
                sub_path_encoded = _to_unicode(sub_path)
                for sub_folder in _current_folder.sub_folders:
                    if sub_path_encoded == sub_folder.name:
                        _current_folder = sub_folder
                        found = True
                        break
                if not found:
                    path_walked.append(sub_path)
                    sys.stderr.write('cd: Folder not found: %s\n' % '/'.join(path_walked))
                    return False
        path_walked.append(sub_path)
    return True


def ls(client, name):
    global _current_folder

    def print_folder(folder):
        for entity_name in sorted([entity.name for entity in folder.sub_folders]):
            print '%s/' % entity_name
        for entity_name in sorted([entity.name for entity in folder.files]):
            print '%s' % entity_name

    _load_files_if_necessary(client, _current_folder)
    if name is None:
        print_folder(_current_folder)
    else:
        name_encoded = _to_unicode(name)
        for sub_folder in _current_folder.sub_folders:
            if sub_folder.name == name_encoded:
                _load_files_if_necessary(client, sub_folder)
                print_folder(sub_folder)
                return
        for sub_file in _current_folder.files:
            if sub_file.name == name_encoded:
                print '%s - %s - %d' % (sub_file.name, sub_file.creationDate, sub_file.size)
                return
        sys.stderr.write('ls: File/Folder not found: %s\n' % name)


def mkdir(client, name):
    global _current_folder
    f = client.folders.create(name, _current_folder.folder_id)
    _current_folder.sub_folders.append(_Folder(f.id, _current_folder, f.name))


def rm(client, name):
    global _current_folder
    name_encoded = _to_unicode(name)
    _load_files_if_necessary(client, _current_folder)
    for sub_file in _current_folder.files:
        if sub_file.name == name_encoded:
            client.files.delete(sub_file.id)
            _load_files_if_necessary(client, _current_folder, True)
            return
    idx = 0
    for sub_directory in _current_folder.sub_folders:
        if sub_directory.name == name_encoded:
            client.folders.delete(sub_directory.folder_id)
            _current_folder.sub_folders.pop(idx)
            return
        idx += 1
    sys.stderr.write('rm: File/Folder not found: %s\n' % name)


def upload(client, input_path, extensions=None):
    global _current_folder
    filter_extensions_splitted = [] if extensions is None else extensions.split(',')

    def keep_file(file_name):
        dot_position = file_name.rfind('.')
        return len(filter_extensions_splitted) == 0 \
               or dot_position >= 0 and file_name[dot_position + 1:] in filter_extensions_splitted \
               or dot_position == -1 and '' in filter_extensions_splitted

    if os.path.isfile(input_path):
        _load_files_if_necessary(client, _current_folder)
        _log_file_activity(input_path)
        if _is_file_present(_current_folder, os.path.basename(input_path)):
            print 'ALREADY EXISTS'
        else:
            client.files.upload(input_path, _current_folder.folder_id)
            _load_files_if_necessary(client, _current_folder, True)
            print 'OK'
    elif os.path.isdir(input_path):
        _upload_directory(client, input_path, _current_folder, keep_file)
    else:
        sys.stderr.write('upload: Bad system file, must be either a directory or a file: %s\n' % input_path)
        return


def download(client, output_path, name):
    global _current_folder
    if not os.path.isdir(output_path):
        sys.stderr.write('download: invalid directory: %s\n' % output_path)
        return
    elif name == '.':
        _download_directory(client, _current_folder, output_path)
    else:
        _load_files_if_necessary(client, _current_folder)
        name_encoded = _to_unicode(name)
        for sub_file in _current_folder.files:
            if sub_file.name == name_encoded:
                file_output_path = os.path.join(output_path, sub_file.name)
                _log_file_activity(file_output_path)
                client.files.download(sub_file.downloadUrl, file_output_path)
                print 'OK'
                return

        for sub_directory in _current_folder.sub_folders:
            if sub_directory.name == name:
                destination_path = os.path.join(output_path, sub_directory.name)
                if not os.path.exists(destination_path):
                    _create_local_directory(destination_path)
                if not os.path.isdir(destination_path) or not os.access(destination_path, os.W_OK):
                    sys.stderr.write('download: %s exist and is not a writable directory\n' % destination_path)
                    return
                else:
                    _download_directory(client, sub_directory, destination_path)
                    return
        sys.stderr.write('download: File/Folder not found: %s\n' % name)


def freespace(client):
    freespace_in_octet = client.freespace.get().freespace
    print freespace_in_octet
    one_ko = 1024
    one_mo = 1024 * one_ko
    one_go = 1024 * one_mo
    if freespace_in_octet < one_ko:
        print '%d o' % freespace_in_octet
    elif freespace_in_octet < one_mo:
        print '%0.1f Ko' % (float(freespace_in_octet) / one_ko)
    elif freespace_in_octet < one_go:
        print '%0.1f Mo' % (float(one_go) / one_mo)
    else:
        print '%0.1f Go' % (float(freespace_in_octet) / one_go)


def reload_cache(client):
    global _root
    global _current_folder
    flat_hierarchy = client.folders.get(flat=True, tree=True)
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
        else:
            _current_folder = folders_by_id[_current_folder.folder_id]


def pwd():
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


def _upload_directory(client, directory_path, current_directory, keep_file):
    local_directory_name = os.path.basename(directory_path)
    if len(local_directory_name) == 0:
        # Occurs if directory_path ends with /
        local_directory_name = os.path.basename(os.path.dirname(directory_path))
    encoded_directory_name = _to_unicode(local_directory_name)
    remote_directory = None
    for sub_folder in current_directory.sub_folders:
        if sub_folder.name == encoded_directory_name:
            remote_directory = sub_folder
            _load_files_if_necessary(client, remote_directory)
            break
    if remote_directory is None:
        f = client.folders.create(local_directory_name, current_directory.folder_id)
        remote_directory = _Folder(f.id, current_directory, f.name)
        current_directory.sub_folders.append(remote_directory)
    sub_folders = []
    new_files = False
    for sub_entity in sorted(os.listdir(directory_path)):
        full_path = os.path.join(directory_path, sub_entity)
        if os.path.isfile(full_path) and keep_file(sub_entity):
            _log_file_activity(full_path)
            if remote_directory.files is not None and _is_file_present(remote_directory, sub_entity):
                print 'ALREADY EXISTS'
            else:
                client.files.upload(full_path, remote_directory.folder_id)
                print 'OK'
                new_files = True
        elif os.path.isdir(full_path):
            sub_folders.append(full_path)
    if new_files:
        remote_directory.files = None
    for sub_folder in sub_folders:
        _upload_directory(client, sub_folder, remote_directory, keep_file)


def _is_file_present(remote_directory, local_filename):
    encoded_filename = _to_unicode(local_filename)
    already_exists = False
    for sub_file in remote_directory.files:
        if sub_file.name == encoded_filename:
            already_exists = True
            break
    return already_exists


def _create_local_directory(destination_path):
    os.mkdir(destination_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def _download_directory(client, folder, destination_path):
    _load_files_if_necessary(client, folder)
    for sub_file in folder.files:
        file_output_path = os.path.join(destination_path, sub_file.name)
        _log_file_activity(file_output_path)
        client.files.download(sub_file.downloadUrl, file_output_path)
        print 'OK'
    for sub_folder in folder.sub_folders:
        sub_folder_path = os.path.join(destination_path, sub_folder.name)
        if not os.path.exists(sub_folder_path):
            _create_local_directory(sub_folder_path)
        if not os.path.isdir(sub_folder_path) or not os.access(sub_folder_path, os.W_OK):
            sys.stderr.write('download: %s exist and is not a writable directory\n' % sub_folder_path)
            return
        else:
            _download_directory(client, sub_folder, sub_folder_path)


def _load_files_if_necessary(client, folder, force=False):
    if folder.files is None or force:
        folder.files = client.folders.get(folder.folder_id, showthumbnails=True).files

def _to_unicode(name):
    return unicode(name, "utf-8", errors="ignore")


def _log_file_activity(file_path):
    sys.stdout.write('%s ...' % file_path)
    sys.stdout.flush()
