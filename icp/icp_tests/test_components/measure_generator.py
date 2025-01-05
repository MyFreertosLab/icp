import numpy as np
import struct
import time
from icp.utils.constants import TOPICS, FORMATS, MPUMessageType


# Measure Generator Utility
class MeasureGenerator:
    def __init__(self, frequency=500):
        self.frequency = frequency
        self.position = np.array([0.0, 0.0, 1.0])  # Default aligned with Z-axis
        self.position_mag = np.array([18.817428588867188, 39.208831787109375, 10.782428741455078])  # Default aligned with Z-axis
        self.temp_mean = 27.0
        self.temp_var = 0.3

    def generate_accel_gyro(self):
        noise = np.random.normal(0, 1, 3)
        accel = self.position + noise
        gyro = np.random.normal(0, 1, 3)  # Gyroscope at rest
        temp = np.random.normal(self.temp_mean, self.temp_var)
        return accel, gyro, temp

    def generate_magnet(self):
        noise = np.random.normal(0, 1, 3)
        magnetic_field = self.position_mag + noise  # Simplified simulation
        return magnetic_field

    def generate_measurements(self):
        timestamp = int(time.time())

        # Generate IMU data
        accel, gyro, temp_accel = self.generate_accel_gyro()
        imu_payload = struct.pack(
            FORMATS[MPUMessageType.IMU],  # Tipo messaggio, timestamp, accel[3], gyro[3], temp
            MPUMessageType.IMU.value,
            timestamp,
            *accel,
            *gyro,
            temp_accel
        )

            # Generate Magnetometer data
        magnetic_field = self.generate_magnet()
        magneto_payload = struct.pack(
            FORMATS[MPUMessageType.MAGNETO],  # Tipo messaggio, timestamp, magneto[3]
            MPUMessageType.MAGNETO.value,
            timestamp,
            *magnetic_field
        )

        # Yield IMU data
        yield TOPICS["mpu_measures"], imu_payload

        # Yield Magnetometer data
        yield TOPICS["mpu_measures"], magneto_payload

