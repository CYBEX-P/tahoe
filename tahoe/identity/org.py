"""Org Class."""

if __name__ != 'tahoe.identity.org':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os

import tahoe
from tahoe import Attribute, Object, parse
from tahoe.identity.error import UserError
from tahoe.identity.identity import Identity
from tahoe.identity.error import UserIsAdminError, UserIsInAclError, \
     UserIsNotInAclError, UserIsInOrgError, UserIsNotAdminError, \
     UserIsNotInOrgError, UserIsOnlyAdminError


# Default MongoDB Projection
_P = {'_id': 0}


class Org(Identity):
    def __init__(self, orgname, user, admin, name='', **kwargs):
        """
        Creates an Org with specified orgname.

        Paramters
        ---------
        orgname : str
            The orgname of the Org. `orgname` is the unique identifier
            of an Org in TAHOE.
        user : (list of) tahoe.Idenity.User or User._hash
            Users of the Org.
        admin : (list of) tahoe.Idenity.User or User._hash
            Users of the Org.
        name : str, optional
            Full name of the Org

        Returns
        -------
        tahoe.identity.Org
            The creatd Org object.
        """

        if not isinstance(user, list):
            user = [user]
        

        user = self._validate_instance(user, ["user"])
        admin = self._validate_instance(admin, ["user"])


        user_obj = list()
        admin_obj = list()
        # print(user, admin)
        self._usr_ref = list()
        for u in user:
            # print(type(u))
            if isinstance(u, str):
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


