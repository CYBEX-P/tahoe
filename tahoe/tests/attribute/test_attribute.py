"""unittest's for tahoe.attribute.attribute.py"""

if __name__ != 'tahoe.tests.attribute.test_attribute':
    import sys, os
    J = os.path.join
    sys.path = ['..', J('..','..'), J('..','..','..')] + sys.path
    del J, sys, os

import builtins
import pdb
from pprint import pprint
import unittest

from tahoe import Instance, Attribute, Event, Object, Session
from tahoe.backend import MongoBackend, MockMongoBackend
from tahoe.tests.test_backend import MongoBackendTest
    

def setUpModule():
    _backend = MongoBackendTest.setUpClass()
    Instance.set_backend(_backend)

    builtins.orgid = 'a441b15fe9a3cf56661190a0b93b9dec7d041272' \
                '88cc87250967cf3b52894d11'

def tearDownModule():
    MongoBackendTest.tearDownClass()


class SetBackendTest(unittest.TestCase):
    """
    Examples
    --------
    Correct Way to set default backend::
        
        >>> from tahoe import Instance, Attribute, MongoBackend
        >>> _backend = MongoBackend()
        >>> Instance.set_backend(_backend)

    Wrong ways to set default backend::

        >>> from tahoe import NoBackend, MongoBackend
        >>> no_backend = NoBackend()
        >>> no_backend
        NoBackend()
        
        >>> mongo_backend = MongoBackend(dbname="test_db")
        >>> mongo_backend
        MongoBackend("localhost:27017", "test_db", "instance")
        
        >>> Attribute.set_backend(no_backend)
        >>> Atrribute._backend
        NoBackend()

        >>> a = Attribute("test", "test")
        >>> a._backend
        NoBackend()

        >>> Attribute.set_backend(mongo_backend)
        >>> Attribute._backend
        MongoBackend("localhost:27017", "test_db", "instance")

        >>> a2 = Attribute("test", "test2")
        >>> a2._backend
        MongoBackend("localhost:27017", "test_db", "instance")

        >>> a2._backend = NoBackend()
        >>> Attribute._backend
        NoBackend()
    """
    pass


    
class SubTypeTest(unittest.TestCase):
    """
    Examples
    --------
    `sub_type` must be valid Python identifier::

        >>> Attribute(1, "test")
        TypeError: sub_type = <class 'int'>, expected 'str'

        >>> Attribute("str w space", "test")
        ValueError: sub_type = 'str w space'

        >>> Attribute("str-w-minus", "test")
        ValueError: sub_type = 'str-w-minus'

        >>> a = Attribute("test_attribute", "test")
        >>> a.data
        'test'
    """
    
    def test_type(self):
        self.assertRaises(TypeError, Attribute, 1, 'test')

    def test_value_space(self):
        self.assertRaises(ValueError, Attribute, 'str w space', 'test')

    def test_value_minus(self):
        self.assertRaises(ValueError, Attribute, 'str-w-minus', 'test')

    def test_value_underscore(self):
        a = Attribute('test_attribute', 'test')
        


    

