# Test for Starter Component
import pytest
from icp.components.starter import Starter
from icp.utils.constants import TOPICS

def test_starter():
    starter = Starter(None)
    assert starter is not None

