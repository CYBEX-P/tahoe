"""unittests for tahoe.identity.org"""

import builtins
import hashlib
import pdb
from pprint import pprint
import unittest

if __name__ != 'tahoe.tests.identity.test_org':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os

from tahoe import Instance, Attribute, Object
from tahoe.identity import User, Org
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import setUpBackend, tearDownBackend
from tahoe.identity.org import AdminIsNotUserError, UserIsAdminError, \
    UserIsNotAdminError, UserIsInOrgError

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

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        
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
        EQ(o.data['admin'][0]['cybexp_user'][0]['email_addr'][0],
           'user1@example.com')
        EQ(o.data['admin'][0]['cybexp_user'][0]['name'][0],
           'User 1')
        EQ(o.data['admin'][0]['cybexp_user'][0]['password'][0],
           expected_pass)
        EQ(od['data']['admin'][0]['cybexp_user'][0]['email_addr'][0],
           'user1@example.com')
        EQ(od['data']['admin'][0]['cybexp_user'][0]['name'][0],
           'User 1')
        EQ(od['data']['admin'][0]['cybexp_user'][0]['password'][0],
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

    def test_acl(self):
        EQ = self.assertEqual
        IN = self.assertIn
        NIN = self.assertNotIn

        EQ(len(o._acl), 1)
        EQ(len(od['_acl']), 1)

        IN(u1._hash, o._acl)
        NIN(u2._hash, o._acl)
        NIN(u3._hash, o._acl)

        IN(u1._hash, od['_acl'])
        NIN(u2._hash, od['_acl'])
        NIN(u3._hash, od['_acl'])

    def test_hash(self):
        expected_hash = 'b92cd7e4702ec0691f9975fb3dd552a46a3' \
                        'e4dfb25726b258870133425b48373'
        EQ = self.assertEqual
        EQ(o._hash, expected_hash)
        EQ(od['_hash'], expected_hash)


class InfoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Org._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()

    def test_admins(self):
        EQ = self.assertEqual

        admins = o.get_admins()

        EQ(type(admins), list)
        EQ(len(admins), 1)

        adm1 = admins[0]

        EQ(adm1._hash, u1._hash)
        EQ(adm1.email, u1.email)

    def test_users(self):
        EQ = self.assertEqual
        users = o.get_users()
        EQ(type(users), list)
        EQ(len(users), 1)
        usr1 = users[0]
        EQ(usr1._hash, u1._hash)
        EQ(usr1.email, u1.email)


class AddAdminTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Org._backend.drop()
        make_test_data()
        builtins.o10 = Org('test_org_10', [u1,u2], u2, 'Test Org 10')
        builtins.o11 = Org('test_org_11', [u1,u2], [u1,u2], 'Test Org 11')
        builtins.o12 = Org('test_org_11', [u1,u2,u3], [u1,u2], 'Test Org 11')

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        del builtins.o10, builtins.o11, builtins.o12

    def test_1_add_admin(self):
        IN = self.assertIn
        INN = self.assertIsNotNone
        
        o10.add_admin(u1)
        o10d = Instance._backend.find_one({'_hash': o10._hash})

        o10_email = []
        for a in o10.data['admin'][0]['cybexp_user']:
            o10_email.append(a['email_addr'][0])
        o10d_email =  []
        for a in o10d['data']['admin'][0]['cybexp_user']:
            o10d_email.append(a['email_addr'][0])

        IN(u1._hash, o10._cref)
        IN(u1._hash, o10._ref)
        IN(u1._hash, o10._usr_ref)
        IN(u1._hash, o10._adm_ref)
        IN(u1._hash, o10._acl)
        IN(u1.email, o10_email)

        INN(o10d)
        IN(u1._hash, o10d['_cref'])
        IN(u1._hash, o10d['_ref'])
        IN(u1._hash, o10d['_usr_ref'])
        IN(u1._hash, o10d['_adm_ref'])
        IN(u1._hash, o10d['_acl'])
        IN(u1.email, o10d_email)

    def test_2_user_is_admin_error(self):
        self.assertRaises(UserIsAdminError, o10.add_admin, u2)
        self.assertRaises(UserIsAdminError, o12.add_admin, u2)

    def test_3_admin_not_user_error(self):
        self.assertRaises(AdminIsNotUserError, o10.add_admin, u3)



class AddUserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Org._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()

    def test_1_add_user(self):
        Org._backend.drop()
        make_test_data()
        
        EQ = self.assertEqual
        IN = self.assertIn
        NIN = self.assertNotIn
        INN = self.assertIsNotNone
        
        o2 = Org('test_org', u2, u2, 'Test Org')
        o2d = Instance._backend.find_one({'_hash': o2._hash})

        o2_email = [ u['email_addr'][0] for u in o2.data['cybexp_user'] ]
        o2d_email = [ u['email_addr'][0] for u in o2d['data']['cybexp_user'] ]

        NIN(u1._hash, o2._cref)
        NIN(u1._hash, o2._ref)
        NIN(u1._hash, o2._usr_ref)
        NIN(u1._hash, o2._acl)
        NIN(u1.email, o2_email)

        INN(o2d)
        NIN(u1._hash, o2d['_cref'])
        NIN(u1._hash, o2d['_ref'])
        NIN(u1._hash, o2d['_usr_ref'])
        NIN(u1._hash, o2d['_acl'])
        NIN(u1.email, o2d_email)
        
        
        o2.add_user(u1)
        o2d = Instance._backend.find_one({'_hash': o2._hash})

        o2_email = [ u['email_addr'][0] for u in o2.data['cybexp_user'] ]
        o2d_email = [ u['email_addr'][0] for u in o2d['data']['cybexp_user'] ]

        IN(u1._hash, o2._cref)
        IN(u1._hash, o2._ref)
        IN(u1._hash, o2._usr_ref)
        IN(u1._hash, o2._acl)
        IN(u1.email, o2_email)

        INN(o2d)
        IN(u1._hash, o2d['_cref'])
        IN(u1._hash, o2d['_ref'])
        IN(u1._hash, o2d['_usr_ref'])
        IN(u1._hash, o2d['_acl'])
        IN(u1.email, o2d_email)

        delete_test_data()
        make_test_data()

    def test_2_user_in_org_error(self):
        self.assertRaises(UserIsInOrgError, o.add_user, u1)


class DelAdminTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Org._backend.drop()
        make_test_data()
        builtins.o10 = Org('test_org_10', [u1,u2], [u1, u2], 'Test Org 10')
        builtins.o11 = Org('test_org_11', [u1,u2], [u1], 'Test Org 11')
        builtins.o12 = Org('test_org_11', [u1,u2,u3], [u1,u2], 'Test Org 11')

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        del builtins.o10, builtins.o11, builtins.o12

    def test_1_del_admin(self):
        IN = self.assertIn
        NIN = self.assertNotIn
        INN = self.assertIsNotNone

        o10.del_admin(u1)
        o10d = Instance._backend.find_one({'_hash': o10._hash})

        o10_email = []
        for a in o10.data['admin'][0]['cybexp_user']:
            o10_email.append(a['email_addr'][0])
        o10d_email =  []
        for a in o10d['data']['admin'][0]['cybexp_user']:
            o10d_email.append(a['email_addr'][0])

        IN(u1._hash, o10._cref)
        IN(u1._hash, o10._ref)
        IN(u1._hash, o10._usr_ref)
        NIN(u1._hash, o10._adm_ref)
        IN(u1._hash, o10._acl)
        NIN(u1.email, o10_email)

        INN(o10d)
        IN(u1._hash, o10d['_cref'])
        IN(u1._hash, o10d['_ref'])
        IN(u1._hash, o10d['_usr_ref'])
        NIN(u1._hash, o10d['_adm_ref'])
        IN(u1._hash, o10d['_acl'])
        NIN(u1.email, o10d_email)

    def test_2_user_is_not_admin_error(self):
        self.assertRaises(UserIsNotAdminError, o10.del_admin, u3)
        self.assertRaises(ValueError, o12.add_admin, o12._hash)

    

class DelUserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Org._backend.drop()
        make_test_data()
        builtins.o10 = Org('test_org_10', [u1,u2], [u1,u2], 'Test Org 10')

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        del builtins.o10

    def test_1_del_user(self):        
        EQ = self.assertEqual
        IN = self.assertIn
        NIN = self.assertNotIn
        INN = self.assertIsNotNone

        o2 = Org('test_org', [u1,u2], u2, 'Test Org')
        o2d = Instance._backend.find_one({'_hash': o2._hash})

        o2_email = [ u['email_addr'][0] for u in o2.data['cybexp_user'] ]
        o2d_email = [ u['email_addr'][0] for u in o2d['data']['cybexp_user'] ]

        IN(u1._hash, o2._cref)
        IN(u1._hash, o2._ref)
        IN(u1._hash, o2._usr_ref)
        IN(u1._hash, o2._acl)
        IN(u1.email, o2_email)

        INN(o2d)
        IN(u1._hash, o2d['_cref'])
        IN(u1._hash, o2d['_ref'])
        IN(u1._hash, o2d['_usr_ref'])
        IN(u1._hash, o2d['_acl'])
        IN(u1.email, o2d_email)

        o2.del_user(u1)
        o2d = Instance._backend.find_one({'_hash': o2._hash})

        o2_email = [ u['email_addr'][0] for u in o2.data['cybexp_user'] ]
        o2d_email = [ u['email_addr'][0] for u in o2d['data']['cybexp_user'] ]

        NIN(u1._hash, o2._cref)
        NIN(u1._hash, o2._ref)
        NIN(u1._hash, o2._usr_ref)
        NIN(u1._hash, o2._acl)
        NIN(u1.email, o2_email)

        INN(o2d)
        NIN(u1._hash, o2d['_cref'])
        NIN(u1._hash, o2d['_ref'])
        NIN(u1._hash, o2d['_usr_ref'])
        NIN(u1._hash, o2d['_acl'])
        NIN(u1.email, o2d_email)


    def test_2_user_is_admin_error(self):
        o2 = Org('test_org', [u1,u2], u2, 'Test Org')
        o2d = Instance._backend.find_one({'_hash': o2._hash})
        self.assertRaises(UserIsAdminError, o2.del_user, u2)

    def test_3_delete_admin_then_user(self):
        pass


    
        
        
        

    
if __name__ == '__main__':
    unittest.main()








