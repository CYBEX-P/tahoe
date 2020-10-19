"""unittests for tahoe.identity.org"""

import builtins
import hashlib
import pdb
import unittest
import time 

if __name__ != 'tahoe.tests.identity.test_org':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os

from tahoe import Instance, Attribute, Object, MongoBackend, DAM, Event
from tahoe.identity import Identity, Org, User, IdentityBackend, MockIdentityBackend
# from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import tearDownBackend



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






def setUpIdentBackend():
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    dbname = "b27d7fd0-832a-4a74-b7e9-1a7b7b86860f"
    try:
        #raise ConnectionFailure  # debug delete me
        client = MongoClient()
        client.admin.command('ismaster')
        _backend = IdentityBackend(dbname=dbname)
    except ConnectionFailure:
        _backend = MockIdentityBackend(dbname=dbname)
    _backend.drop()
    return _backend

def setUpBackend():
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    dbname = "e3010ec9-e2b8-4273-af46-d7a0a82af95d"
    try:
        #raise ConnectionFailure  # debug delete me
        client = MongoClient()
        client.admin.command('ismaster')
        _backend = MongoBackend(dbname=dbname)
    except ConnectionFailure:
        _backend = MockMongoBackend(dbname=dbname)
    _backend.drop()
    return _backend

def tearDownBackend(_backend):
    dbname = _backend.database.name
    _backend.database.client.drop_database(dbname)
    





def make_test_data():

    builtins.ident_records = 20
    builtins.backend_records = 9
    builtins.numb_events = 3
    builtins.numb_att_sets = 3
    builtins.numb_users = 3
    builtins.numb_orgs = 2

    b_db_name = "tahoe_db"
    b_c_name = "e3010ec9-e2b8-4273-af46-d7a0a82af95d"
    i_db_name = "identity_db"
    i_c_name = "b27d7fd0-832a-4a74-b7e9-1a7b7b86860f"

    mongo_backend = MongoBackend(mongo_url="mongodb://localhost", dbname=b_db_name, collname=b_c_name)
    identity_backend = IdentityBackend(mongo_url="mongodb://localhost", dbname=i_db_name, collname=i_c_name)
    Instance._backend = mongo_backend
    Identity._backend = identity_backend

    mongo_backend.drop()
    identity_backend.drop()

    DAM_backend = DAM.DAM(identity_backend,mongo_url="mongodb://localhost", dbname=b_db_name, collname=b_c_name)

    builtins.u1 = User('user1@example.com', 'pass1', 'User 1')
    builtins.u2 = User('user2@example.com', 'pass2', 'User 2')
    builtins.u3 = User('user3@example.com', 'pass3', 'User 3')


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

    # builtins.d1 = {att1,att2}
    # builtins.d2 = {att3,att4}
    # builtins.d3 = {att5,att6}

    builtins.event_by_org1 = Event("sighting",d1, o1._hash, time.time())
    builtins.event_by_org2 = Event("sighting",d2, o2._hash, time.time())
    builtins.event_by_org_r = Event("sighting",d3, "org3", time.time())

    query = {'itype': 'event'}
    query2 = {}

    filt = {"_id":0}#, "timestamp":0}

    print("not passthrough")
    builtins.r_control = [item for item in Instance._backend.find(query,filt)]
    builtins.r1 = [item for item in DAM_backend.find(u1,query,filt)]
    print("len r1:", len(r1))
    builtins.r2 = [item for item in DAM_backend.find(u2,query,filt)]
    builtins.r3 = [item for item in DAM_backend.find(u3,query,filt)]
    builtins.r4 = [item for item in DAM_backend.find("RANDOM_USER",query,filt)]

    print("passthrough:", DAM_backend.database.name)

    builtins.r_control_all = [item for item in Instance._backend.find(query2,filt)]
    builtins.r1_p = [item for item in DAM_backend.find(u1,query2,filt)]
    builtins.r2_p = [item for item in DAM_backend.find(u2,query2,filt)]
    builtins.r3_p = [item for item in DAM_backend.find(u3,query2,filt)]
    builtins.r4_p = [item for item in DAM_backend.find("RANDOM_USER",query2,filt)]


    # builtins.aon = Attribute('orgname', 'unr')
    # builtins.an = Attribute('name', 'University of Nevada Reno')
    # builtins.oadm = Object('admin', u1)

    # builtins.ae = Attribute('email_addr', 'user1@example.com')

    # hashed_pass = hashlib.sha256('Abcd1234'.encode('utf-8')).hexdigest()
    # builtins.ap = Attribute('password', hashed_pass)

    # builtins.aun = Attribute('name', 'User 1')
    

def delete_test_data():
    del builtins.u1, builtins.u2, builtins.u3, \
        builtins.o1, builtins.o2, builtins.o1d, builtins.o2d, \
        builtins.att1, builtins.att2, builtins.att3, builtins.att4, builtins.att5, builtins.att6, \
        builtins.event_by_org1, builtins.event_by_org2, builtins.event_by_org_r, \
        builtins.r_control, builtins.r1, builtins.r2, builtins.r3, builtins.r4, \
        builtins.r_control_all, builtins.r1_p, builtins.r2_p, builtins.r3_p, builtins.r4_p


# def setUpModule():
#     _backend = setUpBackend()
#     Instance.set_backend(_backend)

#     assert User._backend is Identity._backend
#     assert Org._backend is Identity._backend
#     assert isinstance(Org._backend, (IdentityBackend, MockIdentityBackend))
    

def tearDownModule():
    # tearDownBackend(Instance._backend)
    # tearDownBackend(Identity._backend)
    pass

class InitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # mongo_backend = setUpBackend()
        # identity_backend = setUpIdentBackend()

        # Instance._backend = mongo_backend
        # Identity._backend = identity_backend

        # Instance._backend.drop()
        # Identity._backend.drop()

        # assert User._backend is Identity._backend
        # assert Org._backend is Identity._backend
        # assert isinstance(Org._backend, (IdentityBackend, MockIdentityBackend))

        # assert Identity._backend is not Instance._backend
       
        make_test_data()

    @classmethod
    def tearDownClass(cls):
        delete_test_data()
        
        
    def test_init(self):
        self.assertIsNotNone(o1d)
        self.assertIsNotNone(o2d)


    def test_dbdata_count(self):
        EQ = self.assertEqual

        ident_backend = Identity._backend
        back_backend = Instance._backend

        total_c_i = ident_backend.count_documents({},{})

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



