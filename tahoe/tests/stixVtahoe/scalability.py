import random
import string
import timeit
import time

import tahoe
from tahoe import Instance, Attribute, Object, Event, MongoBackend

tahoe_dbname = "33d5822c-7a0b-4896-a44c-5b40a98328fc"
_backend = MongoBackend(dbname=tahoe_dbname)

Instance._backend = _backend


stix_dbname = "4edf1bc7-7d53-4adf-810c-7078165d0bd5"
stix_db = MongoBackend(dbname=stix_dbname)

_backend.drop()
stix_db.drop()


_backend.create_index("_ref")

def random_str():
    n = random.randint(5, 30)
    allowed_characters = string.ascii_letters + string.digits + '_'
    arr = []
    for i in range(n):
        c = random.choice(allowed_characters)
        arr.append(c)

    s = ''.join(arr)
    return s


def random_email():
    s = random_str()
    e = s + '@gmail.com'
    return e


def get_one_stix():
    """Generate random STIX email event."""

    d = {
        "0": {
            "type": "email-addr",
            "value": random_email(),
            "display_name": random_str()
            },
        "1": {
            "type": "email-addr",
            "value": random_email(),
            "display_name": random_str()
            },
        "2": {
            "type": "email-message",
            "from_ref": "0",
            "to_refs": ["1"],
            "date": random_str(),
            "subject": random_str()
            }
        }
    stix_db.insert_one(d)
    return d


def get_100_stix():
    _ = [get_one_stix() for i in range(100)]


def get_one_tahoe():
    aef = Attribute('email_addr', random_email())
    anf = Attribute('name', random_str())
    of = Object('from', [aef, anf])

    aet = Attribute('email_addr', random_email())
    ant = Attribute('name', random_str())
    ot = Object('to', [aet, ant])

    asub = Attribute("subject", random_str())

    e = Event('email', [of, ot, asub], random_str(), random.random() )

    return e

def get_100_tahoe():
    _ = [get_one_tahoe() for i in range(100)]


num_query = 100

x = []
y_tahoe = []
y_stix = []


d = "lookup@gmail.com"
ae = Attribute('email_addr', d)

##for i in range(0, 20, 1):
##    get_100_tahoe()
##    get_100_stix()
##
####    time.sleep(2)
##
##    t1 = timeit.timeit(lambda: _backend.find_one({"sub_type":"email", "_ref":ae._hash}), number=num_query)
##    t2 = timeit.timeit(lambda: stix_db.find_one({"0.value": d}), number=num_query)
##
##    x.append(i)
##    y_tahoe.append(t1)
##    y_stix.append(t2)
##
##
##    print(f"{10000/num_query*t1:10.5f} {10000/num_query*t2:10.5f}")
##
##


####### Plot

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
x = [i*200 for i in x]
y_tahoe = [0.043945300000000076, 0.048104499999999994, 0.049017700000000275, 0.048417399999999944, 0.048960300000000956, 0.048436299999998766, 0.04888919999999963, 0.048120700000001904, 0.047664499999999776, 0.0488964999999979, 0.049375099999998895, 0.048577300000000264, 0.04860160000000013, 0.048342599999998015, 0.049821500000000185, 0.04938010000000048, 0.0483880000000122, 0.049443000000010784, 0.04894990000000132, 0.04942159999999751]
y_stix = [0.04375529999999994, 0.05194199999999993, 0.059344900000000145, 0.0635178999999999, 0.06790909999999961, 0.07086600000000054, 0.07822009999999935, 0.08262020000000092, 0.08690570000000264, 0.09023979999999909, 0.0960692000000023, 0.10012849999999673, 0.10324070000000063, 0.10796690000000098, 0.11357230000000129, 0.11692880000000372, 0.12136110000000144, 0.12614189999999326, 0.13130189999999686, 0.14116539999999134]

import matplotlib as mpl
from matplotlib import pyplot as plt

##mpl.style.use('seaborn')

plt.plot(x, y_tahoe, '+-b', x, y_stix, '+-r')
plt.grid('minor')
plt.legend(['TAHOE', 'STIX'])
plt.xlabel('Number of Email events in the database')
plt.ylabel(f'Time taken for {num_query} queries (s)')
plt.title('STIX vs TAHOE Scalability')
plt.show()





















