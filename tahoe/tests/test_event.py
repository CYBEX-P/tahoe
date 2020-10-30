"""`unittests for tahoe.event"""
import builtins

if __name__ != 'tahoe.tests.test_event':
    import sys
    sys.path = ['..', '../..'] + sys.path
    del sys

import pdb
import unittest

from tahoe import Instance, Attribute, Object, Event
from tahoe.backend import MongoBackend, MockMongoBackend
from tahoe.tests.test_backend import MongoBackendTest


def setUpModule():
    _backend = MongoBackendTest.setUpClass()
    Instance.set_backend(_backend)

    assert Attribute._backend is Instance._backend
    assert Object._backend is Instance._backend
    assert Event._backend is Instance._backend
   

def tearDownModule():
    MongoBackendTest.tearDownClass()


def make_test_data():
    
    builtins.afn = Attribute('filename', 'virus.exe')
    builtins.afs = Attribute('filesize', 20012)
    builtins.of = Object('file', [afn, afs])
    builtins.au = Attribute('url', 'example.com')

    builtins.orgid = 'a441b15fe9a3cf56661190a0b93b9dec7d041272' \
                '88cc87250967cf3b52894d11'''
    builtins.timestamp = 100

    builtins.e = Event('file_download', [au, of], orgid, timestamp)


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
        assert isinstance(Event._backend, (MongoBackend, MockMongoBackend))
        Event._backend.drop()

    def test_init(self):
        data = Attribute("test", "test")
        orgid = 'a441b15fe9a3cf56661190a0b93b9dec7d041272' \
                '88cc87250967cf3b52894d11'''
        timestamp = -1

        e = Event('test', data, orgid, timestamp)
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertIsNotNone(e_d)

        e_hash_expected = '2a3cca131a1724c92cc1a823da9603b60bf' \
                          '037550e07bcabd1f1622d77762983'

        self.assertEqual(e._ben_ref, [])
        self.assertEqual(e_d['_ben_ref'], [])

        self.assertEqual(e._cref, [data._hash])
        self.assertEqual(e_d['_cref'], [data._hash])

        self.assertEqual(e._hash, e_hash_expected)
        self.assertEqual(e_d['_hash'], e_hash_expected)

        self.assertEqual(e._mal_ref, [])
        self.assertEqual(e_d['_mal_ref'], [])

        self.assertEqual(e._ref, [data._hash])
        self.assertEqual(e_d['_ref'], [data._hash])

        self.assertEqual(e.category, 'unknown')
        self.assertEqual(e_d['category'], 'unknown')

        self.assertEqual(e.data['test'][0], 'test')
        self.assertEqual(e_d['data']['test'][0], 'test')

        self.assertEqual(e.itype, 'event')
        self.assertEqual(e_d['itype'], 'event')

        self.assertEqual(e.orgid, orgid)
        self.assertEqual(e_d['orgid'], orgid)

        self.assertEqual(e.sub_type, 'test')
        self.assertEqual(e_d['sub_type'], 'test')
        
        self.assertEqual(e.timestamp, -1)
        self.assertEqual(e_d['timestamp'], -1)


class CategoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(Event._backend, (MongoBackend, MockMongoBackend))
        Event._backend.drop()

    def __init__(self, *args, **kwargs):
        self.a1 = Attribute("test", "test")
        self.orgid = 'a441b15fe9a3cf56661190a0b93b9dec7d041272' \
                '88cc87250967cf3b52894d11'''
        self.timestamp = 100
        super().__init__(*args, **kwargs)

    def test1_unknown(self):
        e = Event('test', self.a1, self.orgid, self.timestamp)
        e_d = e._backend.find_one({'_hash': e._hash})
        self.assertEqual(e.category, 'unknown')
        self.assertEqual(e_d['category'], 'unknown')

    def test2_benign(self):
        e = Event('test', self.a1, self.orgid, self.timestamp, category='benign')
        e_d = e._backend.find_one({'_hash': e._hash})
        self.assertEqual(e.category, 'unknown')
        self.assertEqual(e_d['category'], 'unknown')

        e._backend.drop()
        e = Event('test', self.a1, self.orgid, self.timestamp, category='benign')
        e_d = e._backend.find_one({'_hash': e._hash})
        self.assertEqual(e.category, 'unknown')
        self.assertEqual(e_d['category'], 'unknown')

        e.set_category('benign')
        e_d = e._backend.find_one({'_hash': e._hash})
        self.assertEqual(e.category, 'benign')
        self.assertEqual(e_d['category'], 'benign')


    def test3_malicious(self):
        Event._backend.drop()
        e = Event('test', self.a1, self.orgid, self.timestamp)
        e_d = e._backend.find_one({'_hash': e._hash})
        self.assertEqual(e.category, 'unknown')
        self.assertEqual(e_d['category'], 'unknown')

        e.set_category('malicious')
        e_d = e._backend.find_one({'_hash': e._hash})
        self.assertEqual(e.category, 'malicious')
        self.assertEqual(e_d['category'], 'malicious')


class ContextTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(Event._backend, (MongoBackend, MockMongoBackend))
        Event._backend.drop()
        make_test_data()

    def test_01_benign(self):
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertNotIn(au._hash, e._ben_ref)
        self.assertNotIn(au._hash, e_d['_ben_ref'])
        
        e.set_context(au, 'benign')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertIn(au._hash, e._ben_ref)
        self.assertIn(au._hash, e_d['_ben_ref'])

    def test_02_change_to_malicious(self):
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertIn(au._hash, e._ben_ref)
        self.assertIn(au._hash, e_d['_ben_ref'])

        e.set_context(au, 'malicious')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertNotIn(au._hash, e._ben_ref)
        self.assertNotIn(au._hash, e_d['_ben_ref'])

        self.assertIn(au._hash, e._mal_ref)
        self.assertIn(au._hash, e_d['_mal_ref'])

    def test_03_change_to_unknown(self):
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertIn(au._hash, e._mal_ref)
        self.assertIn(au._hash, e_d['_mal_ref'])

        e.set_context(au, 'unknown')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertNotIn(au._hash, e._ben_ref)
        self.assertNotIn(au._hash, e_d['_ben_ref'])

        self.assertNotIn(au._hash, e._mal_ref)
        self.assertNotIn(au._hash, e_d['_mal_ref'])
        
        
    def test_04_set_multiple_context_together(self):
        e.set_context(au, 'benign', of, 'malicious')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertIn(au._hash, e._ben_ref)
        self.assertIn(au._hash, e_d['_ben_ref'])

        self.assertIn(of._hash, e._mal_ref)
        self.assertIn(of._hash, e_d['_mal_ref'])

    def test_05_typeerror_wrong_datatype(self):
        self.assertRaises(TypeError, e.set_context, 2, 'malicious')
        self.assertRaises(TypeError, e.set_context, [2], 'benign')
        self.assertRaises(TypeError, e.set_context, {au}, 'unknown')

    def test_06_valueerror_same_data_multiple_context(self):
        self.assertRaises(ValueError,
                          e.set_context, au, 'benign', au, 'malicious')
        self.assertRaises(ValueError,
                          e.set_context, au, 'malicious', au, 'unknown')
        self.assertRaises(ValueError,
                          e.set_context, au, 'unknown', au, 'benign')

    def test_07_valueerror_wrong_context(self):
        self.assertRaises(ValueError, e.set_context, au, 'wrong_context')
        self.assertRaises(ValueError, e.set_context, au, 5)

    def test_08_valueerror_same_context_twice(self):
        self.assertRaises(ValueError,
                          e.set_context, au, 'benign', of, 'benign')
        self.assertRaises(ValueError,
                          e.set_context, au, 'malicious', of, 'malicious')
        self.assertRaises(ValueError,
                          e.set_context, au, 'unknown', of, 'unknown')

    def test_09_multiple_data(self):
        e.set_context([au, of], 'benign')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertIn(au._hash, e._ben_ref)
        self.assertIn(au._hash, e_d['_ben_ref'])
        self.assertIn(of._hash, e._ben_ref)
        self.assertIn(of._hash, e_d['_ben_ref'])

        e.set_context([au, of], 'malicious')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertNotIn(au._hash, e._ben_ref)
        self.assertNotIn(au._hash, e_d['_ben_ref'])
        self.assertNotIn(of._hash, e._ben_ref)
        self.assertNotIn(of._hash, e_d['_ben_ref'])
        self.assertIn(au._hash, e._mal_ref)
        self.assertIn(au._hash, e_d['_mal_ref'])
        self.assertIn(of._hash, e._mal_ref)
        self.assertIn(of._hash, e_d['_mal_ref'])

        e.set_context([au, of], 'unknown')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertNotIn(au._hash, e._mal_ref)
        self.assertNotIn(au._hash, e_d['_mal_ref'])
        self.assertNotIn(of._hash, e._mal_ref)
        self.assertNotIn(of._hash, e_d['_mal_ref'])

    def test_10_gradnchild(self):
        e.set_context(afn, 'benign', afs, 'malicious')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertNotIn(afn._hash, e._mal_ref)
        self.assertNotIn(afn._hash, e_d['_mal_ref'])
        self.assertNotIn(afs._hash, e._ben_ref)
        self.assertNotIn(afs._hash, e_d['_ben_ref'])
        self.assertIn(afn._hash, e._ben_ref)
        self.assertIn(afn._hash, e_d['_ben_ref'])
        self.assertIn(afs._hash, e._mal_ref)
        self.assertIn(afs._hash, e_d['_mal_ref'])

    def test_11_child_and_grandchild(self):
        Event._backend.drop()
        make_test_data()
        
        e.set_context([afn, au, of], 'malicious', [afs], 'benign')
        e.set_context(afn, 'benign', au, 'malicious', afs, 'unknown')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertNotIn(afn._hash, e._mal_ref)
        self.assertIn(afn._hash, e._ben_ref)
        self.assertNotIn(au._hash, e._ben_ref)
        self.assertIn(au._hash, e._mal_ref)
        self.assertNotIn(afs._hash, e._ben_ref)
        self.assertNotIn(afs._hash, e._mal_ref)

        self.assertNotIn(afn._hash, e_d['_mal_ref'])
        self.assertIn(afn._hash, e_d['_ben_ref'])
        self.assertNotIn(au._hash, e_d['_ben_ref'])
        self.assertIn(au._hash, e_d['_mal_ref'])
        self.assertNotIn(afs._hash, e_d['_ben_ref'])
        self.assertNotIn(afs._hash, e_d['_mal_ref'])

    def test_12_get_context_child(self):
        Event._backend.drop()
        make_test_data()
        cntxt = e.get_context(au)
        self.assertEqual(cntxt[0], 'unknown')

    def test_13_get_context_grand_child(self):
        cntxt = e.get_context(afn)
        self.assertEqual(cntxt[0], 'unknown')

    def test_14_changed(self):
        e.set_context(afn, 'malicious', of, 'benign')
        self.assertEqual(e.get_context(afn)[0], 'malicious')
        self.assertEqual(e.get_context(of)[0], 'benign')

    def test_15_get_context_multiple(self):
        cntxt = e.get_context([afn, of])
        self.assertEqual(cntxt, ['malicious', 'benign'])

        cntxt = e.get_context([of, au, afn])
        self.assertEqual(cntxt, ['benign', 'unknown', 'malicious'])

        
        


class CategoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(Event._backend, (MongoBackend, MockMongoBackend))
        Event._backend.drop()
        make_test_data()

    def test_category_benign(self):
        e.set_category('benign')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertEqual(e.category, 'benign')
        self.assertEqual(e_d['category'], 'benign')

    def test_category_malicious(self):
        e.set_category('malicious')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertEqual(e.category, 'malicious')
        self.assertEqual(e_d['category'], 'malicious')

    def test_category_unknown(self):
        e.set_category('unknown')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertEqual(e.category, 'unknown')
        self.assertEqual(e_d['category'], 'unknown')

    def test_category_multiple(self):
        e.set_category('unknown')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertEqual(e.category, 'unknown')
        self.assertEqual(e_d['category'], 'unknown')

        e.set_category('malicious')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertEqual(e.category, 'malicious')
        self.assertEqual(e_d['category'], 'malicious')

        e.set_category('benign')
        e_d = e._backend.find_one({'_hash': e._hash})

        self.assertEqual(e.category, 'benign')
        self.assertEqual(e_d['category'], 'benign')
        


def make_threatrank_data():
    oid = "identity--e7c981ed-ab33-4d7a-b55d-db9413560040"

    # =================================
    # Event Email 1 ===================
    # =================================

    timestamp1 = 1236092478

    received = ['(qmail 71864 invoked by uid 60001); Tue, 03 Mar 2009 15:01:19 +0000',
                'from [60.abc.xyz.215] by web53402.mail.re2.yahoo.com via HTTP; Tue, 03 Mar 2009 07:01:18 -0800 (PST)']
    att_received_0 = Attribute('att_email_header_received', received[0])
    att_received_1 = Attribute('att_email_header_received', received[1])
    obj_received = Object('obj_email_header_received', [att_received_0, att_received_1])

    from_ip = '60.abc.xyz.215'
    from_email = 'dn...etto@yahoo.com'
    att_from_ip = Attribute('ip', from_ip)
    att_from_email = Attribute('email_addr', from_email)
    obj_from = Object('from', [att_from_ip, att_from_email])

    subject = 'AIAA Technical Committees'
    att_subject = Attribute('subject', subject)
                      
    to_email = 'johndoe1@lockheedmartin.com'
    att_to_email = Attribute('email_addr', to_email)
    obj_to = Object('to', att_to_email)

    reply_to = 'dn...etto@yahoo.com'
    att_reply_to = Attribute('email_addr', reply_to)
    obj_reply_to = Object('reply_to', att_reply_to)

    message_id = '<107017.64068.qm@web53402.mail.re2.yahoo.com>'
    att_message_id = Attribute('message_id', message_id)

    mime_ver = '1.0'
    att_mime_ver = Attribute('mime_ver', mime_ver)

    x_mailer = 'YahooMailWebService/0.7.289.1'
    att_x_mailer = Attribute('x_mailer', x_mailer)

    content_type = 'multipart/mixed; boundary="Boundary_(ID_Hq9CkDZSoSvBMukCRm7rsg)"'
    att_content_type = Attribute('content_type', content_type)

    body = """Please submit one copy (photocopies are acceptable) of this form, and one copy of nominee’s resume to: AIAA Technical Committee Nominations, 1801 Alexander Bell Drive, Reston, VA 20191. Fax number is 703/264-7551. Form can also be submitted via our web site at www.aiaa.org, Inside AIAA, Technical Committees"""
    att_body = Attribute('body', body)

    data = [obj_received, obj_from, att_subject, obj_to, obj_reply_to, att_message_id,
            att_mime_ver, att_x_mailer, att_content_type, att_body]
    mal_data = [att_from_ip, att_from_email, att_subject, att_reply_to, att_message_id, att_body]
    event_email_1 = Event('email', data, oid, timestamp1, mal_data=mal_data)
    event_email_1.set_category('malicious')

    builtins.event_email_1 = event_email_1



    # =================================
    # Event Email 2 ===================
    # =================================

    timestamp2 = 1236151908

    received = ['(qmail 97721 invoked by uid 60001); 4 Mar 2009 14:35:22 -0000',
                'from [216.abc.xyz.76] by web53411.mail.re2.yahoo.com via HTTP; Wed, 04 Mar 2009 06:35:20 PST']
    att_received_0 = Attribute('att_email_header_received', received[0])
    att_received_1 = Attribute('att_email_header_received', received[1])
    obj_received = Object('obj_email_header_received', [att_received_0, att_received_1])

    from_ip = '216.abc.xyz.76'
    from_email = 'dn...etto@yahoo.com'
    att_from_ip = Attribute('ip', from_ip)
    att_from_email = Attribute('email_addr', from_email)
    obj_from = Object('from', [att_from_ip, att_from_email])

    subject = '7th Annual U.S. Missile Defense Conference'
    att_subject = Attribute('subject', subject)
                      
    to_email = 'johndoe2@lockheedmartin.com'
    att_to_email = Attribute('email_addr', to_email)
    obj_to = Object('to', att_to_email)

    reply_to = 'dn...etto@yahoo.com'
    att_reply_to = Attribute('email_addr', reply_to)
    obj_reply_to = Object('reply_to', att_reply_to)

    message_id = '<107017.64068.qm@web53402.mail.re2.yahoo.com>'
    att_message_id = Attribute('message_id', message_id)

    mime_ver = '1.0'
    att_mime_ver = Attribute('mime_ver', mime_ver)

    x_mailer = 'YahooMailWebService/0.7.289.1'
    att_x_mailer = Attribute('x_mailer', x_mailer)

    content_type = 'multipart/mixed; boundary="0-760892832-1236177320=:97248"'
    att_content_type = Attribute('content_type', content_type)

    body = "Welcome to the 7th Annual U.S. Missile Defense Conference"
    att_body = Attribute('body', body)

    data = [obj_received, obj_from, att_subject, obj_to, obj_reply_to, att_message_id,
            att_mime_ver, att_x_mailer, att_content_type, att_body]
    #mal_data = [att_from_ip, att_from_email, att_subject, att_reply_to, att_message_id, att_body]
    event_email_2 = Event('email', data, oid, timestamp2)

    builtins.event_email_2 = event_email_2




    # =================================
    # Event Email 3 ===================
    # =================================


    timestamp3 = 1237793508

    received = ['(qmail 97721 invoked by uid 60001); 4 Mar 2009 14:35:22 -0000',
                '(qmail 82085 invoked by uid 60001); Mon, 23 Mar 2009 17:14:21 +0000',
                'from [216.abc.xyz.76] by web43406.mail.sp1.yahoo.com via HTTP; Mon, 23 Mar 2009 10:14:21 -0700 (PDT)']
    att_received_0 = Attribute('att_email_header_received', received[0])
    att_received_1 = Attribute('att_email_header_received', received[1])
    att_received_2 = Attribute('att_email_header_received', received[2])                        
    obj_received = Object('obj_email_header_received', [att_received_0, att_received_1, att_received_2])

    from_ip = '216.abc.xyz.76'
    from_email = 'ginette.c...@yahoo.com'
    att_from_ip = Attribute('ip', from_ip)
    att_from_email = Attribute('email_addr', from_email)
    obj_from = Object('from', [att_from_ip, att_from_email])

    subject = 'Celebrities Without Makeup'
    att_subject = Attribute('subject', subject)
                      
    to_email = 'johndoe3@lockheedmartin.com'
    att_to_email = Attribute('email_addr', to_email)
    obj_to = Object('to', att_to_email)

    message_id = '<297350.78665.qm@web43406.mail.sp1.yahoo.com>'
    att_message_id = Attribute('message_id', message_id)

    mime_ver = '1.0'
    att_mime_ver = Attribute('mime_ver', mime_ver)

    x_mailer = 'YahooMailWebService/0.7.289.1'
    att_x_mailer = Attribute('x_mailer', x_mailer)

    content_type = 'multipart/mixed; boundary="Boundary_(ID_DpBDtBoPTQ1DnYXw29L2Ng)"'
    att_content_type = Attribute('content_type', content_type)

    body = ""
    att_body = Attribute('body', body)

    data = [obj_received, obj_from, att_subject, obj_to, att_message_id,
            att_mime_ver, att_x_mailer, att_content_type, att_body]
    #mal_data = [att_from_ip, att_from_email, att_subject, att_reply_to, att_message_id, att_body]
    event_email_3 = Event('email', data, oid, timestamp3)

    builtins.event_email_3 = event_email_3

        
class ThreatRankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert isinstance(Event._backend, (MongoBackend, MockMongoBackend))
        Event._backend.drop()
        make_threatrank_data()

    def test_01(self):
        tr = event_email_1.threatrank()
        print(tr)
        tr = event_email_2.threatrank()
        print(tr)
        tr = event_email_3.threatrank()
        print(tr)

        


if __name__ == '__main__':
    unittest.main()

    


