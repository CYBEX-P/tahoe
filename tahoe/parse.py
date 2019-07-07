import json, os
from pymongo import MongoClient

from .backend import get_backend, NoBackend, MongoBackend
from .instance import Attribute, Object, Event, Session, Raw

def parse(instance, backend=NoBackend()):
    if os.getenv("_MONGO_URL"): backend = get_backend()
    else: backend = backend
    if isinstance(instance, str): instance = json.loads(instance)
    instance.pop("_id", None)
    t = Attribute('text', 'mock')
    t.__dict__, t.backend = instance, backend
    t.__class__ = {'attribute':Attribute, 'event':Event, 'object':Object, 'raw':Raw, 'session':Session}.get(instance['itype'])
    t.validate()
    return t
