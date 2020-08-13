import sys
sys.path.append("../../tahoe0.7-dev")

from tahoe import Instance, Attribute, Object, MongoBackend, DAM, Event
from tahoe.identity import Identity, Org, User, IdentityBackend
import time, json
from pprint import pprint


def filter_dict(dat, l):
   new_dat = dict()

   for it in l:
      try:
         new_dat[it] = dat[it]
      except:
         pass
   return new_dat


mongo_backend = MongoBackend(mongo_url="mongodb://localhost", dbname='tahoe_db')
identity_backend = IdentityBackend(mongo_url="mongodb://localhost")
Instance._backend = mongo_backend
Identity._backend = identity_backend

DAM_backend = DAM.DAM(identity_backend,mongo_url="mongodb://localhost")

u1 = User("u1@example.com", password="p1", name="User1")
u2 = User("u2@abc.com", password="p2", name="User2")
u3 = User("u3@hotmail.com", password="p3", name="User3")


print("user1:", filter_dict(u1.data, ["name", "email_addr"]))
print("user2:", filter_dict(u2.data, ["name", "email_addr"]))
print("user3:", filter_dict(u3.data, ["name", "email_addr"]))
print()

org1 = Org("org of user1",[u1, u2],[u1],"u1_Org")
org2 = Org("org of user2",[u3, u2],[u2],"u2_Org")

print("org1: {'admin':[u1], 'users': [u1, u2]}")
print("org2: {'admin':[u2], 'users': [u2, u3]}")
print("org_random: {'admin':[u99], 'users': [u99]}")
print()


r = "fake-org"

att1 = Attribute("domain", "dns1.cloudflare.com")
att2 = Attribute("ip", "1.1.1.1")

att3 = Attribute("domain", "dns1.google.com")
att4 = Attribute("ip", "8.8.8.8")

att5 = Attribute("domain", "dns2.example.com")
att6 = Attribute("ip", "8.8.4.4")

d1 = [att1,att2]
d2 = [att3,att4]
d3 = [att5,att6]


print("att1:",filter_dict(att1.doc,["sub_type","data"]))
print("att2:",filter_dict(att2.doc,["sub_type","data"]))
print()
print("att3:",filter_dict(att3.doc,["sub_type","data"]))
print("att4:",filter_dict(att4.doc,["sub_type","data"]))
print()
print("att5:",filter_dict(att5.doc,["sub_type","data"]))
print("att6:",filter_dict(att6.doc,["sub_type","data"]))
print()


event_by_org1 = Event("sighting",d1, org1._hash, time.time())
event_by_org2 = Event("sighting",d2, org2._hash, time.time())
event_by_org_r = Event("sighting",d3, r, time.time())

events = dict()
events["event1_by_org1"] = [filter_dict(att1.doc,["sub_type","data"]),filter_dict(att2.doc,["sub_type","data"])]
events["event2_by_org2"] = [filter_dict(att3.doc,["sub_type","data"]),filter_dict(att4.doc,["sub_type","data"])]
events["event3_by_org_random"] = [filter_dict(att5.doc,["sub_type","data"]),filter_dict(att6.doc,["sub_type","data"])]
pprint(events)
print()

query = {'itype': 'event'}
filter = {"_hash":1, "data":1,"itype":1,"_id":0 }

print("Query:",query)
print("Filter:",filter)
print()

r_control = mongo_backend.find(query,filter)
r1 = DAM_backend.find(u1,query,filter)
r2 = DAM_backend.find(u2,query,filter)
r3 = DAM_backend.find(u3,query,filter)
print()

print("######### Control ################")
pprint([t for t in r_control])
print()
print(f"######### {query} by User 1 #########")
pprint([t for t in r1])
print()
print(f"######### {query} by User 2 #########")
pprint([t for t in r2])
print()
print(f"######### {query} by User 3 #########")
pprint([t for t in r3])
print()


