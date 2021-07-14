"""A piece of TAHOE data is called an instance."""

# Common notations in code
# ========================
# q : dict, query (MongoDB)
# p : dict, projection (MongoDB)
# r : Cursor/empty_list/dict/None, return value of query
#     pymongo.cursor.Cursor -- if find() returns data
#     empty_list [] -- if find() has no match
#     dict -- if find_one() returns data
#     None -- if find_one() has no match
# a : dict/Attribute, TAHOE attribute
# e : dict/Event, TAHOE event
# i : dict/Event, TAHOE instance (attribute, object, event, etc.)
# o : dict/Object, TAHOE object
# u : str, TAHOE _hash field (SHA256 hash)


from collections import defaultdict
import copy
import json
import hashlib


if __name__ in ["__main__", "instance"]:
    from backend import Backend, NoBackend
    from misc import dtresolve, limitskip, branches, features, canonical
    from parse import parse, getclass
    from exceptions import DependencyError, BackendError
else:
    from .backend import Backend, NoBackend
    from .misc import dtresolve, limitskip, branches, features, canonical
    from .parse import parse, getclass
    from .exceptions import DependencyError, BackendError
  

# === Global Variables ===

_P = {'_id': 0}  # Default projection for MongoDB queries
_LIM = 10


class Instance():
    """
    A piece of TAHOE data is called an Instance.

    Attributes
    ----------
    itype : {"attribute", "object", "event", "session", "raw"}
        Instance type.
    sub_type : str
        Instance sub type. e.g. "ipv4", "email_addr"`.
    _hash : str
        SHA-256 digest of ``self._unique``.
        A globally unique but reproducible ID of the instance.
    _backend : tahoe._backend.Backend
        Data storage. Default `NoBackend`. Use `NoBackend` for only
        data sharing and `MongoBackend` for storing the data.

        Each _backend variable maintains a database connection. So,
        ideally this attribute belongs to the class not an instance.
        This reduces number of database connections.

    Examples
    --------
    Setting default MongoBackend::

        >>> from tahoe import MongoBackend, Instance, Attribute
        >>> _backend = MongoBackend()
        >>> Instance._backend = _backend
        >>> a = Attribute("ipv4", "1.1.1.1")
        >>> print(a._backend)
        MongoBackend('mongodb://localhost:27017', 'tahoe_db', 'instance')
    """

    _backend = NoBackend()
    """For performance, `_backend` should be a class variable not an
    instance variable. To set: ``Instance.set_backend(_backend)``"""


    def __init__(self, **kwargs):
        if '_backend' in kwargs:
            self._backend = kwargs.pop('_backend')  # to override class _backend
        self._validate_param(_backend=self._backend)
        
        sub_type = kwargs.pop("sub_type")
        self._validate_param(sub_type=sub_type)

        self.sub_type = sub_type
        self._hash = hashlib.sha256(self._unique).hexdigest()

        dup = self._backend.find_one({"_hash" : self._hash}, _P)
        if dup:
            for k, v in dup.items():
                setattr(self, k, v)
        else:
            self._backend.insert_one(self.doc)

    
    def __str__(self):
        return self.json


    # Public methods

    def branches(self):
        d = self.data
        
        def branch(val, old=[]):
            b = []
            if isinstance(val, dict):
                for k in val: b += branch(val[k], old+[str(k)])
            elif isinstance(val, list):
                for k in val: b += branch(k, old)
            else:
                b.append(old + [val])
            return b

        return branch(d)


    def delete(self, delete_children=True):
        """Deletes this instance and all children."""

        r = self._backend.find_one({'_ref': self._hash}, {**_P, '_hash': 1})
        if r:
            raise DependencyError(f"referred in {r['_hash']}")
        self._backend.delete_one({'_hash': self._hash})

        if not hasattr(self, '_cref') or not delete_children:
            return

        r = self._backend.find({'_hash': {'$in': self._cref}})
        for i in r:
            I = parse(i, self._backend, validate=False)
            try:
                I.delete()
            except DependencyError:
                pass

                   
    @property    
    def doc(self):
        ignore_keys = ['_backend']
        d = {}
        for k, v in vars(self).items():
            if k not in ignore_keys:
                d[k] = v
        return d


    def get_parents(self, q={}, p=_P):
