from jsonschema import Draft7Validator
from uuid import uuid4
import json, pdb, os, pytz, pathlib, logging

if __name__ == "__main__": from backend import get_backend, Backend, MongoBackend, NoBackend
else: from .backend import get_backend, Backend, MongoBackend, NoBackend

##schema = {k : json.loads(open(((__file__[:-11]+ "schema\\%s.json") %k)).read()) for k in ["attribute","object","event","session","raw"]}
_ATT_ALIAS = {"ipv4":"ip", "ipv6":"ip", "md5":"hash", "sha256":"hash"}

class Instance():
    def __init__(self, backend):
        self.backend = get_backend() if os.getenv("_MONGO_URL") else backend
        if not isinstance(backend, Backend): raise TypeError('Backend cannot be of type ' + str(type(backend)))

        duplicate = self.get_duplicate()
        if duplicate: [setattr(self,k,v) for k,v in duplicate.items()]
        else: 
            if not hasattr(self, 'uuid'): self.uuid = self.itype + '--' + str(uuid4())
            self._ref = []
            self.backend.insert_one(self.doc())
##      self.validate()        

    def __str__(self): return self.json()

    def doc(self): return {k:v for k,v in vars(self).items() if v is not None and k not in ['backend','schema']}

    def get_duplicate(self):
        doc, keys_to_remove = self.doc(), ["uuid", "_ref", "filters"]
        for k in keys_to_remove: doc.pop(k, None)
        return self.backend.find_one({"$and" : self.json_dot(doc)})

    def json(self): return json.dumps(self.doc())

    def json_dot(self, val, old = ""):
        dota = []
        if isinstance(val, dict):
            for k in val.keys(): dota += self.json_dot(val[k], old + str(k) + ".") 
        elif isinstance(val, list):
            for k in val: dota += self.json_dot(k, old) 
        else: dota = [{old[:-1] : val}]
        return dota
    
    def child_ref(self, instances):
        if not isinstance(instances, list): instances = [instances]
        uuids = [i.uuid for i in instances]
        if self.itype != 'session': uuids += [r for i in instances for r in i._ref]
        self.backend.update_one( {"uuid":self.uuid}, {"$addToSet" : {"_ref" : {"$each" : uuids}} })
        self.sync()          

    def serialize(self): pass

    def sync(self): self._ref = self.backend.find_one({"uuid" : self.uuid})["_ref"]

    def update(self, update):
        for k,v in update.items(): setattr(self, k, v)
        self.backend.update_one({"uuid" : self.uuid}, {"$set" : update})

##    def validate(self): Draft7Validator(schema[self.itype]).validate(self.doc())

    def verify_data(self, instances):
        if type(instances) is not list: instances = [instances]
        instances = list(dict.fromkeys(instances))
        if len(instances)==0: raise ValueError("data cannot be empty")
        if not all(map(lambda x: x in [Attribute, Object], [type(i) for i in instances])):
            raise TypeError("data must be of type tahoe Attribute or Object")
        return instances

    
class Raw(Instance):
    def __init__(self, raw_type, data, orgid=None, timestamp=None, timezone="UTC", backend=NoBackend()):
        if isinstance(data, str): data = json.loads(data)
        self.itype, self.raw_type, self.data, self.orgid, self.timestamp, self.timezone = 'raw', raw_type, data, orgid, timestamp, timezone
        super().__init__(backend)        


class Session(Instance):
    def __init__(self, session_type, data, _ref=[], backend=NoBackend()):
        self.itype, self.session_type, self._ref, self.backend = 'session', session_type, _ref, backend
        data = self.verify_data(data)
        self.data = [obj.get_data() for obj in data]
        super().__init__(backend)
        self.child_ref(data)

    def __iter__(self): return iter( self.backend.find({"uuid":{"$in" : self._ref}, "itype":"event"}))
        
    def add_event(self, new_events): self.child_ref(new_events)

    def related_uuid(self, level, v):
        u = []
        r = self.backend.find({"itype":"event","uuid":{"$in":self._ref}},{"uuid":1,"itype":1,"_ref":1})
        print("query --------------------------")
        for e in r:
##            if e["uuid"] == v: continue
            e = parse(e, self.backend)
            u += e.related_uuid(level)
        return u

    
