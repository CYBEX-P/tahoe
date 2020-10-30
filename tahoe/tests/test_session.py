"""unittests for tahoe.session"""

if __name__ != 'tahoe.tests.test_session':
    import sys
    sys.path = ['..', '../..'] + sys.path
    del sys

import pdb
import unittest

from tahoe import Instance, Attribute, Object, Event, Session
from tahoe.backend import MongoBackend, MockMongoBackend
from tahoe.tests.test_backend import MongoBackendTest


def setUpModule():
    _backend = MongoBackendTest.setUpClass()
    Instance.set_backend(_backend)

    assert Attribute._backend is Instance._backend
    assert Object._backend is Instance._backend
    assert Event._backend is Instance._backend
    assert Session._backend is Instance._backend
   

def tearDownModule():
    MongoBackendTest.tearDownClass()


def make_test_data():
    import builtins
    builtins.afn = Attribute('filename', 'virus.exe')
    builtins.afs = Attribute('filesize', 20012)
    builtins.of = Object('file', [afn, afs])

    builtins.au = Attribute('url', 'example.com')

    builtins.orgid = 'a441b15fe9a3cf56661190a0b93b9dec7d041272' \
                '88cc87250967cf3b52894d11'''

    builtins.e1 = Event('file_download', [au, of], orgid, 100)
    builtins.e2 = Event('file_download', [au, of], orgid, 200)
    builtins.e3 = Event('file_download', [au, of], orgid, 300)

    builtins.ausr = Attribute('user', 'johndoe')
    builtins.aday = Attribute('day', 'monday')
    builtins.os = Object('session', [ausr, aday])

class SetBackendTest(unittest.TestCase):
    """
    Examples
    --------
    Correct Way to set default backend::
        
        >>> from tahoe import Instance, Attribute, Object, MongoBackend
        >>> _backend = MongoBackend()
        >>> Instance.set_backend(_backend)
        >>> Instance._backend
        MongoBackend("localhost:27017", "tahoe_db", "instance")
        >>> Attribute._backend is Instance._backend
        True
        >>> Object._backend is Instance._backend
        True
        >>> Event._backend is Instance._backend
        

    Wrong ways to set default backend::

        >>> Attribute._backend = MongoBackend()

        >>> from tahoe import NoBackend, MongoBackend
        >>> no_backend = NoBackend()
        >>> no_backend
        NoBackend()
        
        >>> mongo_backend = MongoBackend(dbname="test_db")
        >>> mongo_backend
        MongoBackend("localhost:27017", "test_db", "instance")
        
        >>> Object.set_backend(no_backend)
        >>> Object._backend
        NoBackend()

        >>> a = Attribute("test", "test")
        >>> o = Object('test', [a])
        >>> o._backend
        NoBackend()

        >>> Object.set_backend(mongo_backend)
        >>> Object._backend
        MongoBackend("localhost:27017", "test_db", "instance")

        >>> a2 = Attribute("test", "test2")
        >>> a2._backend
        MongoBackend("localhost:27017", "test_db", "instance")

        >>> a2._backend = NoBackend()
        >>> Attribute._backend
        NoBackend()
    """
    pass


class InitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        assert isinstance(Session._backend, (MongoBackend, MockMongoBackend))
        Session._backend.drop()
        make_test_data()

    def test_01_init_no_data(self):
        s = Session('test')
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIsNotNone(s_d)

        self.assertEqual(s.itype, 'session')
        self.assertEqual(s.sub_type, 'test')
        self.assertEqual(s_d['itype'], 'session')
        self.assertEqual(s_d['sub_type'], 'test')

        u = s.data['sessionid'][0]
        u_d = s_d['data']['sessionid'][0]
        self.assertEqual(u, u_d)

        import uuid
        uuid.UUID(u)

        au = Attribute('sessionid', u)
        self.assertIn(au._hash, s._cref)
        self.assertIn(au._hash, s_d['_cref'])
        self.assertIn(au._hash, s._ref)
        self.assertIn(au._hash, s_d['_ref'])

    def test_02_init_w_attribute(self):
        s = Session('test', ausr)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIsNotNone(s_d)

        self.assertEqual(s.itype, 'session')
        self.assertEqual(s.sub_type, 'test')
        self.assertEqual(s_d['itype'], 'session')
        self.assertEqual(s_d['sub_type'], 'test')

        u = s.data['user'][0]
        u_d = s_d['data']['user'][0]
        self.assertEqual(u, u_d)
        self.assertEqual(u, 'johndoe')

        self.assertIn(ausr._hash, s._cref)
        self.assertIn(ausr._hash, s_d['_cref'])
        self.assertIn(ausr._hash, s._ref)
        self.assertIn(ausr._hash, s_d['_ref'])

    def test_03_init_w_object(self):
        s = Session('test', os)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIsNotNone(s_d)

        self.assertEqual(s.itype, 'session')
        self.assertEqual(s.sub_type, 'test')
        self.assertEqual(s_d['itype'], 'session')
        self.assertEqual(s_d['sub_type'], 'test')

        u = s.data['session'][0]['user'][0]
        u_d = s_d['data']['session'][0]['user'][0]
        self.assertEqual(u, u_d)
        self.assertEqual(u, 'johndoe')

        d = s.data['session'][0]['day'][0]
        d_d = s_d['data']['session'][0]['day'][0]
        self.assertEqual(d, d_d)
        self.assertEqual(d, 'monday')

        self.assertNotIn(ausr._hash, s._cref)
        self.assertNotIn(ausr._hash, s_d['_cref'])
        self.assertIn(ausr._hash, s._ref)
        self.assertIn(ausr._hash, s_d['_ref'])
        self.assertNotIn(aday._hash, s._cref)
        self.assertNotIn(aday._hash, s_d['_cref'])
        self.assertIn(aday._hash, s._ref)
        self.assertIn(aday._hash, s_d['_ref'])
        self.assertIn(os._hash, s._cref)
        self.assertIn(os._hash, s_d['_cref'])
        self.assertIn(os._hash, s._ref)
        self.assertIn(os._hash, s_d['_ref'])

        
class AddRemoveEventTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(Session._backend, (MongoBackend, MockMongoBackend))
        Session._backend.drop()
        make_test_data()

    def test_01_add_event(self):
        s = Session('test', os)
        s.add_event(e1)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIn(e1._hash, s._ref)
        self.assertIn(e1._hash, s_d['_ref'])

    def test_02_add_2nd_event(self):
        s = Session('test', os)
        s.add_event(e2)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIn(e2._hash, s._ref)
        self.assertIn(e2._hash, s_d['_ref'])

    def test_03_remove_event(self):
        s = Session('test', os)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIn(e1._hash, s._ref)
        self.assertIn(e1._hash, s_d['_ref'])
        
        s.remove_event(e1)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertNotIn(e1._hash, s._ref)
        self.assertNotIn(e1._hash, s_d['_ref'])

    def test_03_remove_2nd_event(self):
        s = Session('test', os)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIn(e2._hash, s._ref)
        self.assertIn(e2._hash, s_d['_ref'])
        
        s.remove_event(e2)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertNotIn(e2._hash, s._ref)
        self.assertNotIn(e2._hash, s_d['_ref'])

    def test_04_add_multiple_event(self):
        s = Session('test', os)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertNotIn(e1._hash, s._ref)
        self.assertNotIn(e1._hash, s_d['_ref'])
        self.assertNotIn(e2._hash, s._ref)
        self.assertNotIn(e2._hash, s_d['_ref'])
        self.assertNotIn(e3._hash, s._ref)
        self.assertNotIn(e3._hash, s_d['_ref'])

        s.add_event([e1, e2, e3])
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIn(e1._hash, s._ref)
        self.assertIn(e1._hash, s_d['_ref'])
        self.assertIn(e2._hash, s._ref)
        self.assertIn(e2._hash, s_d['_ref'])
        self.assertIn(e3._hash, s._ref)
        self.assertIn(e3._hash, s_d['_ref'])

    def test_05_remove_multiple_event(self):
        s = Session('test', os)
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertIn(e1._hash, s._ref)
        self.assertIn(e1._hash, s_d['_ref'])
        self.assertIn(e2._hash, s._ref)
        self.assertIn(e2._hash, s_d['_ref'])
        self.assertIn(e3._hash, s._ref)
        self.assertIn(e3._hash, s_d['_ref'])

        s.remove_event([e1, e2, e3])
        s_d = s._backend.find_one({'_hash': s._hash})

        self.assertNotIn(e1._hash, s._ref)
        self.assertNotIn(e1._hash, s_d['_ref'])
        self.assertNotIn(e2._hash, s._ref)
        self.assertNotIn(e2._hash, s_d['_ref'])
        self.assertNotIn(e3._hash, s._ref)
        self.assertNotIn(e3._hash, s_d['_ref'])

        


if __name__ == '__main__':
    unittest.main()

    


