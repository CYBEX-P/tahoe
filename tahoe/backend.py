"""
A TAHOE backend stores TAHOE data.

NoBackend is for data sharing only. It does not deduplicate data.
MongoBackend or MemoryBackend deduplicates data. Use them for storing.
"""

import os
import pdb

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


class MemoryBackend(Backend):
    """
    Stores TAHOE instances in a Python ``list``.

    Warning
    -------
    Use for testing only. Not optimal for a lot of data,
    because ``list`` search is linear.
    """

    def __init__(self):
        raise NotImplementedError
    
        self.instance = []
        super().__init__()

    def find(self, q, p, *args, **kwargs):
        pass
    

class MongoBackend(Collection, Backend):
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




##    def find_one(self, *args, **kwargs):
##        r = self.coll.find_one(*args, **kwargs)
##        if not r: r = []
##        return r

##    def __str__(self):
##        return f'ss{1}'
    


# def get_backend(_MONGO_URL="_MONGO_URL", _DB="_TAHOE_DB", default_db="tahoe_db", _COLL="_TAHOE_COLL", default_coll="instances", backendclass=MongoBackend):

  # mongo_url = os.getenv(_MONGO_URL)
  # db = os.getenv(_DB, default_db)
  # coll = os.getenv(_COLL, default_coll)

  # client = MongoClient(mongo_url, connect=False)
  # db = client.get_database(db)
  # backend = backendclass(db, name=coll)
  # return backend
        
# def get_report_backend():
  # return get_backend("CYBEXP_API_MONGO_URL", "CYBEXP_API_REPORT_DB", "report_db", "CYBEXP_API_REPORT_COLL", "report")
    

##def get_mongo_backend(mongo_url, dbname='tahoe_db', collname='instances', backend_class=MongoBackend):
##  client = MongoClient(mongo_url, connect=False)
##  db = client.get_database(dbname)
##  backend = backend_class(db, name=collname)
##  return backend
##
##def set_class_backend(class_list, backend):
##  if not isinstance(class_list, list): class_list = [class_list]
##  for t in class_list: t.backend=backend
##    
##def set_mongo_backend(class_list, mongo_url, dbname='tahoe_db', collname='instances', backend_class=MongoBackend):
##  backend = get_mongo_backend(mongo_url, dbname, collname, backend_class)
##  set_class_backend(class_list, backend)
##  return backend
    
    
    
    
    
    
    
    
    
    
    
    
    
    
