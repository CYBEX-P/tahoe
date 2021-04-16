"""
A TAHOE backend stores TAHOE data.

NoBackend is for data sharing only. It does not deduplicate data.
MongoBackend or MemoryBackend deduplicates data. Use them for storing.
"""

import os
import pdb

import mongomock
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection


if __name__ != 'tahoe.backend':
    import sys
    sys.path = ['..'] + sys.path
    del sys
import tahoe


_P = {"_id":0} 
"""Default projection for MongoDB queries."""


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

    NoBackend does not implement the methods `find_one, insert one`
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


class _MongoBackendBase(Backend):    

    def find_attribute(self, sub_type, data, p=_P, parse=False):
        """
        Find attribute by `sub_type` and `data`.

        Parameters
        ----------
        sub_type : str
            Type of the `Attribute`, e.g. ``ipv4, email-addr``.
        data : int or float or str or bool or None
            Data of the Attribute. e.g. ``1.1.1.1``. JSON has only 4
            basic types: `number (float), str, bool, None`. However,
            python and BSON (MongoDB format) can also store `int`.
        p : dict
            MongoDB projection
        parse : bool
            If True the dict is parsed into tahoe.Attribute.

        Returns
        -------
        None
            If attribute does not exist.
        dict
            If parse=False.
        tahoe.Attribute
            If parse=True.
        """

        thisatt = tahoe.Attribute(sub_type, data, _backend=tahoe.NoBackend())
        _hash = thisatt._hash

        r = self.find_one({"itype": "attribute", "_hash": thisatt._hash}, p)       
        if parse:
            r = tahoe.parse(r, backend=self, validate=False)
        return r
        
    

class MongoBackend(pymongo.collection.Collection, _MongoBackendBase):
   """Inherits everything from pymongo.collection.Collection."""
   
   def __init__(self, mongo_url=None, dbname="tahoe_db",
                collname="instance", create=False, **kwargs):
       client = MongoClient(mongo_url, connect=False)
       db = client.get_database(dbname)
       _MongoBackendBase.__init__(self)
       Collection.__init__(self, db, collname,  create, **kwargs)

   def __repr__(self):
       host, port = self.database.client.address
       dbname = self.database.name
       collname = self.name
       return f"MongoBackend('mongodb://{host}:{port}', " \
            f"'{dbname}', '{collname}')"


class MockMongoBackend(mongomock.Collection, _MongoBackendBase):
   def __init__(self, mongo_url=None, dbname="tahoe_db",
                collname="instance", create=False, **kwargs):
       client = mongomock.MongoClient(mongo_url)
       db = client.get_database(dbname)
       _MongoBackendBase.__init__(self)
       mongomock.Collection.__init__(self, db, collname, db._store)

   def __repr__(self):
       host, port = self.database.client.address
       dbname = self.database.name
       collname = self.name
       return f"MockMongoBackend('mongodb://{host}:{port}', " \
            f"'{dbname}', '{collname}')"



    
    
    
    
    
    
    
    
    
    
    
    
    
    
