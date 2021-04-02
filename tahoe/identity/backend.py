"""
IdentityBackend has methods for managing user, org and input config.
"""

import jwt

if __name__ != 'tahoe.identity.backend':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
import tahoe


_P = {"_id":0} 
"""Default projection for MongoDB queries."""


class DuplicateUserError(ValueError):
    """The username(email) already exists in DB."""
    pass

class DuplicateOrgError(ValueError):
    """The orgname already exists in DB."""
    pass

class _IdentityBackendBase():
    """
    Parent of both IdentityBackend and MockIdentityBackend so that
    same methods are not written twice.

    Identity DB stores user, org and input-config data. IdentityBackend
    is a python class used to interact with identity DB. It has special
    methods to manage users, orgs and input-configs. Inherits the
    special methods from `_IdentityBackendBase`.

    Warning
    -------
    If you are writing new methods for this class, choose method
    names that do not conflict with `pymongo.Collection` because
    IdentityBackend has that as a higher priority parent class.
    """

    def create_superuser(self, email, password, name):
        return NotImplemented
        

    def create_user(self, email, password, name):
        """
        Creates an user with specified email address.

        Paramters
        ---------
        email : str
            The email address of the user.

            Note that email address is also the username and the
            unique identifier of a user in TAHOE.
        password : str
            Plaintext password of the user.
        name : str
            Full name of the user

        Returns
        -------
        tahoe.identity.User
            The creatd user object.

        Raises
        ------
        tahoe.identity.backend.DuplicateUserError
            If email address is already registered.
        """
        
        if self.user_exists(email):
            raise DuplicateUserError("Username (email) already exists!")
        
        return tahoe.identity.User(email, password, name, _backend=self)

