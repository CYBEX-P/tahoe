import json
from collections import defaultdict

def dtresolve(start , end) -> dict:
  d = defaultdict(dict)
  if start: d['timestamp']['$gte'] = start
  if end: d['timestamp']['$lte'] = end
  return dict(d)
    
def limitskip(limit=10, skip=0, page=1):
  if page>1: skip = (page-1)*limit
  return {'limit': max(limit,10), 'skip':max(skip,0)}
    
def branches(d):
  def branch(val, old=[]):
    b = []
    if isinstance(val, dict):
        for k in val: b += branch(val[k], old+[str(k)])
    elif isinstance(val, list):
        for k in val: b += branch(k, old)
    else:
        b.append(old + [val])
    return b

  return branch(d)

def features(d, sub_type=None, data=None, sep='.', root_only=False):
  brn = branches(d)
  r = defaultdict(list)
  for b in brn:
    if (sub_type and data) and not (b[-2]==sub_type and b[-1]==data): continue
    k, v = b[:-1], b[-1]
    if root_only:
      r[sep.join(k)].append(v)
    else:
      for i in range(len(k)):
        r[sep.join(k[-i:])].append(v)
  return {k : list(set(v)) for k,v in r.items()} 


def canonical(val):
  '''same as json.dumps(, sort_keys=True)
  but lists are also sorted'''
  if isinstance(val, dict):
    r = {k : canonical(v) for k,v in val.items()}
    val = json.dumps(r, sort_keys=True)
  elif isinstance(val, list):
    r = [canonical(i) for i in val]
    val = json.dumps(sorted(list(set(r))), sort_keys=True)
  elif isinstance(val, str):
    val = json.dumps(val.strip())
  else:
    val = json.dumps(val)
  return val


def decanonical(s):
  '''canonical string to python dict'''
  try:
    d = json.loads(s)
    if isinstance(d, dict):
      for k,v in d.items():
        d[k] = decanonical(v)
    elif isinstance(d, list):
      d = [decanonical(i) for i in d]
  except:
    d = s
  return d



##def canonicalize(val):
##    if isinstance(val, dict):
##        r = {k : canonicalize(v) for k,v in val.items()}
##        return str(dict(sorted(r.items())))
##    elif isinstance(val, list):
##        r = [canonicalize(i) for i in val]
##        return str(sorted(list(set(r))))
##    elif isinstance(val, str):
##        val = val.strip()
##    return(str(val))
