
ITYPE_CLASS_MAP = {}

def parse(instance, backend, validate=True):
    if isinstance(instance, str): instance = json.loads(instance)
    instance.pop("_id", None)
    t = ITYPE_CLASS_MAP['attribute']['default']('mock', 'mock')
    t.__dict__ = instance

    itype = instance['itype']
    sub_type = instance['sub_type']
    t.__class__ = getclass(itype, sub_type)
##    if validate: t.validate()
    return t

def _create_itype_class_map():
    from .attribute import Attribute
    from .object import Object
    from .event import Event
    from .raw import Raw
    from .session import Session
    from .tdql import TDQL
    from .identity import Org, User
    

    ITYPE_CLASS_MAP['attribute'] = {'default': Attribute}
    ITYPE_CLASS_MAP['event'] = {'default': Event}
    ITYPE_CLASS_MAP['object'] = {'default': Object}
    ITYPE_CLASS_MAP['object']['query'] = TDQL
    
    ITYPE_CLASS_MAP['org'] = {'default': Org}
    ITYPE_CLASS_MAP['raw'] = {'default': Raw}
    ITYPE_CLASS_MAP['session'] = {'default': Session}
    
    ITYPE_CLASS_MAP['user'] = {'default':User}

def getclass(itype, sub_type='default'):
    global ITYPE_CLASS_MAP
    try:
        class_ = ITYPE_CLASS_MAP[itype][sub_type]
    except KeyError:
        class_ = ITYPE_CLASS_MAP[itype]['default']
    return class_
    
