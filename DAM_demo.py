import sys
sys.path.append("../../tahoe0.7-dev")

from tahoe import Instance, Attribute, Object, MongoBackend, DAM, Event
from tahoe.identity import Identity, Org, User, IdentityBackend
import time
from pprint import pprint

b1 = MongoBackend(mongo_url="mongodb://localhost", dbname='tahoe_db')
b2 = IdentityBackend(mongo_url="mongodb://localhost")
Instance._backend = b1
Identity._backend = b2

DAM_backend = DAM.DAM(b2,mongo_url="mongodb://localhost")

u1 = User("u1@abc.com")
u2 = User("u2@abc.com")
u3 = User("u3@abc.com")

print("user1:",u1._hash)
print("user2:",u2._hash)
print("user3:",u3._hash)
print()

org1 = Org("org of user1",[u1, u2],[u1],"u1_Org")
org2 = Org("org of user2",[u3, u2],[u2],"u2_Org")

print("org1(*u1, u2):",org1._hash)
print("org2(*u2, u3):",org2._hash)
r = "fake-org"


att1 = Attribute("ip", "1.1.1.1")
att2 = Attribute("domain", "cloudflare.com")
att3 = Attribute("domain", "dns1.google.com")
att4 = Attribute("ip", "8.8.8.8")
att5 = Attribute("ip", "8.8.4.4")
att6 = Attribute("domain", "dns2.example.com")

d1 = [att1,att2]
d2 = [att3,att4]
d3 = [att5,att6]


event_by_org1 = Event("sighting",d1, org1._hash, time.time())
event_by_org2 = Event("sighting",d2, org2._hash, time.time())
event_by_org_r = Event("sighting",d3, r, time.time())

events = dict()
events["event1_by_org1"] = [a.doc for a in [att1,att2]]
events["event2_by_org2"] = [a.doc for a in [att3,att4]]
events["event3_by_org_random"] = [a.doc for a in [att5,att6]]
pprint(events)
print()

query = {'itype': 'event'}
filter = {"_hash":1, "data":1,"itype":1,"_id":0 }

print("Query:",query)
print("FIlter:",filter)
print()

r_control = b1.find(query,filter)
r1 = DAM_backend.find(u1,query,filter)
r2 = DAM_backend.find(u2,query,filter)
r3 = DAM_backend.find(u3,query,filter)
print()

print("######### Control ################")
pprint([t for t in r_control])
print("######### {} by User 1 #########")
pprint([t for t in r1])
print("######### {} by User 2 #########")
pprint([t for t in r2])
print("######### {} by User 3 #########")
pprint([t for t in r3])
print("##################################")


