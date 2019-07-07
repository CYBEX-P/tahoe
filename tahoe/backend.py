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
    def insert_one(self, *args, **kwargs): self.coll.insert_one(*args, **kwargs)
    def insert_many(self, *args, **kwargs): self.coll.insert_many(*args, **kwargs)
    
    def find(self, query, projection={"_id" : 0}): return self.coll.find(query, projection)
    def find_one(self, query, projection={"_id" : 0}): return self.coll.find_one(query, projection)

    def update_one(self, query, update, *args, **kwargs): self.coll.update_one(query, update, *args, **kwargs)

    def update_many(self, query, update, *args, **kwargs): self.coll.update_many(query, update, *args, **kwargs)
    
    def add_ref_uuid(self, inst_uuid, ref_array, ref_uuid):
        self.coll.update_one( {"uuid" : inst_uuid}, {"$addToSet": {ref_array: ref_uuid}})

    def get_instance(self, query, projection={"_id" : 0}):
        query = {"$and": query}
        return self.coll.find_one(query, projection)
    

def get_backend():
    mongo_url = os.getenv("_MONGO_URL")
    analytics_db = os.getenv("_ANALYTICS_DB", "tahoe_db")
    analytics_coll = os.getenv("_ANALYTICS_COLL", "instances")

    client = MongoClient(mongo_url)
    analytics_db = client.get_database(analytics_db)
    analytics_backend = MongoBackend(analytics_db)
    return analytics_backend
