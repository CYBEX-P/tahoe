from jsonschema import Draft7Validator
from uuid import uuid4
import json, pdb

if __name__ == "__main__": from backend import MongoBackend, NoBackend
else: from .backend import MongoBackend, NoBackend

class Instance():
    def __init__(self, backend):
        if type(backend) not in [NoBackend, MongoBackend]: raise TypeError('Backend cannot be of type ' + str(type(backend)))
        self.backend = backend
        duplicate = self.get_duplicate()
        if duplicate: [setattr(self,k,v) for k,v in duplicate.items()]
        else:
            self.uuid = self.itype + '--' + str(uuid4())
            self.validate()
            self.backend.insert_one(self.document())

    def document(self): return {k:v for k,v in vars(self).items() if v and k not in ['backend']}

    def json(self): return json.dumps(self.document())

    def __str__(self): return self.json()

    def serialize(self): pass

    def validate(self):
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
        query = self.json_2_query_list(self.document())
        duplicate = self.backend.get_instance(query)
        return duplicate

class Raw(Instance):
    def __init__(self, raw_type, data, orgid=None, timestamp=None, timezone="UTC", backend=NoBackend()):
        if isinstance(data, str): data = json.loads(data)
        self.itype, self.raw_type, self.data, self.orgid, self.timestamp, self.timezone = 'raw', raw_type, data, orgid, timestamp, timezone
        super().__init__(backend)        

class Session(Instance):
    def __init__(self, session_type, identifiers, event_ref = [], backend=NoBackend()):
        if not isinstance(identifiers, list): identifiers = [identifiers]
        if not isinstance(event_ref, list): event_ref = [event_ref]
        self.itype, self.session_type, self.event_ref = 'session', session_type, event_ref
        self.identifiers = [obj.data() for obj in identifiers]
        super().__init__(backend)
        for obj in identifiers: obj.update_event_uuid(self.uuid)

    def add_event(self, event):
        self.event_ref.append(event.uuid)
        self.backend.add_ref_uuid(self.uuid, "event_ref", event.uuid)
    
class Event(Instance):
    def __init__(self, event_type, orgid, objects, timestamp, malicious=False, backend=NoBackend()):
        if type(objects) is not list: objects = [objects]
        self.itype, self.event_type, self.orgid, self.timestamp, self.malicious = 'event', event_type, orgid, timestamp, malicious
        self.objects = [obj.data() for obj in objects]
        super().__init__(backend)
        for obj in objects: obj.update_event_uuid(self.uuid)

class Object(Instance):
    def __init__(self, obj_type, attributes, backend=NoBackend()):
        if type(attributes) is not list: attributes = [attributes]
        self.itype, self.obj_type = 'object', obj_type
        self.attributes = {att.att_type : att.value for att in attributes}
        super().__init__(backend)
        for att in attributes: att.update_obj_uuid(self.uuid)

    def data(self): return {self.obj_type : {k:v for k,v in self.attributes.items()} }

    def update_event_uuid(self, event_uuid): self.backend.add_ref_uuid(self.uuid, "_event_ref", event_uuid)
        

class Attribute(Instance):
    def __init__(self, att_type, value, backend=NoBackend()):
        self.itype, self.att_type, self.value = 'attribute', att_type, value
        super().__init__(backend)

    def update_obj_uuid(self, obj_uuid): self.backend.add_ref_uuid(self.uuid, "_obj_ref", obj_uuid)




def example1():
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
    URI = 'mongodb://cybexp_user:CybExP_777@134.197.21.231:27017/?authSource=admin'
    client = MongoClient(URI)
    db = MongoBackend(client.tahoe_db)

    data = json.loads(j)

    url = data['url']
    filename = url.split('/')[-1]
    sha256 = data['shasum']

    url_att = Attribute('url', url, backend=db)
    filename_att = Attribute('filename', filename, backend=db)
    sha256_att = Attribute('sha256', sha256, backend=db)

    url_obj = Object('url', [url_att], backend=db)   
    file_obj = Object('file', [filename_att, sha256_att], backend=db)

    timestamp = data["@timestamp"]
    timestamp = dt.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
    e = Event('file_download', 'identity--61de9cc8-d015-4461-9b34-d2fb39f093fb',
              [url_obj, file_obj], timestamp, backend=db)

    hostname = data['host']['name']
    hostname_att = Attribute('hostname', hostname, backend=db)
    sessionid = data['session']
    sessionid_att = Attribute('sessionid', sessionid, backend=db)

    session_obj = Object('session_identifier', [hostname_att, sessionid_att], backend=db)
    session = Session('cowrie_session', session_obj, backend=db)
    session.add_event(e)

    raw_type = "x-unr-honeypot"
    orgid = "identity--f27df111-ca31-4700-99d4-2635b6c37851"
    orgid = None
    raw = Raw(raw_type, data, orgid, backend=db)

                     

    from pprint import pprint
    pprint(raw.document())
    print("\n")
    
    pprint(url_att.document())
    print("\n")
    pprint(filename_att.document())
    print("\n")
    pprint(sha256_att.document())
    print("\n")
    
    pprint(url_obj.document())
    print("\n")
    pprint(file_obj.document())
    print("\n")
    
    pprint(e.document())
    print("\n")
    
    pprint(session.document())


if __name__ == "__main__": example1()
