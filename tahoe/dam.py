"""TAHOE DAM Module does access control."""

import pdb

if __name__ != 'tahoe.dam':
    import sys, os
    sys.path = ['..'] + sys.path
    del sys, os
import tahoe
##from tahoe import MongoBackend, NoBackend, MockMongoBackend
##from tahoe.identity import IdentityBackend, User


class ImpossibleError(Exception):
    """This should not happend exception!"""
    pass

class MissingUserError(Exception):
    """Keyword argument `user` is missing for _DAMBASE.find!"""
    pass

class InvalidUserHashError(Exception):
    pass


class _DAMBase():
    _identity_backend = tahoe.NoBackend()
    
    """
    Parent of both DAM and MockDAM so that same methods are not written
    twice.

    DAM inherits all methods from MongoBackend (or MockMongoBackend). It
    decorates the find and find_one methods to modify the query dict.
    The decorator take in a key-word argument called `user` & ensures
    the user finds only the data they have access to.
 
    Notes
    -----
    For DAM to work _identity_backend must have users, orgs & _acl.

    See Also:
    ---------
    MongoBackend: tahoe.MongoBackend
    """

    def enforce_acl(func):
        """Decorator that enforces ACL for find/find_one."""
      
        def wrapper(self, *args, **kwargs):
            """
            Gets user_acl for `user` and adds that to query.

            user_acl is a list of orgs the `user` has access to.
            
     
            Parameters
            ----------
            query : dict
            
            user = tahoe.identity.User or str
                User or User._hash or  who is queyring the data.

            Raises
            ------
            TypeError
                If `user` is not tahoe.identity.User._hash or of type
                tahoe.identity.User.
            """

            query = args[0] 

            if query.get("itype") != "event":
                user = kwargs.pop("user", None)
                return func(self, *args, **kwargs)

            try:
                user = kwargs.pop("user")
            except KeyError:
                raise MissingUserError("Keyword argument `user` is missing!")

            if isinstance(user, str):
               user = self._identity_backend.find_user(_hash=user, parse=True)
               if user is None:
                   raise InvalidUserHashError("`user` is not valid _hash!")
            elif not isinstance(user, tahoe.identity.User):
               raise TypeError(f"Invalid type '{type(user)}' for 'user'!")

            allowed_orgs = user.orgs_user_of(return_type="_hash")

            
            args = list(args) # convert tuple to list, make it editable

            if "orgid" in query:
               raise ImpossibleError("'orgid' already part of query!")

            acl_query = {"orgid": {"$in": allowed_orgs}} 
            args[0] = {**query, **acl_query}


            result = func(self, *args, **kwargs)

            return result

        return wrapper

    @enforce_acl
    def find(self, *args, **kwargs):
        """Find many documents from TAHOE DB."""

        return super().find(*args,**kwargs)

    @enforce_acl
    def find_one(self, *args, **kwargs):
        """Find one document from TAHOE DB."""

        return super().find_one(*args,**kwargs)

    


class DAM(_DAMBase, tahoe.MongoBackend):
    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------
        _identity_backend = tahoe.identity.IdentityBackend (optional)
            Where users, orgs, _acls are stored. This backend is used
            to pull user_acl for access control.

        See Also
        --------
        User : tahoe.identity.User
        Org : tahoe.identity.Org
        """

        if "_identity._backend" in kwargs:
            self._identity_backend = kwargs["_identity_backend"]
        super().__init__(*args, **kwargs)



class MockDAM(_DAMBase, tahoe.backend.MockMongoBackend):
    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------
        _identity_backend : tahoe.identity.IdentityBackend (optional)
            Where users, orgs, _acls are stored. This backend is used
            to pull user_acl for access control.

        See Also
        --------
        User : tahoe.identity.User
        Org : tahoe.identity.Org
        """

        if "_identity._backend" in kwargs:
            self._identity_backend = kwargs["_identity_backend"]
        super().__init__(*args, **kwargs)










