import os, collections, time
from pymongo.collection import Collection

if __name__ != 'tahoe.report':
    import sys
    sys.path = ['..'] + sys.path
    del sys
import tahoe

_LIM = 10000
_P = {"_id": 0}

class Report(tahoe.Instance):
    def __init__(self, qtype, userid, timestamp, data,
                 current_page=1, next_page=1, **kwargs):

        self.itype = 'report'
        self.userid = userid
        self.timestamp = timestamp
        self.current_page = current_page
        self.next_page = next_page

        self.data = data

        super().__init__(sub_type=qtype, **kwargs)
        

