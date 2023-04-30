from enum import Enum

LOCATION_HOME = "home"
LOCATION_DACHA_BASE = "dacha"
LOCATION_DACHA_ZIG = "dacha_zig"

class Location(Enum):
    HOME = 1
    DACHA_BASE = 2
    DACHA_ZIG = 3

class DeviceType(Enum):
    TEMPERATURE = 1
    MOVEMENT = 2
    WATER_LEAK = 3

    def name(type):
        if type == DeviceType.TEMPERATURE:
            return "temperature"
        elif type == DeviceType.MOVEMENT:
            return "movement"
        elif type == DeviceType.WATER_LEAK:
            return "water_gauge"


