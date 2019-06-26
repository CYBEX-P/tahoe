class Backend():
    def __init__(self): return None
    def get_instance(self, *args): return None
    def add_ref_uuid(self, *args): return None
    def insert_one(self, *args): return None

class NoBackend(Backend):
    def __init__(self): super().__init__()

class MongoBackend(Backend):
    def __init__(self, db): self.coll = db.instances

    def get_instance(self, query, projection=None):
        query = {"$and": query}
        if not projection: projection = {"_id" : 0}
        return self.coll.find_one(query, projection)

    def add_ref_uuid(self, inst_uuid, ref_array, ref_uuid):
        self.coll.update_one( {"uuid" : inst_uuid}, {"$addToSet": {ref_array: ref_uuid}})

    def insert_one(self, document): self.coll.insert_one(document)
