class InvalidSynthax(Exception):
    pass


def parse_line(line):
    line = line.rstrip('\r\n').strip(' \t').replace('\t', ' ')
    idx_first_space = line.find(' ')
    if idx_first_space == -1:
        return [line]
    else:
        command_name = line[:idx_first_space]
        parameters = line[idx_first_space:].lstrip(' ')
        result = [command_name]
        result.extend(_split_parameters(parameters))
        return result


def _split_parameters(parameters):
    result = []
    escape_character = '\\'
    split_character = ' '
    quoting_character = '"'
    special_characters = [escape_character, split_character, quoting_character]
    previous_escape = False
    quoting = False
    current_parameter = []
    for character in parameters:
        if previous_escape or character not in special_characters:
            current_parameter.append(character)
            previous_escape = False
        elif character == escape_character:
            previous_escape = True
        elif character == quoting_character:
            quoting = not quoting
        elif character == split_character:
            if quoting:
                current_parameter.append(character)
            elif len(current_parameter) > 0:
                result.append(''.join(current_parameter))
                current_parameter = []
    if quoting:
        print 'parameters=%s' % parameters
        print 'result=%s' % result
        print 'current_parameter=%s' % current_parameter
        raise InvalidSynthax('Unfinished quoting: %s' % parameters)
    if len(current_parameter) > 0:
        result.append(''.join(current_parameter))
    return result
