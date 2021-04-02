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

import tahoe
from tahoe import Instance, Attribute, Object
from tahoe.identity import User, Org
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import setUpBackend, tearDownBackend

def make_test_data():
    builtins.u = User('johndoe@example.com', 'Abcd1234', 'John Doe')
    builtins.ud = u._backend.find_one({'_hash': u._hash}, {'_id': 0})

    builtins.ae = Attribute('email_addr', 'johndoe@example.com')

    hashed_pass = hashlib.sha256('Abcd1234'.encode('utf-8')).hexdigest()
    builtins.ap = Attribute('password', hashed_pass)

    builtins.an = Attribute('name', 'John Doe')

    builtins.u1 = User('user1@example.com', 'Abcd1234', 'User 1')
    builtins.u2 = User('user2@example.com', 'Abcd1234', 'User 2')
    builtins.u3 = User('user3@example.com', 'Abcd1234', 'User 3')
    builtins.u4 = User('user4@example.com', 'Abcd1234', 'User 4')
    builtins.u5 = User('user5@example.com', 'Abcd1234', 'User 5')

    builtins.o1 = Org('org1', u1, u1, 'Organization 1')
    builtins.o2 = Org('org2', [u1,u2], u2, 'Organization 2')
    builtins.o3 = Org('org3', [u2], u2, 'Organization 3')
    builtins.o4 = Org('org4', [u4, u5], [u4,u5], 'Organization 4')


def delete_test_data():
    del builtins.u, builtins.ud, builtins.ae, builtins.ap, builtins.an,
    builtins.u1, builtins.u2, builtins.u3, builtins.o1, builtins.o2,
    builtins.o3, builtins.u4, builtins.u5, builtins.o4


def setUpModule():
    _backend = setUpBackend()
    Instance.set_backend(_backend)

    assert User._backend is Instance._backend
    assert isinstance(User._backend, (IdentityBackend, MockIdentityBackend))
    

def tearDownModule():
    tearDownBackend(Instance._backend)


class InitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        User._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()

    def test_01_check_pass(self):
        self.assertTrue(u.check_pass('Abcd1234'))
        self.assertFalse(u.check_pass('wrong_pass'))

    def test_02_change_pass(self):
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

        u.change_pass('newpassword')
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


class OrgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        User._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()

    def test_orgs_admin_of(self):
        IN = self.assertIn
        RAS = self.assertRaises

        r = u1.orgs_admin_of()
        for i in r:
            IN(i['_hash'], [o1._hash])

        r = u3.orgs_admin_of()
        RAS(StopIteration, r.next)
               
    def test_orgs_user_of(self):
        IN = self.assertIn
        RAS = self.assertRaises
        
        r = u1.orgs_user_of()
        for i in r:
            IN(i['_hash'], [o1._hash, o2._hash])

        r = u3.orgs_user_of()
        RAS(StopIteration, r.next)



class IsAdminOfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        User._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()

    def test_1_one_user_one_admin(self):
        self.assertEqual(True, u1.is_admin_of(o1))

    def test_2_two_user_one_admin(self):
        self.assertEqual(True, u2.is_admin_of(o2))

    def test_3_two_user_two_admin(self):
        self.assertEqual(True, u4.is_admin_of(o4))

    def test_4_False_org(self):
        self.assertEqual(False, u1.is_admin_of(o4))

    def test_5_one_user_one_admin_hash(self):
        self.assertEqual(True, u1.is_admin_of(o1._hash))
            
    def test_6_two_user_one_admin_hash(self):
        self.assertEqual(True, u2.is_admin_of(o2._hash))

    def test_7_two_user_two_admin_hash(self):
        self.assertEqual(True, u4.is_admin_of(o4._hash))

    def test_8_False_org_hash(self):
        self.assertEqual(False, u1.is_admin_of(o4._hash))

    def test_9_valueerror_invalid_org_hash(self):
        self.assertRaises(ValueError, u1.is_admin_of, 'abc')

    def test_10_valueerror_hash_is_valid_but_not_org(self):
        self.assertRaises(ValueError, u1.is_admin_of, u2._hash)

if __name__ == '__main__':
    unittest.main()








