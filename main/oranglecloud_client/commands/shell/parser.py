def parse_line(line):
    line = line.rstrip('\r\n').lstrip(' \t').replace('\t', ' ')
    idx_first_space = line.find(' ')
    if idx_first_space == -1:
        return line, ()
    else:
        command_name = line[:idx_first_space]
        parameters = line[idx_first_space:].lstrip(' ')
        return command_name, _split_parameters(parameters)


def _split_parameters(parameters):
    result = []
    escape_character = '\\'
    split_character = ' '
    previous_escape = False
    current_parameter = []
    for character in parameters:
        if previous_escape or (character != escape_character and character != split_character):
            current_parameter.append(character)
            previous_escape = False
        elif character == escape_character:
            previous_escape = True
        elif len(current_parameter) > 0:
            result.append(''.join(current_parameter))
            current_parameter = []
    if len(current_parameter) > 0:
        result.append(''.join(current_parameter))
    print '_split_parameters - %s => %s' % (parameters, str(result))
    return tuple(result)


