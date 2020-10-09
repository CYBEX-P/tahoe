"""unittests for tahoe.backend"""

if __name__ != 'tahoe.tests.test_backend':
    import sys
    sys.path = ['..', '../..'] + sys.path
    del sys

import pdb
import unittest

from tahoe.backend import *


class NoBackendTest(unittest.TestCase):
    pass


class MongoBackendTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure

        dbname = "1ef0534d-6ef7-4624-84c2-7bf59f1b3927"

        try:
            raise ConnectionFailure
            client = MongoClient()
            client.admin.command('ismaster')
            
            cls._backend = MongoBackend(dbname=dbname)

        except ConnectionFailure:
            cls._backend = MongoBackend(dbname=dbname, mock=True)

        cls._backend.drop()
        
        return cls._backend

    @classmethod
    def tearDownClass(cls):
        dbname = cls._backend.database.name
        result = cls._backend.database.client.drop_database(dbname)

    def test01_repr(self):
        EQ = self.assertEqual
        if self._backend.mock:
            EQ(repr(self._backend), "MongoMockBackend('localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")
        else:
            EQ(repr(self._backend), "MongoBackend('localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")

    def test02_str(self):
        EQ = self.assertEqual
        if self._backend.mock:
            EQ(str(self._backend), "MongoMockBackend('localhost:27017'," + 
                " '1ef0534d-6ef7-4624-84c2-7bf59f1b3927', 'instance')")
        else:
            EQ(str(self._backend), "MongoBackend('localhost:27017'," + 
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




    
        
if __name__ == '__main__':
    unittest.main()

