import sys

from orangecloud_client.commands.shell.commands import cd, ls, mkdir, upload, rm, download, freespace, reload_cache, \
    pwd, get_path
from orangecloud_client.commands.shell.parser import parse_line, InvalidSynthax


def launch_interactive_shell(client):
    ask_exit = False
    reload_cache(client)
    commands_mapping = dict(cd=cd, ls=ls, mkdir=mkdir, upload=upload, download=download, freespace=freespace,
                            reload_cache=reload_cache, pwd=pwd, rm=rm)
    sys.stdout.write('''
Welcome to the orangecloud shell. Type \'help\' to know all the available commands
''')

    while not ask_exit:
        sys.stdout.write('%s >' % get_path())
        try:
            command_name, parameters = parse_line(sys.stdin.readline())
            if command_name == 'exit':
                break
            elif command_name == 'help':
                sys.stderr.write('Available commands: %s\n' % ', '.join(commands_mapping.keys()))
            else:
                command = commands_mapping.get(command_name)
                if command is None:
                    sys.stderr.write('Command not found: %s\n' % command_name)
                else:
                    command(client, *parameters)
        except InvalidSynthax, ex:
            sys.stderr.write('%s\n', ex.message)
