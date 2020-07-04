"""unittests for tahoe.identity.user"""

import builtins
import hashlib
import pdb
import unittest

if __name__ != 'tahoe.tests.identity.test_user':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os

from tahoe import Instance, Attribute
from tahoe.identity import Identity, User
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import IdentityBackendTest


def make_test_data():
    builtins.u = User('johndoe@example.com', 'Abcd1234', 'John Doe')
    builtins.ud = u._backend.find_one({'_hash': u._hash}, {'_id': 0})

    builtins.ae = Attribute('email_addr', 'johndoe@example.com')

    hashed_pass = hashlib.sha256('Abcd1234'.encode('utf-8')).hexdigest()
    builtins.ap = Attribute('password', hashed_pass)

    builtins.an = Attribute('name', 'John Doe')


def delete_test_data():
    del builtins.u, builtins.ud, builtins.ae, builtins.ap, builtins.an


def setUpModule():
    _backend = IdentityBackendTest.setUpClass()
    Instance.set_backend(_backend)

    assert Identity._backend is Instance._backend
    

def tearDownModule():
    IdentityBackendTest.tearDownClass()


class InitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(User._backend, (IdentityBackend, MockIdentityBackend))
        User._backend.drop()

        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        
    def test_init(self):
        self.assertIsNotNone(ud)

    def test_itype(self):
        EQ = self.assertEqual
        EQ(u.itype, 'object')
        EQ(ud['itype'], 'object')

    def test_sub_type(self):
        EQ = self.assertEqual
        EQ(u.sub_type, 'cybexp_user')
        EQ(ud['sub_type'], 'cybexp_user')

    def test_data_email_addr(self):
        EQ = self.assertEqual
        EQ(u.data['email_addr'][0], 'johndoe@example.com')
        EQ(ud['data']['email_addr'][0], 'johndoe@example.com')

    def test_data_password(self):
        EQ = self.assertEqual
        expected_pass = '3f21a8490cef2bfb60a9702e9d2ddb7' \
                   'a805c9bd1a263557dfd51a7d0e9dfa93e'
        EQ(u.data['password'][0], expected_pass)
        EQ(ud['data']['password'][0], expected_pass)

    def test_data_name(self):
        EQ = self.assertEqual
        EQ(u.data['name'][0], 'John Doe')
        EQ(ud['data']['name'][0], 'John Doe')

    def test_cref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(u._cref), 3)
        EQ(len(ud['_cref']), 3)
        
        IN(ae._hash, u._cref)
        IN(ap._hash, u._cref)
        IN(an._hash, u._cref)
        IN(ae._hash, ud['_cref'])
        IN(ap._hash, ud['_cref'])
        IN(an._hash, ud['_cref'])

    def test_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(u._ref), 3)
        EQ(len(ud['_ref']), 3)
        
        IN(ae._hash, u._ref)
        IN(ap._hash, u._ref)
        IN(an._hash, u._ref)
        IN(ae._hash, ud['_ref'])
        IN(ap._hash, ud['_ref'])
        IN(an._hash, ud['_ref'])

    def test_hash(self):
        expected_hash = '3c89f0d12d487a409f5fee0307647d5b' \
                        'b6c825107c488eae2bf738d6651b9f47'
        EQ = self.assertEqual
        EQ(u._hash, expected_hash)
        EQ(ud['_hash'], expected_hash)

    
class PasswordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(User._backend, (IdentityBackend, MockIdentityBackend))
        User._backend.drop()

        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()

    def test_01_checkpass(self):
        self.assertTrue(u.checkpass('Abcd1234'))
        self.assertFalse(u.checkpass('wrong_pass'))

    def test_02_changepass(self):
        EQ = self.assertEqual
        NEQ = self.assertNotEqual
        IN = self.assertIn
        NIN = self.assertNotIn
        
        old_pass = '3f21a8490cef2bfb60a9702e9d2ddb7' \
                   'a805c9bd1a263557dfd51a7d0e9dfa93e'
        EQ(u.data['password'][0], old_pass)
        EQ(ud['data']['password'][0], old_pass)
        EQ(len(u._cref), 3)
        EQ(len(ud['_cref']), 3)
        EQ(len(u._ref), 3)
        EQ(len(ud['_ref']), 3)
        IN(ap._hash, u._cref)
        IN(ap._hash, ud['_cref'])
        IN(ap._hash, u._ref)
        IN(ap._hash, ud['_ref'])

        u.changepass('newpassword')
        builtins.ud = u._backend.find_one({'_hash': u._hash}, {'_id': 0})

        NEQ(u.data['password'][0], old_pass)
        NEQ(ud['data']['password'][0], old_pass)
        EQ(len(u._cref), 3)
        EQ(len(ud['_cref']), 3)
        EQ(len(u._ref), 3)
        EQ(len(ud['_ref']), 3)
        NIN(ap._hash, u._cref)
        NIN(ap._hash, ud['_cref'])
        NIN(ap._hash, u._ref)
        NIN(ap._hash, ud['_ref'])

        new_pass = '089542505d659cecbb988bb5ccff5bccf85b' \
                   'e2dfa8c221359079aee2531298bb'
        builtins.ap = Attribute('password', new_pass)
        
        EQ(u.data['password'][0], new_pass)
        EQ(ud['data']['password'][0], new_pass)
        EQ(len(u._cref), 3)
        EQ(len(ud['_cref']), 3)
        EQ(len(u._ref), 3)
        EQ(len(ud['_ref']), 3)
        IN(ap._hash, u._cref)
        IN(ap._hash, ud['_cref'])
        IN(ap._hash, u._ref)
        IN(ap._hash, ud['_ref'])


if __name__ == '__main__':
    unittest.main()








