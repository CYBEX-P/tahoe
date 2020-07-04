"""
An attribute holds a single piece of information, like an IP address.
"""

import pdb

if __name__ != 'tahoe.attribute':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
import tahoe



# === Global Variables ===

dtresolve = tahoe.misc.dtresolve

_P = {'_id': 0}
"""Default projection for MongoDB queries"""



class Attribute(tahoe.Instance):
    """
    An attribute holds a single piece of information, like an URL.

    Attributes
    ----------
    itype : str
        Constant value `attribute`. (Automatically set)
    sub_type : str
        Type of the `attribute`, e.g. `ipv4, email-addr`.
    data : int/float/str/bool/None
        Data of the Attribute. e.g. `1.1.1.1`. JSON has only 4
        basic types: `number (float), str, bool, None`. However,
        python and BSON (MongoDB format) can also store `int`.
    _hash : str
        SHA-256 digest of ``<itype, sub_type, data>``.
        A globally unique but reproducible ID of the attribute.
    _backend : tahoe.backend.Backend, default=NoBackend()
        Data storage. Use `NoBackend` for only data
        sharing and `MongoBackend` for storing the data.
        For performance, `_backend` should be a class variable not an
        instance variable. Set it like ``Instance._backend = backend``.


    Examples
    --------
    Creating an `Attribute` with `NoBackend`::

        >>> from tahoe import Attribute
        >>> a = Attribute('ipv4', '1.1.1.1')
        >>> print(a)
        '{"itype": "attribute", "sub_type": "ipv4", "data": "1.1.1.1",
        "_hash": "78d01c690f21c6d5519f164bf7e4f17b6dc825c46ec89aa8..."}'
        >>> print(a._backend)
        NoBackend

    Creating an `Attribute` with `MongoBackend`::

        >>> from tahoe import Instance, Attribute, MongoBackend
        >>> backend = MongoBackend('mongodb://localhost')
        >>> Instance._backend = backend
        >>> a = Attribute('ipv4', '1.1.1.1')
        >>> print(a._backend)
        MongoBackend('localhost:27017', 'tahoe_db', 'instance')
    
    Example of an ipv4 Attribute in JSON format::

        {
            "itype" : "attribute",
            "sub_type" : "ipv4",
            "data" : "1.1.1.1"
            "_hash" : "78d01c690f21c6d5519f164bf7e4f17b6dc825c46e2c..."
        }

    More examples in tahoe.tests.attribute.attribute_test

    Notes
    -----
    An attribute's ``_backend`` can be set in 3 ways:

    1. ``Instance._backend = backend`` (recommended)
    2. ``Attribute._backend = backend`` (not recommended)
    3. ``a = Attribute('ipv4', '1.1.1.1', _backend=_backend)``

    Never use 2. Use 3 only if you want a different `_backend` than the
    default class `_backend`.


    Warning
    -------
    DO NOT change the value for any field. E.g::
    
        >>> a.data = "2.2.2.2"
        >>> a.sub_type = "url"
        
    The behavior is undefined.
    """

        
    def __init__(self, sub_type, data, **kwargs):
        """
        Parameters
        ----------
        sub_type : str
            Type of the `Attribute`, e.g. ``ipv4, email-addr``.
        data : int or float or str or bool or None
            Data of the Attribute. e.g. ``1.1.1.1``. JSON has only 4
            basic types: `number (float), str, bool, None`. However,
            python and BSON (MongoDB format) can also store `int`.
        **kwargs 
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

            If data is not `int/float/str/bool/None`.
        """
        
        
        self._validate_data(data)

        self.itype = 'attribute'
        self.data = data

        super().__init__(sub_type=sub_type, **kwargs)


    # Public methods in alphabetical order    
        
    def count(self, start=0, end=0, category='all', context='all'):
        """
        Count the number of events where this attribute is seen.

        Parameters
        ----------
        start : int or float, default=0
            Unix time (UTC). Count events newer than `start`.
        end : int or float, default=0
            Unix time (UTC). Count events older than `end`. 0 means now.
        category: {"all", "benign", "malicious", "unknown"},
        default="all"
            If "malicious", count only malicious events.
        context: {"all", "benign", "malicious"}, default="all"
            If "malicious", count events where this attribute was seen
            in a malicious context.

        Returns
        -------
        count : int
        """
        
        self._validate_param(start=start, end=end)

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
        
        return self._backend.count_documents(q)

    def events(self, p=_P, start=0, end=None, limit=0, skip=0, page=1,
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
            Unix time (UTC). Fetch events older than `end`.
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


    # Protected & Private Methods in alphabetical order

    def _validate_data(self, data):        
        if not isinstance(data, (int, float, str, bool, type(None))):
            raise TypeError(f"data = {type(data)}, expected" \
                " (int, float, str, bool, NoneType)")



    
            
        
                         



