"""unittests for tahoe.identity.identity"""

import builtins
import hashlib
import pdb
import unittest

if __name__ != 'tahoe.tests.identity.test_identity':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os

from tahoe import Instance, Attribute, Object
from tahoe.identity import Identity, User, Org
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.identity.error import InvalidUserHashError
from tahoe.tests.identity.test_backend import setUpBackend, tearDownBackend


def setUpModule():    
    _backend = setUpBackend()

    Instance.set_backend(_backend)
    Attribute.set_backend(_backend)
    Object.set_backend(_backend)
    
    Identity.set_backend(_backend)
    User.set_backend(_backend)
    Org.set_backend(_backend)

    assert Instance._backend is Attribute._backend
    assert Instance._backend is Object._backend
    assert Instance._backend is User._backend
    assert Instance._backend is Org._backend
    

def tearDownModule():
    tearDownBackend(Instance._backend)



def make_test_data():
    builtins.u1 = User('user1@example.com', 'Abcd1234', 'User 1')
    builtins.u2 = User('user2@example.com', 'Abcd1234', 'User 2')
    builtins.u3 = User('user3@example.com', 'Abcd1234', 'User 3')

    builtins.o = Org('unr', u1, u1, 'University of Nevada Reno')
    builtins.od = o._backend.find_one({'_hash': o._hash})

    builtins.aon = Attribute('orgname', 'unr')
    builtins.an = Attribute('name', 'University of Nevada Reno')
    builtins.oadm = Object('admin', u1)

    builtins.ae = Attribute('email_addr', 'user1@example.com')

    hashed_pass = hashlib.sha256('Abcd1234'.encode('utf-8')).hexdigest()
    builtins.ap = Attribute('password', hashed_pass)

    builtins.aun = Attribute('name', 'User 1')
    

def delete_test_data():
    del builtins.u1, builtins.u2, builtins.u3, builtins.o, builtins.od, \
        builtins.aon, builtins.an, builtins.oadm, builtins. ae, \
        builtins. ap, builtins.aun




class SetBackendTest(unittest.TestCase):
    """
    Examples
    --------
    Correct way of setting default backend::
        
        >>> from tahoe import Instance
        >>> from tahoe.identity import Identity
        >>> _backend = MongoBackend("test_db")
        >>> Instance.set_backend(_backend)
        >>> Instance._backend
        MongoBackend("localhost:27017", "test_db", "instance")
        >>> Identity._backend
        MongoBackend("localhost:27017", "test_db", "instance")

    Wrong way of setting default backend::

        >>> from tahoe import Instance
        >>> from tahoe.identity import Identity
        >>> Identity._backend = MongoBackend()
        >>> Identity._backend
        MongoBackend('localhost:27017', 'tahoe_db', 'instance')
        >>> Instance._backend
        NoBackend()

    """
    def test_backend(self):
        self.assertIs(Identity._backend, Instance._backend)

class ValidateUserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        User._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()

    def test_valid_user(self):
        EQ = self.assertEqual

        res = u1._validate_user(u1)

        EQ(type(res), list)
        EQ(len(res), 1)
        EQ(res[0]._hash, u1._hash)

    def test_valid_user_one_tuple(self):
        EQ = self.assertEqual

        res = u1._validate_user((u1))

        EQ(type(res), list)
        EQ(len(res), 1)
        EQ(res[0]._hash, u1._hash)

    def test_valid_user_list(self):
        EQ = self.assertEqual
        IN = self.assertIn

        res = u1._validate_user([u1, u2])
        res_hash = [u._hash for u in res]

        EQ(type(res), list)
        EQ(len(res), 2)
        IN(u1._hash, res_hash)
        IN(u2._hash, res_hash)

    def test_typeerror_invalid_user_type_int(self):
        self.assertRaises(TypeError, u1._validate_user, 2)

    def test_typeerror_invalid_user_type_tuple(self):
        self.assertRaises(TypeError, u1._validate_user, (u1, u2))

    def test_valid_hash(self):
        EQ = self.assertEqual

        res = u1._validate_user(u1._hash)

        EQ(type(res), list)
        EQ(len(res), 1)
        EQ(res[0]._hash, u1._hash)

    def test_valid_hash_list(self):
        EQ = self.assertEqual
        IN = self.assertIn

        res = u1._validate_user([u1, u2])
        res_hash = [u._hash for u in res]

        EQ(type(res), list)
        EQ(len(res), 2)
        IN(u1._hash, res_hash)
        IN(u2._hash, res_hash)

    def test_valid_user_hash_mixed_list(self):
        EQ = self.assertEqual
        IN = self.assertIn

        res = u1._validate_user([u1, u2._hash])
        res_hash = [u._hash for u in res]

        EQ(type(res), list)
        EQ(len(res), 2)
        IN(u1._hash, res_hash)
        IN(u2._hash, res_hash)

        res = u1._validate_user([u1._hash, u2])
        res_hash = [u._hash for u in res]

        EQ(type(res), list)
        EQ(len(res), 2)
        IN(u1._hash, res_hash)
        IN(u2._hash, res_hash)

    def test_InvalidUserHashError_invalid_hash(self):
        self.assertRaises(InvalidUserHashError, u1._validate_user, 'abc')

    def test_typeerror_invalid_type_int_in_list(self):
        self.assertRaises(TypeError, u1._validate_user, [u1, 2])

    def test_InvalidUserHashError_invalid_str_hash_in_list(self):
        self.assertRaises(InvalidUserHashError, u1._validate_user, [u1, 'abc'])

    def test_InvalidUserHashError_invalid_empty_list(self):
        self.assertRaises(ValueError, u1._validate_user, [])

    def test_InvalidUserHashError_hash_is_tahoe_object_but_not_user(self):
        self.assertRaises(InvalidUserHashError, u1._validate_user, o._hash)
    
    

if __name__ == '__main__':
    unittest.main()

    