##    def create_org(self, orgname, user, admin, name):
##        """
##        Creates an Org with specified orgname.
##
##        Paramters
##        ---------
##        orgname : str
##            The orgname of the Org. `orgname` is the unique identifier
##            of an Org in TAHOE.
##        user : (list of) tahoe.Idenity.User or User._hash
##            Users of the Org.
##        admin : (list of) tahoe.Idenity.User or User._hash
##            Users of the Org.
##        name : str, optional
##            Full name of the Org
##
##        Returns
##        -------
##        tahoe.identity.Org
##            The creatd Org object.
##
##        Raises
##        ------
##        tahoe.identity.backend.DuplicateError
##            If `orgname` is already registered.
##        """
##        
##        if self.user_exists(email):
##            raise DuplicateUserError("Username (email) already exists!")
##        
##        return tahoe.identity.User(email, password, name, _backend=self)

    def find_user(self, email=None, _hash=None, p=_P, parse=False):
        """
        Find user by email address or `_hash`.

        Note that both `email` and `_hash` are unique for a Tahoe user.
        If both `email` and `_hash` are given, `email` is used.

        Parameters
        ----------
        email : str, optional
            Email address of user, either `email` or `_hash` is required.
        _hash : str, optional
            `_hash` of the user, either `email` or `_hash` is required.
        p : dict
            MongoDB projection
        parse : bool
            If True the dict is parsed into tahoe object.

        Returns
        -------
        None
            If user does not exist.
        dict
            If parse=False.
        tahoe.identity.user.User
            If parse=True.
        """

        if email is None and _hash is None:
            raise ValueError("Either 'email' or '_hash' is required")        

        if email:
            thisuser = tahoe.identity.User(email, _backend=tahoe.NoBackend())
            _hash = thisuser._hash
        r = self.find_one({"itype":"object",
                           "sub_type":"cybexp_user",
                           "_hash": _hash}, p)
        if parse:
            r = tahoe.parse(r, backend=self, validate=False)
        return r

    def find_org(self, orgname=None, _hash=None, p=_P, parse=False):
        """
        Find organization by `orgname` or `_hash`.

        Note that both `orgname` and `_hash` are unique for a Tahoe Org.
        If both `orgname` and `_hash` are given, `orgname` is used.
        `Org.orgname` must not be confused with `Org.name`.

        Parameters
        ----------
        orgname : str
            Unique orgname of Org, either `orgname` or `_hash` is required.
        _hash : str, optional
            `_hash` of the org, either `orgname` or `_hash` is required.
        p : dict
            MongoDB projection
        parse : bool
            If True the dict is parsed into tahoe object.

        Returns
        -------
        None
            If org does not exist.
        dict
            If parse=False.
        tahoe.identity.user.Org
            If parse=True.
        """

        if orgname is None and _hash is None:
            raise ValueError("Either 'orgname' or '_hash' is required") 

        if orgname:
            mock_user = tahoe.identity.User("mock_user",
                                        _backend=tahoe.NoBackend())
            thisorg = tahoe.identity.Org(orgname, [mock_user], [mock_user],
                                        _backend=tahoe.NoBackend())
            _hash = thisorg._hash
        r = self.find_one({"itype":"object",
                           "sub_type":"cybexp_org",
                           "_hash": _hash}, p)

        if parse:
            r = tahoe.parse(r, backend=self)
        return r

    def get_all_plugin(self, enabled=True):
        """
        Get names of valid input plugins.

        An input plugin implements one particular method to fetch
        data from an input source. Examples are - realtime websocket,
        read from a file, call an api etc.

        Parameters
        ----------
        enabled : bool, default=True
            If `True` get only the plugins currently enabled/running.

        Returns
        -------
        all_plugin : list
            A list of all plugin names (each plugin name as a string).
        """
        
        ae = tahoe.Attribute('enabled', enabled)
        q = {'sub_type': 'cybexp_input_config', '_cref': ae._hash}
        p = {'_id': 0, 'data.plugin': 1}
        r = self.find(q, p)
        all_plugin = [c['data']['plugin'][0] for c in r]
        return all_plugin

    def get_config(self, plugin_lst=None, name_lst=None, enabled=True):
        """
        Gets all input configurations in this IdentityBackend.

        This method is used by input module to lookup existing
        input configs in the database.

        Parameters
        ----------
        plugin_lst : list, optional
            The list of input plugin names to fetch from DB.
            
            Example: `plugin_lst = ['websocket']`.
        name_lst : list, optional
            The list of config names to fetch from DB.

            Note: name is the unique identifier of an input config.
            Example: `plugin_lst = ['unr-honeypot-london']`.
        enabled : bool, default=True
            Only fetch the input configs currently enabled/running.

        Returns
        -------
        r : list
            A list of input configs (each config as a dictionary).
        """
        
        ae = tahoe.Attribute('enabled', enabled)
        
        q = {'sub_type': 'cybexp_input_config', '_cref': {'$eq': ae._hash}}
            
        if plugin_lst or name_lst:
            _hash_lst = []

            if plugin_lst:
                for p in plugin_lst:
                    ap = tahoe.Attribute('plugin', p)
                    _hash_lst.append(ap._hash)

            if name_lst:
                  for n in name_lst:
                      an = tahoe.Attribute('name', n)
                      _hash_lst.append(an._hash)
            
            q['_cref']['$in'] = _hash_lst
        
        r = self.find(q, {'_id': 0})
        return list(r)

    def org_exists(self, orgname):
        """
        Returns True if orgname exists in this IdenityBackend

        Note that orgname is the unique identifier of a cybexp org.

        Parameters
        ----------
        orgname : str
            The unique identifier of a cybexp org.

        Returns
        -------
        bool
            True if orgname exists, False otherwise.
        """
        
        return self.find_org(orgname, {**_P, "_hash":1}) is not None

    def user_exists(self, email):
        """
        Returns True if email (username) exists in this IdenityBackend.

        Note that email address is also the username and unique
        identifier of a user in cybexp database.

        Parameters
        ----------
        email : str
            The unique identifier of a cybexp user.

        Returns
        -------
        bool
            True if email exists, False otherwise.
        """
        
        return self.find_user(email, {**_P, "_hash":1}) is not None
    
    
class IdentityBackend(tahoe.MongoBackend, _IdentityBackendBase):
    """
    Used to interact with identity database.

    Identity DB stores user, org and input-config data. IdentityBackend
    is a python class used to interact with identity DB. It has special
    methods to manage users, orgs and input-configs. Inherits the
    special methods from `_IdentityBackendBase`.
    """

    def __init__(self, mongo_url=None, dbname="identity_db",
                 collname="instance", create=False, **kwargs):
        super().__init__(mongo_url, dbname, collname, create, **kwargs)
        
    
class MockIdentityBackend(tahoe.backend.MockMongoBackend, _IdentityBackendBase):
    """
    MockIdentityBackend uses `mongomock` for testing.

    Lookup 'pyhon mongomock library' to know more about mongomock.
    Identity DB stores user, org and input-config data. IdentityBackend
    is a python class used to interact with identity DB. It has special
    methods to manage users, orgs and input-configs. Inherits the
    special methods from `_IdentityBackendBase`.
    """

    def __init__(self, mongo_url=None, dbname="identity_db",
                 collname="instance", create=False, **kwargs):
        super().__init__(mongo_url, dbname, collname, create, **kwargs)


