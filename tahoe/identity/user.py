"""User class."""

import copy
import hashlib

if __name__ != 'tahoe.identity.user':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os

import tahoe
from tahoe import Attribute
from tahoe.identity.error import PasswordError, UserExistsError, OrgExistsError
from tahoe.identity.identity import Identity

_P = {'_id': 0}


class User(Identity):
    def __init__(self, email, password='', name='',
                 sub_type='cybexp_user', **kwargs):

        assert sub_type in ['cybexp_user', 'cybexp_superuser']
        
        email_att = Attribute('email_addr', email, _backend=self._backend)

        hashed_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
        pass_att = Attribute('password', hashed_pass, _backend=self._backend)

        name_att = Attribute('name', name, _backend=self._backend)

        super().__init__(sub_type, [email_att, pass_att, name_att], **kwargs)

    def __repr__(self):
        return f"User('{self.data['email_addr'][0]}')"

    def _get_allowed_acl(self):
        return NotImplemented

    @property
    def _unique(self):
        unique = self.itype + self.sub_type + self.data['email_addr'][0]
        return unique.encode('utf-8')

    def add_config(self, jsonfile):
        # should this be allowed ? 
        # self._get_alled_acl()
        return NotImplemented

    def change_email(self):
        return NotImplemented
        # if we change the email, hash changes then
        # we need to update reference filed in orgs

    def change_pass(self, newpassword):
        if not all([isinstance(newpassword, str)
                    or 7 < len(newpassword) or 64 < len(newpassword)]):
            raise PasswordError('Password must be str of len [8,64]')

        oldpass = self.data['password'][0]
        oldpass = Attribute('password', oldpass, _backend=self._backend)

        newpass = hashlib.sha256(newpassword.encode('utf-8')).hexdigest()
        newpass = Attribute('password', newpass, _backend=self._backend)

        self.replace_instance(oldpass, newpass)

    def check_pass(self, password):
        return self.data['password'][0] == \
               hashlib.sha256(password.encode('utf-8')).hexdigest()

    @property
    def doc_no_pass(self):
        b = self.__dict__.pop('_backend', None)
        user = copy.deepcopy(self)
        if b:
            self._backend = b
        
        passwd = user.data.pop('password')[0]
        att_passwd = Attribute('password', passwd, _backend=tahoe.NoBackend())
        passwd_hash = att_passwd._hash
        user._cref.remove(passwd_hash)
        user._ref.remove(passwd_hash)

        return user.doc
    
    @property
    def email(self):
        return self.data['email_addr'][0]

    def is_admin_of(self, org):
        """
        Returns True if self is admin of org.

        Paramters
        ---------
        org : tahoe.Identity.Org or str
            If str then org is considered to be `_hash` of Org.
        """

        if isinstance(org, str):
            org = self._backend.find_org(_hash=org, parse=True)
        if not self._is_instance(org, "org"):
            raise ValueError(f"Invalid org or org hash!")
        return self._hash in org._adm_ref

    def is_user_of(self, org):
        """
        Returns True if self is user of org.

        Paramters
        ---------
        org : tahoe.Identity.Org or str
            If str then org is considered to be `_hash` of Org.
        """

        if isinstance(org, str):
            org = self._backend.find_org(_hash=org, parse=True)
        if not self._is_instance(org, "org"):
            raise ValueError(f"Invalid org or org hash!")
        return self._hash in org._usr_ref

    def orgs_admin_of(self):
        """
        Returns orgs which this user are admin of.

        Returns
        -------
        pymongo.cursor.Cursor
            An iterable of the complete `dict` of the orgs.
        """
        
        q = {'itype': 'object', 'sub_type': 'cybexp_org',
             '_adm_ref': self._hash}
        r = self._backend.find(q, _P)
        return r

    def orgs_user_of(self, return_type="instance"):
        """
        Returns orgs which this user belongs to.

        Parameters
        ----------
        return_type : {"instance", "_hash"}

        Returns
        -------
        pymongo.cursor.Cursor
            An iterable of the complete `dict` of the orgs.
        """

        q = {'itype': 'object', 'sub_type': 'cybexp_org',
                 '_usr_ref': self._hash}
        
        if return_type == "instance":
            p = _P
        elif return_type == "_hash":
            p = {"_hash": 1, **_P}
            
        r = self._backend.find(q, p)

        if return_type == "_hash":
            r = [i['_hash'] for i in r]

        return r
            

    

class SuperUser(User):
    def __init__(self, email, password='', name='', **kwargs):

        super().__init__(email, password, name,
                         sub_type='cybexp_superuser', **kwargs)

    def __repr__(self):
        return f"SuperUser('{self.data['email_addr'][0]}')"

    def create_user(self, email, password, name):
        """
        Creates an user with specified email address.

        Paramters
        ---------
        email : str
            The email address of the user.

            Note that email address is also the username and the
            unique identifier of a user in TAHOE.
        password : str
            Plaintext password of the user.
        name : str
            Full name of the user

        Returns
        -------
        tahoe.identity.User
            The creatd user object.

        Raises
        ------
        tahoe.identity.backend.DuplicateUserError
            If email address is already registered.
        """
        
        if self._backend.user_exists(email):
            raise UserExistsError(f"Username/email = {email} already exists!")
        
        return User(email, password, name, _backend=self._backend)

    def create_org(self, orgname, user, admin, name):
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

        Raises
        ------
        tahoe.identity.backend.DuplicateError
            If `orgname` is already registered.
        """
        
        if self._backend.org_exists(orgname):
            raise OrgExistsError(f"Orgname = {orgname} already exists!")
        
        return tahoe.identity.Org(orgname, user, admin, name)









