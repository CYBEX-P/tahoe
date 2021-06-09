"""unittests for tahoe.identity.org"""

import builtins
import hashlib
import pdb
import unittest
import time 

if __name__ != 'tahoe.tests.test_dam':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os

from tahoe.dam import DAM, MockDAM
from tahoe.tests.identity.test_backend import setUpBackend, tearDownBackend
from tahoe.identity import Identity, Org, User, IdentityBackend, \
     MockIdentityBackend
from tahoe import Instance, Attribute, Object, Event, Session
from tahoe.backend import MongoBackend, MockMongoBackend


def setUpDAM():
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    dbname = "e3010ec9-e2b8-4273-af46-d7a0a82af95d"
    try:
##        raise ConnectionFailure  # debug delete me
        client = MongoClient()
        client.admin.command('ismaster')
        _dam = DAM(dbname=dbname)
        _backend = MongoBackend(dbname=dbname)
    except ConnectionFailure:
        _dam = MockDAM(dbname=dbname)
        _backend = MockMongoBackend(dbname=dbname)
    _dam.drop()
    return _dam, _backend

def tearDownDAM(_dam):
    dbname = _dam.database.name
    _dam.database.client.drop_database(dbname)


def setUpModule():
    _identity_backend = setUpBackend()
    _dam, _backend = setUpDAM()

    _dam._identity_backend = _identity_backend

    Instance.set_backend(_dam)
    Identity._backend = _identity_backend
    builtins._backend = _backend
    

    assert isinstance(Identity._backend,
                       (IdentityBackend, MockIdentityBackend))
    assert User._backend is Identity._backend
    assert Org._backend is Identity._backend
     
    
def tearDownModule():
    tearDownDAM(Instance._backend)
    tearDownBackend(Identity._backend)
    del builtins._backend
    pass


class Hashablelist(list):
    def __init__(self, me):
        super().__init__(me)
    def __hash__(self):

        temp1 = list()
        for it in self.items():
            if isinstance(it,dict):
                temp1.append(Hashabledict(it))
            elif isinstance(it, list):
                temp1.append(Hashablelist(it))
        return hash((frozenset(temp1)))

class Hashabledict(dict):
    def __init__(self, me):
        super().__init__(me)
    def __hash__(self):
        # return hash((frozenset(self), frozenset(self.itervalues())))

        temp1 = list()
        for it in self.items():
            if isinstance(it,dict):
                temp1.append(Hashabledict(it))
            elif isinstance(it, list):
                temp1.append(Hashablelist(it))
        return hash((frozenset(self), frozenset(temp1)))

        # return hash(tuple(sorted(self.items())))

def toHashable(listDicts):
    return [Hashabledict(item) if isinstance(item,dict) else item  for item in listDicts]

def Diff(list1, list2):
    list1 = toHashable(list1)
    list2 = toHashable(list2)
    return (list(list(set(list1)-set(list2)) + list(set(list2)-set(list1)))) 


def att_to_edata(*attDocs):
    edat = dict()

    for doc in attDocs:
        try:
            key = doc["sub_type"]
            edat[key] = [doc["data"]]
        except:
            pass
    return edat



def make_test_data():

    builtins.ident_records = 24
    builtins.backend_records = 10
    builtins.numb_events = 3
    builtins.numb_att_sets = 3
    builtins.numb_users = 4
    builtins.numb_orgs = 2

    builtins.u1 = User('user1@example.com', 'pass1', 'User 1')
    builtins.u2 = User('user2@example.com', 'pass2', 'User 2')
    builtins.u3 = User('user3@example.com', 'pass3', 'User 3')
    ru = User('user4@example.com', 'pass4', 'User 4')

    builtins.o1 = Org("org of user1",[u1, u2],[u1],"u1_Org")
    builtins.o2 = Org("org of user2",[u3, u2],[u2],"u2_Org")

    builtins.o1d = o1._backend.find_one({'_hash': o1._hash})
    builtins.o2d = o2._backend.find_one({'_hash': o2._hash})

    builtins.att1 = Attribute("domain", "dns1.cloudflare.com")
    builtins.att2 = Attribute("ip", "1.1.1.1")

    builtins.att3 = Attribute("domain", "dns1.google.com")
    builtins.att4 = Attribute("ip", "8.8.8.8")

    builtins.att5 = Attribute("domain", "dns2.example.com")
    builtins.att6 = Attribute("ip", "8.8.4.4")

    d1 = [att1,att2]
    d2 = [att3,att4]
    d3 = [att5,att6]


    builtins.event_by_org1 = Event("sighting",d1, o1._hash, time.time())
    builtins.event_by_org2 = Event("sighting",d2, o2._hash, time.time())
    builtins.event_by_org_r = Event("sighting",d3, "org3", time.time())

    query = {'itype': 'event'}
    query2 = {}

    filt = {"_id":0}

    dam = Instance._backend
    
    builtins.r_control = list(_backend.find(query,filt))
    builtins.r1 = [i for i in dam.find(query,filt,user=u1)]
    builtins.r2 = [i for i in dam.find(query,filt,user=u2)]
    builtins.r3 = [i for i in dam.find(query,filt,user=u3)]
    builtins.r4 = [i for i in dam.find(query,filt,user=ru._hash)]


    builtins.r_control_all = list(_backend.find(query2,filt))
    builtins.r1_p = [item for item in dam.find(query2,filt,user=u1)]
    builtins.r2_p = [item for item in dam.find(query2,filt,user=u2)]
    builtins.r3_p = [item for item in dam.find(query2,filt,user=u3)]
    builtins.r4_p = [item for item in dam.find(query2,filt,user=ru._hash)]

    