##      I didn't make parents a property like doc or json because,
##      database query takes a long time. It is not a good practice
##      to wrap time consuming functions into properties.
        
        return self._backend.find({"_ref": self._hash, **q}, p)


    @property
    def json(self):
        return json.dumps(self.doc)


    def related(self, itype='all', level=1, p=_P, start=0, end=0,
            limit=0, skip=0, page=1, category='all', context='all'):
        """
        Get instances related to self.

        TAHOE stores data as network graphs. The nodes in the graph are
        TAHOE instances like attributes, objects, events, sessions etc.
        If two TAHOE instances are connected in a graph in the db, we
        call them related instances. This method gets all instances
        related to self.

        Parameters
        ----------
        itype: {"all", "attribute", "object", "event"}
            Get the related instances of `itype` only.
        level: int
            
        p: dict
            the projection of the database query
            Default: '_P' or whatever is the default id
        start: int/float

        end: int/float

        limit: int

        skip: int

        page: int

        """

        if not isinstance(level, int):
            raise TypeError(f"type(level)={type(level)}, expected 'int'!")
        if level < 0:
            raise ValueError(f"Expected level>=0 got '{level}'!")
        elif level == 0:
            return [], page, 1
        
        rel_hash = self.related_hash(level, set(), start, end,
                        limit, skip, page, category, context)
        if not rel_hash:
            return [], page, 1

        q = {"_hash": {"$in": rel_hash}}
        if itype != 'all':
            q.update({"itype": itype})

        rel = [i for i in self._backend.find(q, p)]
 
        return rel, page, page+1

        
    def related_hash(self, level=0, visited=None, start=0, end=0,
            limit=0, skip=0, page=1, category='all', context='all'):
        """Gets the _hash of all instances related to self."""

        if visited is None:
            visited = set()
        
        if not isinstance(level, int):
            raise TypeError(f"Expected type(level)='int' got '{type(level)}'!")
        if level < 0:
            raise ValueError(f"Expected level>=0 got '{level}'!")
        elif level == 0:
            return []

        all_rel_hash = set()

        p = {**_P, "itype": 1, "sub_type": 1, "_hash": 1, "_ref": 1}
        r = self.events(p, start, end, limit, skip, page, category, context)
        
        for e in r:
            if e['_hash'] in visited:
                continue
            else:
                visited.add(e['_hash'])
            E = parse(e, self._backend, validate=False)
            this_rel_hash = E.related_hash(level-1, visited)
            all_rel_hash.update(this_rel_hash)

        return list(all_rel_hash)


    @classmethod
    def set_backend(cls, _backend):
        """Sets _backend of the class in Python."""
        
        cls._backend = _backend


    # Protected & Private methods

    def _is_instance(self, instance, type_str):
        """Returns True instance of type `tahoe.type_str`."""

        instance_type = getclass(type_str)
        return isinstance(instance, instance_type)


    @property
    def _unique(self):
        """Globally unique representation of the instance."""

        unique = self.itype + self.sub_type + canonical(self.data)
        return unique.encode('utf-8')


    def _update(self, update=None):
        """
        Updates fields of a TAHOE instance in both backend and Python
        object.

        Parameters
        ----------
        update : dict or None
            If None the Python object just syncs with backend.

        Warning
        -------
        Does not update `_hash` or `_ref`.        
        """

        q = {"_hash":self._hash}
        if update is None:
            ret = self._backend.find_one(q, _P)
        else:
            ret = self._backend.find_one_and_update(q, {"$set":update},
                                                    _P, return_document=True)
        if ret is None:
            raise BackendError('Cannot find instance in backend!')
        for k, v in ret.items():
            setattr(self, k, v)


    # Methods to validate common function parameters

    def _validate_param(self, **kwargs):
        """Basic validation of some commmon function parameters."""
        
        for k, v in kwargs.items():
            if k == '_backend':
                if not isinstance(v, Backend):
                    raise TypeError(f"{k}={type(v)}, expected 'tahoe.Backend'")
            elif k == 'category':
                if v not in {'benign', 'malicious', 'unknown'}:
                    raise ValueError(f"{k} = '{v}'")
            elif k == 'context':
                if v not in {'benign', 'malicious', 'unknown'}:
                    raise ValueError(f"{k} = '{v}'")
            elif k in ['end', 'start']:
                if not isinstance(v, (int, float)):
                    raise TypeError(f"{k} = {type(v)}, expected 'int/float'")
            elif k in ['limit', 'skip', 'page']:
                if not isinstance(v, int):
                    raise TypeError(f"{k} = {type(v)}, expected 'int'")
                if v < 0:
                    raise ValueError(f"{k} = '{v}'")
            elif k == 'orgid':
                if not isinstance(v, str):
                    raise TypeError(f"{k} = {type(v)}, expected 'str'")
            elif k == 'sub_type':
                if not isinstance(v, str):
                    raise TypeError(f"{k} = {type(v)}, expected 'str'")
                if not v.isidentifier():
                    raise ValueError(f"{k} = '{v}'")
            elif k == 'timestamp':
                if not isinstance(v, (int, float)):
                    raise TypeError(f"{k} = {type(v)}, expected 'int/float'")
            else:
                raise KeyError(f"{k} = '{v}'")



