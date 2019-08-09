from jsonschema import Draft7Validator
from uuid import uuid4
from sys import getsizeof as size
from collections import defaultdict
import json, pdb, os, pytz, pathlib, logging, time, hashlib

if __name__ in ["__main__", "instance"]: from backend import get_backend, Backend, MongoBackend, NoBackend
else: from .backend import get_backend, Backend, MongoBackend, NoBackend

##schema = {k : json.loads(open(((__file__[:-11]+ "schema\\%s.json") %k)).read()) for k in ["attribute","object","event","session","raw"]}
_ATT_ALIAS = {
    "asn":["AS"],
    "btc":["cryptocurrency_address"],
    "comment":["text"],
    "creation_date":["date"],
    "cve_id":["vulnerability"],
    "hex_data":["data"],
    "imphash":["hash", "checksum"],
    "ipv4":["ip"],
    "ipv6":["ip"],
    "md5":["hash", "checksum"],
    "pattern":["data"],
    "pdb":["filepath"],
    "pehash":["hash", "checksum"],
    "premium_rate_telephone_number":["prtn", "phone_number"],
    "sha1":["hash", "checksum"],
    "sha224":["hash", "checksum"],
    "sha256":["hash", "checksum"],
    "sha384":["hash", "checksum"],
    "sha512":["hash", "checksum"],
    "sha512/224":["hash", "checksum"],
    "sha512/256":["hash", "checksum"],
    "sigma":["siem"],
    "snort":["nids"],
    "ssdeep":["hash", "checksum"],
    "url":["uri"],
    "user_agent":["http_user_agent"],
    "yara":["nids"]
}


class Instance():
    backend = get_backend() if os.getenv("_MONGO_URL") else NoBackend()
    
    def __init__(self, **kwargs):
        if type(self.backend) == NoBackend and os.getenv("_MONGO_URL"):
            self.backend = get_backend()
        if 'backend' in kwargs:
            self.backend = kwargs.get('backend') 
        if not isinstance(self.backend, Backend):
            raise TypeError('backend cannot be of type ' + str(type(self.backend)))

        self.sub_type = kwargs.pop("sub_type")
        unique = self.itype + self.sub_type + self.canonical_data()
        self._hash = hashlib.sha256(unique.encode('utf-8')).hexdigest()
        
        dup = self.duplicate()
        if dup: [setattr(self,k,v) for k,v in dup.items()]
        else: 
            if not hasattr(self, 'uuid') or not self.uuid:
                self.uuid = self.itype + '--' + str(uuid4())
            self.backend.insert_one(self.doc())
##      self.validate()        

    def __str__(self): return self.json()

    def branches(self):
        
        def branch(val, old=[]):
            b = []
            if isinstance(val, dict):
                for k in val: b += branch(val[k], old+[str(k)])
            elif isinstance(val, list):
                for k in val: b += branch(k, old)
            else:
                b.append(old + [val])
            return b

        return branch(self.data)

    def canonical_data(self):

        def canonicalize(val):
            if isinstance(val, dict):
                r = {k : canonicalize(v) for k,v in val.items()}
                return str(dict(sorted(r.items())))
            elif isinstance(val, list):
                r = [canonicalize(i) for i in val]
                return str(sorted(list(set(r))))
            elif isinstance(val, str):
                val = val.strip()
            return(str(val))

        return canonicalize(self.data)

    def doc(self): return {k:v for k,v in vars(self).items() if v is not None and k not in ['backend','schema']}

    def duplicate(self): return self.backend.find_one({"_hash" : self._hash})

    def json(self): return json.dumps(self.doc())

##    def json_dot(self, data, old = ""):
##        return [{old + ".".join(i[:-1]) : i[-1]} for i in self.branch(data)]
        
    def related(self, lvl=1, itype=None, p={"_id":0}):
        rel_uuid = list(set(self.related_uuid(lvl)))
        q = {"uuid": {"$in": rel_uuid}}
        if itype: q.update({"itype":itype})
        return self.backend.find(q, p)

    def related_uuid(self, lvl, v=[]):
        uuids = []
        for e in self.events({"itype":1,"uuid":1,"_ref":1}):
            if e["uuid"] in v: continue
            uuids += parse(e, self.backend, False).related_uuid(lvl-1,v)
        return uuids

    def parents(self, q={}, p={"_id":0}):
        return self.backend.find({**{"_ref":self.uuid}, **q}, p)

    def update(self, update):
        for k,v in update.items(): setattr(self, k, v)
        self.backend.update_one({"uuid" : self.uuid}, {"$set" : update})

