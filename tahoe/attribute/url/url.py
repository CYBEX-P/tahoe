"""
An URL Attribute implements methods to enrich an URL.
"""

if __name__ != 'tahoe.attribute.url.url':
    import sys, os
    J = os.path.join
    sys.path = ['..', J('..','..'), J('..','..','..')] + sys.path
    del J, sys, os

import pdb
import tahoe

# === Global Variables ===

A = tahoe.Attribute
O = tahoe.Object
E = tahoe.Event

_P = {'_id': 0}
"""Default projection for MongoDB queries"""



class URL(A):
    def __init__(self, data, **kwargs):

        if not isinstance(data, str):
            raise TypeError(f"data = {type(data)}, expected 'str'")

        super().__init__('url', data, **kwargs)

    

