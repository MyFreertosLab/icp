# Test for Starter Component
import pytest
from icp.components.starter import Starter

def test_starter():
    starter = Starter(None)
    assert starter is not None

