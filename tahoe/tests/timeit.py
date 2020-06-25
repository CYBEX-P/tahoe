"""
Testing tahoe\_backend.py

Needs MongoDB at localhost:27017 (without auth) to run tests.
"""

import pdb
from pprint import pprint
from timeit import timeit
import unittest

from tahoe import MongoBackend, Attribute, Object


##rb = None  # debug delete me
##lb = None  # debug delete me

class TimeItTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mongo_url = "mongodb://cybexp_user:CybExP_777@134.197.21.231:27017/" + \
            "?authSource=admin"
        _backend = MongoBackend(mongo_url, dbname='tahoe_db',
                                collname='instances')
        cls.remote_backend = _backend

        _backend = MongoBackend(dbname='phish_db', collname='instances')
        cls.local_backend = _backend

##        global rb, lb  # debug delete me
##        rb = cls.remote_backend  # debug delete me
##        lb = cls.local_backend  # debug delete me

    
    def test01_find_one_attribute(self):
        """
        Compare query speed with  (_hash vs uuid vs _id)

        Test
        ----
        There are 2 unique identifiers for each TAHOE document:
        `_hash, _id` - all of which are indexed. _id is of type
        ObjectId (12 bytes), _hash is a 64 char string (64 bytes).

        Result
        ------
        On average, query by `_hash` is slower from query by `_id`
        by `0.1s` for `50,000` queries or, `2e-06 s` per query. 

        Conclusion
        ----------
        Insignificant difference. _hash can be used as identifier.

        Design Decision
        ---------------
        TAHOE will use _hash as unique identifier.
        """
        
        b = self.local_backend
        db = b.database
        

        match = {'itype': 'attribute'}
        sample = {'size': 50000}
        
        r = b.aggregate([{'$match': match}, {'$sample': sample}])

        t1_tot = 0  # query using _hash
##        t2_tot = 0  # query using uuid 
        t3_tot = 0  # query using _id
        
        for a in r:
            db.command({ "planCacheClear": "collection_name"})
        
            _hash = a['_hash']
            uuid = a['uuid']
            _id = a['_id']
            
            p = {'_id': 0}
            q1 = {'itype': 'attribute', '_hash': _hash}
##            q2 = {'itype': 'attribute', 'uuid': uuid}
            q3 = {'itype': 'attribute', '_id': _id}

            t1 = timeit(lambda: b.find_one(q1, p), number=1)
##            t2 = timeit(lambda: b.find_one(q2, p), number=1)
            t3 = timeit(lambda: b.find_one(q3, p), number=1)

            t1_tot += t1
##            t2_tot += t2
            t3_tot += t3

##        self.assertLess(abs(t1_tot - t2_tot), 1)
        self.assertLess(abs(t1_tot - t3_tot), 1)

    def test02_get_vs_make_data(self):
        """
        Test how much longer it takes to store data field of events (or
        objects) vs making the data fied on the fly during a query.

        Test
        ----
        The data field in `Object, Event, Session` are redundant.
        Morever, the data field is seldom used. This function tests
        how long it takes to make the data on the fly during a query.

        The data field can be made in two ways: (1) in python client
        (2) in MongoDB using aggregation pipeline. The advantage of (1)
        is the query is simple and I don't plan on implementing the
        `aggregate` method for other backends. The advantage of (2) is
        saving network traffic. Network traffic is mainly saved because
        (1) only query is made rather than two (see `mage_data_python()`
        and `make_data_aggregate()` below).

        Tests are performed twice: once on local mongodb (fast network)
        and once on remote mongodb (slow network, avg ping = 55ms).
        

        Result
        ------
        For Local MongoBackend for 2000 queries:
            (1) get data = 1.6884 s
            (2) make data in python = 5.598 s
            (3) make data in mongo aggregatin = 18.317 s

        For Remote MongoBackend for 2000 queries:
            (1) get data = 124.313 s
            (2) make data in python = 249.794 s
            (3) make data in mongo aggregation = 135.460

        2nd Run::
            (1) local: get=1.952, make_python=6.285,
            make_aggregation=22.367

            (2) remote: get=118.882, make_python=232.268,
            make_aggregation=118.143

        
        Conclusion
        ----------
        For Local MongoBackend:
            Surprisingly, aggregation is much slower than making data
            in Python. Also, getting data 3-4 times faster than making
            data in Python.

        For Remote MongoBackend:
            The average ping of the remote backend is 55ms. So, network
            speed takes over. And oviously, get data is only 9% faster.

        As expected, get data is the best option. But more testing is
        needed because (1) data is seldom used, need to count how many
        queries use data (2) these aggregations will be in report
        cluster, which is 1ms away from archive db. So, effect of
        network might be negligible.

        

        Design Decision
        ---------------
        For now, I will use method (1) get data, however more testing
        is needed.

        The key factors to be tested: (1) report cluster is
        only 1ms away from archive db, so network lag should be minimal
        (2) how many orospective reports actually use the data field
        (spoiler: none of them as of now!).

        Only viable use of the data field is in Adam's frontend to show
        data of an event or object in a succint manner. Event and Object
        are not in the frontend yet, but Adam plans on adding them.
        """
        
        rb = self.remote_backend
        lb = self.local_backend
        rdb = rb.database
        ldb = lb.database

        
        match = {'itype': 'object'}
        sample = {'size': 2000}
       

        def get_data(_hash, b):
            r = b.find_one({'_hash': _hash}, {'data': 1, '_id':0})
            d = r['data']

        def make_data_python(_hash, b):
            r = b.find_one({'_hash': _hash}, {'_ref': 1, '_id':0})
            _ref = r['_ref']

            q = {'itype': 'attribute', 'uuid': {'$in': _ref}}
            p = {'data': 1, '_id':0}
            r = b.find(q, p)

            d = [a['data'] for a in r if 'data' in a]

        
        def make_data_aggregate(_hash, b):
            match = {'$match': {'_hash': _hash}}
            unwind = {'$unwind': '$_ref'}
            lookup = {
                '$lookup': {
                    'from': 'instances',
                    'localField': '_ref',
                    'foreignField': 'uuid',
                    'as': 'data'
                }}
            project = {'$project': {'_id': 0, 'data.data': 1}}

            pipeline = [match, unwind, lookup, project]
            r = b.aggregate(pipeline)

            data = []
            for i in r:
                for d in i['data']:
                    if 'data' in d:
                        data.append(d['data'])
    

        for b, db, n in [(lb, ldb, 'local'), (rb, rdb, 'remote')]:
            r = b.aggregate([{'$match': match}, {'$sample': sample}])
            r_hash = [o['_hash'] for o in r]
            
            t1_tot = 0
            t2_tot = 0
            t3_tot = 0
            for _hash in r_hash:
                db.command({ "planCacheClear": "collection_name"})
                t1 = timeit(lambda: get_data(_hash, b), number=1)
                db.command({ "planCacheClear": "collection_name"})
                t2 = timeit(lambda: make_data_python(_hash, b), number=1)
                db.command({ "planCacheClear": "collection_name"})
                t3 = timeit(lambda: make_data_aggregate(_hash, b), number=1)
                          
                t1_tot += t1
                t2_tot += t2
                t3_tot += t3

            print(f"{n}: get={t1_tot:.3f}, make_python={t2_tot:.3f}" +
                  f", make_aggregation={t3_tot:.3f}")
    
        
if __name__ == '__main__':
    unittest.main()

