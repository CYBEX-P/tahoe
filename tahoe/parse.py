import json

from instance import Session, Event, Object, Attribute
from backend import NoBackend

def parse(instance, backend=NoBackend()):
    if isinstance(instance, str): instance = json.loads(instance)
    instance.pop("_id", None)
    t = Attribute('text', 'mock')
    t.__dict__, t.backend = instance, backend
    t.__class__ = {'attribute': Attribute, 'event':Event, 'object':Object, 'session':Session}.get(instance['itype'])
    t.validate()
    return t

##j = {
##    "_id" : 'ObjectId("5d133d562358dd06288b9cad")',
##    "itype" : "event",
##    "event_type" : "file_download",
##    "orgid" : "identity--61de9cc8-d015-4461-9b34-d2fb39f093fb",
##    "timestamp" : 1551854788.515,
##    "malicious" : False,
##    "objects" : [ 
##        {
##            "url" : {
##                "url" : "http://165.227.0.144:80/bins/rift.x86"
##            }
##        }, 
##        {
##            "file" : {
##                "filename" : "rift.x86",
##                "sha256" : "bf69f4219069098da61a80641265d8834b474474957742510105d70703ebdb27"
##            }
##        }
##    ],
##    "uuid" : "event--2780be80-dd8c-4c22-90b4-3bf09da2b2b8"
##}
##
##a = parse(j)
##print(a)
