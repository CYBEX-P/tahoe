
ITYPE_CLASS_MAP = {'str': {'default':str}}

def parse(instance, backend, validate=True):
    """
    Parses the passed encoded json instance into an 'ITYPE_CLASS_MAP' of it's key elements, sets the backend
    identity of the class map, and returns a parsed class map dict of the attributes and their itypes.

    Parameters
    ----------
    instance: json dict object
        Contains unparsed Tahoe object instance
    backend: string
        the backend identity/location for where the tahoe object will go to
    
    Returns
    -------
    t: dict
        a parsed tahoe object dictionary with the corresponding itype and sub_type representation

    """
    if isinstance(instance, str):
        instance = json.loads(instance)
    instance.pop("_id", None)
    t = ITYPE_CLASS_MAP['attribute']['default']('mock', 'mock')
    t.__dict__ = instance

    itype = instance['itype']
    sub_type = instance['sub_type']
    t.__class__ = getclass(itype, sub_type)

    if t._backend != backend:
        t._backend = backend
        
##    if validate: t.validate()
    return t

def _create_itype_class_map():
    from .attribute import Attribute
    from .object import Object
    from .event import Event
    from .raw import Raw
    from .session import Session
    from .tdql import TDQL
    from .identity.org import Org
    from .identity.user import User
    

    ITYPE_CLASS_MAP['attribute'] = {'default': Attribute}
    ITYPE_CLASS_MAP['event'] = {'default': Event}
    ITYPE_CLASS_MAP['object'] = {'default': Object}
    ITYPE_CLASS_MAP['object']['query'] = TDQL

    ITYPE_CLASS_MAP['object']['cybexp_user'] = User
    ITYPE_CLASS_MAP['object']['cybexp_org'] = Org
    
    ITYPE_CLASS_MAP['org'] = {'default': Org}
    ITYPE_CLASS_MAP['raw'] = {'default': Raw}
    ITYPE_CLASS_MAP['session'] = {'default': Session}
    
    ITYPE_CLASS_MAP['user'] = {'default':User}

def getclass(itype, sub_type='default'):
    """
    Utility function that returns a variable 'class_' containing the itype and sub_type values from 'ITYPE_CLASS_MAP'.
    This function is used to ensure there is dictionary key errors behind the call. Otherwise the the sub_type is set
    to 'default'.

    Parameters
    ----------
    itype: str
        the itype of the ITYPE_CLASS_MAP dict
    sub_type:
        the sub_type of the ITYPE_CLASS_MAP dict
    
    Raises
    ------
    KeyError:
        Invalid key value pulled from ITYPE_CLASS_MAP, set the the sub_type value to 'default'.

    Returns
    -------
    class_: dict
        the class representation with the itype and sub_type

    """
    global ITYPE_CLASS_MAP
    try:
        class_ = ITYPE_CLASS_MAP[itype][sub_type]
    except KeyError:
        class_ = ITYPE_CLASS_MAP[itype]['default']
    return class_
    
