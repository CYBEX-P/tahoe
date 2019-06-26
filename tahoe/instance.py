from jsonschema import Draft7Validator
from uuid import uuid4
import json, pdb

from backend import MongoBackend, NoBackend

class Instance():
    def __init__(self, backend):
        if type(backend) not in [NoBackend, MongoBackend]: raise TypeError('Backend cannot be of type ' + type(backend))
        duplicate = self.get_duplicate(backend)
        if not duplicate:
            self.uuid = self.itype + '--' + str(uuid4())
            self.validate()
            backend.insert_one(vars(self))
        else: self.__dict__ = duplicate

    def __str__(self): return self.json()

    def validate(self):
        instance = vars(self)
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

    def get_duplicate(self, backend):
        query = self.json_2_query_list(vars(self))
        duplicate = backend.get_instance(query)
        return duplicate

    def json(self): return json.dumps(vars(self))
    
    def serialize(self): pass
                
    
class Event(Instance):
    def __init__(self, event_type, orgid, objects, timestamp, malicious=False, backend=NoBackend()):
        if type(objects) is not list: objects = [objects]
        self.itype, self.event_type, self.orgid, self.timestamp, self.malicious = 'event', event_type, orgid, timestamp, malicious
        self.objects = [obj.data() for obj in objects]
        super().__init__(backend)
        for obj in objects: obj.update_event_uuid(self.uuid, backend)


class Object(Instance):
    def __init__(self, obj_type, attributes, backend=NoBackend()):
        if type(attributes) is not list: attributes = [attributes]
        self.itype, self.obj_type = 'object', obj_type
        self.attributes = {att.att_type : att.value for att in attributes}
        super().__init__(backend)
        for att in attributes: att.update_obj_uuid(self.uuid, backend)

    def add_event_ref(uuid): self._event_ref.append(uuid)

    def data(self): return {self.obj_type : {k:v for k,v in self.attributes.items()} }

    def update_event_uuid(self, event_uuid, backend): backend.add_ref_uuid(self.uuid, "_event_ref", event_uuid)
        

class Attribute(Instance):
    def __init__(self, att_type, value, backend=NoBackend()):
        self.itype, self.att_type, self.value = 'attribute', att_type, value
        super().__init__(backend)

    def update_obj_uuid(self, obj_uuid, backend): backend.add_ref_uuid(self.uuid, "_obj_ref", obj_uuid)


##j = r"""{
##    "sensor" : "ssh-peavine",
##    "@timestamp" : "2019-03-06T06:46:28.515Z",
##    "geoip" : {
##        "country_code2" : "US",
##        "location" : {
##            "lat" : 37.3501,
##            "lon" : -121.9854
##        },
##        "region_code" : "CA",
##        "postal_code" : "95051",
##        "timezone" : "America/Los_Angeles",
##        "continent_code" : "NA",
##        "city_name" : "Santa Clara",
##        "longitude" : -121.9854,
##        "ip" : "165.227.0.144",
##        "country_name" : "United States",
##        "dma_code" : 807,
##        "latitude" : 37.3501,
##        "region_name" : "California",
##        "country_code3" : "US"
##    },
##    "host" : {
##        "name" : "ssh-peavine"
##    },
##    "session" : "619c9c48b812",
##    "@version" : "1",
##    "eventid" : "cowrie.session.file_download",
##    "timestamp" : "2019-03-06T06:46:27.400128Z",
##    "src_ip" : "165.227.0.144",
##    "outfile" : "var/lib/cowrie/downloads/bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27",
##    "beat" : {
##        "version" : "6.5.4",
##        "name" : "ssh-peavine",
##        "hostname" : "ssh-peavine"
##    },
##    "tags" : [ 
##        "beats_input_codec_plain_applied", 
##        "geoip", 
##        "beats_input_codec_json_applied"
##    ],
##    "shasum" : "bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27",
##    "prospector" : {
##        "type" : "log"
##    },
##    "msg" : "Downloaded URL (http://165.227.0.144:80/bins/rift.x86) with SHA-256 bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27 to var/lib/cowrie/downloads/bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27",
##    "source" : "/home/cowrie/cowrie/var/log/cowrie/cowrie.json",
##    "offset" : 23030686,
##    "url" : "http://165.227.0.144:80/bins/rift.x86",
##    "destfile" : "-"
##}"""
##
##from datetime import datetime as dt
##from pymongo import MongoClient
##URI = 'mongodb://cybexp_user:CybExP_777@134.197.21.231:27017/?authSource=admin'
##client = MongoClient(URI)
##db = MongoBackend(client.tahoe_db)
##
##data = json.loads(j)
##
##url = data['url']
##filename = url.split('/')[-1]
##sha256 = data['shasum']
##
##url_att = Attribute('url', url, backend=db)
##filename_att = Attribute('filename', filename, backend=db)
##sha256_att = Attribute('sha256', sha256, backend=db)
##
##url_obj = Object('url', [url_att], backend=db)   
##file_obj = Object('file', [filename_att, sha256_att], backend=db)
##
##timestamp = data["@timestamp"]
##timestamp = dt.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
##e = Event('file_download', 'identity--61de9cc8-d015-4461-9b34-d2fb39f093fb',
##          [url_obj, file_obj], timestamp, backend=db)
##
##
##print(url_att.uuid, '\n', url_obj.uuid, '\n', e.uuid)
