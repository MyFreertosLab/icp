# Measure Generator Utility
import numpy as np

class MeasureGenerator:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 1.0])

    def generate(self):
        noise = np.random.normal(0, 1, 3)
        return self.position + noise

