"""Database Utilities ( :
MongoDB, managed programmatically with pymongo"""
# External Imports
import pymongo
# No Internal Imports

DB = pymongo.MongoClient('localhost', 27017).inspire_bot_db

def add_document(collection: str, document: dict) -> None:
    """Adds a document to the specified collection
    'collection' is the collection name to insert the document into
    'document' is a dictionary containing the data to add to the collection
    returns nothing"""
    if not isinstance(collection, str):
        raise TypeError('Parameter "collection" must be a string')
    if not isinstance(document, dict):
        raise TypeError('Parameter "document" must be a dictionary')
    DB[collection].insert_one(document)


def find_random_document(collection: str) -> dict:
    """Finds a random document from the user-defined collection
    returns the document"""
    document = list(DB[collection].aggregate([{'$sample': {'size': 1}}]))
    if document != []:
        return document[0]
    return {'text': 'There are no documents stored, try storing some : )'}


def find_document(collection: str, query: dict=None, regex: list=None) -> dict:
    """Finds a document that matches the query or regex within the collection
    'collection' is the collection to search
    'query' is a key value pair within the desired document
    'regex' is a list where item 0 is the field, and item 1 is the regex
    Note that 'regex' should the following format: ['field', 'regex']
    """
    if regex is not None:
        return DB[collection].find_one({regex[0]: {'$regex': regex[1]}})
    elif query is not None:
        return DB[collection].find_one(query)
    raise Exception('Didnt specify a query or a regex')
