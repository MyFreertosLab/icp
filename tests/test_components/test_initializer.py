# Test for Initializer Component
import pytest
from icp.components.initializer import Initializer

def test_initializer():
    initializer = Initializer(None)
    assert initializer is not None

