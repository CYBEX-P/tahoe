"""
A TAHOE Raw documents stores raw user data.
"""

if __name__ != 'tahoe.raw':
    import sys
    sys.path = ['..'] + sys.path
    del sys
import tahoe


# === Global Variables ===

_P = {'_id': 0}
"""Default projection for MongoDB queries"""



class Raw(tahoe.Instance):
    """
    A Raw document holds raw user data.

 
    """
    
    def __init__(self, sub_type, data, orgid, timezone="UTC", **kwargs):
        if isinstance(data, str):
            data = json.loads(data)
        self.itype = 'raw
        self.data = data
        self.orgid = orgid
        self.timezone = timezone
        super().__init__(sub_type=sub_type, **kwargs)
      
    def add_ref(self, _ref):
        if hasattr(self, '_ref'):
            _ref = self._ref + _ref
        _ref = list(set(_ref))
        self._update({'_ref': _ref})
