"""
A TAHOE backend stores TAHOE data.

NoBackend is for data sharing only. It does not deduplicate data.
MongoBackend or MemoryBackend deduplicates data. Use them for storing.
"""

import os
import pdb

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
import mongomock


class Backend:
    """Base class for TAHOE Backends"""

    def __repr__(self):
        return 'Backend()'
    
    def aggregate(self, *args, **kwargs):
        return NotImplementedError
    
    def find(self, *args, **kwargs):
        return NotImplementedError
    
    def find_one(self, *args, **kwargs):
        return NotImplementedError
    
    def insert_one(self, *args, **kwargs):
        return NotImplementedError
    
    def update_one(self, *args, **kwargs):
        return NotImplementedError
    
    def update_many(self, *args, **kwargs):
        return NotImplementedError

    
class NoBackend(Backend):
    """
    NoBackend is for data sharing only, not storing data.

    NoBackend does not implement the functions ``find_one, insert one``
    etc. So,

    1. You cannot lookup the data.
    2. The data are lost when you exit Python.
    
    """
    
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return 'NoBackend()'

    def aggregate(self, *args, **kwargs):
        return None
    
    def find(self, *args, **kwargs):
        return []
    
    def find_one(self, *args, **kwargs):
        return []
    
    def insert_one(self, *args, **kwargs):
        return None
    
    def update_one(self, *args, **kwargs):
        return None
    
    def update_many(self, *args, **kwargs):
        return None


# class MongoBackend(pymongo.collection.Collection,
#                    mongomock.collection.Collection, Backend):
#     """
#     Inherits methods from pymongo.collection.Collection.
#     """
    
#     def __init__(self, mongo_url=None, dbname="tahoe_db",
#                  collname="instance", create=False, mock=False, **kwargs):

#         self.mock = mock
        
#         if self.mock:
#             client = mongomock.MongoClient(mongo_url, connect=False)
#             db = client.get_database(dbname)
#             # pdb.set_trace()
#             mongomock.collection.Collection.__init__(
#                 self, db, collname, db._store)
#         else:
#             client = pymongo.MongoClient(mongo_url, connect=False)
#             db = client.get_database(dbname)
#             pymongo.collection.Collection.__init__(
#                 self, db, collname,  create, **kwargs)
#         Backend.__init__(self)

#     def __repr__(self):
#         if self.mock:
#             class_name = "MongoMockBackend"
#         else:
#             class_name = "MongoBackend"
#         host, port = self.database.client.address
#         dbname = self.database.name
#         collname = self.name
        
#         return f"{class_name}('{host}:{port}', '{dbname}', '{collname}')"




    

class MongoBackend(pymongo.collection.Collection, Backend):
   """Inherits everything from pymongo.collection.Collection."""
   
   def __init__(self, mongo_url=None, dbname="tahoe_db",
                collname="instance", create=False, **kwargs):
       client = MongoClient(mongo_url, connect=False)
       db = client.get_database(dbname)
       Backend.__init__(self)
       Collection.__init__(self, db, collname,  create, **kwargs)

   def __repr__(self):
       host, port = self.database.client.address
       dbname = self.database.name
       collname = self.name
       return f"MongoBackend('{host}:{port}', '{dbname}', '{collname}')"


class MockMongoBackend(mongomock.Collection, Backend):
   def __init__(self, mongo_url=None, dbname="tahoe_db",
                collname="instance", create=False, **kwargs):
       client = mongomock.MongoClient(mongo_url)
       db = client.get_database(dbname)
       Backend.__init__(self)
       mongomock.Collection.__init__(self, db, collname, db._store)

   def __repr__(self):
       host, port = self.database.client.address
       dbname = self.database.name
       collname = self.name
       return f"MongoBackend('{host}:{port}', '{dbname}', '{collname}')"



    
    
    
    
    
    
    
    
    
    
    
    
    
    
