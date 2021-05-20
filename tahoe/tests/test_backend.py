"""unittests for tahoe.backend"""

import builtins
import pdb
from pprint import pprint
import unittest

if __name__ != 'tahoe.tests.identity.test_org':
    import sys, os
    J = os.path.join
    sys.path = ['..', J('..','..')] + sys.path
    del sys, os

from tahoe import Attribute
from tahoe.backend import *


class NoBackendTest(unittest.TestCase):
    pass


class MongoBackendTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls, dbname=''):
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure

        assert dbname in ('', 'tahoe_db', 'report_db')
        dbname = dbname + "1ef0534d-6ef7-4624-84c2-7bf59f1b3927"

        try:
            raise ConnectionFailure
            client = MongoClient()
            client.admin.command('ismaster')
            
            cls._backend = MongoBackend(dbname=dbname)

        except ConnectionFailure:
            cls._backend = MockMongoBackend(dbname=dbname)

        cls._backend.drop()
        
        return cls._backend

    @classmethod
    def tearDownClass(cls):
        dbname = cls._backend.database.name
        result = cls._backend.database.client.drop_database(dbname)

    def test01_repr(self):
        EQ = self.assertEqual
        if isinstance(self._backend, MockMongoBackend):
            EQ(repr(self._backend), "MockMongoBackend(" +
                "'mongodb://localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")
        elif isinstance(self._backend, MongoBackend):
            EQ(repr(self._backend), "MongoBackend(" +
                "'mongodb://localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")

    def test02_str(self):
        EQ = self.assertEqual
        if isinstance(self._backend, MockMongoBackend):
            EQ(repr(self._backend), "MockMongoBackend(" +
                "'mongodb://localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")
        elif isinstance(self._backend, MongoBackend):
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


class FindAttributeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Attribute._backend = MongoBackendTest.setUpClass()
        Attribute._backend.drop()

    @classmethod
    def tearDownClass(cls):
        MongoBackendTest.tearDownClass()

    def test_01(self):
        b = Attribute._backend
        
        a1 = Attribute('test_sub_type', 'test_data')
        a1d = b.find_one({'_hash': a1._hash}, {'_id':0})

        a11 = b.find_attribute('test_sub_type', 'test_data', parse=True)
        a11d = b.find_attribute('test_sub_type', 'test_data')
        
        self.assertEqual(a1.doc, a11.doc)
        self.assertEqual(a1d, a11d)

        


    
        
if __name__ == '__main__':
    unittest.main()

