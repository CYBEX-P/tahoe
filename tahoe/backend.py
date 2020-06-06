from pymongo import MongoClient
from pymongo.collection import Collection
import os

class Backend():
    def __init__(self, *args, **kwargs): return None
    def aggregate(self, *args, **kwargs): return None
    def find(self, *args, **kwargs): return []
    def find_one(self, *args, **kwargs): return []
    def insert_one(self, *args, **kwargs): return None
    def update_one(self, *args, **kwargs): return None
    def update_many(self, *args, **kwargs): return None
    

class NoBackend(Backend):
    def __init__(self): super().__init__()

class MongoBackend(Collection, Backend):
    def __init__(self, database, name="instances", create=False, **kwargs):
        self.coll = database.get_collection(name)
        Backend.__init__(self)
        Collection.__init__(self, database, name,  create, **kwargs)

    def find(self, *args, **kwargs):
        r = self.coll.find(*args, **kwargs)
        if not r: r = []
        return r

    def find_one(self, *args, **kwargs):
        r = self.coll.find_one(*args, **kwargs)
        if not r: r = []
        return r


def get_backend():
    mongo_url = os.getenv("_MONGO_URL")
    db = os.getenv("_TAHOE_DB", "tahoe_db")
    coll = os.getenv("_TAHOE_COLL", "instances")

    client = MongoClient(mongo_url)
    db = client.get_database(db)
    backend = MongoBackend(db, name=coll)
    return backend
    
    
def get_report_db():
    mongo_url = os.getenv("CYBEXP_API_MONGO_URL")
    report_db = os.getenv("CYBEXP_API_REPORT_DB", "report_db")

    client = MongoClient(mongo_url)
    report_db = client.get_database(report_db)
    
    return report_db
    
def get_query_backend():
    report_db = get_report_db()
    
    if 'query' not in report_db.list_collection_names():
      report_db.create_collection('query', capped=True, size=9999999, max=999)

    query_backend = MongoBackend(report_db, name='query')
    
    return query_backend

    
def get_report_backend():
    report_db = get_report_db()
    report_backend = MongoBackend(report_db, name='report')
    
    return report_backend