from jsonschema import Draft7Validator
from uuid import uuid4
from pymongo import MongoClient
from dateutil.parser import parse as parse_time
import json, pdb, os, pytz

if __name__ == "__main__": from backend import MongoBackend, NoBackend
else: from .backend import env_config_2_backend, MongoBackend, NoBackend

class Instance():
    def __init__(self, backend):
        if os.getenv("_MONGO_URL"): self.backend = env_config_2_backend()
        else: self.backend = backend
        if not isinstance(backend, Backend): raise TypeError('Backend cannot be of type ' + str(type(backend)))
        
        duplicate = self.get_duplicate()
        if duplicate: [setattr(self,k,v) for k,v in duplicate.items()]
        else:
            self.uuid = self.itype + '--' + str(uuid4())
            self.validate()
            self.backend.insert_one(self.document())

    def document(self): return {k:v for k,v in vars(self).items() if v is not None and k not in ['backend']}

    def json(self): return json.dumps(self.document())

    def __str__(self): return self.json()

    def serialize(self): pass

    def validate(self):
        print(self.itype)
        instance = self.document()
        schema_name = __file__.rsplit('\\',1)[0] + "\\schema\\" + self.itype + ".json"
        with open(schema_name) as f: schema = json.load(f)
        d = Draft7Validator(schema)
        d.validate(instance)

    def json_2_query_list(self, val, old = ""):
        dota = []
        if isinstance(val, dict):
            for k in val.keys(): dota += self.json_2_query_list(val[k], old + str(k) + ".") 
        elif isinstance(val, list):
            for k in val: dota += self.json_2_query_list(k, old) 
        else: dota = [{old[:-1] : val}]
        return dota 

    def get_duplicate(self):
        keys_to_remove = ["uuid", "event_ref", "_obj_ref", "_event_ref", "_raw_ref", "_session_ref", "filters"]
        doc = self.document()
        for k in keys_to_remove: doc.pop(k, None)
        
        query = self.json_2_query_list(doc)
        duplicate = self.backend.get_instance(query)
        return duplicate

    def update(self, update):
        for k,v in update.items(): setattr(self, k, v)
        self.backend.update_one({"uuid" : self.uuid}, {"$set" : update})

    def update_cross_ref(self, instance_uuid_list):
        self.backend.update_one( {"uuid":self.uuid}, {"$addToSet" : {"_ref" : {"$each" : instance_uuid_list}} })
        self.backend.update_many( {"uuid" : {"$in" : instance_uuid_list} }, {"$addToSet" : {"_ref" : self.uuid} } )

class Raw(Instance):
    def __init__(self, raw_type, data, orgid=None, timestamp=None, timezone="UTC", backend=NoBackend()):
        if isinstance(data, str): data = json.loads(data)
        self.itype, self.raw_type, self.data, self.orgid, self.timestamp, self.timezone = 'raw', raw_type, data, orgid, timestamp, timezone
        super().__init__(backend)        

class Session(Instance):
    def __init__(self, session_type, identifiers, _ref=[], backend=NoBackend()):
        if not isinstance(identifiers, list): identifiers = [identifiers]
        self.itype, self.session_type, self._ref, self.backend = 'session', session_type, _ref, backend
        self.identifiers = [obj.data() for obj in identifiers]
        super().__init__(backend)
        self.update_cross_ref([obj.uuid for obj in identifiers])

    def __iter__(self): return iter( self.backend.find( {"$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"event"} ] }))
        
    def add_event(self, event_list):
        if not isinstance(event_list, list): event_list = [event_list]
        event_uuid_list = [event.uuid for event in event_list]
        self._ref + event_uuid_list
        self.update_cross_ref(event_uuid_list)
        
    
class Event(Instance):
    def __init__(self, event_type, orgid, objects, timestamp, malicious=False, backend=NoBackend()):
        if type(objects) is not list: objects = [objects]
        self.itype, self.event_type, self.orgid, self.timestamp, self.malicious = 'event', event_type, orgid, timestamp, malicious
        self.objects = [obj.data() for obj in objects]
        super().__init__(backend)
        self.update_cross_ref([obj.uuid for obj in objects])

    def __iter__(self): return iter(self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"object"} ] }))

    def sessions(self): return iter(self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"session"} ] }))

    def add_object(self, new_objects):
        if not isinstance(new_objects, list): new_objects = [new_objects]
        self.objects += [obj.data() for obj in new_objects]
        self.update_cross_ref([obj.uuid for obj in new_objects])

class Object(Instance):
    def __init__(self, obj_type, attributes, backend=NoBackend()):
        if type(attributes) is not list: attributes = [attributes]
        self.itype, self.obj_type = 'object', obj_type
        self.attributes = { (att[0].att_type if type(att)==list else att.att_type) : ([a.value for a in att] if type(att)==list else att.value) for att in attributes }
        super().__init__(backend)
        self.update_cross_ref(self.att_uuid(attributes))
    
    def __iter__(self): return iter(self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"attribute"} ] }))
    
    def events(self): return iter(self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"event"} ] }))

    def event_uuid(self): return [event["uuid"] for event in self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"event"} ] })]

    def att_uuid(self, attributes): return [a.uuid for att in [[att] if not isinstance(att,list) else att for att in attributes] for a in att]

    def data(self): return {self.obj_type : {k:v for k,v in self.attributes.items()} }       

    def add_attribute(self, new_attributes):
        if not isinstance(new_attributes, list): new_attributes = [new_attributes]
        old_obj = self.data() 
        self.attributes.update({ (att[0].att_type if type(att)==list else att.att_type) : ([a.value for a in att] if type(att)==list else att.value) for att in new_attributes })       
        new_obj = self.data()
        self.update_cross_ref(self.att_uuid(new_attributes))
        self.backend.update_many({"uuid" : {"$in" : self.event_uuid()}}, {"$pull" : {"objects" : old_obj}})
        self.backend.update_many({"uuid" : {"$in" : self.event_uuid()}}, {"$push" : {"objects" : new_obj}})

class Attribute(Instance):
    def __init__(self, att_type, value, backend=NoBackend()):
        self.itype, self.att_type, self.value = 'attribute', att_type, value
        super().__init__(backend)

    def objects(self): return iter(self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"object"} ] }))

    def count(self, start=None, end=None):
##        from .parse import parse
        for obj in self.objects():
            if not start and not end: return sum([ref[:5]=="event" for ref in obj["_ref"]])
            elif start and not end: sum([start < e.timestamp for e in parse(obj).events()])
            elif not start and end: sum([e.timestamp < end for e in parse(obj).events()])
            else: return sum([start < e.timestamp < end for e in parse(obj).events()])


