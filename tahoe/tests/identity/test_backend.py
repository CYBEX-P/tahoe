"""unittests for tahoe.identity.backend"""

import pdb
import unittest

if __name__ != 'tahoe.tests.identity.test_backend':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os


from tahoe.identity.backend import *


def setUpBackend():
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    dbname = "1ef0534d-6ef7-4624-84c2-7bf59f1b3927"
    try:
        raise ConnectionFailure  # debug delete me
        client = MongoClient()
        client.admin.command('ismaster')
        _backend = IdentityBackend(dbname=dbname)
    except ConnectionFailure:
        _backend = MockIdentityBackend(dbname=dbname)
    _backend.drop()
    return _backend

def tearDownBackend(_backend):
    dbname = _backend.database.name
    _backend.database.client.drop_database(dbname)
    

class IdentityBackendTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._backend = setUpBackend()

    @classmethod
    def tearDownClass(cls):
        tearDownBackend(cls._backend)

    def test01_repr(self):
        EQ = self.assertEqual
        if isinstance(self._backend, MockIdentityBackend):
            EQ(repr(self._backend), "MockMongoBackend(" +
                "'mongodb://localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")
        elif isinstance(self._backend, IdentityMongoBackend):
            EQ(repr(self._backend), "MongoBackend(" +
                "'mongodb://localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")

    def test02_str(self):
        EQ = self.assertEqual
        if isinstance(self._backend, MockIdentityBackend):
            EQ(repr(self._backend), "MockMongoBackend(" +
                "'mongodb://localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")
        elif isinstance(self._backend, IdentityBackend):
            EQ(repr(self._backend), "MongoBackend(" +
                "'mongodb://localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")

    def test03_find(self):
        rr = self._backend.find({})

    def test04_find_one(self):
        self.assertIsNone(self._backend.find_one())

    def test05_insert_one(self):
        _id = self._backend.insert_one({'a': 1}).inserted_id
        doc = self._backend.find_one({'_id': _id})
        self.assertEqual(doc['a'], 1)

    def test06_update_one(self):
        result = self._backend.update_one({'a': 1}, {'$set': {'b': 2}})
        self.assertTrue(result.acknowledged)
        doc = self._backend.find_one({'a': 1})
        self.assertEqual(doc['b'], 2)

    def test07_isinstance(self):
        self.assertIsInstance(self._backend,
                              (IdentityBackend, MockIdentityBackend))
        
if __name__ == '__main__':
    unittest.main()

