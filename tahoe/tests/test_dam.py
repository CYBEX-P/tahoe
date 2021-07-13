"""unittests for tahoe.dam"""

import builtins as B
import hashlib
import pdb
import unittest
import time 

if __name__ != 'tahoe.tests.test_dam':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os
import tahoe
from tahoe import Instance, Attribute, Object, Event, Session
from tahoe.identity import Identity, Org, User
from tahoe.backend.dam import DamBackend, MockDamBackend
from tahoe.tests.test_backend import setUpBackend, tearDownBackend
from tahoe.tests.identity.test_backend import setUpBackend as setUpIdBackend, \
     tearDownBackend as tearDownIdBackend

def setUpModule():
    
    _backend = setUpBackend()
    _id_backend = setUpIdBackend()

    Instance.set_backend(_backend)
    Attribute.set_backend(_backend)
    Object.set_backend(_backend)
    Event.set_backend(_backend)
    Session.set_backend(_backend)
    Identity._backend = _id_backend
    User._backend = _id_backend
    Org._backend = _id_backend

    assert Instance._backend is Attribute._backend
    assert Instance._backend is Object._backend
    assert Instance._backend is Event._backend
    assert Instance._backend is Session._backend

    assert Identity._backend is User._backend
    assert Identity._backend is Org._backend
    
def tearDownModule():
    tearDownBackend(Instance._backend)
    tearDownIdBackend(Identity._backend)
    

def make_test_data():

    B.u1 = User('user1@example.com', 'pass1', 'User 1')
    B.u2 = User('user2@example.com', 'pass2', 'User 2')
    B.u3 = User('user3@example.com', 'pass3', 'User 3')
    B.u4 = User('user4@example.com', 'pass4', 'User 4')

    B.o1 = Org("org1",[u1], [u1], "Organization 1")
    B.o2 = Org("org2",[u2, u3], [u2], "Organization 2")
    B.o3 = Org("org3", u3, u3, "Organization 3")

    B.a1 = Attribute("ip", "1.1.1.1")
    B.a2 = Attribute("url", "1.com")
    B.a3 = Attribute("ip", "2.2.2.2")
    B.a4 = Attribute("url", "2.com")
    B.a5 = Attribute("url", "3.com")
    
    B.e11 = Event("test_event", [a1,a2], o1._hash, 1)
    B.e21 = Event("test_event", [a1,a2], o2._hash, 2)
    B.e22 = Event("test_event", [a3,a4], o2._hash, 3)
    B.e31 = Event("test_event", [a1,a5], o3._hash, 4)

    
def delete_test_data():
    del B.u1, B.u2, B.u3, B.u4, \
        B.o1, B.o2, B.o3, \
        B.a1, B.a2, B.a3, B.a4, \
        B.e11, B.e21, B.e22, B.e31 \



class CountTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Instance._backend.drop()
        make_test_data()
        cls.EQ = cls.assertEqual

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        Instance._backend.drop()
    
    def test_01_u1_a1(self):
        _dam = DamBackend(u1, Attribute._backend)
        a1._backend = _dam
        self.EQ(a1.count(), 1)

    def test_02_u2_a1(self):
        a1._backend = DamBackend(u2, Attribute._backend)
        self.EQ(a1.count(), 1)

    def test_03_u3_a1(self):
        a1._backend = DamBackend(u3, Attribute._backend)
        self.EQ(a1.count(), 2)

    def test_03_u4_a1(self):
        a1._backend = DamBackend(u4, Attribute._backend)
        self.EQ(a1.count(), 0)

class RelatedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Instance._backend.drop()
        make_test_data()
        cls.EQ = cls.assertEqual

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        Instance._backend.drop()
      
    def test_01_u1_a1(self):
        _dam = DamBackend(u1, Attribute._backend)
        a1._backend = _dam
        a1.related()
        self.EQ(len(a1.related()[0]), 3)
        
    def test_02_u2_a1(self):
        a1._backend = DamBackend(u2, Attribute._backend)
        self.EQ(len(a1.related()[0]), 3)

    def test_03_u3_a1(self):
        a1._backend = DamBackend(u3, Attribute._backend)
        self.EQ(len(a1.related()[0]), 5)
    
if __name__ == '__main__':
    unittest.main()



