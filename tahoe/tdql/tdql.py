
if __name__ != 'tahoe.tdql.tdql':
    import sys
    sys.path = ['..', '..\..'] + sys.path
    del sys
import tahoe

import os
    
# class ThreatQL()

class TDQL(tahoe.Instance):
  
    def __init__(self, sub_type, data, userid, timestamp, host='localhost', port=0, nonce='', **kwargs):
        self.itype, self.data = 'query', data
        self.userid, self.timestamp = userid, timestamp
        self.status, self.report_id = 'invalid', ''
        self._socket = [host, port, nonce]

        # if force_redo flag is set,
        # self.unique = randoom number

        super().__init__(sub_type=sub_type, **kwargs)

    @property
    def _unique(self):
        unique = self.itype + self.sub_type + tahoe.misc.canonical(self.data) + \
            self.userid + str(int(self.timestamp)//60//60)  # expires in an hour
        return unique.encode('utf-8')

    def setsocket(self, host, port, nonce):
        self._update({'_socket': [host, port, nonce]})

    def setstatus(self, status):
        self._update({'status': status})


