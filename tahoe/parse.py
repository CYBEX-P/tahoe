
ITYPE_CLASS_MAP = {}

def parse(instance, backend, validate=True):
    if isinstance(instance, str): instance = json.loads(instance)
    instance.pop("_id", None)
    t = ITYPE_CLASS_MAP.get('attribute')('mock', 'mock')
    t.__dict__ = instance
    if instance['itype'] == 'object' and instance['sub_type'] == "cybexp_user":
        t.__class__ = ITYPE_CLASS_MAP.get('user')
    elif instance['itype'] == 'object' and instance['sub_type'] == "cybexp_org":
        t.__class__ = ITYPE_CLASS_MAP.get('org')
    else: 
        t.__class__ = ITYPE_CLASS_MAP.get(instance['itype'])
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
    

    ITYPE_CLASS_MAP['attribute'] = Attribute
    ITYPE_CLASS_MAP['event'] = Event
    ITYPE_CLASS_MAP['object'] = Object
    ITYPE_CLASS_MAP['org'] = Org
    ITYPE_CLASS_MAP['raw'] = Raw
    ITYPE_CLASS_MAP['session'] = Session
    ITYPE_CLASS_MAP['tdql'] = TDQL
    ITYPE_CLASS_MAP['user'] = User
