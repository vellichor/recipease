import test_base

import pytest

from recipease.utils.strings import *

def test_printable_quantity():
  assert "1/2" == printable_qty(0.5)
  assert "3 1/7" == printable_qty(3.14159)
