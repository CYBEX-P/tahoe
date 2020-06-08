"""
User = UserModel in flask code see = https://github.com/CYBEX-P/cybexp-cs/blob/5707b87e9166470ce48d884e11d8d677ec1cfeee/api/models.py#L4
Additional = Org, Config
IdentityBackend: query database
User: create, modify user, get JWT token etc.
Org: create org, add user, get JWT token etc.

Future work:
- expire JWT
--- justify expire JWT (why should tokens expire?)
--- code renew token like flask-jwt
--- provide automatic renewal mechanism for machines
- revoke JWT using blacklist (not required if expire quick)
- Org.addadmin(user)
- Org.deladmin(user)
- CybexAdminUser
- decorators: @user_required, @org_required (no argument)
--- use werkzeug.local.LocalProxy to get token from falcon
- separate JWT class
--- User, Org inherit JWT class as 2nd parent
--- JWT class is initialized in falcon/flask/django like jwt = JWT(secret, algo)
--- so manual setting of Identity.secret, Identity.algo is not required in falcon
"""


# ==== Import ====

if __name__ in ["__main__", "identity"]:
  from instance import Attribute, Object, Instance
  from backend import NoBackend, MongoBackend, set_mongo_backend
else:
  from .instance import Attribute, Object, Instance
  from .backend import NoBackend, MongoBackend, set_mongo_backend

import hashlib, uuid, jwt, pdb



# ==== Globals ====

P = {"_id":0}



# ==== Exceptions ====

class PasswordError(Exception):
  pass

class UserError(Exception):
  pass


# ==== Class Backend ====

class IdentityBackend(MongoBackend):
  def finduser(self, email, projection=P):
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

class Config(Object):
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

