
ITYPE_CLASS_MAP = {}

def parse(instance, backend, validate=True):
    if isinstance(instance, str): instance = json.loads(instance)
    instance.pop("_id", None)
    t = ITYPE_CLASS_MAP.get('attribute')('mock', 'mock')
    t.__dict__ = instance
    t.__class__ = ITYPE_CLASS_MAP.get(instance['itype'])
##    if validate: t.validate()
    return t

def _create_itype_class_map():
    from .attribute import Attribute
    from .object_ import Object

    ITYPE_CLASS_MAP['attribute'] = Attribute
    ITYPE_CLASS_MAP['object'] = Object