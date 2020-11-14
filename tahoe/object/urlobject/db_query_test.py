import sys
from pathlib import Path
# tahoe_path = Path('C:\\Users\\Goofy Goober\\Documents\\All Programming material\\Cybex\\sam docs\\tahoe')
tahoe_path = Path('/home/goofygooby/Project_and_work/All Programming material/Cybex/sam docs/tahoe')
sys.path.append('/home/goofygooby/Project_and_work/All Programming material/Cybex/tahoe_TVAPI/tahoe/tahoe/object/urlobject')
sys.path.insert(1, str(tahoe_path.resolve()))


import tahoe
import uuid
from tahoe import NoBackend, Attribute, parse
from tahoe.identity import IdentityBackend, Identity, User, Org, InputConfig
from tahoe import Instance
from urlobject.urlobject import UrlObject
ident_backend = IdentityBackend(mongo_url='mongodb://localhost', create=False)

Instance._backend =  ident_backend #overrides the base level instance, globally ran

test_case = UrlObject('http://formacao.org.br/wx.htm')

exit()

data = []
new_att = Attribute('seconds_between_fetches', 43200)
data.append(new_att)

InputConfig(
            plugin='openphish', #HTTP GET? adjust to get from  multiple sources
            name="attempt_2",
            typetag='openphish-file-feed',
            orgid=str(uuid.uuid4()),
            timezone='UTC',
            data=data,
            enabled=True,
            _backend=ident_backend #<----- overrides line #14, manual
           )