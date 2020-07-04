"""
Identity class is a base class for User and Org.
"""

import uuid

if __name__ != 'tahoe.identity.identity':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
import tahoe


P = {"_id":0} 
"""Default projection for MongoDB queries."""


class Identity(tahoe.Object):
    secret = 'secret'
    algo='HS256'

    def getpayload(self, token):
        """
        Parameters
        ----------
        token : str
            JWT token to be decoded.
        """
        secret = self.secret
        algo = self.algo
        return jwt.decode(token, secret, algo)

##    def isvaliduser(self, token):
##        return self.getpayload(token)['sub_type'] == 'user'
##
##    def isvalidorg(self, token, **kwargs):
##        return getpayload(token, **kwargs)['sub_type'] == 'org'

    @property 
    def token(self):
        payload = {'sub_type': self.sub_type,
                   '_hash' : self._hash,
                   'jti' : str(uuid.uuid4())}
        return jwt.encode(payload, self.secret, self.algo).decode('utf-8')    

    

    
