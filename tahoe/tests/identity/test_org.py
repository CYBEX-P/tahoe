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

from tahoe import Instance, Attribute, Object
from tahoe.identity import User, Org
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import setUpBackend, tearDownBackend


def make_test_data():
    builtins.u1 = User('user1@example.com', 'Abcd1234', 'User 1')
    builtins.u2 = User('user2@example.com', 'Abcd1234', 'User 2')
    builtins.u3 = User('user3@example.com', 'Abcd1234', 'User 3')

    builtins.o = Org('unr', u1, u1, 'University of Nevada Reno')
    builtins.od = o._backend.find_one({'_hash': o._hash})

    builtins.aon = Attribute('orgname', 'unr')
    builtins.an = Attribute('name', 'University of Nevada Reno')
    builtins.oadm = Object('cybexp_org_admin', u1)

    builtins.ae = Attribute('email_addr', 'user1@example.com')

    hashed_pass = hashlib.sha256('Abcd1234'.encode('utf-8')).hexdigest()
    builtins.ap = Attribute('password', hashed_pass)

    builtins.aun = Attribute('name', 'User 1')
    

def delete_test_data():
    del builtins.u1, builtins.u2, builtins.u3, builtins.o, builtins.od, \
        builtins.aon, builtins.an, builtins.oadm, builtins. ae, \
        builtins. ap, builtins.aun


def setUpModule():
    _backend = setUpBackend()
    Instance.set_backend(_backend)

    assert User._backend is Instance._backend
    assert Org._backend is Instance._backend
    assert isinstance(Org._backend, (IdentityBackend, MockIdentityBackend))
    

def tearDownModule():
    tearDownBackend(Instance._backend)


class InitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Org._backend.drop()
        make_test_data()

##    @classmethod
##    def tearDownClass(cls):
##        delete_test_data()
        
    def test_init(self):
        self.assertIsNotNone(od)

    def test_itype(self):
        EQ = self.assertEqual
        EQ(o.itype, 'object')
        EQ(od['itype'], 'object')

    def test_sub_type(self):
        EQ = self.assertEqual
        EQ(o.sub_type, 'cybexp_org')
        EQ(od['sub_type'], 'cybexp_org')

    def test_data_orgname(self):
        EQ = self.assertEqual
        EQ(o.data['orgname'][0], 'unr')
        EQ(od['data']['orgname'][0], 'unr')

    def test_data_name(self):
        EQ = self.assertEqual
        EQ(o.data['name'][0], 'University of Nevada Reno')
        EQ(od['data']['name'][0], 'University of Nevada Reno')

    def test_data_user(self):
        EQ = self.assertEqual
        expected_pass = '3f21a8490cef2bfb60a9702e9d2ddb' \
                        '7a805c9bd1a263557dfd51a7d0e9dfa93e'
        EQ(o.data['cybexp_user'][0]['email_addr'][0], 'user1@example.com')
        EQ(o.data['cybexp_user'][0]['name'][0], 'User 1')
        EQ(o.data['cybexp_user'][0]['password'][0], expected_pass)
        EQ(od['data']['cybexp_user'][0]['email_addr'][0], 'user1@example.com')
        EQ(od['data']['cybexp_user'][0]['name'][0], 'User 1')
        EQ(od['data']['cybexp_user'][0]['password'][0], expected_pass)

    def test_data_admin(self):
        EQ = self.assertEqual
        expected_pass = '3f21a8490cef2bfb60a9702e9d2ddb' \
                        '7a805c9bd1a263557dfd51a7d0e9dfa93e'
        EQ(o.data['cybexp_org_admin'][0]['cybexp_user'][0]['email_addr'][0],
           'user1@example.com')
        EQ(o.data['cybexp_org_admin'][0]['cybexp_user'][0]['name'][0],
           'User 1')
        EQ(o.data['cybexp_org_admin'][0]['cybexp_user'][0]['password'][0],
           expected_pass)
        EQ(od['data']['cybexp_org_admin'][0]['cybexp_user'][0]['email_addr'][0],
           'user1@example.com')
        EQ(od['data']['cybexp_org_admin'][0]['cybexp_user'][0]['name'][0],
           'User 1')
        EQ(od['data']['cybexp_org_admin'][0]['cybexp_user'][0]['password'][0],
           expected_pass)
        
    def test_cref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(o._cref), 4)
        EQ(len(od['_cref']), 4)
        
        IN(an._hash, o._cref)
        IN(aon._hash, o._cref)
        IN(u1._hash, o._cref)
        IN(oadm._hash, o._cref)
        IN(an._hash, od['_cref'])
        IN(aon._hash, od['_cref'])
        IN(u1._hash, od['_cref'])
        IN(oadm._hash, od['_cref'])

    def test_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(o._ref), 7)
        EQ(len(od['_ref']), 7)
        
        IN(ae._hash, o._ref)
        IN(ap._hash, o._ref)
        IN(aun._hash, o._ref)
        IN(an._hash, o._ref)
        IN(aon._hash, o._ref)
        IN(u1._hash, o._ref)
        IN(oadm._hash, o._ref)
        IN(an._hash, od['_ref'])
        IN(aon._hash, od['_ref'])
        IN(u1._hash, od['_ref'])
        IN(oadm._hash, od['_ref'])
        IN(ae._hash, od['_ref'])
        IN(ap._hash, od['_ref'])
        IN(aun._hash, od['_ref'])

    def test_usr_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(o._usr_ref), 1)
        EQ(len(od['_usr_ref']), 1)

        IN(u1._hash, o._usr_ref)
        IN(u1._hash, od['_usr_ref'])

    def test_adm_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(o._adm_ref), 1)
        EQ(len(od['_adm_ref']), 1)

        IN(u1._hash, o._adm_ref)
        IN(u1._hash, od['_adm_ref'])

    def test_hash(self):
        expected_hash = 'b92cd7e4702ec0691f9975fb3dd552a46a3' \
                        'e4dfb25726b258870133425b48373'
        EQ = self.assertEqual
        EQ(o._hash, expected_hash)
        EQ(od['_hash'], expected_hash)

    
if __name__ == '__main__':
    unittest.main()








