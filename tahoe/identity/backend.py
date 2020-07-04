"""
IdentityBackend implements extra methods for user and input management.
"""

if __name__ != 'tahoe.identity.backend':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
import tahoe


P = {"_id":0} 
"""Default projection for MongoDB queries."""


class IdentityBackend(tahoe.MongoBackend):
    """
    IdentityBackend stores user, org and input-config data and has
    special methods to manage them.
    """

    def find_user(self, email, p=P):
        """
        Find user by email address; email is unique id of user in TAHOE.

        Parameters
        ----------
        email : str
            email address (unique id) of users
        p : dict
            MongoDB projection
        """

        thisuser = tahoe.identity.User(email, backend=tahoe.NoBackend())
        return self.backend.find_one({"_hash": thisuser._hash}, p)

    def user_exists(self, email):
        return self.find_user(email, {**P, "_hash":1}) is not None
    

class MockIdentityBackend(tahoe.backend.MockMongoBackend):
    """
    IdentityBackend stores user, org and input-config data and has
    special methods to manage them.
    """

    def find_user(self, email, p=P):
        """
        Find user by email address; email is unique id of user in TAHOE.

        Parameters
        ----------
        email : str
            email address (unique id) of users
        p : dict
            MongoDB projection
        """

        thisuser = tahoe.identity.User(email, backend=tahoe.NoBackend())
        return self.backend.find_one({"_hash": thisuser._hash}, p)

    def user_exists(self, email):
        return self.find_user(email, {**P, "_hash":1}) is not None

