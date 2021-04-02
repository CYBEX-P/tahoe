"""
An URLObject stores information related to an URL attribute.
"""

if __name__ != 'tahoe.object.URLObject.URLObject':
    import sys, os
    J = os.path.join
    sys.path = ['..', J('..','..'), J('..','..','..')] + sys.path
    del J, sys, os

import pdb
import tahoe

# === Global Variables ===

A = tahoe.Attribute
O = tahoe.Object
_P = {'_id': 0}
"""Default projection for MongoDB queries"""
_MAX_ENRICH_TRY = 3

class URLObject(tahoe.Object):
    """
    An URLObject stores information related to an URL attribute.

    Attributes
    ----------
    itype : str
        Constant value `object`. (Automatically set)
    sub_type : str
        Constant value `url`. (Automatically set)
    data : dict (json object)
        Data of the object. Dict is JSON object. So keys are `str`.
        Values are `int/float/str/bool/None/list/dict`. Example::
        
            "data" : {
                "ipv4" : ["5.188.86.172"],
                "geoip" : [
                    {
                        "continent_code" : ["EU"],
                        "timezone" : ["Europe/Dublin"],
                        "country_name" : ["Ireland"],
                        "ip" : ["5.188.86.172"],
                        "longitude" : [-8.95],
                        "city_name" : ["Macroom"],
                        "region_code" : ["CO"],
                        "latitude" : [51.9],
                        "region_name" : ["County Cork"]
                    }
                ]
            }

        Note that `data` attribute is a dict whereas `data` parameter
        of `__init__` is a `list`. See `Object.__init__()` for more.    
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
        

    Examples
    --------
    Creating an `Object` with `NoBackend`::

        >>> a1 = Attribute("att_type", "value")
        >>> o1 = Object("obj_type", a1)
        >>> o1.data
        {'att_type': ['value']}
        >>> o1._backend
        NoBackend()
        >>> o1._hash
        'a730521ee3b1f3665f25634de1421942d52119b58bf68498cd2
        beba8d73925be'

    More examples in :ref:`tahoe.tests.object.object_test`

    Notes
    -----
    An object's `_backend` can be set in 3 ways:

    1. `Instance._backend = backend` (recommended)
    2. `Object._backend = backend` (not recommended)
    3. `O = Object("file", [a], _backend=backend)` (not recommended)

    Never use 2. Use 3 only if you want a different `_backend` than the
    default class `_backend`.


    Warning
    -------
    DO NOT change the value for any field. e.g.::
    
        o.data["ipv4"][0] = "2.2.2.2"
        o.data = {"ipv4": ["2.2.2.2"]}
        o._ref.append("af2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e989156
        2113d8a62add1bf")

    The behavior is undefined.
 
    """
    
    def __init__(self, data, **kwargs):
        """
        Parameters
        ----------
        data : str
            The URL.
        *kwargs : dict
            keyword arguments, see *Other Parameters*.

        Other Parameters
        ----------------
        _backend : tahoe.backend.Backend, default=cls._backend
            If given the instance `_backend` will be different from
            class `_backend`. Please lookup *Python Class and Instance
            Variables* if you don't know the difference. You shouldn't
            use this parameter for normal operation. Rather Set class
            backend like `Instance._backend = backend`.

        Raises
        ------
        TypeError
            If data is not `str`.
        """

        if not isinstance(data, str):
            raise TypeError(f"data = {type(data)}, expected 'str'")
        
        au = A('url', data, **kwargs)

        super().__init__(sub_type='url', data=[au], **kwargs)

    

    # Public methods

    def enrich_dns(self, force=False):
        if not self.should_enrich('dns'): return
        
        self.enrich_host()

        dns_att = get_dns_att(self.data['host_attributes'][0]['host'][0])
        dns_obj = Object('dns_attributes', dns_att)
        self.add_instance(dns_obj, update=True)

        enid = 'dns'
        self.record_enrichment(enid)

    def enrich_geoip(self):
        if not self.should_enrich('geoip'): return
        
        self.enrich_host()

        geoip_att = get_geoip_att(self.data['host_attributes'][0]['ip'][0])
        geoip_obj = Object('geoip_attributes', geoip_att)
        self.add_instance(geoip_obj, update=True)

        enid = 'geoip'
        self.record_enrichment(enid)

    def enrich_host(self):
        if not self.should_enrich('host'): return
        
        host_att = get_host_att(self.data['url'][0])
        ip_obj = Object('host_attributes', host_att)
        self.add_instance(ip_obj, update=True)

        enid = 'host'
        self.record_enrichment(enid)

    def enrich_ipwhois(self):
        if not self.should_enrich('ipwhois'): return
        
        self.enrich_host()

        ipwhois_att = get_ipwhois_att(self.data['host_attributes'][0]['ip'][0])
        ipwhois_obj = Object('ipwhois_attributes', ipwhois_att)
        self.add_instance(ipwhois_obj, update=True)

        enid = 'ipwhois'
        self.record_enrichment(enid)

    def enrich_lexical(self):
        if not self.should_enrich('lexical'): return
        
        lex_att = get_lexical_att(self.data['url'][0])
        lex_obj = Object('lexical_attributes', lex_att)
        self.add_instance(lex_obj, update=True)

        enid = 'lexical'
        self.record_enrichment(enid)

    def enrich_ngram(self):
        if not self.should_enrich('ngram'): return

        ngram_att = get_ngram_att(self.data['url'][0])
        ngram_obj = Object('ngram_attributes', ngram_att)
        self.add_instance(ngram_obj, update=True)

        enid = 'ngram'
        self.record_enrichment(enid)

    def enrich_virustotal(self):
        return NotImplemented
        # call virus total api with the url
        # get the score
        # make an attribute out of the score
        # store the score using self.add_instance()

    def enrich_whois(self):
        if not self.should_enrich('whois'): return
        
        self.enrich_host()

        whois_att = get_whois_att(self.data['host_attributes'][0]['host'][0])
        whois_obj = Object('whois_attributes', whois_att)
        self.add_instance(whois_obj, update=True)

        enid = 'whois'
        self.record_enrichment(enid)
        
    def feature_vector(self):
        d = copy.deepcopy(self.data)
        
        m = d.pop('malicious')[0]
        u = d.pop('url')[0]
        s = d.pop('source')[0]        
        
        of = features(d, sep='_', root_only=True)
        
        if len(of) != 142: raise RuntimeError('Enrichment not complete')
        
        f = sorted([ [k,v[0]] for k,v in of.items()])
        
        for j in range(len(f)):
            k = f[j][0]
            v = f[j][1]
            
            if isinstance(v, float):
                f[j][1] = round(v, 3)
            
            if not isinstance(v, str): continue
            if not v: continue
            
            v = v.lower().strip().replace('.','')
            v = hashlib.md5(v.encode('utf-8')).hexdigest()
                      
            p = {"itype": k, "sub_type" : v, "tag":"feature_code"}
            r = self.backend.find_one(p)
            
            if r:
                code = r['data']
            else:
                pmax = {"itype": k, "sub_type" : "max_code", "tag":"feature_code"}
                r = self.backend.find_one(pmax)
                
                if not r:
                    code = 1
                    self.backend.insert_one({'data':code, **pmax})
                    self.backend.insert_one({'data':code, **p})
                else:
                    code = r['data'] + 1
                    self.backend.update_one(pmax, {'$set' : {'data':code}})
                    self.backend.insert_one({'data':code, **p})
                
            f[j][1] = code

        
        f = [v for (k,v) in f]
        f = [-1 if not v else v for v in f]
        
        return f
        
    def isenriched(self, enid):
        if enid == 'dns':
            return 'dns_attributes' in self.data \
                   and self.data['dns_attributes'][0]['dns_ttl'][0] != None
        
        if enid == 'host':
            return 'host_attributes' in self.data \
                   and self.data['host_attributes'][0]['ip'][0] != None
        
        if enid == 'whois':
            return 'whois_attributes' in self.data and \
                   self.data['whois_attributes'][0]['days_creation'][0] != None
            
        return hasattr(self, '_enrichment') and enid in self._enrichment

    def ismaxenrichretry(self, enid):
            return hasattr(self, '_enrichment') and enid in self._enrichment and \
                    self._enrichment[enid] >= _MAX_ENRICH_TRY
    
    def record_enrichment(self, enid):
        assert enid in ['dns', 'geoip', 'host', 'ipwhois', 'lexical', 'whois', ], "Invalid enrichment id!"
        
        if not hasattr(self, '_enrichment'): self._enrichment = {enid:1}
        elif not enid in self._enrichment: self._enrichment[enid] = 1
        else: self._enrichment[enid] += 1
        
        self.backend.update_one(
            {"uuid":self.uuid}, { '$inc': { '_enrichment.'+enid : 1} })

    def should_enrich(self, enid):
        return not self.isenriched(enid) and not self.ismaxenrichretry(enid)

    # protected or private methods
    
    @property                 
    def _unique(self):
        unique = self.itype + self.sub_type + self.data['url'][0]
        return unique.encode('utf-8')





























