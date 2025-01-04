# Test for Point Estimation Component
import pytest
from icp.components.point_estimation import PointEstimation

def test_point_estimation():
    point_estimation = PointEstimation(None)
    assert point_estimation is not None

