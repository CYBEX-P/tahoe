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
    special methods to manage them. IdentityBackend is also the base
    for other classes in Tahoe when dealing with the location of the 
    backend. Each iteration of this class requires a source in which 
    the data will be sent towards. In local host case -
    E.G: "mongodb://localhost:27017/"
    """

    def __init__(self, mongo_url=None, dbname="identity_db",
                 collname="identity_coll", create=False, **kwargs):
        super().__init__(mongo_url, dbname, collname, create, **kwargs)
        
    def create_user(self, u):
        return NotImplemented

    def get_config(self, plugin_lst=None, name_lst=None, enabled=True):
        """

        Gets and and establishes the backend configuration with plugin_lst and adds
        the values of the name_lst parameter as well. If either or both parameters is not 'None',
        their values are pulled from them and stored in a list as a tahoe.Attribute hashmap as either
        a plugin or name attribute object. The function then looks for the id of the backend and 
        returns the object as a list.
        
        Parameters
        ----------
        plugin_lst: List of Str
          The list of plugins 
        name_lst: list of Str
          List of the names of the passed files that contain the information and
          other data
        enabled: Bool
          Enables a Tahoe Attribute


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

    def get_all_plugin(self, enabled=True):
        """
        Input config utility function. Finds and returns all available
        plugins from the database.

        Parameters
        ----------
        enabled: Bool
        
        """
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

        fake_user = tahoe.identity.User("fake_user",_backend=tahoe.NoBackend() )
        thisorg = tahoe.identity.Org(orgname, [fake_user],[fake_user], _backend=tahoe.NoBackend())
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

       fake_user = tahoe.identity.User("fake_user",_backend=tahoe.NoBackend() )
       thisorg = tahoe.identity.Org(orgname, [fake_user],[fake_user], _backend=tahoe.NoBackend())
       return self.find_one({"_hash": thisorg._hash}, p) 

   def user_exists(self, email):
       """
       Utility function, pulls and return a bool where the email is existant or not
       """
       return self.find_user(email, {**P, "_hash":1}) is not None

   def org_exists(self, orgname):
       """
       Utility function, pulls and returns a bool where the organization name is existant or not
       """
       return self.find_org(orgname, {**P, "_hash":1}) is not None