def delete_test_data():
    del builtins.u1, builtins.u2, builtins.u3, \
        builtins.o1, builtins.o2, builtins.o1d, builtins.o2d, \
        builtins.att1, builtins.att2, builtins.att3, builtins.att4, builtins.att5, builtins.att6, \
        builtins.event_by_org1, builtins.event_by_org2, builtins.event_by_org_r, \
        builtins.r_control, builtins.r1, builtins.r2, builtins.r3, builtins.r4, \
        builtins.r_control_all, builtins.r1_p, builtins.r2_p, builtins.r3_p, builtins.r4_p




class InitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):       
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        
        
    def test_01_init(self):
        self.assertIsNotNone(o1d)
        self.assertIsNotNone(o2d)


    def test_dbdata_count(self):
        EQ = self.assertEqual

        ident_backend = Identity._backend
        back_backend = Instance._backend

        total_c_i = ident_backend.count_documents({})

        email_c = ident_backend.count_documents({"itype":"attribute", "sub_type":"email_addr"})
        password_c = ident_backend.count_documents({"itype":"attribute", "sub_type":"password"})
        name_c = ident_backend.count_documents({"itype":"attribute", "sub_type":"name"})
        user_c = ident_backend.count_documents({"itype":"object", "sub_type":"cybexp_user"})
        orgname_c = ident_backend.count_documents({"itype":"attribute", "sub_type":"orgname"})
        org_c = ident_backend.count_documents({"itype":"object", "sub_type":"cybexp_org"})
        admin_c = ident_backend.count_documents({"itype":"object", "sub_type":"admin"})

        total_c_b = back_backend.count_documents({},{})

        ip_c = back_backend.count_documents({"itype":"attribute", "sub_type":"ip"})
        domain_c = back_backend.count_documents({"itype":"attribute", "sub_type":"domain"})
        event_c = back_backend.count_documents({"itype":"event", "sub_type":"sighting"})

        EQ(total_c_i, ident_records)
        EQ(total_c_b, backend_records)
        
        EQ(email_c, numb_users)
        EQ(password_c, numb_users)
        EQ(name_c, numb_users+numb_orgs)
        EQ(user_c, numb_users)
        EQ(orgname_c, numb_orgs)
        EQ(org_c, numb_orgs)
        EQ(admin_c, numb_orgs)

        EQ(ip_c, numb_att_sets)
        EQ(domain_c, numb_att_sets)
        EQ(event_c, numb_events)

    def _test_DAM_count(self):
        # test by count, if any records that should not be there we can catch by just counting
        EQ = self.assertEqual

        EQ(len(r_control_all), backend_records)
        EQ(len(r_control), numb_events)

        # test DAM filtering, query = {events}
        EQ(len(r1), 1) # by user 1
        EQ(len(r2), 2) # by user 2
        EQ(len(r3), 1) # by user 3
        EQ(len(r4), 0) # by fake user, should return 0

        # test passthrough, query = {}
        EQ(len(r1_p), backend_records) # by user 1
        EQ(len(r2_p), backend_records) # by user 2
        EQ(len(r3_p), backend_records) # by user 3
        EQ(len(r4_p), backend_records) # by user fake

    def test_DAM_data(self):
        # test the actual data

        EQ = self.assertEqual
        IN = self.assertIn

        
        EQ(r1[0]["_hash"], event_by_org1._hash)
        EQ(r1[0]["data"], att_to_edata(att1.doc, att2.doc) )

        EQ(r2[0]["_hash"], event_by_org1._hash)
        EQ(r2[1]["_hash"], event_by_org2._hash)
        EQ(r2[0]["data"], att_to_edata(att1.doc, att2.doc) )
        EQ(r2[1]["data"], att_to_edata(att3.doc, att4.doc) )


        EQ(r3[0]["_hash"], event_by_org2._hash)
        EQ(r3[0]["data"], att_to_edata(att3.doc, att4.doc) )

        EQ(len(r4), 0) # by fake user, should return 0


        for item in r1+r2+r2+r4:
            EQ(item["itype"], "event")

        # test passthrough data 

        EQ(r1_p, r_control_all)
        EQ(r2_p, r_control_all)
        EQ(r3_p, r_control_all)
        EQ(r4_p, r_control_all)


    
if __name__ == '__main__':
    unittest.main()



