from enum import Enum

# MQTT Topics
TOPICS = {
    "starter_hello": "/imu/calibration/st/hello",
    "mpu_hello": "/imu/calibration/mpu/hello",
    "starter_events": "/imu/calibration/st/events",
    "initializer_calreq": "/imu/calibration/init/calreq",
    "initializer_events": "/imu/calibration/init/events",
    "mpu_calres": "/imu/calibration/mpu/calres",
    "stabilized_events": "/imu/calibration/stb/events",
    "pe_events": "/imu/calibration/pe/events",
    "mpu_command": "/imu/calibration/mpu/command",
    "mpu_measures": "/imu/calibration/mpu/measures",
    "pe_points": "/imu/calibration/pe/points",
    "mv_events": "/imu/calibration/mv/events",
    "fpe_events": "/imu/calibration/fpe/events",
    "ee_events": "/imu/calibration/ee/events"
}

# Enum per il tipo di messaggio
class MPUMessageType(Enum):
    IMU = 1
    MAGNETO = 2
    MPU9250_CONFIG_DATA = 3
    CALIBRATION_COMMAND = 4
    SENSOR_MODEL = 5

# Formati binari
FORMATS = {
    MPUMessageType.IMU: "II3f3ff",  # uint32_t timestamp, float[3] accel, float[3] gyro, float temp
    MPUMessageType.MAGNETO: "II3f", # uint32_t timestamp, float[3] magneto
    MPUMessageType.MPU9250_CONFIG_DATA: "IIBBBH",  # uint32_t timestamp, 3x uint8, 1x uint16
    MPUMessageType.SENSOR_MODEL: "II60s", # uint32_t timestamp, 60 bytes blob
}

