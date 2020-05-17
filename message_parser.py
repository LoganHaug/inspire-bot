"""Message Parser
Parses discord messages and executes commands based on message text"""
# External Imports
import time
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

def add_moderator(user_id: int) -> str:
    """Gives moderator privledges to a user
    returns a message for the bot to say"""
    user_document = database_utils.find_document('users', query={'user-id': user_id})
    database_utils.update_document('users', user_document, {'is-moderator': True})
    return COMMAND_SCHEMA['bot-messages']['made-user-mod']


def remove_moderator(user_id: int) -> str:
    """Revokes moderator privledges from a user
    returns a message for the bot to say"""
    user_document = database_utils.find_document('users', query={'user-id': user_id})
    database_utils.update_document('users', user_document, {'is-moderator': False})
    return COMMAND_SCHEMA['bot-messages']['removed-user-mod']


def has_privledges(user_id: int) -> int:
    """Checks if a user is an admin or moderator
    'user_id' is the discord user id number of the user to check
    returns 2 if user is admin, 1 if user is moderator, and 0 otherwise"""
    user_document = database_utils.find_document('users', query={'user-id': user_id})
    if user_document is None:
        return 0
    if user_document['is-admin'] is True:
        return 2
    if user_document['is-moderator'] is True:
        return 1
    return 0


def add_quote(message_text: list, user_id: int) -> str:
    """Adds a quote to the quotes collection
    'message_text' is a list of strings that represent the message text split
    by spaces
    'user_id' is the discord user id number of the user who issued the command
    returns message text the bot should send to the issued command channel"""
    if has_privledges(user_id) in [1, 2]:
        if len(message_text) < 3:
            return COMMAND_SCHEMA['bot-messages']['failed-quote']
        # list of message_text: command call, quote text, quote author
        document = {'quote-text': message_text[1],
                    'quote-author': message_text[2],
                    'time-quoted': time.time(), 'inserted_by': user_id}
        if database_utils.find_document('quotes', {'quote-text': message_text[1]}) is not None:
            return COMMAND_SCHEMA['bot-messages']['already-quoted']
        database_utils.add_document('quotes', document)
        return COMMAND_SCHEMA['bot-messages']['successful-quote-insert']
    return COMMAND_SCHEMA['bot-messages']['no-privledges']


def find_random_quote() -> str:
    """Returns a random quote from the quotes collection"""
    document = database_utils.find_random_document('quotes')
    return f'```"{document["quote-text"]}"\n   -{document["quote-author"]}```'


def parse_message(message_text: str, user_id: int) -> str:
    """Parses a user message, and executes commands based on message text
    'message_text' is the message text to parse
    'author_id' is the discord id of the user that sent the message
    returns a message for the bot to say in response to a command"""
    database_utils.validate_arguments({'message_text': [message_text, str],
                                       'user-id': [user_id, int]})
    if not message_text.startswith(COMMAND_SCHEMA['command-prefix']):
        return None
    message_text = shlex.split(message_text)
    message_text[0] = message_text[0][1:]
    if message_text[0] in COMMANDLIST:
        user_document = database_utils.find_document('users', query={'user-id': user_id})
        if user_document is None:
            user_document = {'user-id': user_id,
                             'is-admin': False,
                             'is-moderator': False,
                             'num-commands': 1}
            database_utils.add_document('users', user_document)
        else:

            database_utils.update_document('users', user_document,
                                           {'num-commands': user_document['num-commands'] + 1})
        user_command = COMMANDLIST[message_text[0]]
        function = user_command + '('
        if COMMANDS[user_command]['parameters'] is None:
            function += ')'
            return eval(function)
        num_arguments = 0
        for argument in COMMANDS[user_command]['parameters']:
            if num_arguments != len(COMMANDS[user_command]['parameters']) - 1:
                function += argument + ', '
            else:
                function += argument + ')'
            num_arguments += 1
        return eval(function)
    return COMMAND_SCHEMA['bot-messages']['no-command']
