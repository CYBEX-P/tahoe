"""TAHOE DAM Module does access control."""

from .backend import MongoBackend, MockMongoBackend

if __name__ != 'tahoe.dam':
    import sys, os
    sys.path = ['..'] + sys.path
    del sys, os
import tahoe


class ImpossibleError(Exception):
    """This should not happend exception!"""
    pass


class _DAMBase(): 
    """
    Parent of both DAM and MockDAM so that same methods are not
    written twice.

    DAM inherits all methods from MongoBackend (or MockMongoBackend).
    It decorates the find and find_one methods to modify the query
    dict. The decorator take in a key-word argument called `user` &
    ensures the user finds only the data they have access to.
 
    Notes
    -----
    For DAM to work _id_backend must have users, orgs & _acl.

    See Also:
    ---------
    MongoBackend: tahoe.MongoBackend
    """       

    def enforce_acl(func):
        """Decorator that enforces ACL for find/find_one."""
      
        def wrapper(self, query, *args, **kwargs):
            """
            Gets `orgs_user_of` for `_DAMBase.user` and adds that to
            the query only when query includes {"itype": "event"}.
            
     
            Parameters
            ----------
            query : dict
            """

            if query.get("itype") != "event":
                return func(self, query, *args, **kwargs)

            if "orgid" in query:
               raise ImpossibleError("'orgid' already part of query!")

            allowed_orgs = self.user.orgs_user_of(return_type="_hash")
            query = {**query, "orgid": {"$in": allowed_orgs}}
            
            result = func(self, query, *args, **kwargs)
            return result

        return wrapper

    @enforce_acl
    def count_documents(self, *args, **kwargs):
        """Count number of documents in TAHOE DB."""

        return super().count_documents(*args,**kwargs)

    @enforce_acl
    def find(self, *args, **kwargs):
        """Find many documents from TAHOE DB."""

        return super().find(*args,**kwargs)

    @enforce_acl
    def find_one(self, *args, **kwargs):
        """Find one document from TAHOE DB."""

        return super().find_one(*args,**kwargs)


class DamBackend(_DAMBase, MongoBackend):
    def __init__(self, user, _backend, create=False, **kwargs):
        """
        Parameters
        ----------
        user : tahoe.identity.user.User
            The calling user.

        See Also
        --------
        User : tahoe.identity.User
        """

        if not isinstance(user, tahoe.identity.User):
           raise TypeError(f"Invalid type '{type(user)}' for 'user'!")
        self.user = user
        
        mongo_url = _backend.mongo_url
        dbname = _backend.database.name
        collname = _backend.name
        super().__init__(mongo_url, dbname, collname, create, **kwargs)

    def __repr__(self):
       mongo_url = self.mongo_url
       dbname = self.database.name
       collname = self.name
       return f"DamBackend('{mongo_url}', '{dbname}', '{collname}')"


class MockDamBackend(_DAMBase, MockMongoBackend):
    
    def __init__(self, user, _backend, create=False, **kwargs):
        """
        Parameters
        ----------
        user : tahoe.identity.user.User
            The calling user.

        See Also
        --------
        User : tahoe.identity.User
        """

        if not isinstance(user, tahoe.identity.User):
           raise TypeError(f"Invalid type '{type(user)}' for 'user'!")
        self.user = user
        
        mongo_url = _backend.mongo_url
        dbname = _backend.database.name
        collname = _backend.name
        super().__init__(mongo_url, dbname, collname, create, **kwargs)

    def __repr__(self):
       mongo_url = self.mongo_url
       dbname = self.database.name
       collname = self.name
       return f"MockDamBackend('{mongo_url}', '{dbname}', '{collname}')"