class Event(Instance):
    def __init__(self, event_type, orgid, data, timestamp, malicious=False, backend=NoBackend()):
        self.itype, self.event_type, self.orgid, self.timestamp, self.malicious = 'event', event_type, orgid, timestamp, malicious
        data = self.verify_data(data)        
        self.data = [i.get_data() for i in data]
        super().__init__(backend)
        self.child_ref(data)

    def __iter__(self): return iter(self.backend.find({"uuid":{"$in" : self._ref}, "itype":"object"}))

    def related_uuid(self, level):
        if level == 0: return self._ref + [self.uuid]
        u = []
        r = self.backend.find({"itype":"session","_ref":self.uuid},{"itype":1,"_ref":1})
        print("query --------------------------")
        for s in r:
            s = parse(s, self.backend)
            u += s.related_uuid(level-1, self.uuid)
        return u


##    def sessions(self): return iter(self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"session"} ] }))

##    def add_object(self, new_objects):
##        if not isinstance(new_objects, list): new_objects = [new_objects]
##        self.objects += [obj.data() for obj in new_objects]
##        self.child_ref([obj.uuid for obj in new_objects])


class Object(Instance):
    def __init__(self, obj_type, data, backend=NoBackend()):
        self.itype, self.obj_type = 'object', obj_type
        data = self.verify_data(data)
        self.data = [i.get_data() for i in data]
        super().__init__(backend)
        self.child_ref(data)
    
    def __iter__(self): return iter(self.backend.find({"uuid":{"$in" : self._ref}, "itype":"attribute"}))    

##    def event_uuid(self): return [event["uuid"] for event in self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"event"} ] })]
    
    def events(self): return iter(self.backend.find({"uuid":{"$in" : self._ref}, "itype":"event"}))

    def get_data(self): return {self.obj_type : self.data}

##    def add_attribute(self, new_attributes):
##        if not isinstance(new_attributes, list): new_attributes = [new_attributes]
##        old_obj = self.data() 
##        self.attributes += [att.data() for att in new_attributes]
##        new_obj = self.data()
##        self.child_ref(new_attributes)
##        self.backend.update_many({"uuid" : {"$in" : self.event_uuid()}}, {"$pull" : {"objects" : old_obj}})
##        self.backend.update_many({"uuid" : {"$in" : self.event_uuid()}}, {"$push" : {"objects" : new_obj}})


class Attribute(Instance):
    def __init__(self, att_type, data, backend=NoBackend(), uuid=None):
        self.itype, self.att_type, self.data = 'attribute', att_type, data
        if uuid: self.uuid = uuid
        super().__init__(backend)
        self.create_alias()

##    def count(self, start=None, end=None, count=0):
##        for obj in self.objects():
##            if not start and not end: count += sum([ref[:5]=="event" for ref in obj["_ref"]])
##            elif start and not end: count += sum([start <= e["timestamp"] for e in parse(obj).events()])
##            elif not start and end: count += sum([e["timestamp"] <= end for e in parse(obj).events()])
##            else: count += sum([start <= e["timestamp"] <= end for e in parse(obj).events()])
##        return count
    
    def create_alias(self):
        att_type_lst = _ATT_ALIAS.get(self.att_type)
        if not att_type_lst: return
        if not isinstance(att_type_lst, list): att_type_lst = [att_type_lst]
        for att_type in att_type_lst: Attribute(att_type, self.data, backend=self.backend, uuid = self.uuid)

    def get_data(self): return {self.att_type : self.data}
    
    def objects(self): return iter(self.backend.find({ "$and" : [ {"uuid":{"$in" : self._ref}}, {"itype":"object"} ] }))

    def related_uuid(self, level=1):
        projection = {"itype":1,"uuid":1,"_ref":1}
        u = []
        r = self.backend.find({"itype":"event", "_ref":self.uuid},projection)
        print("query ------------------------------ ")
        for e in r:
            e = parse(e, self.backend)
            u += e.related_uuid(level-1)
        return u
    
    
    

def parse(instance, backend=NoBackend(), validate=True):
    backend = get_backend() if os.getenv("_MONGO_URL") else backend
    if isinstance(instance, str): instance = json.loads(instance)
    instance.pop("_id", None)
    t = Attribute('text', 'mock')
    t.__dict__, t.backend = instance, backend
    t.__class__ = {'attribute':Attribute, 'event':Event, 'object':Object, 'raw':Raw, 'session':Session}.get(instance['itype'])
##    if validate: t.validate()
    return t





































