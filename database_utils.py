"""Database Utilities ( :
MongoDB, managed programmatically with pymongo"""
# External Imports
import pymongo
# No Internal Imports

DB = pymongo.MongoClient('localhost', 27017).inspire_bot_db


def validate_arguments(arguments: dict) -> None:
    """Validates the types of arguements, raises errors if invalid
    'arguments' is a dictionary where the key is the name of the argument, the
    value is a list where the first indice is the actual argument, and the
    second is the type the argument should be"""
    if not isinstance(arguments, dict):
        raise TypeError('Argument "arguments" should be a dict')
    for argument in arguments:
        if not isinstance(arguments[argument][0], arguments[argument][1]):
            raise TypeError(f'Argument {argument} should be a {arguments[argument][1]}')


def add_document(collection: str, document: dict) -> None:
    """Adds a document to the specified collection
    'collection' is the collection name to insert the document into
    'document' is a dictionary containing the data to add to the collection
    returns nothing"""
    validate_arguments({'collection': [collection, str],
                        'document': [document, dict]})
    DB[collection].insert_one(document)


def find_random_document(collection: str) -> dict:
    """Finds a random document from the user-defined collection
    returns the document"""
    validate_arguments({'collection': [collection, str]})
    document = list(DB[collection].aggregate([{'$sample': {'size': 1}}]))
    if document != []:
        return document[0]
    return {'text': 'There are no documents stored, try storing some : )'}


def find_document(collection: str, query: dict = None, regex: list = None) -> dict:
    """Finds a document that matches the query or regex within the collection
    'collection' is the collection to search
    'query' is a key value pair within the desired document
    'regex' is a list where item 0 is the field, and item 1 is the regex
    Note that 'regex' should the following format: ['field', 'regex']
    """
    if query is not None:
        return DB[collection].find_one(query)
    if regex is not None:
        return DB[collection].find_one({regex[0]: {'$regex': regex[1]}})
    raise Exception('Didnt specify a query or a regex')


def update_document(collection: str, query: dict, data: dict) -> None:
    """Appends or overwrites documents
    'collection' is the collection to search
    'query' is a key value pair to search with
    'data' is the data to update the document with
    Returns nothing"""
    validate_arguments({'collection': [collection, str],
                        'query': [query, dict],
                        'data': [data, dict]})
    new_document = find_document(collection, query=query)
    if new_document is None:
        raise Exception('Didnt find a document to update')
    DB[collection].delete_one(query)
    for key in data:
        new_document[key] = data[key]
    add_document(collection, new_document)
