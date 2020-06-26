"""
An Event, e.g. an email, consists of one or more Attributes or Objects,
along with a timestamp.

A TAHOE Event as a network graph::

    [{
      "itype" : "attribute",
      "sub_type" : "ip",
      "data" : "0.1.2.3",
      "_hash" : "0xA1..."
    },
    {
      "itype" : "object",
      "sub_type" : "source",
      "_ref" : [ "0xA1..." ],
      "_hash" : "0xB1...",
    },
    {
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
    },
    {
      "itype" : "event",
      "sub_type" : "file_download",
      "timestamp" : 1568315400,
      "category" : "malicious",
      "malicious_score" : -1.0,
      "_mal_ref" : [ "0xB1...", "0xB2..." ],
      "_ref" : [ "0xB1...", "0xB2..." ],
      "_hash" : "0xE1...",
    }]

This above event is a graph with `5` edges: `0xE1 --> 0xB1, 0xE1 -->
0xB2, 0xB2 -->, 0xA2, 0xB2 --> 0xA3, 0xB1 --> 0xA1`. So, both the
objects and their attributes must be included in the list.
"""


__version__ = '0.1'
__author__ = 'Farhan Sadique <qclass@protonmail.com>'
__date__ = '21 June 2020'

import pdb

if __name__ != 'tahoe.event.event':
    import sys
    sys.path += ['..', '../..']
    del sys
import tahoe


# === Global Variables ===

_P = {'_id': 0}
"""Default projection for MongoDB queries"""



