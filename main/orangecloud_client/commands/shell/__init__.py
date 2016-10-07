import sys
import traceback
from argparse import ArgumentParser, Action

from orangecloud_client.commands.shell.commands import cd, ls, mkdir, upload, rm, download, freespace, reload_cache, \
    pwd, get_path
from orangecloud_client.commands.shell.parser import parse_line, InvalidSynthax


class StorePositional(Action):
    ORDER_ARGS_ATTRIBUTE_NAME = 'ordered_args'

    def __call__(self, _, namespace, values, option_string=None):
        if ('%s' % StorePositional.ORDER_ARGS_ATTRIBUTE_NAME) not in namespace:
            setattr(namespace, StorePositional.ORDER_ARGS_ATTRIBUTE_NAME, [])
        previous = namespace.ordered_args
        previous.append((self.dest, values))
        setattr(namespace, StorePositional.ORDER_ARGS_ATTRIBUTE_NAME, previous)


parser = ArgumentParser(add_help=True)
parser.prog = ''
subparsers = parser.add_subparsers(help='commands', dest='action')

sub_parser = subparsers.add_parser('cd', help='Change directory')
sub_parser.add_argument('path', action=StorePositional, type=str, help='The path composed of names and ..')

sub_parser = subparsers.add_parser('mkdir', help='Create a directory')
sub_parser.add_argument('name', action=StorePositional, type=str, help='The folder name')

sub_parser = subparsers.add_parser('ls', help='List file or directory')
sub_parser.add_argument('name', action=StorePositional, metavar='name', nargs='?', type=str,
                        help='The sub-folder/file name')

sub_parser = subparsers.add_parser('rm', help='Remove a file/folder')
sub_parser.add_argument('name', action=StorePositional, help='The sub-folder/file name')

subparsers.add_parser('freespace', help='Display freespace')

sub_parser = subparsers.add_parser('upload', help='Upload a file')
sub_parser.add_argument('input_path', action=StorePositional, help='The file/folder path')

sub_parser = subparsers.add_parser('download', help='Download a file/directory')
sub_parser.add_argument('output_path', action=StorePositional, help='The output directory (must exist)')
sub_parser.add_argument('name', action=StorePositional, help='The sub-folder/file name (may be \'.\')')

subparsers.add_parser('help', help='Prints help')
subparsers.add_parser('pwd', help='Display current path')
subparsers.add_parser('reload_cache', help='Reload local cache')
subparsers.add_parser('exit', help='Exit shell')



def launch_interactive_shell(client):
    global parser
    ask_exit = False
    reload_cache(client)
    commands_mapping = dict(cd=(cd, False),
                            ls=(ls, True),
                            mkdir=(mkdir, True),
                            upload=(upload, True),
                            download=(download, True),
                            freespace=(freespace, True),
                            reload_cache=(reload_cache, True),
                            pwd=(pwd, False),
                            rm=(rm, True))
    sys.stdout.write('''
Welcome to the orangecloud shell. Type \'help\' to know all the available commands
''')

    while not ask_exit:
        sys.stdout.write('%s >' % get_path())
        try:
            namespace = parser.parse_args(parse_line(sys.stdin.readline()))
            action, arguments = namespace.action, {name: value for name, value in
                                                   getattr(namespace, StorePositional.ORDER_ARGS_ATTRIBUTE_NAME, [])}
            if action == 'exit':
                break
            elif action == 'help':
                parser.print_help()
            else:
                command, need_client = commands_mapping.get(action)
                if command is None:
                    parser.print_help()
                elif need_client:
                    command(client, **arguments)
                else:
                    command(**arguments)
        except BaseException, ex:
            type_exc = type(ex)
            if type_exc == InvalidSynthax:
                sys.stderr.write('%s\n' % ex.message)
            elif type(ex) != SystemExit:
                traceback.print_exc()
