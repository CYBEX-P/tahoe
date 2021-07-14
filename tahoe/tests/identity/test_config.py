"""unittests for tahoe.identity.config"""

import builtins
import hashlib
import pdb
import unittest

if __name__ != 'tahoe.tests.identity.test_config':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os

from tahoe import Instance, Attribute, Object
from tahoe.identity.config import InputConfig, WebSocketConfig
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import setUpBackend, tearDownBackend


def setUpModule():
    _backend = setUpBackend()

    Instance.set_backend(_backend)
    Attribute.set_backend(_backend)
    Object.set_backend(_backend)
    InputConfig.set_backend(_backend)
    WebSocketConfig.set_backend(_backend)

    assert Instance._backend is Attribute._backend
    assert Instance._backend is Object._backend
    assert Instance._backend is InputConfig._backend
    assert Instance._backend is WebSocketConfig._backend


def tearDownModule():
    tearDownBackend(Instance._backend)


def make_test_data():
    builtins.plugin = 'websocket'
    builtins.name = 'Jay\'s Honeypot London'
    builtins.typetag = 'unr-honeypot'
    builtins.orgid = 'a441b15fe9a3cf56661190a0b93b9dec7d04127288cc' \
        '87250967cf3b52894d11'
    builtins.timezone = 'US/Pacific'
    builtins.url = 'ws://119.122.58.51:5000/'

    builtins.ap = Attribute('plugin', plugin)
    builtins.an = Attribute('name', name)
    builtins.att = Attribute('typetag', typetag)
    builtins.ao = Attribute('orgid', orgid)
    builtins.at = Attribute('timezone', timezone)
    builtins.au = Attribute('url', url)
    builtins.ae = Attribute('enabled', True)
    
    builtins.ic = InputConfig(plugin, name, typetag, orgid, timezone, au)
    builtins.icd = ic._backend.find_one({'_hash': ic._hash})
    
    builtins.wsc = WebSocketConfig(name, typetag, orgid, timezone, url)
    builtins.wscd = wsc._backend.find_one({'_hash': wsc._hash})    
    

def delete_test_data():
    del builtins.plugin, builtins.name, builtins.typetag, builtins.orgid, \
        builtins.timezone, builtins.url, builtins.ap, builtins.an, \
        builtins.att, builtins.ao, builtins.at, builtins.au, builtins.ae, \
        builtins.ic, builtins.icd, builtins.wsc, builtins.wscd
    


class InputConfigInitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        InputConfig._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        
    def test_init(self):
        self.assertIsNotNone(icd)

    def test_itype(self):
        EQ = self.assertEqual
        EQ(ic.itype, 'object')
        EQ(icd['itype'], 'object')

    def test_sub_type(self):
        EQ = self.assertEqual
        EQ(ic.sub_type, 'cybexp_input_config')
        EQ(icd['sub_type'], 'cybexp_input_config')

    def test_data_plugin(self):
        EQ = self.assertEqual
        EQ(ic.data['plugin'][0], plugin)
        EQ(icd['data']['plugin'][0], plugin)

    def test_data_name(self):
        EQ = self.assertEqual
        EQ(ic.data['name'][0], name)
        EQ(icd['data']['name'][0], name)

    def test_data_typetag(self):
        EQ = self.assertEqual
        EQ(ic.data['typetag'][0], typetag)
        EQ(icd['data']['typetag'][0], typetag)

    def test_data_orgid(self):
        EQ = self.assertEqual
        EQ(ic.data['orgid'][0], orgid)
        EQ(icd['data']['orgid'][0], orgid)

    def test_data_timezone(self):
        EQ = self.assertEqual
        EQ(ic.data['timezone'][0], timezone)
        EQ(icd['data']['timezone'][0], timezone)
        
    def test_cref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(ic._cref), 7)
        EQ(len(icd['_cref']), 7)
        
        IN(ap._hash, ic._cref)
        IN(an._hash, ic._cref)
        IN(att._hash, ic._cref)
        IN(ao._hash, ic._cref)
        IN(at._hash, ic._cref)
        IN(au._hash, ic._cref)
        IN(ae._hash, ic._cref)
        IN(ap._hash, icd['_cref'])
        IN(an._hash, icd['_cref'])
        IN(att._hash, icd['_cref'])
        IN(ao._hash, icd['_cref'])
        IN(at._hash, icd['_cref'])
        IN(au._hash, icd['_cref'])
        IN(ae._hash, icd['_cref'])

    def test_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(ic._ref), 7)
        EQ(len(icd['_ref']), 7)
        
        IN(ap._hash, ic._ref)
        IN(an._hash, ic._ref)
        IN(att._hash, ic._ref)
        IN(ao._hash, ic._ref)
        IN(at._hash, ic._ref)
        IN(au._hash, ic._ref)
        IN(ae._hash, ic._ref)
        IN(ap._hash, icd['_ref'])
        IN(an._hash, icd['_ref'])
        IN(att._hash, icd['_ref'])
        IN(ao._hash, icd['_ref'])
        IN(at._hash, icd['_ref'])
        IN(au._hash, icd['_ref'])
        IN(ae._hash, icd['_ref'])


    def test_hash(self):
        expected_hash = '7644c763afc91a8ad2a45756838236dd69b49b11' \
                        'ad6d0b5bac3f8fcf341bfe5e'
        EQ = self.assertEqual
        EQ(ic._hash, expected_hash)
        EQ(icd['_hash'], expected_hash)


class WebSocketConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        InputConfig._backend.drop()
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        
    def test_init(self):
        self.assertIsNotNone(wscd)

    def test_itype(self):
        EQ = self.assertEqual
        EQ(wsc.itype, 'object')
        EQ(wscd['itype'], 'object')

    def test_sub_type(self):
        EQ = self.assertEqual
        EQ(wsc.sub_type, 'cybexp_input_config')
        EQ(wscd['sub_type'], 'cybexp_input_config')

    def test_data_plugin(self):
        EQ = self.assertEqual
        EQ(wsc.data['plugin'][0], plugin)
        EQ(wscd['data']['plugin'][0], plugin)

    def test_data_name(self):
        EQ = self.assertEqual
        EQ(wsc.data['name'][0], name)
        EQ(wscd['data']['name'][0], name)

    def test_data_typetag(self):
        EQ = self.assertEqual
        EQ(wsc.data['typetag'][0], typetag)
        EQ(wscd['data']['typetag'][0], typetag)

    def test_data_orgid(self):
        EQ = self.assertEqual
        EQ(wsc.data['orgid'][0], orgid)
        EQ(wscd['data']['orgid'][0], orgid)

    def test_data_timezone(self):
        EQ = self.assertEqual
        EQ(wsc.data['timezone'][0], timezone)
        EQ(wscd['data']['timezone'][0], timezone)
        
    def test_cref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(wsc._cref), 7)
        EQ(len(wscd['_cref']), 7)
        
        IN(ap._hash, wsc._cref)
        IN(an._hash, wsc._cref)
        IN(att._hash, wsc._cref)
        IN(ao._hash, wsc._cref)
        IN(at._hash, wsc._cref)
        IN(au._hash, wsc._cref)
        IN(ae._hash, wsc._cref)
        IN(ap._hash, wscd['_cref'])
        IN(an._hash, wscd['_cref'])
        IN(att._hash, wscd['_cref'])
        IN(ao._hash, wscd['_cref'])
        IN(at._hash, wscd['_cref'])
        IN(au._hash, wscd['_cref'])
        IN(ae._hash, wscd['_cref'])

    def test_ref(self):
        EQ = self.assertEqual
        IN = self.assertIn

        EQ(len(wsc._ref), 7)
        EQ(len(wscd['_ref']), 7)
        
        IN(ap._hash, wsc._ref)
        IN(an._hash, wsc._ref)
        IN(att._hash, wsc._ref)
        IN(ao._hash, wsc._ref)
        IN(at._hash, wsc._ref)
        IN(au._hash, wsc._ref)
        IN(ae._hash, wsc._ref)
        IN(ap._hash, wscd['_ref'])
        IN(an._hash, wscd['_ref'])
        IN(att._hash, wscd['_ref'])
        IN(ao._hash, wscd['_ref'])
        IN(at._hash, wscd['_ref'])
        IN(au._hash, wscd['_ref'])
        IN(ae._hash, wscd['_ref'])


    def test_hash(self):
        expected_hash = '7644c763afc91a8ad2a45756838236dd69b49b11' \
                        'ad6d0b5bac3f8fcf341bfe5e'
        EQ = self.assertEqual
        EQ(wsc._hash, expected_hash)
        EQ(wscd['_hash'], expected_hash)

    
if __name__ == '__main__':
    unittest.main()








