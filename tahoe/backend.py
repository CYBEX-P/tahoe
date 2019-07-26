from pymongo import MongoClient
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

class MongoBackend(Backend):
    def __init__(self, db): self.coll = db.instances
    def aggregate(self, *args, **kwargs): return self.coll.aggregate(*args, **kwargs)
    def count(self, *args, **kwargs): return self.coll.count(*args, **kwargs)
    
    def find(self, query, projection={"_id" : 0}, *args, **kwargs):
        r = self.coll.find(query, projection, *args, **kwargs)
        if not r: pdb.set_trace()
        return {} if not r else r
    
    def find_one(self, query, projection={"_id" : 0}): return self.coll.find_one(query, projection)
    
    def insert_many(self, *args, **kwargs): self.coll.insert_many(*args, **kwargs)
    def insert_one(self, *args, **kwargs): self.coll.insert_one(*args, **kwargs)
    def replace_one(self, *args, **kwargs): self.coll.replace_one(*args, **kwargs)
    def update_many(self, *args, **kwargs): self.coll.update_many(*args, **kwargs)
    def update_one(self, *args, **kwargs): self.coll.update_one(*args, **kwargs)
    

def get_backend():
    mongo_url = os.getenv("_MONGO_URL")
    analytics_db = os.getenv("_ANALYTICS_DB", "tahoe_db")
    analytics_coll = os.getenv("_ANALYTICS_COLL", "instances")

    client = MongoClient(mongo_url)
    analytics_db = client.get_database(analytics_db)
    analytics_backend = MongoBackend(analytics_db)
    return analytics_backend
