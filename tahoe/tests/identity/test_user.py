"""unittests for tahoe.identity.user"""

import builtins
import hashlib
import pdb
from pprint import pprint
import unittest

if __name__ != 'tahoe.tests.identity.test_user':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os

import tahoe
from tahoe import Instance, Attribute, Object
from tahoe.identity import User, SuperUser, Org
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import setUpBackend, tearDownBackend
from tahoe.identity.error import UserExistsError


def setUpModule():
    _backend = setUpBackend()

    Instance.set_backend(_backend)
    Attribute.set_backend(_backend)
    Object.set_backend(_backend)
    User.set_backend(_backend)
    SuperUser.set_backend(_backend)
    Org.set_backend(_backend)

    assert Instance._backend is Attribute._backend
    assert Instance._backend is Object._backend
    assert Instance._backend is User._backend
    assert Instance._backend is SuperUser._backend
    assert Instance._backend is Org._backend


def tearDownModule():
    tearDownBackend(Instance._backend)


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

    builtins.su1 = SuperUser('super1@example.com', 'Defg1234', 'Super 1')
    builtins.su1d = su1._backend.find_one({'_hash': su1._hash}, {'_id': 0})
    builtins.sae = Attribute('email_addr', 'super1@example.com')
    sup_hashed_pass = hashlib.sha256('Defg1234'.encode('utf-8')).hexdigest()
    builtins.sap = Attribute('password', sup_hashed_pass)
    builtins.san = Attribute('name', 'Super 1')

def delete_test_data():
    del builtins.u, builtins.ud, builtins.ae, builtins.ap, builtins.an,
    builtins.u1, builtins.u2, builtins.u3, builtins.o1, builtins.o2,
    builtins.o3, builtins.u4, builtins.u5, builtins.o4, builtins.su1,
    builtins.su1d, builtins.sae, builtins.sap, builtins.san
    



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



class SuperUserTest(unittest.TestCase):
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
        EQ(su1.itype, 'object')
        EQ(su1d['itype'], 'object')

    def test_sub_type(self):
        EQ = self.assertEqual
        EQ(su1.sub_type, 'cybexp_superuser')
        EQ(su1d['sub_type'], 'cybexp_superuser')

    def test_data_email_addr(self):
        EQ = self.assertEqual
        EQ(su1.data['email_addr'][0], 'super1@example.com')
        EQ(su1d['data']['email_addr'][0], 'super1@example.com')

    def test_data_password(self):
        EQ = self.assertEqual
        expected_pass = '1916a74dd92d2dae7e45b3518d2c56e0daa' \
                        '17dbd89c823b306ba1b13fb21be98'
        EQ(su1.data['password'][0], expected_pass)
        EQ(su1d['data']['password'][0], expected_pass)

    def test_data_name(self):
        EQ = self.assertEqual
        EQ(su1.data['name'][0], 'Super 1')
        EQ(su1d['data']['name'][0], 'Super 1')

    def test_cref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(su1._cref), 3)
        EQ(len(su1d['_cref']), 3)
        
        IN(sae._hash, su1._cref)
        IN(sap._hash, su1._cref)
        IN(san._hash, su1._cref)
        IN(sae._hash, su1d['_cref'])
        IN(sap._hash, su1d['_cref'])
        IN(san._hash, su1d['_cref'])

    def test_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(u._ref), 3)
        EQ(len(ud['_ref']), 3)
        
        IN(sae._hash, su1._ref)
        IN(sap._hash, su1._ref)
        IN(san._hash, su1._ref)
        IN(sae._hash, su1d['_ref'])
        IN(sap._hash, su1d['_ref'])
        IN(san._hash, su1d['_ref'])

    def test_hash(self):
        expected_hash = '3631303c39397a327e65ee6626f42dd'\
                        '613effff21b7351a1d30bbd47e751f895'
        EQ = self.assertEqual
        EQ(su1._hash, expected_hash)
        EQ(su1d['_hash'], expected_hash)


class CreateUserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        User._backend.drop()
        make_test_data()
        builtins.u10 = su1.create_user('user10@abc.co', 'A2', 'User 10')
        builtins.u10d = u10._backend.find_one({'_hash': u10._hash}, {'_id': 0})
        builtins.u10ae = Attribute('email_addr', 'user10@abc.co')
        u10_hashed_pass = hashlib.sha256('A2'.encode('utf-8')).hexdigest()
        builtins.u10ap = Attribute('password', u10_hashed_pass)
        builtins.u10an = Attribute('name', 'User 10')

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        del builtins.u10, builtins.u10d, builtins.u10ae, builtins.u10ap,
        builtins.u10an

    def test_init(self):
        self.assertIsNotNone(ud)

    def test_itype(self):
        EQ = self.assertEqual
        EQ(u10.itype, 'object')
        EQ(u10d['itype'], 'object')

    def test_sub_type(self):
        EQ = self.assertEqual
        EQ(u10.sub_type, 'cybexp_user')
        EQ(u10d['sub_type'], 'cybexp_user')

    def test_data_email_addr(self):
        EQ = self.assertEqual
        EQ(u10.data['email_addr'][0], 'user10@abc.co')
        EQ(u10d['data']['email_addr'][0], 'user10@abc.co')

    def test_data_password(self):
        EQ = self.assertEqual
        expected_pass = 'c8361f9b468e68c86da024270e094' \
                        '9ce139cb704b8d7cce586681b99f3a7ea56'
        EQ(u10.data['password'][0], expected_pass)
        EQ(u10d['data']['password'][0], expected_pass)

    def test_data_name(self):
        EQ = self.assertEqual
        EQ(u10.data['name'][0], 'User 10')
        EQ(u10d['data']['name'][0], 'User 10')

    def test_cref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(u10._cref), 3)
        EQ(len(u10d['_cref']), 3)
        
        IN(u10ae._hash, u10._cref)
        IN(u10ap._hash, u10._cref)
        IN(u10an._hash, u10._cref)
        IN(u10ae._hash, u10d['_cref'])
        IN(u10ap._hash, u10d['_cref'])
        IN(u10an._hash, u10d['_cref'])

    def test_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(u10._ref), 3)
        EQ(len(u10d['_ref']), 3)
        
        IN(u10ae._hash, u10._ref)
        IN(u10ap._hash, u10._ref)
        IN(u10an._hash, u10._ref)
        IN(u10ae._hash, u10d['_ref'])
        IN(u10ap._hash, u10d['_ref'])
        IN(u10an._hash, u10d['_ref'])

    def test_hash(self):
        expected_hash = 'd81ff9d941586ddf14e7b1893462f' \
                        '842b1b80afb50eb64d298e369ea3a6d38f3'
        EQ = self.assertEqual
        EQ(u10._hash, expected_hash)
        EQ(u10d['_hash'], expected_hash)
        
    def test_user_exists_error(self):
        self.assertRaises(UserExistsError,
            su1.create_user, 'user10@abc.co', 'A2', 'User 10')
    








        

if __name__ == '__main__':
    unittest.main()








