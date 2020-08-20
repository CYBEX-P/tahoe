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

    def __init__(self, mongo_url=None, dbname="identity_db",
                 collname="identity_coll", create=False, **kwargs):
        super().__init__(mongo_url, dbname, collname, create, **kwargs)
        
    def create_user(self, u):
        return NotImplemented

    def get_config(self, plugin_lst=None, name_lst=None, enabled=True):
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

    def get_all_plugin(self, enabled=True):
        ae = tahoe.Attribute('enabled', enabled)
        q = {'sub_type': 'cybexp_input_config', '_cref': ae._hash}
        p = {'_id': 0, 'data.plugin': 1}
        r = self.find(q, p)
        all_plugin = [c['data']['plugin'][0] for c in r]
        return all_plugin

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

        thisuser = tahoe.identity.User(email, _backend=tahoe.NoBackend())
        return self.find_one({"_hash": thisuser._hash}, p)

    def find_org(self, orgname, p=P):
        """
        Find org by orgname; orgname is unique id of org in TAHOE.

        Parameters
        ----------
        orgname : str
            orgname (unique id) of orgs
        p : dict
            MongoDB projection
        """

        thisorg = tahoe.identity.Org(orgname, _backend=tahoe.NoBackend())
        return self.find_one({"_hash": thisorg._hash}, p) 

    def user_exists(self, email):
        return self.find_user(email, {**P, "_hash":1}) is not None

    def org_exists(self, orgname):
        return self.find_org(orgname, {**P, "_hash":1}) is not None

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

    def find_org(self, orgname, p=P):
        """
        Find org by orgname; orgname is unique id of org in TAHOE.

        Parameters
        ----------
        orgname : str
            orgname (unique id) of orgs
        p : dict
            MongoDB projection
        """

        thisorg = tahoe.identity.Org(orgname, _backend=tahoe.NoBackend())
        return self.find_one({"_hash": thisorg._hash}, p) 

    def user_exists(self, email):
        return self.find_user(email, {**P, "_hash":1}) is not None

    def org_exists(self, orgname):
        return self.find_org(orgname, {**P, "_hash":1}) is not None

