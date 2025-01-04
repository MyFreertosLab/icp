# Test for Measure Generator
import pytest
from icp.utils.measure_generator import MeasureGenerator

def test_measure_generator():
    generator = MeasureGenerator()
    data = generator.generate()
    assert len(data) == 3