##    @property
##    def acl(self):
##        return self._acl
##
##    # @acl.setter # this decorator breaks it 
##    def set_acl(self,admin, acl):
##        """
##        Parameters
##        ----------
##        admin: str or User
##            `User` or hash of user that will change the acl, must be admin
##        acl: list
##            list of hashes and `Users` , used as new acl
##        Returns
##        -------
##        bool
##            True if ACL update was successful
##        Raises
##        ------
##        TypeError
##            if `admin` is not of type `User` or string
##        """
##
##        print("admin", admin)
##        if isinstance(admin,str):
##            admin_hash = admin
##        elif self._validate_instance(admin, ["user"]):
##            admin_hash = admin._hash
##        else:
##            raise TypeError
##
##        print("admin is fine")
##
##
##        if admin_hash in self._adm_ref:
##            if isinstance(acl, list) and all([isinstance(s,str) or self._validate_instance(s, ['user']) for s in acl]):
##                new_acl = self._adm_ref # admins will always be in the ACL
##                for u in acl:
##                    if isinstance(u, str):
##                        new_acl.append(u)
##                    else:
##                        new_acl.append(u._hash)
##                self._acl = list(set(new_acl))
##                self._update({"_acl": new_acl})
##                return True
##            else:
##                raise TypeError
##        return False

    def add_admin(self, user):
        """
        Add user to self as admin (self is an Org).

        Parameters
        ----------
        user : tahoe.Identity.User or str or list
            If `str`, user is assumed to be `_hash` of user. If `list`
            it must contain User or valid User._hash.

        Returns
        -------
        None
        """

        q = {
            'itype':'object',
            'sub_type': 'admin',
            '_hash': {'$in': self._cref}
        }
        old_admin_dict = self._backend.find_one(q, _P)
        old_admin = parse(old_admin_dict,
                          backend=self._backend, validate=False)

        user = self._validate_user(user)
        user_hash = [u._hash for u in user]

        new_admin_data = self.get_admins()
        for u in user:
            if u.is_admin_of(self):
                raise UserIsAdminError(f"User is already admin = {u._hash}!")
            if not u.is_user_of(self):
                self.add_user(u)
            new_admin_data.append(u)

        new_admin = Object('admin', new_admin_data, _backend=self._backend)

        self.replace_instance(old_admin, new_admin)

        new_adm_ref = self._adm_ref + user_hash
        self._update({'_adm_ref': new_adm_ref })

    def add_config(self, config):
        return NotImplemented

    def add_user(self, user):
        """
        Add user to self (self is an Org).

        Parameters
        ----------
        user : tahoe.Identity.User or str or list
            If `str`, user is assumed to be `_hash` of user. If `list`
            it must contain User or valid User._hash.

        Returns
        -------
        None
        """

        user = self._validate_user(user)
        user_hash = [u._hash for u in user]
        for u in user:
            if u.is_user_of(self):
                raise UserIsInOrgError(f"User already in Org = {u._hash}!")
            self.add_instance(u)

        new_usr_ref = self._usr_ref + user_hash
        new_acl = self._acl + user_hash
        self._update({'_usr_ref': new_usr_ref , '_acl': new_acl})

    def add_user_to_acl(self, user):
        """
        Add user to self._acl (self is an Org).

        Parameters
        ----------
        user : tahoe.Identity.User or str or list
            If `str`, user is assumed to be `_hash` of user. If `list`
            it must contain User or valid User._hash.

        Returns
        -------
        None
        """

        user = self._validate_user(user)
        user_hash = []
        for u in user:
            if u._hash in self._acl:
                raise UserIsInAclError(f"User already in ACL = {u._hash}!")
            user_hash.append(u._hash)

        new_acl = self._acl + user_hash
        self._update({'_acl': new_acl})
        
    def del_admin(self, user):
        """
        Remove user as admin of self (self is an Org).

        Parameters
        ----------
        user : tahoe.Identity.User or str
            If `str`, user is assumed to be `_hash` of user.

        Returns
        -------
        None
        """

        q = {
            'itype':'object',
            'sub_type': 'admin',
            '_hash': {'$in': self._cref}
        }
        old_admin_dict = self._backend.find_one(q, _P)
        old_admin = parse(old_admin_dict,
                          backend=self._backend, validate=False)
        
        user = self._validate_user(user)
        user_hash = [u._hash for u in user]

        for u in user:
            if not u.is_admin_of(self):
                raise UserIsNotAdminError(f"User is not admin = {u._hash}!")
            if self.num_admin() == 1:
                raise UserIsOnlyAdminError(f"User is only admin = {u._hash}!")

        new_admin_data = []
        for a in self.get_admins():
            if a._hash not in user_hash:
                new_admin_data.append(a)
        
        new_admin = Object('admin', new_admin_data, _backend=self._backend)

        self.replace_instance(old_admin, new_admin)

        new_adm_ref = [u for u in self._adm_ref if u not in user_hash]
        self._update({'_adm_ref': new_adm_ref })

    def del_user(self, user):
        """
        Delete user from self (self is an Org).

        Parameters
        ----------
        user : tahoe.Identity.User or str
            If `str`, user is assumed to be `_hash` of user.

        Returns
        -------
        None
        """

        user = self._validate_user(user)
        user_hash = [u._hash for u in user]
        for u in user:
            if not u.is_user_of(self):
                raise UserIsNotInOrgError(f"User is not in org = {u._hash}!")
            if u.is_admin_of(self):
                raise UserIsAdminError(f"User is admin = {u._hash}!")
            self.remove_instance(u)

        new_usr_ref = [u for u in self._usr_ref if u not in user_hash]
        new_acl = [u for u in self._acl if u not in user_hash]
        self._update({'_usr_ref': new_usr_ref , '_acl': new_acl})

    def del_user_from_acl(self, user):
        """
        Delete user to self._acl (self is an Org).

        Parameters
        ----------
        user : tahoe.Identity.User or str or list
            If `str`, user is assumed to be `_hash` of user. If `list`
            it must contain User or valid User._hash.

        Returns
        -------
        None
        """

        user = self._validate_user(user)
        user_hash = self._acl
        for u in user:
            if u.is_admin_of(self):
                raise UserIsAdminError(
                    f"Cannot delete admin from ACL = {u._hash}!")
            if u._hash not in self._acl:
                raise UserIsNotInAclError(f"User is not in ACL = {u._hash}!")
            user_hash.remove(u._hash)

        new_acl = user_hash
        self._update({'_acl': new_acl})

    def get_admins(self):
        """
        Get a list of admins of the Org.

        Returns
        -------
        result : list
            A list of dict. Each dict contains complete info about
            an admin.
        """
        
        result = []
        for adm_hash in self._adm_ref:
            adm = self._backend.find_user(_hash=adm_hash, parse=True)
            result.append(adm)
        return result

    def get_users(self):
        """
        Get a list of users of the Org.

        Returns
        -------
        result : list
            A list of dict. Each dict contains complete info about
            a user.
        """
        
        result = []
        for usr_hash in self._usr_ref:
            usr = self._backend.find_user(_hash=usr_hash, parse=True)
            result.append(usr)
        return result

    def num_admin(self):
        return len(self._adm_ref)

    def num_user(self):
        return len(self._usr_ref)

    @property
    def _unique(self):
        unique = self.itype + self.sub_type + self.data['orgname'][0]
        return unique.encode('utf-8')



