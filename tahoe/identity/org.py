"""Org Class."""

if __name__ != 'tahoe.identity.org':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os

from tahoe import Attribute, Object
from tahoe.identity.error import UserError
from tahoe.identity.identity import Identity


class Org(Identity):
    def __init__(self, orgname, user, admin, name='', **kwargs):
        user = self._validate_instance(user, ['user'])
        admin = self._validate_instance(admin, ['user'])
        
        for u in admin:
            if u not in user:
                raise UserError("admin must be a user of this org: " \
                                f"'{u.data['useremail'][0]}'")

        self._usr_ref = [u._hash for u in user]
        self._adm_ref = [u._hash for u in admin]
          
        orgname = Attribute('orgname', orgname, _backend=self._backend)
        name = Attribute('name', name, _backend=self._backend)

        admin = Object('admin', admin, _backend=self._backend)

        super().__init__('cybexp_org', [orgname, name, *user, admin], **kwargs)

    def addadmin(self, user):
        return NotImplemented
        #

    def addconfig(self, config):
        return NotImplemented

    def adduser(self, user):
        return NotImplemented

    def getadmin(self):
        return NotImplemented
    
    def deladmin(self, user):
        return NotImplemented

    def deluser(self, user):
        return NotImplemented

    @property
    def _unique(self):
        unique = self.itype + self.sub_type + self.data['orgname'][0]
        return unique.encode('utf-8')

    def _updatehash(self):
##        newhash = sha256(self._unique)
        return NotImplemented
        # update its _hash in the MongoDB
        # in all references (_ref, _cref, _usr_ref, _acl...)

