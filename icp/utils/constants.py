from enum import Enum

# MQTT Topics
# TOPICS = {
#     "starter_hello": "/imu/calibration/st/hello",
#     "mpu_hello": "/imu/calibration/mpu/hello",
#     "starter_events": "/imu/calibration/st/events",
#     "initializer_calreq": "/imu/calibration/init/calreq",
#     "initializer_events": "/imu/calibration/init/events",
#     "mpu_calres": "/imu/calibration/mpu/calres",
#     "stabilized_events": "/imu/calibration/stb/events",
#     "pe_events": "/imu/calibration/pe/events",
#     "mpu_command": "/imu/calibration/mpu/command",
#     "mpu_measures": "/imu/calibration/mpu/measures",
#     "pe_points": "/imu/calibration/pe/points",
#     "mv_events": "/imu/calibration/mv/events",
#     "fpe_events": "/imu/calibration/fpe/events",
#     "ee_events": "/imu/calibration/ee/events"
# }

# MQTT Topics con formati dei messaggi
TOPICS = {
    "starter_hello": {
        "topic": "/imu/calibration/st/hello",
        "type": "string"  # Tipologia: string
    },
    "mpu_hello": {
        "topic": "/imu/calibration/mpu/hello",
        "type": "string"  # Tipologia: string
    },
    "starter_events": {
        "topic": "/imu/calibration/st/events",
        "type": "json"  # Tipologia: JSON
    },
    "initializer_calreq": {
        "topic": "/imu/calibration/init/calreq",
        "type": "json"  # Tipologia: JSON
    },
    "initializer_events": {
        "topic": "/imu/calibration/init/events",
        "type": "json"  # Tipologia: JSON
    },
    "mpu_calres": {
        "topic": "/imu/calibration/mpu/calres",
        "type": "binary"  # Tipologia: Binary
    },
    "stabilized_events": {
        "topic": "/imu/calibration/stb/events",
        "type": "json"  # Tipologia: JSON
    },
    "pe_events": {
        "topic": "/imu/calibration/pe/events",
        "type": "json"  # Tipologia: JSON
    },
    "mpu_command": {
        "topic": "/imu/calibration/mpu/command",
        "type": "string"
    },
    "mpu_measures": {
        "topic": "/imu/calibration/mpu/measures",
        "type": "binary"  # Tipologia: Binary
    },
    "pe_points": {
        "topic": "/imu/calibration/pe/points",
        "type": "json"  # Tipologia: JSON
    },
    "mv_events": {
        "topic": "/imu/calibration/mv/events",
        "type": "json"  # Tipologia: JSON
    },
    "fpe_events": {
        "topic": "/imu/calibration/fpe/events",
        "type": "json"  # Tipologia: JSON
    },
    "ee_events": {
        "topic": "/imu/calibration/ee/events",
        "type": "json"  # Tipologia: JSON
    }
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

