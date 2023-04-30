from common import DeviceType

TOKEN = 'TELEGRAM_TOKEN_HERE'
proxies = None #{'https': "socks5://localhost:5432"}
MYID = 111111111 # CHAT_ID_HERE
devices = {
        "0x00158d0002b44a2e": (DeviceType.MOVEMENT, "dacha_m kitchen"),
        "0x00158d0002b4755e": (DeviceType.MOVEMENT, "dacha_m ladder"),
        "0x00158d00025f03dd": (DeviceType.TEMPERATURE, "dacha_t 1"),
        "0x00158d0002c9ca28": (DeviceType.TEMPERATURE, "dacha_t 2"),
        "0x00158d0002774f1e": (DeviceType.WATER_LEAK, "dacha_w 1"),
        "0x00158d000233bd2e": (DeviceType.WATER_LEAK, "dacha_w 2"),
}
TEMP1_ID = "0x00158d00025f03dd"
TEMP2_ID = "0x00158d0002c9ca28"
