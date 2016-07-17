#!/usr/bin/python2.7
import os
import logging
import argparse
from oranglecloud_client.commands.interactive import shell
from oranglecloud_client.commands.shell_client import load_client


def mkdir(client, arg):
    response = client.folders.create(arg.name, arg.parent_id)
    print response.id


def rmdir(client, arg):
    client.folders.delete(arg.folder_id)


def ls(client, arg):
    response = client.folders.get(arg.folder_id)
    for sub_folder in response.subFolders:
        print '%s/ - %s' % (sub_folder.name, sub_folder.id)
    for inner_file in response.files:
        print '%s - %s' % (inner_file.name, inner_file.id)


def freespace(client, arg):
    response = client.freespace.get()
    print response.freespace


def details(client, arg):
    response = client.files.get(arg.file_id)
    print '%s\r%d\t%s' % (response.name, response.size, response.creationDate)


def rm(client, arg):
    client.files.delete(arg.file_id)


def upload(client, arg):
    client.files.upload(arg.file_path, arg.parent_id)


def download(client, arg):
    response = client.freespace.get(arg.file_id)
    client.files.download(response.downloadUrl, os.path.join(arg.download_path, response.name))


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(add_help=True)
    subparsers = parser.add_subparsers(help='commands', dest='action')
    # mkdir
    mkdir_parser = subparsers.add_parser('mkdir', help='Create a directory')
    mkdir_parser.add_argument('-name', action='store', dest='name', type=str, required=True, help='The folder name')
    mkdir_parser.add_argument('-parent_id', action='store', dest='parent_id', type=str, default=None,
                              help='The parent folder id (default is root)')
    # rmdir
    rmdir_parser = subparsers.add_parser('rmdir', help='Remove a directory')
    rmdir_parser.add_argument('-folder_id', action='store', dest='folder_id', type=str, required=True,
                              help='The folder id')
    # ls
    ls_parser = subparsers.add_parser('ls', help='List a directory')
    ls_parser.add_argument('-folder_id', action='store', dest='folder_id', type=str, default=None,
                           help='The folder id (default is root)')
    # freespace
    subparsers.add_parser('freespace', help='Display freespace')
    # details
    details_parser = subparsers.add_parser('details', help='Display details of a file')
    details_parser.add_argument('-file_id', action='store', dest='file_id', type=str, required=True,
                                help='The file id')
    # rm
    rm_parser = subparsers.add_parser('rm', help='Remove a file')
    rm_parser.add_argument('-file_id', action='store', dest='file_id', type=str, required=True,
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
    subparsers.add_parser('commands', help='Start interactive commands')

    arguments = parser.parse_args()
    with load_client() as client:
        globals()[arguments.action](client, arguments)


if __name__ == "__main__":
    main()