##    def validate(self): Draft7Validator(schema[self.itype]).validate(self.doc())

    def verified_instances(self, instances, type_list):
        if not isinstance(instances, list): instances = [instances]
        instances = list(set(instances))
        if len(instances)==0: raise ValueError("instances cannot be empty")
        for i in instances:
            if not any([isinstance(i, t) for t in type_list]):
                raise TypeError("instances must be of type tahoe " + " or ".join([str(t) for t in type_list]))
        return instances

    
class Raw(Instance):
    def __init__(self, sub_type, data, orgid, timezone="UTC", **kwargs):
        if isinstance(data, str): data = json.loads(data)
        self.itype, self.data = 'raw', data
        self.orgid, self.timezone = orgid, timezone
        super().__init__(sub_type=sub_type, **kwargs)
        
    
    def update_ref(self, ref_uuid_list):
        if hasattr(self, "_ref"): self._ref = self._ref + ref_uuid_list
        else: self._ref = ref_uuid_list
        self._ref = list(set(self._ref))
        self.backend.update_one({"uuid":self.uuid}, {"$set":{"_ref":self._ref}})


class OES(Instance):
    def __init__(self, data, **kwargs):
        data = self.verified_instances(data, [Attribute, Object])
        d = defaultdict(list)
        for i in data:
            for k,v in i.get_data().items(): d[k] += v
        self.data = dict(d)        

        c_ref = [i.uuid for i in data]
        gc_ref = [r for i in data if hasattr(i, "_ref") for r in i._ref]
        self._ref = list(set(c_ref + gc_ref))
        super().__init__(**kwargs)

    def __iter__(self): return iter(self.backend.find({"uuid":{"$in" : self._ref}}))

    def features(self):
        branches = self.branches()
        r = defaultdict(list)
        for b in branches:
            k, v = b[:-1], b[-1]
            for i in range(len(k)):
                r['.'.join(k[-i:])].append(v)
        return dict(r)    

        
class Session(OES):
    def __init__(self, sub_type, data=None, **kwargs):
        self.itype, self._eref = 'session', []
        super().__init__(data, sub_type=sub_type, **kwargs)

    def events(self, p={"_id":0}): return self.backend.find({"uuid":{"$in" : self._eref}}, p)
        
    def add_event(self, events):
        events = self.verified_instances(events, [Event])
        self._eref = self._eref + [i.uuid for i in events]
        self._eref = list(set(self._eref))
        self.backend.update_one( {"uuid":self.uuid}, {"$set":{"_eref":self._eref}})

    
class Event(OES):
    def __init__(self, sub_type, data, orgid, timestamp, malicious=False, **kwargs):
        self.itype, self.orgid = 'event', orgid
        self.timestamp, self.malicious = timestamp, malicious
        mal_data = kwargs.pop("mal_data",None)
        if mal_data:
            mal_data = self.verified_instances(mal_data, [Attribute, Object])
            self._mal_ref = [i.uuid for i in mal_data]
        super().__init__(data, sub_type=sub_type, **kwargs)

    def delete(self):
        # delete self
        # delete self.uuid from all session._ref
        # delete all attribute in self._ref if attribute.parents().count == 0
        # delete all object in self._ref if object.parents().count == 0
        # delete raw._ref s.t. self.uuid in raw._ref
        # delete raw.filters s.t. self.uuid in raw._ref if len(raw.filters) == 1 else ??
        pass

    def sessions(self, p={"_id":0}): return self.backend.find({"_eref":self.uuid}, p)

    def related_uuid(self, lvl=0, v=[]):
        uuids = self._ref + [self.uuid]
        if lvl == 0: return uuids
        for s in self.sessions({"itype":1,"uuid":1,"_eref":1}):
            uuids += parse(s, self.backend).related_uuid(lvl, v+[self.uuid])
        return uuids