class CountTest(unittest.TestCase):
    """
    Example
    -------
    a1 = Atribute('ip', '1.1.1.1')
    """
    
    @classmethod
    def setUpClass(cls):
        assert isinstance(Attribute._backend, (MongoBackend, MockMongoBackend))
        Attribute._backend.drop()
        assert Attribute._backend is Event._backend

    def test01_count_one(self):
        afn = Attribute('filename', 'virus.exe')
        e = Event('file_download', afn, orgid, 100)
        self.assertEqual(afn.count(), 1)

    def test02_count_multiple(self):
        afn = Attribute('filename', 'virus.exe')
        Event('file_download', afn, orgid, 100)
        Event('file_download', afn, orgid, 200)
        self.assertEqual(afn.count(), 2)

    def test03_start(self):
        afn = Attribute('filename', 'virus.exe')
        Event('file_download', afn, orgid, 100)
        Event('file_download', afn, orgid, 200)
        
        self.assertEqual(afn.count(start=99), 2)
        self.assertEqual(afn.count(start=100), 2)
        self.assertEqual(afn.count(start=101), 1)
        self.assertEqual(afn.count(start=200), 1)
        self.assertEqual(afn.count(start=201), 0)

    def test04_end(self):
        afn = Attribute('filename', 'virus.exe')
        Event('file_download', afn, orgid, 100)
        Event('file_download', afn, orgid, 200)
        
        self.assertEqual(afn.count(end=99), 0)
        self.assertEqual(afn.count(end=100), 1)
        self.assertEqual(afn.count(end=101), 1)
        self.assertEqual(afn.count(end=200), 2)
        self.assertEqual(afn.count(end=201), 2)

    def test04_start_end(self):
        afn = Attribute('filename', 'virus.exe')
        Event('file_download', afn, orgid, 100)
        Event('file_download', afn, orgid, 200)
        Event('file_download', afn, orgid, 300)
        
        self.assertEqual(afn.count(start=150, end=120), 0)
        self.assertEqual(afn.count(start=100, end=100), 1)
        self.assertEqual(afn.count(start=100, end=101), 1)
        self.assertEqual(afn.count(start=200, end=200), 1)
        self.assertEqual(afn.count(start=200, end=201), 1)
        self.assertEqual(afn.count(start=199, end=201), 1)

    def test05_category(self):
        afn = Attribute('filename', 'virus.exe')
        e1 = Event('file_download', afn, orgid, 100)
        e2 = Event('file_download', afn, orgid, 200)
        e3 = Event('file_download', afn, orgid, 300)
        e4 = Event('file_download', afn, orgid, 400)

        e1.set_category('malicious')
        e2.set_category('malicious')
        e3.set_category('benign')

        self.assertEqual(afn.count(category='malicious'), 2)
        self.assertEqual(afn.count(category='benign'), 1)
        self.assertEqual(afn.count(category='unknown'), 1)

    def test06_context(self):
        afn = Attribute('filename', 'virus.exe')
        e1 = Event('file_download', afn, orgid, 100)
        e2 = Event('file_download', afn, orgid, 200)
        e3 = Event('file_download', afn, orgid, 300)
        e3 = Event('file_download', afn, orgid, 400)

        e1.set_context(afn, 'malicious')
        e2.set_context(afn, 'malicious')
        e3.set_context(afn, 'benign')

        self.assertEqual(afn.count(context='malicious'), 2)
        self.assertEqual(afn.count(context='benign'), 1)
        self.assertEqual(afn.count(context='unknown'), 1)

    def test07_count_capped(self):
        Attribute._backend.drop()

        limit = 10

        afn = Attribute('filename', 'virus.exe')

        for t in range(limit+1):
            e = Event('file_download', afn, orgid, t)
        
        self.assertEqual(afn.count(), limit+1)
        self.assertEqual(afn.count(limit=limit), limit)
        
        

class DataTest(unittest.TestCase):
    """
    Examples
    --------

    Data must be `int, float, str, bool, NoneType`::

        >>> Attribute('test', [1,2,3])
        TypeError: data = <class 'list'>, expected (int, float, str, boo
        l, NoneType)        
    """

    def test_type(self):
        self.assertRaises(TypeError, Attribute, 'test', [1,2,3])



