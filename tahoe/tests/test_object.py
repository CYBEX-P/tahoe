"""unittests for tahoe.object"""

if __name__ != 'tahoe.tests.test_object':
    import sys
    sys.path = ['..', '../..'] + sys.path
    del sys

import pdb
import unittest

from tahoe import Instance, Attribute, Object
from tahoe.backend import MongoBackend, MockMongoBackend
from tahoe.tests.test_backend import MongoBackendTest

def setUpModule():
    _backend = MongoBackendTest.setUpClass()
    Instance.set_backend(_backend)

    assert Attribute._backend is Instance._backend
    assert Object._backend is Instance._backend
    

def tearDownModule():
    MongoBackendTest.tearDownClass()


class SetBackendTest(unittest.TestCase):
    """
    Examples
    --------
    Correct Way to set default backend::
        
        >>> from tahoe import Instance, Attribute, Object, MongoBackend
        >>> _backend = MongoBackend()
        >>> Instance.set_backend(_backend)

    Wrong ways to set default backend::
        >>> Object._backend = MongoBackend() # wrong

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
    def test_backend(self):
        self.assertIs(Attribute._backend, Object._backend)
        self.assertIs(Attribute._backend, Instance._backend)
        self.assertIs(Instance._backend, Object._backend)

    
class SubTypeTest(unittest.TestCase):
    """
    Examples
    --------
    `sub_type` must be valid Python identifier.

        >>> a = Attribute("test", "test")
        >>> Object(1, [a])
        TypeError: sub_type = <class 'int'>, expected 'str'

        >>> Object("str w space", [a])
        ValueError: sub_type = 'str w space'

        >>> Object("str-w-minus", [a])
        ValueError: sub_type = 'str-w-minus'

        >>> o = Object("test", [a])
        >>> o.data
        {'test': ['test']}
        >>> 
    """
    
    def test_type(self):
        a = Attribute('test', 'test')
        self.assertRaises(TypeError, Object, 1, [a])

    def test_value_space(self):
        a = Attribute('test', 'test')
        self.assertRaises(ValueError, Object, 'str w space', [a])

    def test_value_minus(self):
        a = Attribute('test', 'test')
        self.assertRaises(ValueError, Object, 'str-w-minus', [a])

    def test_value_underscore(self):
        a = Attribute('test', 'test')
        o = Object('test_object', [a])        
        

class DataTest(unittest.TestCase):
    """
    Examples
    --------
    Data must be list of Attribute, Object::

        >>> o =  Object('test', 0)
        TypeError: instances must be of type tahoe
        <class 'tahoe.attribute.attribute.Attribute'>
        or <class 'tahoe.object.object.Object'>

        >>> o = Object('test', ['string'])
        TypeError: instances must be of type tahoe
        <class 'tahoe.attribute.attribute.Attribute'>
        or <class 'tahoe.object.object.Object'>

        >>> o = Object('test', [])
        ValueError: data cannot be empty

        >>> a = Attribute('test', 'test')
        >>> o = Object('test', [a, 2])
        TypeError: instances must be of type tahoe
        <class 'tahoe.attribute.attribute.Attribute'>
        or <class 'tahoe.object.object.Object'>
        
        >>> o = Object('test', [a])
        >>> o.data
        {'test': ['test']}

        >>> import json
        >>> a1 = Attribute('ipv4', '1.1.1.1')
        >>> a1.data
        '1.1.1.1'
        >>> o1 = Object('host', [a1])
        >>> o1.data
        {'ipv4': ['1.1.1.1']}
        >>> a2 = Attribute('url', 'example.com')
        >>> a2.data
        'example.com'
        >>> o2 = Object('url', [a2, o1])
        >>> json.dumps(o2.data, indent=2)
        >>> print(json.dumps(o2.data, indent=2))
        {
          "host": [
            {
              "ipv4": [
                "1.1.1.1"
              ]
            }
          ],
          "url": [
            "example.com"
          ]
        }
        >>> print(o2._hash)
        b228a4f398f3b974f16ba18c741dbeb09655e4ec9021b7e9c8d90a4210977ce6
             
    """

    def test_type_int(self):
        self.assertRaises(TypeError, Object, 'test', 0)

    def test_type_str(self):
        self.assertRaises(TypeError, Object, 'test', ['string'])

    def test_empty_list(self):
        self.assertRaises(ValueError, Object, 'test', [])

    def test_int_in_list(self):
        a = Attribute('test', 'test')
        self.assertRaises(TypeError, Object, 'test', [a, 2])

    def test_typ_str(self):
        a1 = Attribute('ipv4', '1.1.1.1')
        o1 = Object('host', [a1])
        a2 = Attribute('url', 'example.com')
        o2 = Object('url', [a2, o1])

        h = 'b228a4f398f3b974f16ba18c741dbeb09655e4ec9021b7e9c8d90a4210977ce6'
        self.assertEqual(o2._hash, h)                         
        

class AddRemoveInstanceTest(unittest.TestCase):
    """
    Examples
    --------

    Add or remove an attribute from an object::
    
        >>> a1 = Attribute('username', 'johndoe')
        >>> a2 = Attribute('password', '123456')
        >>> o1 = Object('user', [a1, a2])
        >>> o1.data
        {'password': ['123456'], 'username': ['johndoe']}
        >>> a3 = Attribute('password', 'abcdef')
        >>> o1.add_instance(a3)
        >>> o1.data
        {'password': ['123456', 'abcdef'], 'username': ['johndoe']}
        >>> o1.remove_instance(a2)
        >>> o1.data
        {'username': ['johndoe'], 'password': ['abcdef']}

        >>> a1 = Attribute('username', 'johndoe')
        >>> a2 = Attribute('password', '123456')
        >>>
        >>> o1 = Object('test1', a1) 
        >>> o2 = Object('test2', o1)
        >>> o3 = Object('test3', o2)
        >>>
        >>> o1.add_instance(a2)
        >>>
        >>> r = o2._backend.find_one({'_hash': o2._hash})
        >>> r is None
        True
        >>>
        >>> r = o3._backend.find_one({'_hash': o3._hash})
        >>> r is None
        True
        >>>
        >>> o2 = Object('test2', o1)
        >>> o2.data
        {'test1': [{'password': ['123456'], 'username': ['johndoe']}]}
        >>>
        >>> o3 = Object('test3', o2)
        >>> o3.data
        {'test2': [{'test1': [{'password': ['123456'],
        'username': ['johndoe']}]}]}
        >>>
        >>> o1.add_instance(a3)
        >>>
        >>> o2 = Object('test2', o1)
        >>> o2.data
        {'test1': [{'password': ['abcdef', '123456'],
        'username': ['johndoe']}]}
        >>>
        >>> o3 = Object('test3', o2)
        >>> o3.data
        {'test2': [{'test1': [{'password': ['abcdef', '123456'],
        'username': ['johndoe']}]}]}
        >>>
        >>> o1.remove_instance(a2)
        >>>
        >>> o2 = Object('test2', o1)
        >>> o2.data
        {'test1': [{'username': ['johndoe'], 'password': ['abcdef']}]}
        >>>
        >>> o3 = Object('test3', o2)
        >>> o3.data
        {'test2': [{'test1': [{'username': ['johndoe'],
        'password': ['abcdef']}]}]}
        
    """

    @classmethod
    def setUpClass(cls):
        assert isinstance(Object._backend, (MongoBackend, MockMongoBackend))
        Attribute._backend.drop()

    def test00(self):
        a1 = Attribute('username', 'johndoe')
        a2 = Attribute('password', '123456')      
        a3 = Attribute('password', 'abcdef')        

    def test01_add_instance(self):
        a1 = Attribute('username', 'johndoe')
        a2 = Attribute('password', '123456')
        o1 = Object('user', [a1, a2])
        
        a3 = Attribute('password', 'abcdef')
        o1.add_instance(a3)
        
        self.assertIn('abcdef', o1.data['password'])
        self.assertIn(a3._hash, o1._cref)
        self.assertIn(a3._hash, o1._ref)

        o1_d = o1._backend.find_one({'_hash': o1._hash}, {'_id': 0})

        self.assertIn('abcdef', o1_d['data']['password'])
        self.assertIn(a3._hash, o1_d['_cref'])
        self.assertIn(a3._hash, o1_d['_ref'])

    def test02_remove_instance(self):
        a1 = Attribute('username', 'johndoe')
        a2 = Attribute('password', '123456')      
        a3 = Attribute('password', 'abcdef')
        o1 = Object('user', [a1, a2, a3])
        
        o1.remove_instance(a2)

        self.assertEqual(o1.data['password'][0], 'abcdef')
        self.assertNotIn(a2._hash, o1._cref)
        self.assertNotIn(a2._hash, o1._ref)

        o1_d = o1._backend.find_one({'_hash': o1._hash}, {'_id': 0})

        self.assertEqual(o1_d['data']['password'][0], 'abcdef')
        self.assertNotIn(a2._hash, o1_d['_cref'])
        self.assertNotIn(a2._hash, o1_d['_ref'])

    def test03_chain_edit(self):
        a1 = Attribute('username', 'johndoe')
        a2 = Attribute('password', '123456')
        a3 = Attribute('password', 'abcdef')

        o1 = Object('test1', a1)
        o2 = Object('test2', o1)
        o3 = Object('test3', o2)

        # ----
        o1.add_instance(a2)

        self.assertIsNone(o2._backend.find_one({'_hash': o2._hash}))
        self.assertIsNone(o3._backend.find_one({'_hash': o3._hash}))

        o2 = Object('test2', o1)
        o3 = Object('test3', o2)

        self.assertIn('password', o2.data['test1'][0])
        self.assertIn('123456', o2.data['test1'][0]['password'])

        self.assertIn('password', o3.data['test2'][0]['test1'][0])
        self.assertIn('123456', o3.data['test2'][0]['test1'][0]['password'])

        # ----
        o1.add_instance(a3)

        self.assertIsNone(o2._backend.find_one({'_hash': o2._hash}))
        self.assertIsNone(o3._backend.find_one({'_hash': o3._hash}))

        o2 = Object('test2', o1)
        o3 = Object('test3', o2)

        self.assertIn('password', o2.data['test1'][0])
        self.assertIn('abcdef', o2.data['test1'][0]['password'])

        self.assertIn('password', o3.data['test2'][0]['test1'][0])
        self.assertIn('abcdef', o3.data['test2'][0]['test1'][0]['password'])

        # ----
        o1.remove_instance(a2)

        self.assertIsNone(o2._backend.find_one({'_hash': o2._hash}))
        self.assertIsNone(o3._backend.find_one({'_hash': o3._hash}))

        o2 = Object('test2', o1)
        o3 = Object('test3', o2)

        self.assertIn('password', o2.data['test1'][0])
        self.assertNotIn('123456', o2.data['test1'][0]['password'])

        self.assertIn('password', o3.data['test2'][0]['test1'][0])
        self.assertNotIn('123456', o3.data['test2'][0]['test1'][0]['password'])


        # ----
        
        o1 = Object('test', a1)
        o2 = Object('test', o1)
        o3 = Object('test', o2)
        
        o1.add_instance(a2)   

        self.assertIsNone(o2._backend.find_one({'_hash': o2._hash}))
        self.assertIsNone(o3._backend.find_one({'_hash': o3._hash}))

        o2 = Object('test', o1)
        o3 = Object('test', o2)

        self.assertIn('password', o2.data['test'][0])
        self.assertIn('123456', o2.data['test'][0]['password'])

        self.assertIn('password', o3.data['test'][0]['test'][0])
        self.assertIn('123456', o3.data['test'][0]['test'][0]['password'])


##
##class CountTest(unittest.TestCase):
##    """
##    Example
##    -------
##    a1 = Atribute('ip', '1.1.1.1')
##    e1 = Event
##    """
##    
##    @classmethod
##    def setUpClass(cls):
##        assert isinstance(Attribute._backend, MongoBackend)
##        Attribute._backend.drop()  
##        
##
##class DeleteTest(unittest.TestCase):
##    """
##    Examples
##    --------
##    Example of deleting an attribute::
##    
##        >>> import json
##        >>> from tahoe import MongoBackend, Attribute
##        >>> _backend = MongoBackend()
##        >>> _backend
##        MongoBackend('localhost:27017', 'tahoe_db', 'instance')
##        >>> a = Attribute('ipv4', '1.1.1.1', _backend=_backend)
##        >>> a.uuid
##        'attribute--373ca2ac-deff-4e78-ac8c-fbf0a327d433'
##        >>> print(json.dumps(r, indent=4))
##        {
##            "itype": "attribute",
##            "data": "1.1.1.1",
##            "uuid": "attribute--373ca2ac-deff-4e78-ac8c-fbf0a327d433",
##            "sub_type": "ipv4",
##            "_hash": "4469d1e06fdd2b03ce89abf4dcc354df0be231b97e7293fe17
##            50232d2d3b23a6"
##        }
##        >>> a._delete()
##        >>> r = _backend.find_one({'uuid': a.uuid}, {'_id': 0})
##        >>> r is None
##        True
##        >>> 
##    """
##    
##    @classmethod
##    def setUpClass(cls):
##        assert isinstance(Attribute._backend, MongoBackend)
##        Attribute._backend.drop()
##
##    def test_delete(self):
##        a = Attribute('ipv4', '1.1.1.1')
##        _backend = a._backend
##
##        r = _backend.find_one({'uuid': a.uuid})
##        self.assertEqual(r['uuid'], a.uuid)
##
##        a._delete()
##        r = _backend.find_one({'uuid': a.uuid})
##        self.assertIsNone(r)
##        



        


if __name__ == '__main__':
    unittest.main()

    


