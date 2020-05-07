"""Database Utilities ( :
MongoDB, managed programmatically with pymongo"""
# External Imports
import pymongo
# No Internal Imports

DB = pymongo.MongoClient('localhost', 27017).inspire_bot_db

def add_document(collection: str, data: dict) -> None:
    """Adds a document to the specified collection
    'collection' is the collection name to insert the document into
    'data' is a dictionary containing the data to add to the collection
    returns nothing"""
    if not isinstance(collection, str):
        raise TypeError('Parameter "collection" must be a string')
    if not isinstance(data, dict):
        raise TypeError('Parameter "data" must be a dictionary')
    DB[collection].insert_one(data)


def find_random_document(collection) -> dict:
    """Finds a random document from the user-defined collection
    returns the document"""
    document = list(DB[collection].aggregate([{'$sample': {'size': 1}}]))[0]
    if not isinstance(document, dict):
        return {'text': 'There are no documents stored, try storing some : )'}
    return document
