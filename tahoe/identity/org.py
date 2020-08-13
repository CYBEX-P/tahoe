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

        self._acl = self._adm_ref + self._usr_ref
          
        orgname = Attribute('orgname', orgname, _backend=self._backend)
        name = Attribute('name', name, _backend=self._backend)

        admin = Object('admin', admin, _backend=self._backend)

        super().__init__('cybexp_org', [orgname, name, *user, admin], **kwargs)


    @property
    def acl(self):
        return self._acl
    @acl.setter
    def set_acl(self,admin, acl):
        """
        Parameters
        ----------
        admin: str or User
            `User` or hash of user that will change the acl, must be admin
        acl: list
            list of hashes and `Users` , used as new acl
        Returns
        -------
        bool
            True if ACL update was successful
        Raises
        ------
        TypeError
            if `admin` is not of type `User` or string
        """

        if isinstance(admin,str):
            admin_hash = admin
        elif self._validate_instance(admin, ["user"]):
            admin_hash = admin._hash
        else:
            raise TypeError


        if admin_hash in self._adm_ref:
            if isinstance(acl, list) and all([isinstance(s,str) or self._validate_instance(s, ['user']) for s in acl]):
                new_acl = self._adm_ref # admins will always be in the ACL
                for u in acl:
                    if isinstance(u, str):
                        new_acl.append(u)
                    else:
                        new_acl.append(u._hash)
                self._acl = list(set(new_acl))
                self._update({"_acl": new_acl})
                return True
            else:
                raise TypeError
        return False

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