class Object(OES):
    def __init__(self, sub_type, data, **kwargs):
        self.itype = 'object'
        super().__init__(data, sub_type=sub_type, **kwargs)

    def events(self, p={"_id":0}): return self.parents({"itype":"event"},p)

    def get_data(self): return {self.sub_type : [self.data]}


class Attribute(Instance):   
    def __init__(self, sub_type, data, uuid=None, **kwargs):
        self.itype, self.data, self.uuid = 'attribute', data, uuid
        super().__init__(sub_type=sub_type, **kwargs)

        aka = kwargs.pop("aka",[])
        _aka = kwargs.pop("_aka",[]) + [self.sub_type]
        self.create_alias(aka, _aka)

    def count(self, start=0, end=None):
        if not end: end = time.time()
        return self.backend.count({"itype":"event", "_ref":self.uuid, "timestamp":{"$gte":start, "$lte":end}})
        
    def create_alias(self, aka, _aka):
        aka = aka + _ATT_ALIAS.get(self.sub_type, [])
        for sub_type in set(aka) - set(_aka):
            Attribute(sub_type, self.data, self.uuid,
                      backend = self.backend, _aka = _aka)

    def delete(self):
##        r = self.backend.find({"_ref" : self.uuid})
##        if r: raise DependencyError("Other instances contain this " + self.itype)
##        self.backend.delete_one({"uuid":"self.uuid"})
        pass
        

    def events(self, p={"_id":0}): return self.parents({"itype":"event"}, p)

    def get_data(self): return {self.sub_type : [self.data]}

    def objects(self, p={"_id":0}): return self.parents({"itype":"object"}, p)

    def update(self, update):
        # update format {sub_type : str, data : str}
        # self.backend.update_one({"uuid" : self.uuid}, {"$set" : update})
        # create function get_data_from_ref() for OES
        # get all OESR s.t. {"_ref" : self.uuid}
        # parse all the above OES
        # each OESR.update({data : OESR.get_data_from_ref()})
        pass
    


def parse(instance, backend=NoBackend(), validate=True):
    if isinstance(instance, str): instance = json.loads(instance)
    instance.pop("_id", None)
    t = Attribute('text', 'mock')
    t.__dict__ = instance
    t.__class__ = {'attribute':Attribute, 'event':Event, 'object':Object,
                   'raw':Raw, 'session':Session}.get(instance['itype'])
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
    db = MongoBackend(client.tahoe_db)

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
    e = Event('file_download', [url_att, file_obj],
              'identity--61de9cc8-d015-4461-9b34-d2fb39f093fb', timestamp, backend=db)

    pprint(e.doc())
    print("\n")

    ip_att2 = Attribute("ipv4", "2.2.2.2", backend=db)
    ip_obj = Object("ipv4", [ipv4_att], backend=db)

    e2 = Event('test', [url2_att, ipv4_att, ip_att2, ip_obj],
               'identity--61de9cc8-d015-4461-9b34-d2fb39f093fb', timestamp, backend=db)
    pprint(e2.doc())
    print("\n")
    
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

    sub_type = "x-unr-honeypot"
    orgid = "identity--f27df111-ca31-4700-99d4-2635b6c37851"
    orgid = None
    raw = Raw(sub_type, data, orgid, backend=db)

    
    pprint(raw.doc())
    print("\n")

    d1, d2, d3 = 0, 0, 0
    n = 1
    for i in range(n):
        t1 = time.time()
        uu = url_att.related(lvl=1)
        t2 = time.time()
        uu = url_att.related(lvl=2)
        t3 = time.time()
        uu = url_att.related(lvl=3)
        t4 = time.time()

        d1 += t2-t1
        d2 += t3-t2
        d3 += t4-t3

    print(d1/n, d2/n, d3/n)

    for i in url_att.related(lvl=3): print(i["uuid"])

    print(e.features())
        
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


