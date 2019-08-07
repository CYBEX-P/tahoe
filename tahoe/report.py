import os, collections, time
from pymongo.collection import Collection

if __name__ == "__main__": from instance import *
else: from .instance import *

if __name__ == "__main__":
    config = { 
            "mongo_url" : "mongodb://cybexp_user:CybExP_777@134.197.21.231:27017/?authSource=admin",
            "analytics_db" : "tahoe_db",
            "analytics_coll" : "instances"
        }
    os.environ["_MONGO_URL"] = config.pop("mongo_url")
    os.environ["_TAHOE_DB"] = config.pop("analytics_db", "tahoe_db")
    os.environ["_TAHOE_COLL"] = config.pop("analytics_coll", "instances")


_LIM = 10000

class Report():
    backend = get_backend() if os.getenv("_MONGO_URL") else NoBackend()
    
    def __init__(self, **kwargs):
        if type(self.backend) == NoBackend and os.getenv("_MONGO_URL"): self.backend = get_backend()
        if kwargs.get('backend'): self.backend = kwargs.get('backend') 
        if not isinstance(self.backend, Backend):
            raise TypeError('backend cannot be of type ' + str(type(backend)))

    def attribute_types(self, count=True):
        if not count:
            l = self.backend.distinct("att_type", {"itype":"attribute"})
            return sorted(l)
        
        pipeline = [{ "$match" : { "itype" : "attribute" } },
                    { "$group" : { "_id" : "$att_type", "count" : {"$sum" : 1}}}]
        r = self.backend.aggregate(pipeline)
        d = {i["_id"] : i["count"] for i in r}
        return dict(sorted(d.items()))

    def attribute_values(self, att_type, count=False):
        q = {"itype":"attribute","att_type":att_type}
        p = {"value":1, "uuid":1}
        r = self.backend.find(q,p)
        
        if not count: return sorted([i["value"] for i in r])

        d = {}
        for i in r:
            q = {"itype":"event", "_ref":i["uuid"]}
            d[i["value"]] = self.backend.count_documents(q, limit=_LIM)
        return dict(sorted(d.items()))        
    
    def event_types(self, count=True):
        if not count:
            l = self.backend.distinct("event_type", {"itype":"event"})
            return sorted(l)
        
        pipeline = [{ "$match" : { "itype" : "event" } },
                    { "$group" : { "_id" : "$event_type", "count" : {"$sum" : 1}}}]
        r = self.backend.aggregate(pipeline)
        d = {i["_id"] : i["count"] for i in r}
        return dict(sorted(d.items()))

    def events(self, limit, skip):
        return self.backend.find({"itype":"event"}, limit=limit, skip=skip*limit)
    































##
##class Event(OES, Event):
##    def features(self):
##        features = self.json_dot(self.data)
##
##class Attribute(Attribute):   
##    def count(self, start=0, end=None):
##        if not end: end = time.time()
##        return self.backend.count({"itype":"event", "_ref":self.uuid, "timestamp":{"$gte":start, "$lte":end}})
##
##    def organizations(self):
##        pass
##
##
##
####class Report():
####    backend = get_backend() if os.getenv("_MONGO_URL") else NoBackend()
####    
####    def __init__(self, start=0, end=None, *args, **kwargs):
####        if type(self.backend) == NoBackend and os.getenv("_MONGO_URL"):
####            self.backend = get_backend()
####        if kwargs.get('backend'): self.backend = kwargs.get('backend') 
####        if not isinstance(self.backend, Backend):
####            raise TypeError('backend cannot be of type ' + str(type(backend)))
####
####        if not end: end = time.time()
####        self.q = {"itype":"event", "timestamp":{"$gte":start, "$lte":end}}}
####        
####
####class AttributeTypes(Report):
####    def __init__(self, count=True, *args, **kwargs):
####        super().__init__(*args, **kwargs)
####        b = self.backend
####
####        self.q[]
####
####    def run(self):
####        self.backend.find(q)
####    
##
##

##
##def parse(instance, backend=NoBackend(), validate=True):
##    backend = get_backend() if os.getenv("_MONGO_URL") else backend
##    if isinstance(instance, str): instance = json.loads(instance)
##    instance.pop("_id", None)
##    t = Attribute('text', 'mock')
##    t.__dict__, t.backend = instance, backend
##    t.__class__ = {'attribute':Attribute, 'event':Event, 'object':Object,
##                   'raw':Raw, 'session':Session}.get(instance['itype'])
####    if validate: t.validate()
##    return t
##
##
####    
####
####class Attribute(Attribute):   
####    def count(self, start=0, end=None):
####        if not end: end = time.time()
####        return self.backend.count({"itype":"event", "_ref":self.uuid, "timestamp":{"$gte":start, "$lte":end}})
####
####    def organizations(self):
####        pass
####        
####
####    
####
####    
####
####
##from pprint import pprint
##r = Report()
##res = r.attribute_types()
##print('\n', res)
##res = r.attribute_values("country_name")
##print('\n')
##pprint(res)
##res = r.attribute_values("country_name",count=True)
##print('\n')
##pprint(res)
