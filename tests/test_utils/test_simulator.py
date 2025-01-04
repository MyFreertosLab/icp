# Test for Simulator
import pytest
from icp.utils.simulator import Simulator

def test_simulator():
    simulator = Simulator()
    assert simulator is not None

