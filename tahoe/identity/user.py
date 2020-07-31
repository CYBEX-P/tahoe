"""User class."""

import hashlib

if __name__ != 'tahoe.identity.user':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os

from tahoe import Attribute
from tahoe.identity.error import PasswordError
from tahoe.identity.identity import Identity


class User(Identity):
    def __init__(self, email, password='', name='', **kwargs):
        email_att = Attribute('email_addr', email, _backend=self._backend)

        hashed_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
        pass_att = Attribute('password', hashed_pass, _backend=self._backend)

        name_att = Attribute('name', name, _backend=self._backend)

        super().__init__('cybexp_user', [email_att, pass_att, name_att],
                         **kwargs)

    def __repr__(self):
        return f"User('{self.data['email_addr'][0]}')"

    def _get_allowed_acl(self):
        pass

    def addconfig(self, jsonfile):
        # should this be allowed ? 
        # self._get_alled_acl()
        pass

    def changepass(self, newpassword):
        if not all([isinstance(newpassword, str)
                    or 7 < len(newpassword) or 64 < len(newpassword)]):
            raise PasswordError('Password must be str of len [8,64]')

        oldpass = self.data['password'][0]
        oldpass = Attribute('password', oldpass, _backend=self._backend)

        newpass = hashlib.sha256(newpassword.encode('utf-8')).hexdigest()
        newpass = Attribute('password', newpass, _backend=self._backend)

        self.replace_instance(oldpass, newpass)

    def checkpass(self, password):
        return self.data['password'][0] == \
               hashlib.sha256(password.encode('utf-8')).hexdigest()
        
    @property
    def _unique(self):
        unique = self.itype + self.sub_type + self.data['email_addr'][0]
        return unique.encode('utf-8')


    def change_email(self):
        pass
        # if we change the email, hash changes then we need to update reference filed in orgs












