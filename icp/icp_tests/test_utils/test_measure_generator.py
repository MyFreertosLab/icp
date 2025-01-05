# Test for Measure Generator
import pytest
from icp.icp_tests.test_components.measure_generator import MeasureGenerator

def test_measure_generator():
    generator = MeasureGenerator()
    generator.running = True
    iteration_limit = 10  # Limita il numero di iterazioni
    count = 0

    for payload in generator.generate_measurements():
        count += 1
        if count >= iteration_limit:
            generator.running = False

