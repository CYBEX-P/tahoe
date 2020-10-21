"""Org Class."""

if __name__ != 'tahoe.identity.org':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os

from tahoe import Attribute, Object, parse
from tahoe.identity.error import UserError
from tahoe.identity.identity import Identity


class Org(Identity):
    """
    
    """
    def __init__(self, orgname, user, admin, name='', **kwargs):
        # user = self._validate_instance(user, ['user'])
        # admin = self._validate_instance(admin, ['user'])

        user = self._validate_instance(user, ["user", "str"])
        admin = self._validate_instance(admin, ["user", "str"])


        user_obj = list()
        admin_obj = list()
        # print(user, admin)
        self._usr_ref = list()
        for u in user:
            # print(type(u))
            if isinstance(u,str):
                user_hash = u
                user_obj.append(parse(self._backend.find_one({"_hash":u},{"_id":0}),self._backend))
            elif self._validate_instance(u, ["user"]):
                user_hash = u._hash
                user_obj.append(u)
            else:
                raise TypeError
            self._usr_ref.append(user_hash)

        self._adm_ref = list()
        for ad in admin:
            if isinstance(ad,str):
                admin_hash = ad
                admin_obj.append(parse(self._backend.find_one({"_hash":ad},{"_id":0}),self._backend))
            elif self._validate_instance(ad, ["user"]):
                admin_hash = ad._hash
                admin_obj.append(ad)
            else:
                raise TypeError
            self._adm_ref.append(admin_hash)


        # check this after the above because datatype is already standarized (user hash)
        for u in self._adm_ref:
            if u not in self._usr_ref:
                raise UserError("admin must be a user of this org: " \
                                f"'{u.data['useremail'][0]}'")

        # default ACL
        self._acl = list(set(self._adm_ref + self._usr_ref))
          
        orgname = Attribute('orgname', orgname, _backend=self._backend)
        name = Attribute('name', name, _backend=self._backend)

        admin_obj = Object('admin', admin_obj, _backend=self._backend)

        super().__init__('cybexp_org', [orgname, name, *user_obj, admin_obj], **kwargs)


    @property
    def acl(self):
        return self._acl
    # @acl.setter # this decorator breaks it 
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

        print("admin", admin)
        if isinstance(admin,str):
            admin_hash = admin
        elif self._validate_instance(admin, ["user"]):
            admin_hash = admin._hash
        else:
            raise TypeError

        print("admin is fine")


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
        raise NotImplementedError

    def addconfig(self, config):
        raise NotImplementedError

    def adduser(self, user):
        raise NotImplementedError
    
    def deladmin(self, user):
        # if user is admin
        raise NotImplementedError

    def deluser(self, user):
        # is admiin?
        raise NotImplementedError



    def _add_to_acl(self, user):
        raise NotImplementedError
    def _remove_to_acl(self, user):
        raise NotImplementedError





    @property
    def _unique(self):
        unique = self.itype + self.sub_type + self.data['orgname'][0]
        return unique.encode('utf-8')

    # def isAdmin(self, user_id):
    #     return False
    #     # TODO

    def _updatehash(self):
##        newhash = sha256(self._unique)
        return NotImplemented
        # update its _hash in the MongoDB
        # in all references (_ref, _cref, _usr_ref, _acl...)

