from pymongo import MongoClient
from pymongo.collection import Collection
import os

class Backend():
    def __init__(self): return None
    def find(self, *args): return None
    def find_one(self, *args): return None
    def update_one(self, *args): return None
    def update_many(self, *args): return None
    def insert_one(self, *args): return None

class NoBackend(Backend):
    def __init__(self): super().__init__()

class MongoBackend(Collection, Backend):
    def __init__(self, database, name="instances", create=False, **kwargs):
        self.coll = database.get_collection(name)
        Backend.__init__(self)
        Collection.__init__(self, database, name,  create, **kwargs)
        
##    def find(self, query, projection={"_id" : 0}, *args, **kwargs):
##        return self.coll.find(query, projection, *args, **kwargs)
    
##    def find_one(self, query, projection={"_id" : 0}): return self.coll.find_one(query, projection)


def get_backend():
    mongo_url = os.getenv("_MONGO_URL")
    db = os.getenv("_TAHOE_DB", "tahoe_db")
    coll = os.getenv("_TAHOE_COLL", "instances")

    client = MongoClient(mongo_url)
    db = client.get_database(db)
    backend = MongoBackend(db)
    return backend