class Event(tahoe.OES):
    """
    An Event, e.g. an email, consists of one or more Attributes
    or Objects, along with a timestamp.

    Attributes
    ----------
    itype : str
        Constant value `event`. (Automatically set)
    sub_type : str
        Type of the `event`, e.g. `file_download`.
    data : dict (json object)
        Data of the event. Dict is JSON object. So keys are `str`.
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
        of `__init__` is a `list`. See `Event.__init__()` for more.
    orgid : str
        _hash (unique id) of source organization. `orgid` identifies
        the event owner.
    timestamp : float
        Unix timestamp (UTC) denoting when the event was generated.
    category : {"benign", "malicious", "unknown"}
        Denotes if the event is benign, malicious or not anlayzed yet.        
    _hash : str
        SHA-256 digest of `<itype, sub_type, data>`.
        A globally unique but reproducible ID of the attribute.
    _backend : tahoe.backend.Backend, default=NoBackend()
        Data storage. Use `NoBackend` for only data
        sharing and `MongoBackend` for storing the data.
        For performance, `_backend` should be a class variable not an
        instance variable. Set it like ``Instance._backend = backend``.
    _cref : list (JSON array)
        A TAHOE `Event` refers other `Instances (Attribute/Object)`,
        called children. `_cref` stores the `_hashes` of child instances.
        Order of the `_hashes` is insignificant.
    _ref : list (JSON array)
        A TAHOE `Event` refers other `Instances (Attribute/Object)`.
        , which in turn can refer other tahoe `Instances`. `_ref` stores
        the `_hash` of all these `Instances`. Order of the `_hashes` is
        insignificant. `_cref` is a subset of `_ref`.
    _ben_ref : list (JSON array)
        Subset of ``_ref`` referring attributes or objects that were
        seen in a benign context in this event.
    _mal_ref :
        Subset of ``_ref`` referring attributes or objects that were
        seen in a malicous context in this event.
        

    Examples
    --------

    Creating an `Event` with `NoBackend`::

        >>> a1 = Attribute("att_type", "value")
        >>> o1 = Object("obj_type", a1)
        >>> o1.data
        {'att_type': ['value']}
        >>> o1._backend
        NoBackend()
        >>> o1._hash
        'a730521ee3b1f3665f25634de1421942d52119b58bf68498cd2
        beba8d73925be'

    More examples in :ref:`tahoe.tests.object.event_test`

    Notes
    -----
    An event's `_backend` can be set in 3 ways:

    1. `Instance._backend = backend` (recommended)
    2. `Event._backend = backend` (not recommended)
    3. `O = Object("file", [a], _backend=backend)` (not recommended)

    Never use 2. Use 3 only if you want a different `_backend` than the
    default class `_backend`.


    Warning
    -------
    DO NOT change the value for any field. E.g.::
    
        e.data["ipv4"][0] = "2.2.2.2"
        e.data = {"ipv4": ["2.2.2.2"]}
        e._ref.append("af2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e989156
        2113d8a62add1bf")

    The behavior is undefined.
 
    """
    
    def __init__(self, sub_type, data, orgid, timestamp, **kwargs):
        """
        Parameters
        ----------
        sub_type : str
            Type of the `event`, e.g. `file`.
        data : list of tahoe.Attribute or tahoe.Object  
            Note, this list is transformed into a dict (JSON object),
            which can be accessed as `self.data`. Also the uuids of the
            attributes and objects are placed in the `self._cref`.
        orgid : str
            _hash (unique id) of source organization. `orgid`
            identifies the event owner.
        timestamp : int or float
            Unix timestamp (UTC) denoting when the event was generated.

        
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
        ben_data : list of tahoe.Attribute or tahoe.Object
            Instances seen in this event in benign context. Their
            _hashes are stored in _ben_ref and used in ThretRank.
        mal_data : list of tahoe.Attribute or tahoe.Object
            Instances seen in this event in malicious conext. Their
            _hashes are stored in _mal_ref and used in ThretRank.
        
        Raises
        ------
        TypeError
            If sub_type is not `str`.

            If data is not `Atrribute or Object`.
        """

        self._validate_param(orgid=orgid, timestamp=timestamp)
        data = self._validate_data(data, ['attribute', 'object'])
        
        self.itype = 'event'
        self.orgid = orgid
        self.timestamp = float(timestamp)
        self.category = 'unknown'
        
        self.data = self._makedata(data)
        self._cref, self._ref = self._makeref(data)
        self._ben_ref, self._mal_ref = [], []

        ben_data = kwargs.pop('ben_data', [])
        mal_data = kwargs.pop('mal_data', [])

        self._ben_ref, self._mal_ref = \
            self._make_context_ref(ben_data, mal_data)
        
        super().__init__(sub_type=sub_type, **kwargs)


    def get_context(self, data):
        if not isinstance(data, list):
            data = [data]
        if not self.isparent(data):
            raise ValueError("instance is not a child")
        
        context = []
        for I in data:
            if I._hash in self._ben_ref:
                context.append("benign")
            elif I._hash in self._mal_ref:
                context.append("malicious")
            else:
                context.append("unknown")
        return context


    def isparent(self, data):
        data = self._validate_data(data)
        return all([I in self._cref for I in data])

    def set_category(self, category):
        """
        Parameters
        ----------
        category : {"benign", "malicious", "unknown"}
            Denotes if the event is benign or malicious or unknown.
        """
        self._validate_param(category=category)
        self._update({'category': category})

    def set_context(self, data, context, *args):
        """
        Parameters
        ----------
        data : list of tahoe.Attribute or tahoe.Object
        context : {"benign", "malicious", "unknown"}
            The context in which data were seen in this event.
        *args : variable length argument list

        More Parameters
        ---------------
        data2 : list of tahoe.Attribute or tahoe.Object
        context2 : {"benign", "malicious", "unknown"}
        data3 : list of tahoe.Attribute or tahoe.Object
        context3 : {"benign", "malicious", "unknown"}

        Raises
        ------
        ValueError
            If data, data2, data3 are not Attribute or Object.

            If context, context2, context3 are not in
            {"benign", "malicious", "unknown"}
            
            If there are common instances between data, data2, data3

            
        Examples
        --------
        Set context of one Attribute a as malicious::

            >>> e.isparent(a)
            True
            >>> e.set_context([a], "malicious")
            >>> e.get_context(a)
            ["malicious"]

        Set contexts of multiple Attributes or Objects::

            >>> a.itype
            "attribute"
            >>> o.itype
            "object"
            >>> e.isparent([a, o])
            True
            >>> e.set_context([a, o], "benign")
            >>> e.get_context([a, o])
            ["benign", "benign"]

        Set different contexts of multiple Attributes or Objects::

            >>> e.isparent([a1, a2, o1])
            True
            >>> e.set_context([a1, o1], "benign", [a2], "malicious")
            >>> e.get_context([a1, a2, o1])
            ["benign", "malicious", "benign"]
            
        """

        if not len(args) in [0, 2, 4]:
            raise ValueError("input argumetns in data, context pairs")

        ben_data, mal_data, unk_data = None, None, None

        argsiter = iter([data, context] + list(args))
        for data, context in zip(argsiter, argsiter):
            if context == 'benign' and ben_data is None:
                ben_data = data
            elif context == 'malicious' and mal_data is None:
                mal_data = data
            elif context == 'unknown' and unk_data is None:
                unk_data = data
            else:
                raise ValueError("invalid argument: {data}, {context}")
            
        ben_ref, mal_ref = self._make_context_ref(ben_data, mal_data, unk_data)

        self._update({'_ben_ref': ben_ref, '_mal_ref': mal_ref})

    
    def _make_context_ref(self, ben_data=None, mal_data=None, unk_data=None):

        if not ben_data and mal_data and unk_data:
            return

        if ben_data:
            ben_data = self._validate_data(ben_data, ['attribute', 'object'])
            new_ben = {i._hash for i in ben_data}
        else:
            new_ben = set()

        if mal_data:
            mal_data = self._validate_data(mal_data, ['attribute', 'object'])
            new_mal = {i._hash for i in mal_data}
        else:
            new_mal = set()

        if unk_data:
            unk_data = self._validate_data(unk_data, ['attribute', 'object'])
            new_unk = {i._hash for i in unk_data}
        else:
            new_unk = set()

        if new_ben.intersection(new_mal):
            raise ValueError("instance cannot be both benign and malicious: " +
                             f"{new_ben.intersection(new_mal)}")
        if new_mal.intersection(new_unk):
            raise ValueError("instance cannot be both malicious and unknown: " +
                             f"{new_mal.intersection(new_unk)}")
        if new_unk.intersection(new_ben):
            raise ValueError("instance cannot be both benign and unknown: " +
                             f"{new_unk.intersection(new_ben)}")

        new_tot = new_ben.union(new_mal.union(new_unk))
        set_cref = set(self._cref)
        set_ben_ref = set(self._ben_ref)
        set_mal_ref = set(self._mal_ref)
        
        if not new_tot.issubset(set_cref):
            raise ValueError("instance not a child: {new_tot - set_cref}")

        for h in new_ben:
            set_ben_ref.add(h)
            if h in set_mal_ref: set_mal_ref.remove(h)
        for h in new_mal:
            if h in set_ben_ref: set_ben_ref.remove(h)
            set_mal_ref.add(h)
        for h in new_unk:
            if h in set_ben_ref: set_ben_ref.remove(h)
            elif h in set_mal_ref: set_mal_ref.remove()

        return list(set_ben_ref), list(set_mal_ref)
    

    def related_hash(self, level=0, visited=None, start=0, end=None,
                     limit=0, skip=0, page=1):

        if visited is None:
            visited = set()

        all_rel_hash = self._ref + [self._hash]

        if not isinstance(level, int):
            raise TypeError(f"level = {type(level)}")
        if level < 0:
            raise ValueError(f"level = {level}")
        elif level == 0:
            return all_rel_hash

        r = self.sessions({"itype":1,"uuid":1,"_eref":1})
        for s in r:
            S = parse(s, self._backend, validate=False)
            this_rel_hash = S.related_hash(level, visited.update(self._hash),
                                           start=statr, end=end)
            all_rel_hash.update(this_rel_hash)
        return all_rel_hash
    

    @property
    def _unique(self):
        unique = self.itype + self.sub_type + self.orgid + \
            str(self.timestamp) + tahoe.misc.canonical(self.data)
        return unique.encode('utf-8')

        





