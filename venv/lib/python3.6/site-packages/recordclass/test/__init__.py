# {{LICENCE}}

from recordclass.test.test_record import *
from recordclass.test.test_memoryslots import *


import sys
_PY36 = sys.version_info[:2] >= (3, 6)

if _PY36:
    from recordclass.test.typing.test_typing import *

def test_all():
    import unittest
    unittest.main(verbosity=2)
