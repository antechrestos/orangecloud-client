

def parse_line(line):
    line = line.rstrip('\r\n').lstrip(' \t')
    command_line_splitted = line.split(' ')
    command_name = command_line_splitted[0]
    parameters = tuple(command_line_splitted[1:])
    return command_name, parameters

