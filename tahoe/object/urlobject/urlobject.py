# if __name__ in ["__main__", "urlobject"]:
#     import sys, os
#     sys.path.append("..")
#     from instance import Attribute, Object
#     from misc import features
#     from feature import *   
# else:

# I changed some pathing up here for testing reasons, there should be no problem after reverting back to previous
# import pathing

import sys, os
sys.path.append('/home/goofygooby/Project_and_work/All Programming material/Cybex/tahoe_TVAPI/tahoe/tahoe/')



from attribute.attribute import Attribute
from object import Object
from misc import features
from vt_py import vt
from vt_api_key import API_key as APIK

 
import copy, pdb, hashlib

    
_MAX_ENRICHMENT_ATTEMPT = 3

class UrlObject(Object):
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
        # call virus total api with the url
        # get the score
        # make an attribute out of the score
        # store the score using self.add_instance()
        """
        Current Base implementation of url object Total Virus enrichment, Establishes a
        client connection with the VT API and pulls the malicious score. The malicious 
        score is essentially a representation of how many security engines have scanned
        and deemed the URL object as "malicious." That 'malcicious score out of however
        many security engines' is turned into an attribute and stored in the Tahoe backend.

        E.G: 'http://formacao.org.br/wx.htm', a phishing URL
            Malicious score = 13
            Total engines that have scanned it = 53

            so an attribute would be like this -> Attribute('Virus_total', 13/53)

        Note: Potential extra enrinchment factors include: the targeted brand(s), the 
        vt community reputation score, suscipicious score (for more forensic information)

        """
        if not self.should_enrich('virustotal') : return

        #the number of security engines and systems
        total_engines = 0

        # Create client-side connection to the VT API
        tahoe_VTAPI_query = vt.Client(APIK)
        
        # Create a url_id token with the url_objects provided URL
        # provided URL to scan goes here
        VT_url_id = vt.url_id(self.data['url'])
        
        # This is the where the actual query is made so the the VT API
        url_stats = tahoe_VTAPI_query.get_object("/urls/{}",VT_url_id)

        malicious_score = url_stats.last_analysis_stats["malicious"]

        for key, value in url.last_analysis_stats.items():
            total_engines += int(value)

        malicious_and_total_score = str(malicious_score) + "/" + str(total_engines)


        tahoe_VTAPI_query.close()

        # some extra code that pulls other information from the API query, more
        """
        targeted_brands = url.targeted_brand
        vt_reputation = url.reputation
        suspicious_score = url.last_analysis_stats["suspicious"]
        """

        VT_attr = Attribute('Virus_Total', malicious_and_total_score)

        self.add_instance(VT_attr, update=True)

        enid = "virustotal"

        self.record_enrichment(endid)


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
                    self._enrichment[enid] >= _MAX_ENRICHMENT_ATTEMPT
    
    def record_enrichment(self, enid):
        assert enid in ['dns', 'geoip', 'host', 'ipwhois', 'lexical', 'whois','virustotal' ], "Invalid enrichment id!"
        
        if not hasattr(self, '_enrichment'): self._enrichment = {enid:1}
        elif not enid in self._enrichment: self._enrichment[enid] = 1
        else: self._enrichment[enid] += 1
        
        self.backend.update_one(
            {"uuid":self.uuid}, { '$inc': { '_enrichment.'+enid : 1} })

    def should_enrich(self, enid):
        return not self.isenriched(enid) and not self.ismaxenrichretry(enid)

