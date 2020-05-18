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


def has_priviledges(user_id: int) -> int:
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


def add_user(user_id, is_admin, is_moderator) -> None:
    """Adds the user to the users collection
    'user_id' is the id of the user to add to the users collection
    returns nothing"""
    # Validate the arguments
    database_utils.validate_arguments({'user_id': [user_id, int],
                                       'is_admin': [is_admin, bool],
                                       'is_moderator': [is_moderator, bool]})
    # Assemble a new user document
    user_document = {'user-id': user_id,
                     'is-admin': is_admin,
                     'is-moderator': is_moderator,
                     'num-commands': 0}
    # Add the document to the user table
    database_utils.add_document('users', user_document)

def add_moderator(user_id: int, mentions: list) -> str:
    """Gives moderator priviledges to a user
    message_text is the message text split using shlex along spaces
    returns a message for the bot to say"""
    if has_priviledges(user_id) not in [2]:
        return COMMAND_SCHEMA['bot-messages']['no-priviledges']
    if mentions == []:
        return COMMAND_SCHEMA['bot-messages']['make-mod-fail']
    # Try to execute this code
    try:
        # Iterate over the mentions in the message
        for mention in mentions:
            # Obtain the user document
            user_document = database_utils.find_document('users', query={'user-id': mention.id})
            # If no user document was found add it and make the user a moderator
            if user_document is None:
                add_user(mention.id, False, True)
            # Otherwise update the users moderator status
            else:
                database_utils.update_document('users', user_document, {'is-moderator': True})
        return COMMAND_SCHEMA['bot-messages']['made-user-mod']
    # If it fails, tell the user it failed
    except:
        return COMMAND_SCHEMA['bot-messages']['make-mod-fail']


def remove_moderator(user_id: int, mentions: list) -> str:
    """Revokes moderator priviledges from a user
    'mentions' is the list of user objects that were mention in the message
    returns a message for the bot to say"""
    if has_priviledges(user_id) not in [2]:
        return COMMAND_SCHEMA['bot-messages']['no-priviledges']
    if mentions == []:
        return COMMAND_SCHEMA['bot-messages']['remove-mod-fail']
    # Try to execute this code
    try:
        # Iterate over the mentions in the message
        for mention in mentions:
            # Find the user document
            user_document = database_utils.find_document('users', query={'user-id': mention.id})
            # If the user document cannot be found add it
            if user_document is None:
                add_user(mention.id, False, False)
            # Otherwise remove the moderator status from the user
            else:
                database_utils.update_document('users', user_document, {'is-moderator': False})
        # Tell the user it removed the moderator status
        return COMMAND_SCHEMA['bot-messages']['removed-user-mod']
    # If the code fails, tell the user it failed
    except:
        return COMMAND_SCHEMA['bot-messages']['remove-mod-fail']


def add_quote(message_text: list, user_id: int) -> str:
    """Adds a quote to the quotes collection
    'message_text' is a list of strings that represent the message text split
    by spaces
    'user_id' is the discord user id number of the user who issued the command
    returns message text the bot should send to the issued command channel"""
    # Checks if the user is an admin or moderator
    if has_priviledges(user_id) in [1, 2]:
        # If the length of message text is less than 3, arguments are missing
        if len(message_text) < 3:
            return COMMAND_SCHEMA['bot-messages']['failed-quote']
        if len(message_text) > 3:
            return COMMAND_SCHEMA['bot-messages']['too-many-parameters']
        # list of message_text: command call, quote text, quote author
        document = {'quote-text': message_text[1],
                    'quote-author': message_text[2],
                    'time-quoted': time.time(), 'inserted_by': user_id}
        # If the quote already exists, tell the user its already quoted
        if database_utils.find_document('quotes', {'quote-text': message_text[1]}) is not None:
            return COMMAND_SCHEMA['bot-messages']['already-quoted']
        # Add the qutoe document
        database_utils.add_document('quotes', document)
        return COMMAND_SCHEMA['bot-messages']['successful-quote-insert']
    return COMMAND_SCHEMA['bot-messages']['no-priviledges']


def find_random_quote() -> str:
    """Returns a random quote from the quotes collection"""
    document = database_utils.find_random_document('quotes')
    return f'```"{document["quote-text"]}"\n   -{document["quote-author"]}```'

def help(message_text: list):
    """Displays the help message associated with the command
    'message_text' is the message text split using shlex along spaces"""
    database_utils.validate_arguments({'message_text': [message_text, list]})
    if len(message_text) == 1:
        user_command = 'help'
    else:
        if message_text[1] not in COMMANDLIST:
            user_command = 'help'
        else:
            user_command = COMMANDLIST[message_text[1]]
    alias = '\nalias: '
    for alas in COMMANDS[user_command]['alias']:
        alias += alas + ' '
    usage = f'\nusage: {COMMAND_SCHEMA["command-prefix"]}' + COMMANDS[user_command]['usage']
    description = COMMANDS[user_command]['description']
    available_commands = '\nAvailable Commands: ' + ''.join([command + ' ' for command in COMMANDS])
    requires_mod = '\nRequires Moderator Status?: ' + str(COMMANDS[user_command]['requires_mod'])
    requires_admin= '\nRequires Administrator Status?: ' + str(COMMANDS[user_command]['requires_admin'])
    return '```' + description + usage + alias + available_commands + requires_mod + requires_admin + '```'

def parse_message(message_text: str, user_id: int, mentions: list) -> str:
    """Parses a user message, and executes commands based on message text
    'message_text' is the message text to parse
    'author_id' is the discord id of the user that sent the message
    'mentions' is the list of member objects that were mentioned in the message
    returns a message for the bot to say in response to a command"""
    # Validates that the arguments are the correct type
    database_utils.validate_arguments({'message_text': [message_text, str],
                                       'user-id': [user_id, int],
                                       'mentions': [mentions, list]})
    # If the message doesn't start with the start character, do nothing
    if not message_text.startswith(COMMAND_SCHEMA['command-prefix']):
        return None
    # Split the message text along spaces, but not within quotations
    message_text = shlex.split(message_text)
    # Remove the command prefix from the message text
    message_text[0] = message_text[0][len(COMMAND_SCHEMA['command-prefix']):]
    # If the command is a valid command
    if message_text[0] in COMMANDLIST:
        # Find the user document
        user_document = database_utils.find_document('users', query={'user-id': user_id})
        # Add the user to the users collection if they aren't in there
        if user_document is None:
            add_user(user_id, False, False)
        # Otherwise increment their number of commands by 1
        else:
            database_utils.update_document('users', user_document,
                                           {'num-commands': user_document['num-commands'] + 1})
        # This line accounts for alias' of the commands
        user_command = COMMANDLIST[message_text[0]]
        # Start making the command into code we can execute
        function = user_command + '('
        # If the command the user wants to run has no parameters, run it
        if COMMANDS[user_command]['parameters'] is None:
            function += ')'
            return eval(function)
        num_arguments = 0
        # Iterate through all of the parameters of the given command
        for argument in COMMANDS[user_command]['parameters']:
            # If the current parameter isn't the last one, use commmas
            if num_arguments != len(COMMANDS[user_command]['parameters']) - 1:
                function += argument + ', '
            # Otherwise close up the function call
            else:
                function += argument + ')'
            num_arguments += 1
        # Run the function
        return eval(function)
    # If the command doesn't execute, tell the user it didn't work
    return COMMAND_SCHEMA['bot-messages']['no-command']
