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
