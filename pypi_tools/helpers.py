from functools import wraps


patterns = {
    '@any_number': lambda x: int(x),
    '@any_string': lambda x: str(x),
    '@any_float': lambda x: float(x)
}


def validate_input(command, custom_error=None, additional_error=None, known_sub_commands=None):
    """ decorator that validate input after command and return error or package name """
    def validate_input_inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = args[0]
            output, sub_command = validate_input_logic(
                message, command, custom_error, additional_error, known_sub_commands)
            message.output = output
            message.sub_command = sub_command
            result = func(message)
            return result
        return wrapper
    return validate_input_inner


def validate_input_logic(message, command, custom_error=None, additional_error=None, known_sub_commands=None):
    """ validate user's input message """

    if known_sub_commands is None:
        known_sub_commands = {}

    sub_command = None

    split_message = message.text.split()

    if len(split_message) == 1:
        if not custom_error:
            output = f"To use command please provide package name after '/{command}' command. \n " \
                     f"Example: '/{command} aiohttp'"
        else:
            output = custom_error
        if additional_error:
            output += additional_error
    else:
        output = split_message[1].replace('_', '-')
        if ':' in message.text:
            # if /search:detailed
            sub_command, package = message.text.split(':')[1].split()
            if sub_command in known_sub_commands:
                sub_command = known_sub_commands[sub_command]
            else:
                for command_name in known_sub_commands:
                    if command_name.startswith('@'):
                        if command_name in patterns:
                            sub_command = patterns[command_name](sub_command)
                if not sub_command:
                    output = f"Unknown sub-command {sub_command}. Possible sub-commands: {known_sub_commands}"
    return output, sub_command
