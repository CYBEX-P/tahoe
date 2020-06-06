if __name__ in ["__main__", "tdql"]:
    from instance import Instance
    from backend import get_query_backend
else: 
    from .instance import Instance
    from .backend import get_query_backend

import os
    

class TDQL(Instance):
  backend = get_query_backend() if os.getenv("CYBEXP_API_MONGO_URL") else NoBackend()
  
  def __init__(self, sub_type, data, userid, timestamp, host='localhost', port=0, nonce='', **kwargs):
    self.itype, self.data = 'query', data
    self.userid, self.timestamp = userid, timestamp
    self.status, self.report_id = 'wait', ''
    self._socket = [host, port, nonce]

    super().__init__(sub_type=sub_type, data=data, **kwargs)
               
  def unique(self):
    unique = self.itype + self.sub_type + self.canonical_data() + self.userid + str(int(self.timestamp)//60//60)  # expires in an hour
    return unique.encode('utf-8')
    
  def setsocket(self, host, port, nonce):
    self.update( {'_socket' : [host, port, nonce]} )