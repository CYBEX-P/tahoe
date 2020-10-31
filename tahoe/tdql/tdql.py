"""TAHOE TDQL class."""

import hashlib
import pdb

if __name__ != 'tahoe.identity.identity':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
from tahoe import Attribute, Object
from tahoe.misc import canonical

    
# class ThreatQL()

class TDQL(Object):
    """
    A TDQL holds report queries in TDQL format.

    Users of CYBEX-P requests reports in a language called TDQL.
    TDQL structures the report query in JSON format.

    Attributes
    ----------
    itype : str
        Constant value `object`. (Automatically set)
    sub_type : str
        Constant value `query`. (Automatically set)
    data : dict
        JSON document with fields data, userid, timestamp, encrypted,
        socket. See __init__ for their description.
    _hash : str
        SHA-256 digest of `<itype, sub_type, data>`.
        A globally unique but reproducible ID of the attribute.
    _backend : tahoe.backend.Backend, default=NoBackend()
        Data storage. Use `NoBackend` for only data
        sharing and `MongoBackend` for storing the data.
        For performance, `_backend` should be a class variable not an
        instance variable. Set it like ``Instance._backend = backend``.
    _cref : list (JSON array)
        A TAHOE `Object` refers other `Instances (Attribute/Object)`,
        called children. `_cref` stores the `_hashes` of child instances.
        Order of the _hashes is insignificant.
    _ref : list (JSON array)
        A TAHOE `Object` refers other `Instances (Attribute/Object)`.
        , which in turn can refer other tahoe `Instances`. `_ref` stores
        the `_hash` of all these `Instances`. Order of the _hashes is
        insignificant. _cref is a subset of _ref.
    """
  
    def __init__(self, qtype, qdata, qhash, userid, timestamp,
                 encrypted=True, **kwargs):
        """
        Parameters
        ----------         
        data : str
            TDQL query is JSON. This JSON is encoded using
            tahoe.misc.canonical() and then stored in this attribute.
            `data` can be encrypted with the public key of the processing
            server; in that case `encrypted` should be `True`.
        userid : str
            `_hash` of the user who requested the report.
        timestamp : float
            Unix timestamp (UTC) denoting when the report was queried.
        encrypted : bool
            Whether the data field is encrypted with the public key of
            the processing server.
        *kwargs : dict
            keyword arguments, see *Other Parameters*.

        Other Parameters
        ----------------
        host : str, default='localhost'
            When a report is ready, the report server notifies the API
            via a network socket (host:port). `host` is the host of
            that network socket.
        port : int, default=0
            When a report is ready, the report server notifies the API
            via a network socket (host:port). `port` is the port of
            that network socket.
        nonce : str, default=''
            When a report is ready, the report server notifies the API
            via a network socket (host:port). `nonce` is sent to the
            socket and acts as a password.
        _backend : tahoe.identity.backend.IdentityBackend,
        default=cls._backend
            If given the instance `_backend` will be different from
            class `_backend`. Please lookup *Python Class and Instance
            Variables* if you don't know the difference. You shouldn't
            use this parameter for normal operation. Rather Set class
            backend like `Instance._backend = backend`.
        """

        aqtype = Attribute('qtype', qtype, _backend=self._backend)
        aqhash = Attribute('qhash', qhash, _backend=self._backend)        
        aqdata = Attribute('qdata', qdata, _backend=self._backend)
        auserid = Attribute('userid', userid, _backend=self._backend)
        atimestamp = Attribute('timestamp', timestamp, _backend=self._backend)
        aencrypted = Attribute('encrypted', encrypted, _backend=self._backend)
        
        astatus = Attribute('status', 'invalid', _backend=self._backend)
        areport_id = Attribute('report_id', '', _backend=self._backend)

        host = kwargs.pop('host', 'localhost')
        port = kwargs.pop('port', 0)
        nonce = kwargs.pop('nonce', '')
        ahost = Attribute('host', host, _backend=self._backend)
        aport = Attribute('port', port, _backend=self._backend)
        anonce = Attribute('nonce', nonce, _backend=self._backend)
        osocket = Object('socket', [ahost, aport, anonce],
                         _backend=self._backend)

        data = [aqtype, aqhash, aqdata, auserid, atimestamp,
                aencrypted, astatus, areport_id, osocket]
        super().__init__('query', data, **kwargs)
            

    @property
    def status(self):
        return self.data['status'][0]

    @status.setter
    def status(self, status):
        """
        Set status of this query.

        Parameters
        ----------
        status : {"wait", "processing", "ready", "failed"}            
        """
        
        if status not in ('wait', 'processing', 'ready', 'failed'):
            raise ValueError(f"status: {status}")

        a_new_status = Attribute('status', status, _backend=self._backend)
        a_old_status = Attribute('status', self.status, _backend=self._backend)
        
        if a_new_status._hash != a_old_status._hash:
            self.replace_instance(a_old_status, a_new_status)

    @property
    def qdata(self):
        return self.data['qdata'][0]

    @property
    def qhash(self):
        return self.data['qhash'][0]
    
    @property
    def qtype(self):
        return self.data['qtype'][0]

    @property
    def report_id(self):
        return self.data['report_id'][0]

    @report_id.setter
    def report_id(self, report_id):
        """
        Set report_id of this query.

        Parameters
        ----------
        report_id : _hash of report           
        """

        a_new_report_id = Attribute('report_id', report_id,
                                    _backend=self._backend)
        a_old_report_id = Attribute('report_id', self.report_id,
                                    _backend=self._backend)

        if a_new_report_id._hash != a_old_report_id._hash:
            self.replace_instance(a_old_report_id, a_new_report_id)

    @property
    def timestamp(self):
        return self.data['timestamp'][0]
    
    @property
    def userid(self):
        return self.data['userid'][0]
    
    @property
    def _unique(self):
        userid = self.data['userid'][0]
        timestamp = self.data['timestamp'][0]
        unique = self.itype + self.sub_type + self.qtype + self.qhash + \
                 userid +  str(int(timestamp)//60//60)
        return unique.encode('utf-8')

    def setsocket(self, host, port, nonce):
        """
        Set the socket host, port, nonce.

        When CYBEX-P API receives a report query (TDQL) it submits
        that to the report server and creates a network socket on a
        random port. When the report is ready, the report server
        notifies the API via that network socket by sending `nonce`.
        `nonce` acts like a password. The socket acts like an IPC.
        The socket attributes are `host`, `port` and `nonce` which
        are set by CYBEX-P API in the TDQL using this function.

        Parameters
        ----------
        host : str
        port : int
        nonce : str
        """
        
        a_new_host = Attribute('host', host, _backend=self._backend)
        a_new_port = Attribute('port', port, _backend=self._backend)
        a_new_nonce = Attribute('nonce', nonce, _backend=self._backend)
        o_new_socket = Object('socket', [a_new_host, a_new_port, a_new_nonce],
                         _backend=self._backend)
        
        old_host = self.data['socket'][0]['host'][0]
        old_port = self.data['socket'][0]['port'][0]
        old_nonce = self.data['socket'][0]['nonce'][0]

        a_old_host = Attribute('host', old_host, _backend=self._backend)
        a_old_port = Attribute('port', old_port, _backend=self._backend)
        a_old_nonce = Attribute('nonce', old_nonce, _backend=self._backend)
        o_old_socket = Object('socket', [a_old_host, a_old_port, a_old_nonce],
                         _backend=self._backend)

        if o_new_socket._hash != o_old_socket._hash:
            self.replace_instance(o_old_socket, o_new_socket)

##    def setstatus(self, status):
##        """
##        Set status of this query.
##
##        Parameters
##        ----------
##        status : {"wait", "processing", "ready"}            
##        """
##        
##        if status not in ('wait', 'processing', 'ready'):
##            raise ValueError(f"status: {status}")
##
##        a_new_status = Attribute('status', status, _backend=self._backend)
##        
##        old_status = self.data['status'][0]
##        a_old_status = Attribute('status', old_status, _backend=self._backend)
##
##        if a_new_status._hash != a_old_status._hash:
##            self.replace_instance(a_old_status, a_new_status)