class DeleteTest(unittest.TestCase):
    """
    Examples
    --------
    Example of deleting an attribute::
    
        >>> import json
        >>> from tahoe import MongoBackend, Attribute
        >>> _backend = MongoBackend()
        >>> _backend
        MongoBackend("localhost:27017", "tahoe_db", "instance")
        >>>
        >>> a = Attribute("ipv4", "1.1.1.1", _backend=_backend)
        >>> r = _backend.find_one({"_hash": a._hash}, {"_id": 0})
        >>> print(json.dumps(r, indent=4))
        {
            "itype": "attribute",
            "data": "1.1.1.1",
            "sub_type": "ipv4",
            "_hash": "4469d1e06fdd2b03ce89abf4dcc354df0be231b97e7293fe17
            50232d2d3b23a6"
        }
        >>>
        >>> a.delete()
        >>> r = _backend.find_one({"_hash": a._hash}, {"_id": 0})
        >>> r is None
        True
        >>> 
    """
    
    @classmethod
    def setUpClass(cls):
        assert isinstance(Attribute._backend, (MongoBackend, MockMongoBackend))
        Attribute._backend.drop()

    def testdelete(self):
        a = Attribute('ipv4', '1.1.1.1')
        _backend = a._backend

        r = _backend.find_one({'_hash': a._hash})
        self.assertEqual(r['_hash'], a._hash)

        a.delete()
        r = _backend.find_one({'_hash': a._hash})
        self.assertIsNone(r)
        

def make_related_data():
    import builtins as b
    
    b.a11 = Attribute('ipv4', '1.1')
    b.a12 = Attribute('ipv4', '1.2')
    b.a21 = Attribute('ipv4', '2.1')
    
    b.e1 = Event('lvl_1', [a11,a12], orgid, 100)
    b.e2 = Event('lvl_2', [a21], orgid, 200)

    b.s1 = Session('lvl_2')
    s1.add_event([e1,e2])

def make_related_data_2():
    make_related_data()
    import builtins as b
    
    b.a31 = Attribute('ipv4', '3.1')
    b.e3 = Event('lvl_1', [a11, a31], orgid, 300)

    e1.set_category('malicious')
    e3.set_category('benign')

    e1.set_context(a11, 'benign')
    e3.set_context(a11, 'malicious')

def make_related_data_3():
    import builtins as b
    b.aip51 = Attribute('ipv4', '5.1')
    b.aip52 = Attribute('ipv4', '5.2')
    b.afn = Attribute('file_name', 'v.exe')
    b.afh = Attribute('sha256', 'AB12')
    b.aes = Attribute('email_addr', 'src@e.com')
    b.aed = Attribute('email_addr', 'dst@e.com')

    b.of = Object('file', [afn, afh])
    b.os = Object('src', [aip51])
    b.ose = Object('src', [aes, aip51])
    b.ode = Object('dst', [aed])

    b.efd = Event('file_download', [of, os, aip52], orgid, 500)
    b.ee = Event('email', [ose, ode], orgid, 600)
    

class RelatedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(Attribute._backend,
                          (MongoBackend, MockMongoBackend))
        Attribute._backend.drop()
        make_related_data()

    def test_00_rel_hash_lvl_0(self):
        r0 = a11.related_hash()
        self.assertEqual(r0, [])
        r0 = a11.related_hash(level=0)
        self.assertEqual(r0, [])

    def test_01_rel_lvl_0(self):
        r0 = a11.related(level=0)
        self.assertEqual(r0[0], [])
        self.assertEqual(r0[1], 1)
        self.assertEqual(r0[1], 1)

    def test_02_rel_hash_lvl_1(self):
        IN = self.assertIn
        EQ = self.assertEqual

        r1 = a11.related_hash(level=1)

        EQ(len(r1), 3)
        IN(a11._hash, r1)
        IN(a12._hash, r1)
        IN(e1._hash, r1)

    def test_03_rel_lvl_1(self):
        IN = self.assertIn
        EQ = self.assertEqual

        r1 = a11.related(level=1)

        EQ(len(r1), 3)
        EQ(len(r1[0]), 3)
        EQ(r1[1], 1)
        EQ(r1[1], 1)
        IN(a11.doc, r1[0])
        IN(a12.doc, r1[0])
        IN(e1.doc, r1[0])

    def test_04_rel_hash_lvl_2(self):
        IN = self.assertIn
        EQ = self.assertEqual

        r2 = a11.related_hash(level=2)
        
        EQ(len(r2), 6)
        IN(a11._hash, r2)
        IN(a12._hash, r2)
        IN(e1._hash, r2)
        IN(a21._hash, r2)
        IN(e2._hash, r2)
        IN(s1._hash, r2)

    def test_05_rel_lvl_2(self):
        IN = self.assertIn
        EQ = self.assertEqual

        r2 = a11.related(level=2)

        EQ(len(r2), 3)
        EQ(len(r2[0]), 6)
        EQ(r2[1], 1)
        EQ(r2[1], 1)
        IN(a11.doc, r2[0])
        IN(a12.doc, r2[0])
        IN(e1.doc, r2[0])
        IN(a21.doc, r2[0])
        IN(e2.doc, r2[0])
        IN(s1.doc, r2[0])

    def test_06_limit_page(self):
        Attribute._backend.drop()
        make_related_data_2()

        IN = self.assertIn
        EQ = self.assertEqual

        r2, pg, nxt = a11.related(level=2, limit=1)

        EQ(len(r2), 6)
        EQ(pg, 1)
        EQ(nxt, 2)
        IN(a11.doc, r2)
        IN(a12.doc, r2)
        IN(e1.doc, r2)
        IN(a21.doc, r2)
        IN(e2.doc, r2)
        IN(s1.doc, r2)

        r2, pg, nxt = a11.related(level=2, limit=0)

        EQ(len(r2), 8)
        EQ(pg, 1)
        EQ(nxt, 2)
        IN(a11.doc, r2)
        IN(a12.doc, r2)
        IN(e1.doc, r2)
        IN(a21.doc, r2)
        IN(e2.doc, r2)
        IN(a31.doc, r2)
        IN(e3.doc, r2)
        IN(s1.doc, r2)

    def test_07_start(self):
        EQ = self.assertEqual
        EQ(len(a11.related_hash(level=2, start=99)), 8)
        EQ(len(a11.related_hash(level=2, start=100)), 8)
        EQ(len(a11.related_hash(level=2, start=101)), 3)
        EQ(len(a11.related_hash(level=2, start=301)), 0)

    def test_08_end(self):
        EQ = self.assertEqual
        EQ(len(a11.related_hash(level=2, end=99)), 0)
        EQ(len(a11.related_hash(level=2, end=100)), 6)
        EQ(len(a11.related_hash(level=2, end=101)), 6)
        EQ(len(a11.related_hash(level=2, end=301)), 8)

    def test_09_start_end(self):
        EQ = self.assertEqual
        EQ(len(a11.related_hash(level=2, start=50, end=99)), 0)
        EQ(len(a11.related_hash(level=2, start=50, end=100)), 6)
        EQ(len(a11.related_hash(level=2, start=100, end=101)), 6)
        EQ(len(a11.related_hash(level=2, start=101, end=301)), 3)
        EQ(len(a11.related_hash(level=2, start=50, end=301)), 8)

    def test_10_category(self):
        EQ = self.assertEqual
        EQ(len(a11.related_hash(level=2, category='all')), 8)
        EQ(len(a11.related_hash(level=2, category='malicious')), 6)
        EQ(len(a11.related_hash(level=2, category='unknown')), 0)
        EQ(len(a11.related_hash(level=2, category='benign')), 3)

    def test_11_context(self):
        EQ = self.assertEqual
        EQ(len(a11.related_hash(level=2, context='all')), 8)
        EQ(len(a11.related_hash(level=2, context='malicious')), 3)
        EQ(len(a11.related_hash(level=2, context='unknown')), 0)
        EQ(len(a11.related_hash(level=2, context='benign')), 6)

    def test_12_summary_graph(self):
        make_related_data_3()
        EQ = self.assertEqual
        r = aip51.related(level=2, summary_graph=True)
##        EQ(len(a11.related_hash(level=2, summary_graph=True)), 7)
        


if __name__ == '__main__':
    unittest.main()

    

