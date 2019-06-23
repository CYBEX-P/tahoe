from jsonschema import Draft7Validator
from collections import OrderedDict
from uuid import uuid4
import json


class Instance():
    def __init__(self, _nid, uuid, _raw_ref, _valid):
        
        if not uuid: uuid = self.itype + '--' + str(uuid4())

        if _nid: self._nid = _nid
        self.uuid = uuid
        self._raw_ref = _raw_ref
        self._valid = _valid

        self.validate()

    def __str__(self):
        return self.json()

    def validate(self):
        instance = vars(self)
        schema_name = "schema\\" + self.itype + ".json"
        with open(schema_name) as f:
            schema = json.load(f)
        d = Draft7Validator(schema)
        d.validate(instance)

    def json(self):
        instance = json.dumps(self.__dict__)
        return instance
    
    def serialize():
        pass

    def bundle():
        pass
                
    
class Event(Instance):
    def __init__(self, event_type, objects, timestamp, malicious=False, _session_ref=[],
                 _nid=None, uuid=None, _raw_ref=[], _valid=True):

        if type(objects) is not list: objects = [objects]

        self.itype = 'event'
        self.event_type = event_type
        self.objects = []
        for o in objects:
            self.objects.append(o.data())    
        self.timestamp = timestamp
        self.malicious = malicious
        self._session_ref = _session_ref
        
        super().__init__(_nid, uuid, _raw_ref, _valid)        



class Object(Instance):
    def __init__(self, obj_type, attributes, _event_ref=[],
                 _nid=None, uuid=None, _raw_ref=[], _valid=True):

        if type(attributes) is not list: attributes = [attributes]

        self.itype = 'object'
        self.obj_type = obj_type
        self.attributes = {}
        for att in attributes:
            self.attributes[att.att_type] = att.value
        self._event_ref = _event_ref
        
        super().__init__(_nid, uuid, _raw_ref, _valid)

    def add_event_ref(uuid):
        self._event_ref.append(uuid)

    def data(self):
        d = {self.obj_type : {} }
        for k,v in self.attributes.items():
            d[self.obj_type][k] = v

        return d

class Attribute(Instance):
    def __init__(self, att_type, value, _obj_ref=[],
                 _nid=None, uuid=None, _raw_ref=[], _valid=True):

        self.itype = 'attribute'
        self.att_type = att_type
        self.value = value
        self._obj_ref = _obj_ref

        super().__init__(_nid, uuid, _raw_ref, _valid)

