#!/usr/bin/python2.7
import os
import logging
import argparse
from oranglecloud_client.commands.interactive import shell
from oranglecloud_client.commands.shell_client import load_client


def _mkdir(client, arg):
    response = client.folders.create(arg.name, arg.parent_id)
    print response.id


def _ls(client, arg):
    if arg.ls_dir:
        response = client.folders.get(arg.id[0])
        for sub_folder in response.subFolders:
            print '%s/ - %s' % (sub_folder.name, sub_folder.id)
        for inner_file in response.files:
            print '%s - %s' % (inner_file.name, inner_file.id)
    else:
        response = client.files.get(arg.id[0])
        print '%s\r%d\t%s' % (response.name, response.size, response.creationDate)


def _rm(client, arg):
    if arg.rmdir:
        client.folders.delete(arg.id[0])
    else:
        client.files.delete(arg.id[0])


def _freespace(client, arg):
    response = client.freespace.get()
    print response.freespace


def _upload(client, arg):
    client.files.upload(arg.file_path, arg.parent_id)


def _download(client, arg):
    response = client.freespace.get(arg.file_id)
    client.files.download(response.downloadUrl, os.path.join(arg.download_path, response.name))


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-debug', action='store_true', dest='loglevel', default=False, help='Set default log to DEBUG')

    subparsers = parser.add_subparsers(help='commands', dest='action')
    # mkdir
    mkdir_parser = subparsers.add_parser('mkdir', help='Create a directory')
    mkdir_parser.add_argument('-name', action='store', dest='name', type=str, required=True, help='The folder name')
    mkdir_parser.add_argument('-parent_id', action='store', dest='parent_id', type=str, default=None,
                              help='The parent folder id (default is root)')
    # rm
    rm_parser = subparsers.add_parser('rm', help='Remove a file/folder')
    rm_parser.add_argument('-r', action='store_true', dest='rm_dir', default=False, help='Flag to remove a directory')
    rm_parser.add_argument('id', metavar='id', nargs=1, help='File/Folder id')

    # ls
    ls_parser = subparsers.add_parser('ls', help='List a directory/display info of a file')
    ls_parser.add_argument('-r', action='store_true', dest='ls_dir', default=False, help='Flag to list a directory')
    ls_parser.add_argument('id', metavar='id', nargs=1, help='File/Folder id')


    # freespace
    subparsers.add_parser('freespace', help='Display freespace')
    # details
    details_parser = subparsers.add_parser('details', help='Display details of a file')
    details_parser.add_argument('-file_id', action='store', dest='file_id', type=str, required=True,
                                help='The file id')

    # upload
    upload_parser = subparsers.add_parser('upload', help='Upload a file')
    upload_parser.add_argument('-file_path', action='store', dest='file_path', type=str, required=True,
                               help='The file path')
    upload_parser.add_argument('-parent_id', action='store', dest='parent_id', type=str, default=None,
                               help='The parent folder id (default is root)')

    # download
    download_parser = subparsers.add_parser('download', help='Download a file')
    download_parser.add_argument('-download_path', action='store', dest='download_path', type=str, required=True,
                                 help='The directory where the file will be downloaded')
    download_parser.add_argument('-file_id', action='store', dest='file_id', type=str, required=True,
                                 help='The file id')

    # commands
    subparsers.add_parser('shell', help='Start interactive commands')

    arguments = parser.parse_args()
    if arguments.loglevel:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    with load_client() as client:
        # this distinction to tells I use th import
        if arguments.action == 'shell':
            shell(client)
        else:
            # all functions are prefixed with underscore
            globals()['_%s' % arguments.action](client, arguments)


if __name__ == "__main__":
    main()
