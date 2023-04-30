from common import DeviceType

TOKEN = 'TELEGRAM_TOKEN_HERE'
proxies = None #{'https': "socks5://localhost:5432"}
MYID = 111111111 # CHAT_ID_HERE

devices = {
        "0x00158d0002e29bd8": (DeviceType.MOVEMENT, "home_m"),
        "0x00158d0002335101": (DeviceType.WATER_LEAK, "vanna"),
        "0x00158d00027abb77": (DeviceType.WATER_LEAK, "kitchen sink"),
        "0x00158d0002336863": (DeviceType.WATER_LEAK, "blue vanna"),
        "0x00158d000233b524": (DeviceType.WATER_LEAK, "kitchen radiator"),
        "0x00158d00027ac180": (DeviceType.WATER_LEAK, "living room radiator"),
        "0x00158d000271bafb": (DeviceType.WATER_LEAK, "bedroom radiator")
    }