if __name__ in ["__main__", "URLObject"]:
    import sys
    sys.path.append("..")
    from instance import Attribute, Object
    from misc import features
    from feature import *   
else: 
    from ..instance import Attribute, Object
    from ..misc import features
    from .feature import *

 
import copy, pdb, hashlib 
    


class URLObject(Object):
    def __init__(self, url_data, malicious=None, source=None, **kwargs):
        if isinstance(url_data, str):
            h = url_data.lower()
            h = h[:4]
            assert h == 'http', 'Valid URL must begin with http'
            url_data = Attribute('url', url_data, **kwargs)

        assert malicious in [True, False, None], "malicious must be True/False/None!"
        ma = Attribute('malicious', malicious)

        assert source==None or isinstance(source, str), "source must be None or str!"
        sa = Attribute('source', source)

        super().__init__(sub_type='url', data=[url_data, ma, sa], **kwargs)
                 
    def unique(self):
        unique = self.itype + self.sub_type + self.data['url'][0]
        return unique.encode('utf-8')

    def enrich_dns(self):
        if not self.should_enrich('dns'): return
        
        self.enrich_host()

        dns_att = get_dns_att(self.data['host_attributes'][0]['host'][0])
        dns_obj = Object('dns_attributes', dns_att)
        self.add_instance(dns_obj, update=True)

        enid = 'dns'
        self.record_enrichment(enid)

    def enrich_geoip(self):
        if not self.should_enrich('geoip'): return
        
        self.enrich_host()

        geoip_att = get_geoip_att(self.data['host_attributes'][0]['ip'][0])
        geoip_obj = Object('geoip_attributes', geoip_att)
        self.add_instance(geoip_obj, update=True)

        enid = 'geoip'
        self.record_enrichment(enid)

    def enrich_host(self):
        if not self.should_enrich('host'): return
        
        host_att = get_host_att(self.data['url'][0])
        ip_obj = Object('host_attributes', host_att)
        self.add_instance(ip_obj, update=True)

        enid = 'host'
        self.record_enrichment(enid)

    def enrich_ipwhois(self):
        if not self.should_enrich('ipwhois'): return
        
        self.enrich_host()

        ipwhois_att = get_ipwhois_att(self.data['host_attributes'][0]['ip'][0])
        ipwhois_obj = Object('ipwhois_attributes', ipwhois_att)
        self.add_instance(ipwhois_obj, update=True)

        enid = 'ipwhois'
        self.record_enrichment(enid)

    def enrich_lexical(self):
        if not self.should_enrich('lexical'): return
        
        lex_att = get_lexical_att(self.data['url'][0])
        lex_obj = Object('lexical_attributes', lex_att)
        self.add_instance(lex_obj, update=True)

        enid = 'lexical'
        self.record_enrichment(enid)

    def enrich_ngram(self):
        if not self.should_enrich('ngram'): return

        ngram_att = get_ngram_att(self.data['url'][0])
        ngram_obj = Object('ngram_attributes', ngram_att)
        self.add_instance(ngram_obj, update=True)

        enid = 'ngram'
        self.record_enrichment(enid)

    def enrich_virustotal(self):
        return NotImplemented
        # call virus total api with the url
        # get the score
        # make an attribute out of the score
        # store the score using self.add_instance()

    def enrich_whois(self):
        if not self.should_enrich('whois'): return
        
        self.enrich_host()

        whois_att = get_whois_att(self.data['host_attributes'][0]['host'][0])
        whois_obj = Object('whois_attributes', whois_att)
        self.add_instance(whois_obj, update=True)

        enid = 'whois'
        self.record_enrichment(enid)
        
    def feature_vector(self):
        d = copy.deepcopy(self.data)
        
        m = d.pop('malicious')[0]
        u = d.pop('url')[0]
        s = d.pop('source')[0]        
        
        of = features(d, sep='_', root_only=True)
        
        if len(of) != 142: raise RuntimeError('Enrichment not complete')
        
        f = sorted([ [k,v[0]] for k,v in of.items()])
        
        for j in range(len(f)):
            k = f[j][0]
            v = f[j][1]
            
            if isinstance(v, float):
                f[j][1] = round(v, 3)
            
            if not isinstance(v, str): continue
            if not v: continue
            
            v = v.lower().strip().replace('.','')
            v = hashlib.md5(v.encode('utf-8')).hexdigest()
                      
            p = {"itype": k, "sub_type" : v, "tag":"feature_code"}
            r = self.backend.find_one(p)
            
            if r:
                code = r['data']
            else:
                pmax = {"itype": k, "sub_type" : "max_code", "tag":"feature_code"}
                r = self.backend.find_one(pmax)
                
                if not r:
                    code = 1
                    self.backend.insert_one({'data':code, **pmax})
                    self.backend.insert_one({'data':code, **p})
                else:
                    code = r['data'] + 1
                    self.backend.update_one(pmax, {'$set' : {'data':code}})
                    self.backend.insert_one({'data':code, **p})
                
            f[j][1] = code

        
        f = [v for (k,v) in f]
        f = [-1 if not v else v for v in f]
        
        return f
        
    def isenriched(self, enid):
        if enid == 'dns':
            return 'dns_attributes' in self.data \
                   and self.data['dns_attributes'][0]['dns_ttl'][0] != None
        
        if enid == 'host':
            return 'host_attributes' in self.data \
                   and self.data['host_attributes'][0]['ip'][0] != None
        
        if enid == 'whois':
            return 'whois_attributes' in self.data and \
                   self.data['whois_attributes'][0]['days_creation'][0] != None
            
        return hasattr(self, '_enrichment') and enid in self._enrichment

    def ismaxenrichretry(self, enid):
            return hasattr(self, '_enrichment') and enid in self._enrichment and \
                    self._enrichment[enid] >= _MAX_ENRICH_TRY
    
    def record_enrichment(self, enid):
        assert enid in ['dns', 'geoip', 'host', 'ipwhois', 'lexical', 'whois', ], "Invalid enrichment id!"
        
        if not hasattr(self, '_enrichment'): self._enrichment = {enid:1}
        elif not enid in self._enrichment: self._enrichment[enid] = 1
        else: self._enrichment[enid] += 1
        
        self.backend.update_one(
            {"uuid":self.uuid}, { '$inc': { '_enrichment.'+enid : 1} })

    def should_enrich(self, enid):
        return not self.isenriched(enid) and not self.ismaxenrichretry(enid)

