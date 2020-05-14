"""Message Parser
Parses discord messages and executes commands based on message text"""
# External Imports
import re
import shlex
import yaml
# Internal Imports
import database_utils

COMMAND_SCHEMA_FILEPATH = 'commands.yml'

with open(COMMAND_SCHEMA_FILEPATH, 'r') as command_schema:
    COMMAND_SCHEMA = yaml.load(command_schema, Loader=yaml.SafeLoader)
    COMMANDS = COMMAND_SCHEMA['commands']
# Stores all possible command alias' as key, and the original command as value
COMMANDLIST = {}
# Generates all alias' for commands
for command in COMMAND_SCHEMA['commands']:
    COMMANDLIST[command] = command
    for alias in COMMANDS[command]['alias']:
        COMMANDLIST[alias] = command


def parse_message(message) -> None:
    """Parses a user message, and executes commands based on message text
    'message' is the message object of the user's message to parse"""
    if not isinstance(message, str):
        raise TypeError('argument "message" is not a string')
    if not message.startswith(COMMAND_SCHEMA['command-prefix']):
        return None
    message = shlex.split(message)
    message[0] = message[0][1:-1]
    if message[0] in COMMMAND_LIST:
        pass
