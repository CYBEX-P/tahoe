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
    

def get_mongo_backend(mongo_url, dbname='tahoe_db', collname='instances', backend_class=MongoBackend):
  client = MongoClient(mongo_url, connect=False)
  db = client.get_database(dbname)
  backend = backend_class(db, name=collname)
  return backend

def set_class_backend(class_list, backend):
  if not isinstance(class_list, list): class_list = [class_list]
  for t in class_list: t.backend=backend
    
def set_mongo_backend(class_list, mongo_url, dbname='tahoe_db', collname='instances', backend_class=MongoBackend):
  backend = get_mongo_backend(mongo_url, dbname, collname, backend_class)
  set_class_backend(class_list, backend)
  return backend
    
    
    
    
    
    
    
    
    
    
    
    
    
    