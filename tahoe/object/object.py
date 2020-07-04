"""
An Object holds complex information, like a file.

A TAHOE Object is a network graph::

    [{
      "itype" : "attribute",
      "sub_type" : "filename",
      "data" : "virus1.exe",
      "_hash" : "0xA2..."
    },
    {
      "itype" : "attribute",
      "sub_type" : "filesize",
      "data" : 22714,
      "_hash" : "0xA3..."
    },
    {
      "itype" : "object",
      "sub_type" : "file",
      "_ref" : [ "0xA2...", "0xA3" ],
      "_hash" : "0xB2...",
    }]

The `_ref` field makes the data a graph with 3 nodes: `0xA2..,
0xA3.., 0xB2..` and 2 edges: `0xA2.. --> 0xB2.., 0xA3.. --> 0xB2..`. 
"""


if __name__ != 'tahoe.object':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
import tahoe


# === Global Variables ===

_P = {'_id': 0}
"""Default projection for MongoDB queries"""



class Object(tahoe.OES):
    """
    An Object holds complex information, like a file.

    Attributes
    ----------
    itype : str
        Constant value `object`. (Automatically set)
    sub_type : str
        Type of the `object`, e.g. `file`.
    data : dict (json object)
        Data of the object. Dict is JSON object. So keys are `str`.
        Values are `int/float/str/bool/None/list/dict`. Example::
        
            "data" : {
                "ipv4" : ["5.188.86.172"],
                "geoip" : [
                    {
                        "continent_code" : ["EU"],
                        "timezone" : ["Europe/Dublin"],
                        "country_name" : ["Ireland"],
                        "ip" : ["5.188.86.172"],
                        "longitude" : [-8.95],
                        "city_name" : ["Macroom"],
                        "region_code" : ["CO"],
                        "latitude" : [51.9],
                        "region_name" : ["County Cork"]
                    }
                ]
            }

        Note that `data` attribute is a dict whereas `data` parameter
        of `__init__` is a `list`. See `Object.__init__()` for more.    
    _hash : str
        SHA-256 digest of `<itype, sub_type, data>`.
        A globally unique but reproducible ID of the attribute.
    _backend : tahoe.backend.Backend, default=NoBackend()
        Data storage. Use `NoBackend` for only data
        sharing and `MongoBackend` for storing the data.
        For performance, `_backend` should be a class variable not an
        instance variable. Set it like ``Instance._backend = backend``.
    _cref : list (JSON array)
        A TAHOE `Object` refers other `Instances (Attribute/Object)`,
        called children. `_cref` stores the `_hashes` of child instances.
        Order of the _hashes is insignificant.
    _ref : list (JSON array)
        A TAHOE `Object` refers other `Instances (Attribute/Object)`.
        , which in turn can refer other tahoe `Instances`. `_ref` stores
        the `_hash` of all these `Instances`. Order of the _hashes is
        insignificant. _cref is a subset of _ref.
        

    Examples
    --------
    Creating an `Object` with `NoBackend`::

        >>> a1 = Attribute("att_type", "value")
        >>> o1 = Object("obj_type", a1)
        >>> o1.data
        {'att_type': ['value']}
        >>> o1._backend
        NoBackend()
        >>> o1._hash
        'a730521ee3b1f3665f25634de1421942d52119b58bf68498cd2
        beba8d73925be'

    More examples in :ref:`tahoe.tests.object.object_test`

    Notes
    -----
    An object's `_backend` can be set in 3 ways:

    1. `Instance._backend = backend` (recommended)
    2. `Object._backend = backend` (not recommended)
    3. `O = Object("file", [a], _backend=backend)` (not recommended)

    Never use 2. Use 3 only if you want a different `_backend` than the
    default class `_backend`.


    Warning
    -------
    DO NOT change the value for any field. e.g.::
    
        o.data["ipv4"][0] = "2.2.2.2"
        o.data = {"ipv4": ["2.2.2.2"]}
        o._ref.append("af2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e989156
        2113d8a62add1bf")

    The behavior is undefined.
 
    """
    
    def __init__(self, sub_type, data, **kwargs):
        """
        Parameters
        ----------
        sub_type : str
            Type of the `object`, e.g. `file`.
        data : list of Attribute, Object
            Note, this list is transformed into a dict (JSON object),
            which can be accessed as `self.data`. Also the _hashs of the
            attributes and objects are placed in the `self._cref`.
        *kwargs : dict
            keyword arguments, see *Other Parameters*.

        Other Parameters
        ----------------
        _backend : tahoe.backend.Backend, default=cls._backend
            If given the instance `_backend` will be different from
            class `_backend`. Please lookup *Python Class and Instance
            Variables* if you don't know the difference. You shouldn't
            use this parameter for normal operation. Rather Set class
            backend like `Instance._backend = backend`.

        Raises
        ------
        TypeError
            If sub_type is not `str`.

            If data is not `Atrribute or Object`.
        """

        data = self._validate_data(data)

        self.itype = 'object'
        self.data = self._makedata(data)
        self._cref, self._ref = self._makeref(data)

        super().__init__(sub_type=sub_type, **kwargs)

    def events(self, p=_P, start=0, end=0, limit=0, skip=0, page=1,
               category='all', context='all'):
        """
        Fetch related events in a time range, with pagination.
        
        Parameters
        ----------
        p : dict, default=_P={_id: 0}
            Projection for MongoDB query.
        start : int or float, default=0
            Unix time (UTC). Fetch events newer than `start`.
        end : int or float, default=None
            Unix time (UTC). Fetch events older than `end`. 0 means now.
        limit: int, default=0
            Fetch maximum `limit` events, used for pagination. `0`
            means no limit.
        skip: int, default=0
            Skip the first `skip` events, don't use this parameter.
        page: int, default=1
            ``skip = (page - 1)*limit``. Use `page` not `skip`.
        category: {"all", "benign", "malicious", "unknown"},
        default="all"
            If "malicious", count only malicious events.
        context: {"all", "benign", "malicious", "unknown"},
        default="all"
            If "malicious", count events where this object was seen
            in a malicious context.

        Returns
        -------
        r: pymongo.cursor.Cursor or []
            Iterable of events which include this object.
        """

        self._valdiate_param(start=start, end=end,
                             limit=limit, skip=skip, page=page)
        
        q = {"itype": "event", **dtresolve(start, end)}

        if category != "all":
            self._validate_param(category=category)
            q['category'] = category

        if context != "all":
            self._validate_param(context=context)
        switch = {'all': '_ref', 'benign': '_ben_ref',
                  'malicious': '_mal_ref', 'unknown': '_ref'}
        q[switch.get(context)] = self._hash
        if context == 'unknown':
            q['_ben_ref'] = {'$ne': self._hash}
            q['_mal_ref'] = {'$ne': self._hash}
            
        return self._backend.find(q, p, **limitskip(limit, skip, page))   

