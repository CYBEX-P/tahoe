if __name__ in ["__main__", "tdql"]:
    from instance import Instance
    from misc import canonical
else: 
    from .instance import Instance
    from .misc import canonical

import os
    

class TDQL(Instance):
  
  def __init__(self, sub_type, data, userid, timestamp, host='localhost', port=0, nonce='', **kwargs):
    self.itype, self.data = 'query', data
    self.userid, self.timestamp = userid, timestamp
    self.status, self.report_id = 'wait', ''
    self._socket = [host, port, nonce]

    super().__init__(sub_type=sub_type, **kwargs)
               
  def unique(self):
    unique = self.itype + self.sub_type + canonical(self.data) + self.userid + str(int(self.timestamp)//60//60)  # expires in an hour
    return unique.encode('utf-8')
    
  def setsocket(self, host, port, nonce):
    self.update( {'_socket' : [host, port, nonce]} )
