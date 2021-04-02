"""
Identity class is a base class for User and Org.
"""

import uuid
import jwt

if __name__ != 'tahoe.identity.identity':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os

import tahoe
from tahoe.parse import parse, getclass


P = {"_id":0} 
"""Default projection for MongoDB queries."""


class Identity(tahoe.Object):
    secret = 'secret'
    algo = 'HS256'
    _id_backend = tahoe.backend.NoBackend()

    @classmethod
    def get_payload(cls, token):
        """
        Decrypt JWT token and get payload.
        
        Parameters
        ----------
        token : str
            JWT token to be decoded.
            
        Returns
        -------
        decoded: dict or None
            decoded payload
            
        Raises
        ------
        jwt.exceptions.*
            when token can not be decoded
        """
        
        secret = cls.secret
        algo = cls.algo
        decoded = jwt.decode(token, secret, algo)
        return decoded

    @classmethod
    def is_token_revoked(cls, token):
         """Not implemneted yet!"""

         return False


##    def isvaliduser(self, token):
##        return self.getpayload(token)['sub_type'] == 'user'
##
##    def isvalidorg(self, token, **kwargs):
##        return getpayload(token, **kwargs)['sub_type'] == 'org'

    @property 
    def token(self):
        """
        Include another field called `index` in payload.
        Increment index everytime user logs in to the system.
        """
        
        payload = {
            'sub_type': self.sub_type,
            '_hash' : self._hash,
            'jti' : str(uuid.uuid4())
        }
        return jwt.encode(payload, self.secret, self.algo).decode('utf-8')


    # Protected & Private Methods

    def _validate_user(self, user):
        """
        Validate if user is a tahoe User (or a list of Users).

        Parameters
        ----------
        user : str or tahoe.Identity.User or list
            If `list`, must contain str or tahoe.Idenity.User.
            str is considered valid tahoe.Identity.User._hash.

        Returns
        -------
        user : list of tahoe.Idneity.User
        """

        valid_type = getclass("user")

        if not isinstance(user, list):
            user = [user]

        new = set() # remove duplicate
        
        for u in user:
            if isinstance(u, str):
                temp = self._backend.find_user(_hash=u, parse=True)
                if temp is None:
                    raise ValueError(f"Invalid user hash={u}")
                u = temp
            elif not self._is_instance(u, "user"):
                raise TypeError(f"Invalid user type={type(u)}")
            new.add(u)

        new = list(new) 

        if len(new)==0:
            raise ValueError("user/admin list cannot be empty!")

        return new

    

    
