"""unittests for tahoe.object"""

if __name__ != 'tahoe.tests.test_tdql':
    import sys
    sys.path = ['..', '../..'] + sys.path
    del sys

import builtins
import hashlib
import pdb
import unittest


from tahoe import Instance, Attribute, Object, TDQL
from tahoe.backend import MongoBackend, MockMongoBackend
from tahoe.tests.test_backend import MongoBackendTest
from tahoe.misc import canonical, decanonical

def setUpModule():
    _backend = MongoBackendTest.setUpClass()
    Instance.set_backend(_backend)
    Attribute.set_backend(_backend)

    assert Attribute._backend is Instance._backend
    assert Object._backend is Instance._backend
    assert TDQL._backend is Instance._backend
    

def tearDownModule():
    MongoBackendTest.tearDownClass()


def make_test_data():
    builtins.data = {
        "type": "count", 
        "data" : {
            "sub_type": "email_addr", 
            "data": "dn...etto@yahoo.com",
            "category": "all",
        "context": "all",
        "last": "1Y"
        }
    }
    builtins.canon_data = canonical(data)
    
    builtins.userid = 'a441b15fe9a3cf56661190a0b93b9dec7d041272' \
            '88cc87250967cf3b52894d11'''
    builtins.timestamp = -1
    builtins.encrypted = False
    builtins.qtype = "count"
    builtins.qdata = canon_data
    builtins.qhash = hashlib.sha256(canon_data.encode()).hexdigest()
    builtins.q = TDQL(qtype, qdata, qhash, userid, encrypted)
    builtins.q_d = q._backend.find_one({'_hash': q._hash})

class AllTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        assert isinstance(TDQL._backend, (MongoBackend, MockMongoBackend))
        

    def test_01_init(self):
        TDQL._backend.drop()
        make_test_data()

        self.assertIsNotNone(q_d)

        q_hash_expected = '61ee1e55f33651cf82746032b9c28' \
                          '1d5a546cf4475adbe96c162aa9ae6be1384'

        self.assertEqual(q.itype, 'object')
        self.assertEqual(q_d['itype'], 'object')

        self.assertEqual(q.sub_type, 'query')
        self.assertEqual(q_d['sub_type'], 'query')

        self.assertEqual(q.data['qdata'][0], canon_data)
        self.assertEqual(q_d['data']['qdata'][0], canon_data)
        
        self.assertEqual(q.data['userid'][0], userid)
        self.assertEqual(q_d['data']['userid'][0], userid)
        
        self.assertNotEqual(q.data['timestamp'][0], -1)
        self.assertNotEqual(q_d['data']['timestamp'][0], -1)

        self.assertEqual(q.data['encrypted'][0], False)
        self.assertEqual(q_d['data']['encrypted'][0], False)

        self.assertEqual(q.data['status'][0], 'invalid')
        self.assertEqual(q_d['data']['status'][0], 'invalid')

        self.assertEqual(q.data['report_id'][0], '')
        self.assertEqual(q_d['data']['report_id'][0], '')

        self.assertEqual(q.data['socket'][0]['host'][0], 'localhost')
        self.assertEqual(q_d['data']['socket'][0]['host'][0], 'localhost')

##        self.assertEqual(q._hash, q_hash_expected)
##        self.assertEqual(q_d['_hash'], q_hash_expected)


    def test_02_setstatus(self):
        TDQL._backend.drop()
        make_test_data()

        EQ = self.assertEqual

        EQ(q.data['status'][0], 'invalid')
        EQ(q_d['data']['status'][0], 'invalid')

        q.status = 'ready'
        builtins.q_d = q._backend.find_one({'_hash': q._hash})

        EQ(q.data['status'][0], 'ready')
        EQ(q_d['data']['status'][0], 'ready')

        self.assertRaises(ValueError, setattr, q, "status", 'anything')

    def test_03_setsocket(self):
        TDQL._backend.drop()
        make_test_data()

        EQ = self.assertEqual

        EQ(q.data['socket'][0]['host'][0], 'localhost')
        EQ(q_d['data']['socket'][0]['host'][0], 'localhost')
        EQ(q.data['socket'][0]['port'][0], 0)
        EQ(q_d['data']['socket'][0]['port'][0], 0)
        EQ(q.data['socket'][0]['nonce'][0], '')
        EQ(q_d['data']['socket'][0]['nonce'][0], '')

        q.setsocket('localhost', 100, 'abcdefgh')
        
        builtins.q_d = q._backend.find_one({'_hash': q._hash})

        EQ(q.data['socket'][0]['host'][0], 'localhost')
        EQ(q_d['data']['socket'][0]['host'][0], 'localhost')
        EQ(q.data['socket'][0]['port'][0], 100)
        EQ(q_d['data']['socket'][0]['port'][0], 100)
        EQ(q.data['socket'][0]['nonce'][0], 'abcdefgh')
        EQ(q_d['data']['socket'][0]['nonce'][0], 'abcdefgh')

    def test_04_unique(self):
        """Ensure _hash is different for related and count."""

        rel_data = {
            "type": "related", 
            "data" : {
                "sub_type": "email_addr", 
                "data": "dn...etto@yahoo.com",
                "category": "all",
            "context": "all",
            "last": "1Y"
            }
        }

        rel_canon_data = canonical(data)
        rel_qtype = "related"
        rel_qdata = rel_canon_data
        rel_qhash = hashlib.sha256(rel_canon_data.encode()).hexdigest()

        rel_q = TDQL(rel_qtype, rel_qdata, rel_qhash,
                     userid, encrypted)
        rel_q_d = rel_q._backend.find_one({'_hash': rel_q._hash})

        self.assertNotEqual(rel_q._hash, q._hash)    
        
       


if __name__ == '__main__':
    unittest.main()

    


