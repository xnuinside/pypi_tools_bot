import xml.etree.ElementTree as ET

patterns = {
    '@any_number': lambda x: int(x),
    '@any_string': lambda x: str(x),
    '@any_float': lambda x: float(x)
}


def parse_xml_file_with_version(_text):
    """parse f"https://pypi.org/rss/project/{package_name}/releases.xml to get list of package releases"""
    root = ET.fromstring(_text)
    versions = {}
    for channel in root:
        for item in channel:
            version = None
            date_ = None
            for elem in item:
                if elem.tag == 'title':
                    version = elem.text
                elif elem.tag == 'pubDate':
                    date_ = elem.text
            if version:
                versions[version] = date_
    return versions


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