def example1():
    from pprint import pprint
    j = r"""{
        "sensor" : "ssh-peavine",
        "@timestamp" : "2019-03-06T06:46:28.515Z",
        "geoip" : {
            "country_code2" : "US",
            "location" : {
                "lat" : 37.3501,
                "lon" : -121.9854
            },
            "region_code" : "CA",
            "postal_code" : "95051",
            "timezone" : "America/Los_Angeles",
            "continent_code" : "NA",
            "city_name" : "Santa Clara",
            "longitude" : -121.9854,
            "ip" : "165.227.0.144",
            "country_name" : "United States",
            "dma_code" : 807,
            "latitude" : 37.3501,
            "region_name" : "California",
            "country_code3" : "US"
        },
        "host" : {
            "name" : "ssh-peavine"
        },
        "session" : "619c9c48b812",
        "@version" : "1",
        "eventid" : "cowrie.session.file_download",
        "timestamp" : "2019-03-06T06:46:27.400128Z",
        "src_ip" : "165.227.0.144",
        "outfile" : "var/lib/cowrie/downloads/bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27",
        "beat" : {
            "version" : "6.5.4",
            "name" : "ssh-peavine",
            "hostname" : "ssh-peavine"
        },
        "tags" : [ 
            "beats_input_codec_plain_applied", 
            "geoip", 
            "beats_input_codec_json_applied"
        ],
        "shasum" : "bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27",
        "prospector" : {
            "type" : "log"
        },
        "msg" : "Downloaded URL (http://165.227.0.144:80/bins/rift.x86) with SHA-256 bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27 to var/lib/cowrie/downloads/bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27",
        "source" : "/home/cowrie/cowrie/var/log/cowrie/cowrie.json",
        "offset" : 23030686,
        "url" : "http://165.227.0.144:80/bins/rift.x86",
        "destfile" : "-"
    }"""

    from datetime import datetime as dt
    from pymongo import MongoClient
    URI = 'mongodb://localhost:27017'
    client = MongoClient(URI)
    db = MongoBackend(client.tahoe_demo)

    data = json.loads(j)

    url = data['url']
    filename = url.split('/')[-1]
    sha256 = data['shasum']

    url_att = Attribute('url', url, backend=db)
    url2_att = Attribute('url', 'example.com', backend=db)
    filename_att = Attribute('filename', filename, backend=db)
    sha256_att = Attribute('sha256', sha256, backend=db)
    ipv4_att = Attribute('ipv4', '1.1.1.1', backend=db)

    pprint(url_att.doc())
    print("\n")
    pprint(filename_att.doc())
    print("\n")
    pprint(sha256_att.doc())
    print("\n")

    url_obj = Object('url', [url_att], backend=db)
    file_obj = Object('file', [filename_att, sha256_att], backend=db)
    test_obj = Object('test', [url_att,file_obj], backend=db)

    pprint(url_obj.doc())
    print("\n")
    pprint(file_obj.doc())
    print("\n")
    pprint(test_obj.doc())
    print("\n")

    for att in file_obj:
        pprint(att)
        print("\n")
    
    timestamp = data["@timestamp"]
    timestamp = dt.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
    e = Event('file_download', 'identity--61de9cc8-d015-4461-9b34-d2fb39f093fb',
              [url_att, file_obj], timestamp, backend=db)

    pprint(e.doc())
    print("\n")

    e2 = Event('test', 'identity--61de9cc8-d015-4461-9b34-d2fb39f093fb',
               [url2_att, ipv4_att], timestamp, backend=db)
    
    hostname = data['host']['name']
    hostname_att = Attribute('hostname', hostname, backend=db)
    sessionid = data['session']
    sessionid_att = Attribute('sessionid', sessionid, backend=db)

    session_obj = Object('session_identifier', [hostname_att, sessionid_att], backend=db)
    session = Session('cowrie_session', session_obj, backend=db)
    session.add_event(e)
    session.add_event(e2)

    pprint(session.doc())
    print("\n")

    raw_type = "x-unr-honeypot"
    orgid = "identity--f27df111-ca31-4700-99d4-2635b6c37851"
    orgid = None
    raw = Raw(raw_type, data, orgid, backend=db)

    
    pprint(raw.doc())
    print("\n")

    uu = url_att.related_uuid(level=2)
    for i in uu: print(i)
    pdb.set_trace()
    
    
    
def example2():
    from pprint import pprint
    config = {}
    os.environ["_MONGO_URL"] = config.pop("mongo_url", "mongodb://cybexp_user:CybExP_777@134.197.21.231:27017/?authSource=admin")
    os.environ["_ANALYTICS_DB"] = config.pop("analytics_db", "tahoe_db")
    os.environ["_ANALYTICS_COLL"] = config.pop("analytics_coll", "instances")

    backend = get_backend()
  
    for i in r:
        pprint(i)
    rr = r
    


if __name__ == "__main__": example1()