class OES(Instance):
    """This is the parent class for Object, Event, Session."""

    # public methods

    def add_instance(self, data):
        """"
        Add an attribute/object to self.

        Parameters
        ----------
        data : tahoe.Attribute, tahoe.Object or list
            The attribute or object or the list of attributes and
            objects to add to self.
        """"
        
        self.edit(add_data=data)


    def remove_instance(self, data):
        """
        Remove an attribute/object from self.
        
        Parameters
        ----------
        data : tahoe.Attribute, tahoe.Object or list
            The attribute or object or the list of attributes and
            objects to remove from self.
        """
        
        self.edit(remove_data=data)


    def replace_instance(self, old, new):
        """
        Replace one or more attribute/object with others in self.
        
        Parameters
        ----------
        old : tahoe.Attribute, tahoe.Object or list
            The attribute or object or the list of attributes and
            objects to remove from self.
        new : tahoe.Attribute, tahoe.Object or list
            The attribute or object or the list of attributes and
            objects to add to self.
        """
        
        self.edit(new, old)


    def edit(self, add_data=None, remove_data=None):
        """
        Add or remove one or more `Attribute/Object`.

        Note that, editing an instance, modifies `self.data,
        self._cref, self._ref, self._hash` of `self`
        and all parents in `self._backend` (e.g. MongoDB).
        
        Parameters
        ----------
        add_data : list of Attribute, Object, default=[]
            Attributes or Objects to be added.
        remove_data : list of Attribute, Object, default=[]
            Attributes or Objects to be removed.

        Raises
        ------
        TypeError
            If `add_data` or `remove_data` is not a list of
            ``Attribute`` or ``Object``
        ValueError
            If any `Instance` in `data` is already a child of this.
            
            If any `Instance` in `remove_data` is not a child of this.

            If both `add_data` and `remove_data` are empty.
            
        Warning
        -------
        Parents will become invalid::

            >>> a1 = Attribute('username', 'johndoe')
            >>> a2 = Attribute('password', '123456')
            >>> o1 = Object('test1', a1)
            >>> o2 = Object('test2', o1)
            >>> o1.add_instance(a2)
            >>> r = o2._backend.find_one({'_hash': o2._hash})
            >>> r is None
            True
        """
        b = self.__dict__.pop('_backend', None)

        old = copy.deepcopy(self)

        if b:
            old._backend = b
            self._backend = b

        if add_data is None:
            add_data = []
        else:
            add_data = self._validate_instance(
                            add_data, ['attribute', 'object'])

        if remove_data is None:
            remove_data = []
        else:
            remove_data = self._validate_instance(
                            remove_data, ['attribute', 'object'])

        if not (add_data + remove_data):
            raise ValueError("add_data or remove_data required")

        for i in add_data:
            if i._hash in self._cref:
                raise ValueError(f"cannot add existing instance: {i._hash}")

        remove_data_ref = set()
        for i in remove_data:
            if i._hash not in self._cref:
                raise ValueError("cannot remove non-existing instance: "
                                 + f"{i._hash}")
            remove_data_ref.add(i._hash)

        new_data = add_data
        q = {'_hash': {'$in': self._cref}}
        for i in self._backend.find(q, _P):
            if i['_hash'] not in remove_data_ref:
                new_data.append(parse(i, self._backend, validate=False))

        self.data = self._makedata(new_data)
        self._cref, self._ref = self._makeref(new_data)
        self._hash = hashlib.sha256(self._unique).hexdigest()

        self._backend.update_one({'_hash': self._hash}, {'$set': self.doc},
                                 upsert=True)

        if old._hash == self._hash:
            return
        
        r = self._backend.find({'_cref': old._hash}, {'_id':0})
        for i in r:
            I = parse(i, self._backend, validate=False)
            I.edit(add_data=self, remove_data=old)

        old.delete()
        

    # protected or private methods
    
    def _makedata(self, data, prev_data=None):
        """
        Note, data is a list of Attribute, Object; whereas prev_data
        is a dict (json object). add_instance() uses prev_data.

        Utility function to pull the data from that was used to initialize an OES object. Creates a default dictionary 
        in list format to hold sub_types and their corresponding data.  'data' is then iterated through and its values
        are pulled and stored in the default dictionary. When finished with 'data', that dictionary with the pulled 
        data values is then returned.

        Parameters
        ----------
        data: list of attributes or object
            contains the data sets for a Tahoe object, event, or session
        prev_data: dict json object
            the previous data set before the set of data that is going to be appended
            
        Returns
        -------
        d: dictionary
            dictionary containing the data pulled from 'data'. The sub_types and their data.    

        """
        
        d = defaultdict(list)
        if prev_data: d.update(prev_data)
        for i in data:
            i_data_doc = {i.sub_type: [i.data]}
            for k, v in i_data_doc.items():
                d[k] += v
        return dict(d)


    def _makeref(self, data, prev_cref=None, prev_ref=None):
        """prev_cref and prev_ref are used by add_instance()"""

        _cref = []
        _ref = []
        if prev_cref: _cref = prev_cref  # children
        if prev_ref: _ref = prev_ref  # children + grand children
        for i in data:
            _cref.append(i._hash)
            _ref.append(i._hash)
            if hasattr(i, '_ref'):  # type(i) == Object
                _ref += i._ref
        return list(set(_cref)), list(set(_ref))


    def _validate_data(self, data):
        return self._validate_instance(data, ['attribute', 'object'])


    def _validate_instance(self, instance, type_list):
        """
        Ensures the the passed instance is valid by ensuring that the passed variables within 'instance'
        are of the type they are by comparing them to the type_list.

        Parameters
        ----------
        instance: a dictionary of string values
            the key value of this function. Items in here will be tested for correct datatype corresponding
            to type_list.
        type_list: list of strings
            the variable names and their corresponding datatypes that will be used to ensure the datatype
            of the values in instance are correct.

        Raises
        ------
        ValueError:
            'instance' is empty
        TypeError:
            the current iteration of data in 'instance' is either not of type tahoe or not a type 
            that is in the passed type_list.
        
        Returns
        -------
        instance: List 
            set list of the instance object 

        """
        type_list = [getclass(t) for t in type_list]
        
        if not isinstance(instance, list):
            instance = [instance]
        instance = list(set(instance))
        if len(instance)==0:
            raise ValueError("data cannot be empty")
        for i in instance:
            if not any([isinstance(i, t) for t in type_list]):
                raise TypeError("instances must be of type tahoe "
                                + " or ".join([str(t) for t in type_list]))
        return instance


















