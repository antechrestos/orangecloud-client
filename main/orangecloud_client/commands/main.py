#!/usr/bin/python2.7
import logging
import sys
from argparse import ArgumentParser

from orangecloud_client.commands.command_client import load_client
from orangecloud_client.commands.shell import launch_interactive_shell


def main():
    parser = ArgumentParser(add_help=True)
    parser.add_argument('-debug', action='store_true', dest='loglevel', default=False, help='Set default log to DEBUG')
    parser.add_argument('-start_directory', action='store', dest='start_directory', default=None,
                        help='Set the start directory')
    parser.add_argument('command', metavar='word', nargs='*', help='command [arg1] ... (if none will start shell)')
    program_arguments = sys.argv[1:]
    idx = 0
    while idx < len(program_arguments):
        if program_arguments[idx] == '-debug':
            idx += 1
        elif program_arguments[idx] == '-start_directory':
            idx += 2
        else:
            break
    command = program_arguments[idx:]
    arguments = parser.parse_args(program_arguments[:idx])
    if arguments.loglevel:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    with load_client() as client:
        launch_interactive_shell(client,
                                 arguments.start_directory,
                                 command if len(command) > 0 else None)


if __name__ == "__main__":
    main()
