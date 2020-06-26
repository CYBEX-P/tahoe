"""unittest's for tahoe.attribute.attribute.py"""

import pdb
import unittest

from tahoe import Instance, Attribute
from tahoe.backend import MongoBackend, MockMongoBackend
from tahoe.tests.test_backend import MongoBackendTest


def setUpModule():
    _backend = MongoBackendTest.setUpClass()
    Instance.set_backend(_backend)

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


class CountTest(unittest.TestCase):
    """
    Example
    -------
    a1 = Atribute('ip', '1.1.1.1')
    e1 = Event
    """
    
    @classmethod
    def setUpClass(cls):
        assert isinstance(Attribute._backend, (MongoBackend, MockMongoBackend))
        Attribute._backend.drop()  
        

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
        



        


if __name__ == '__main__':
    unittest.main()

    


