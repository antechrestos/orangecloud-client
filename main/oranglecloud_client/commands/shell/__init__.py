import sys

from oranglecloud_client.commands.shell.commands import cd, ls, mkdir, upload, download, freespace, reload_cache, pwd, \
    get_path
from oranglecloud_client.commands.shell.parser import parse_line


def launch_interactive_shell(client):
    ask_exit = False
    reload_cache(client)
    commands_mapping = dict(cd=cd, ls=ls, mkdir=mkdir, upload=upload, download=download, freespace=freespace,
                            reload_cache=reload_cache, pwd=pwd)
    sys.stdout.write('''
Welcome to the orangecloud shell. Type \'help\' to know all the available commands
''')

    while not ask_exit:
        sys.stdout.write('%s >' % get_path())
        command_name, parameters = parse_line(sys.stdin.readline())
        if command_name == 'exit':
            break
        elif command_name == 'help':
            sys.stderr.write('Available commands: %s' % ', '.join(commands_mapping.keys()))
        else:
            command = commands_mapping.get(command_name)
            if command is None:
                sys.stderr.write('Command not found: %s' % command_name)
            else:
                command(client, *parameters)