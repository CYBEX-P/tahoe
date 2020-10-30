"""unittests for tahoe.identity.identity"""

import unittest

if __name__ != 'tahoe.tests.identity.test_identity':
    import sys, os
    sys.path = ['..', os.path.join('..', '..'),
                os.path.join('..', '..', '..')] + sys.path
    del sys, os

from tahoe import Instance
from tahoe.identity import Identity
from tahoe.identity.backend import IdentityBackend, MockIdentityBackend
from tahoe.tests.identity.test_backend import IdentityBackendTest


def setUpModule():
    _backend = IdentityBackendTest.setUpClass()
    Instance.set_backend(_backend)

    assert Identity._backend is Instance._backend
    

def tearDownModule():
    IdentityBackendTest.tearDownClass()


class SetBackendTest(unittest.TestCase):
    """
    Examples
    --------
    Correct way of setting default backend::
        
        >>> from tahoe import Instance
        >>> from tahoe.identity import Identity
        >>> _backend = MongoBackend("test_db")
        >>> Instance.set_backend(_backend)
        >>> Instance._backend
        MongoBackend("localhost:27017", "test_db", "instance")
        >>> Identity._backend
        MongoBackend("localhost:27017", "test_db", "instance")

    Wrong way of setting default backend::

        >>> from tahoe import Instance
        >>> from tahoe.identity import Identity
        >>> Identity._backend = MongoBackend()
        >>> Identity._backend
        MongoBackend('localhost:27017', 'tahoe_db', 'instance')
        >>> Instance._backend
        NoBackend()

    """
    def test_backend(self):
        self.assertIs(Identity._backend, Instance._backend)



if __name__ == '__main__':
    unittest.main()

    


