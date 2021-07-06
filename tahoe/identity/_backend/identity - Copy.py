"""
IdentityBackend, User, Org and InputConfig class.
"""

import pdb

if __name__ != 'tahoe.identity':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
import tahoe



# ==== Globals ====
"""
All documents in MongoDB has unique _id field. _id is not part of TAHOE. 
projection={"_id":0}, in a query means do not fetch the _id field.
"""
P = {"_id":0} 



# ==== Exceptions ====

class PasswordError(Exception):
  pass

class UserError(Exception):
  pass


# ==== Class Backend ====

class IdentityBackend(MongoBackend):
  """
  A TAHOE Backend stores data; has methods like find_one, insert_one etc.
  MongoBackend inherits Backend; stores data in MongoDB.
  IdentityBackend stores Users, Orgs, InputConfig etc.
  IdentityBackend has special methods to lookup Users, Orgs etc.
  """

  def finduser(self, email, projection=P):
    """
    find user by email address, email is unique id of user in TAHOE
    """
    
    tempuser = User(email, backend=NoBackend())
    return self.backend.find_one({"_hash" : tempuser._hash}, projection)

  def userexists(self, email):
    return self.finduser(email, {**P, "uuid":1}) is not None
    


# ==== Class Identity ====

class Identity():
  secret = 'secret'
  algo='HS256'
  try: backend = _BACKEND
  except: backend = NoBackend()

  def __init__(self, **kwargs):
    if not hasattr(self, 'uuid') or not self.uuid:
      self.uuid = 'identity--' + str(uuid.uuid4())

    # self.create_index(uuid, _hash, )

  def getpayload(self, token, **kwargs): # kwargs for secret and algo
    secret, algo = kwargs.get('secret', self.secret), kwargs.get('algo', self.algo)
    return jwt.decode(token, secret, algo)
  
  def gettoken(self, **kwargs):
    secret, algo = kwargs.get('secret', self.secret), kwargs.get('algo', self.algo)
    payload = {'sub_type':'org', 'uuid' : self.uuid, 'jti' : str(uuid.uuid4())}
    return jwt.encode(payload, secret, algo).decode('utf-8')    

  def isvaliduser(self, token, **kwargs):
    return getpayload(token, **kwargs)['sub_type'] == 'user'

  def isvalidorg(self, token, **kwargs):
    return getpayload(token, **kwargs)['sub_type'] == 'org'



# ==== Class User ====

class User(Identity, Object):
  def __init__(self, email, password='', name='', **kwargs):
    email = Attribute('useremail', email, backend=self.backend)
    password = Attribute('password', hashlib.sha256(password.encode('utf-8')).hexdigest(), backend=self.backend)
    name = Attribute('name', name, backend=self.backend) # if name: because name=='' during login
    
    Identity.__init__(self, **kwargs)
    Object.__init__(self, sub_type='user', data=[email, password, name], **kwargs)

  def __repr__(self): return f"User('{self.data['useremail'][0]}')" # put repr in eval to get the user object

  def addconfig(self, jsonfile):
    pass

  def changepass(self, newpassword):
    if not all([isinstance(newpassword, str) or 7 < len(newpassword) or 64 < len(newpassword)]):
      raise PasswordError('Password must be str of len [8,64]')
    oldpassword = Attribute('password', self.data['password'][0], backend=self.backend)
    newpassword = Attribute('password', hashlib.sha256(newpassword.encode('utf-8')).hexdigest(), backend=self.backend)
    self.remove_instance(oldpassword)
    self.add_instance(newpassword)

  def checkpass(self, password):
    return self.data['password'][0] == hashlib.sha256(password.encode('utf-8')).hexdigest()

  def unique(self):
    unique = self.itype + self.sub_type + self.data['useremail'][0]
    return unique.encode('utf-8')



# ==== Class Org ====

class Org(Identity, Object):
  def __init__(self, orgname, users, admins, name='', **kwargs):
    if not isinstance(users, list): users = [users]
    if not isinstance(admins, list): admins = [admins]
    for u in users + admins:
      if not isinstance(u, User):
        raise TypeError(str(type(u)))
    for u in admins:
      if u not in users:
        raise UserError(f"admin must be user of this org: '{u.data['useremail'][0]}'")

    self._usr_ref = [u.uuid for u in users]
    self._adm_ref = [u.uuid for u in admins]
      
    orgname = Attribute('orgname', orgname, backend=self.backend)
    name = Attribute('name', name, backend=self.backend)

    admins = Object('admin', admins, backend=self.backend)
    
    Identity.__init__(self, **kwargs)
    Object.__init__(self, sub_type='org', data=[orgname, name, *users, admins], **kwargs)

  def addadmin(self, user):
    pass
  
  def addconfig(self, config):
    pass
  
  def adduser(self, user):
    if not isinstance(user, User):
      raise TypeError(f"unsupported user type: '{str(type(user))}', excpected tahoe.identity.User")
    if user.uuid in self._usr_ref:
      raise UserError(f"user already in org: '{user.data['useremail'][0]}'")
    
    self._usr_ref += [user.uuid]
    self.update({'_usr_ref':self._usr_ref})
    self.add_instance(user)

  def deladmin(self, user):
    pass
  
  def deluser(self, user):
    if not isinstance(user, User):
      raise TypeError(f'unsupported user type: {str(type(user))}, excpected tahoe.identity.User')
    if user.uuid not in self._usr_ref:
      raise UserError(f"User '{user.data['useremail'][0]}' does not belong to this org")

    self._usr_ref.remove(user.uuid)
    self.update({'_usr_ref':self._usr_ref})
    self.remove_instance(user)

  def unique(self):
    unique = self.itype + self.sub_type + self.data['orgname'][0]
    return unique.encode('utf-8')


# ==== Class Config ====

class InputConfig(Identity, Object):
##  def __init__(self, pythondict):
##    #put everything in a Raw
##    pass
  
  def __init__(self, name, plugin, typetag, orgid, timezone, **kwargs):
    
    if not hasattr(self, 'uuid') or not self.uuid:
      self.uuid = 'object--' + str(uuid.uuid4())

    name = Attribute('name', name, backend=self.backend) # human_name
    plugin = Attribute('plugin', plugin, backend=self.backend) # plugin_name
    typetag = Attribute('typetag', typetag, backend=self.backend) # archive_processing_typetag
    orgid = Attribute('orgid', orgid, backend=self.backend) # organization id
    timezone = Attribute('timezone', timezone, backend=self.backend)

    Identity.__init__(self, **kwargs)

    if not hasattr(self, data): self.data=[] # child class will pass data in self.data
    Object.__init__(self, sub_type='input_config', data = self.data + [name, plugin, typetag, orgid, timezone], **kwargs)


class WebSocketConfig(InputConfig):
  pass

class InputPlugin():
  pass


####def example1():
##from pprint import pprint
##
##mongo_url = "mongodb://localhost:27017/"
##dbname = 'identity_db'
##collname = 'identity'
##
##backend = set_mongo_backend([Identity, Instance], mongo_url, dbname, collname, IdentityBackend)
##
##backend.drop()
##
##u1 = User('jdoe@example.com')
##
##o1 = Org('myorg', u1, u1, 'MY ORG INC.')
##
##u2 = User('chuck')
##o1.adduser(u2)
##
##u3 = User('dan')
##o1.adduser(u3)
##
##o1.deluser(u2)
####pprint(o1.doc()['data'])
##
##token = o1.gettoken()
##payload = o1.getpayload(token)
##pprint(payload)

