import paho.mqtt.client as mqtt
import datetime
import json
import sys
from common import DeviceType, Location
import utils
from queue import Queue

temp_queue = Queue()  # indefinite
last_messages = {}  # {id string, (dictionary of message, timestamp)}, to keep track of when device was last seen
on_message = None


def on_connect(client, userdata, flags, rc):
    client.subscribe("+/#")


class OnMessage:
    '''
    Class for message processing from mqtt
    '''
    def __init__(self, devices, bot_token, bot_id, proxies, rpi_location):
        '''

        :param devices: {"0x00158d0002c9ca28" : (DeviceType.TEMPERATURE,"home") }
        '''
        self.devices = devices
        self.bot_token = bot_token
        self.bot_id = bot_id
        self.proxies = proxies
        self.movement_detect = True
        self.rpi_location = rpi_location

    def set_movement(self, flag=True):
        self.movement_detect = flag

    def __call__(self, client, userdata, msg):
        '''
        The method is called when the message arrives
        '''
        now = datetime.datetime.now()
        time = now.strftime('%d-%H:%M')
        try:
            device_id = msg.topic.replace("zigbee2mqtt/", "")
            message = msg.payload.decode('utf-8')
            dic = json.loads(message)
            last_messages[device_id] = (dic, now.timestamp())

            if device_id in self.devices:
                type = self.devices[device_id][0]
                location = self.devices[device_id][1]

                if type == DeviceType.WATER_LEAK:
                    if dic.get("water_leak"):
                        botHandler = utils.BotHandler(self.bot_token, self.proxies)
                        botHandler.send_message(self.bot_id, "water leak at " + location + "\n" + message)

                elif type == DeviceType.MOVEMENT and self.movement_detect:
                    if dic.get("occupancy"):
                        botHandler = utils.BotHandler(self.bot_token, self.proxies)
                        botHandler.send_message(self.bot_id, "movement at " + location + "\n" + message)
                        if self.rpi_location == Location.DACHA_ZIG:
                            utils.send_telegram(botHandler=botHandler, chat_id=self.bot_id, message="", image=True)

                elif type == DeviceType.TEMPERATURE:
                    temp_queue.put((location, time + " " + message))

        except Exception as e:
            print(time, "exception", e, "message=", msg.payload.decode('utf-8'), file=sys.stdout, flush=True)


def get_battery(id, time_back=3600 * 24):
    ts_now = datetime.datetime.now().timestamp()
    res = last_messages.get(id)
    if res is None:
        return None
    dic, ts = res
    if ts + time_back > ts_now:
        battery = dic.get("battery")
        if battery is None:
            return -1
        return battery
    else:
        return None


def get_last_messages(devices):
    res = ""
    for device_id, v in last_messages.items():
        message, timestamp = v
        dt = datetime.datetime.fromtimestamp(timestamp)
        time = dt.strftime('%d-%H:%M')
        dev_t = devices.get(device_id)
        if dev_t is not None:
            s = time + " " + dev_t[1] + " " + json.dumps(message) + "\n"
            res += s
    return res


def get_temp(device):
    for device_id, v in last_messages.items():
        if device == device_id:
            message, timestamp = v
            return message.get("temperature")


def set_movement(flag=True):
    on_message.set_movement(flag)


def zig_start(devices, bot_token, bot_id, proxies, rpi_location):
    '''

    :param devices: {"0x00158d0002c9ca28" : (DeviceType.TEMPERATURE,"home") }
    :return:
    '''
    client = mqtt.Client()
    client.connect("localhost", 1883, 5)

    client.on_connect = on_connect
    global on_message
    on_message = OnMessage(devices, bot_token, bot_id, proxies, rpi_location)
    client.on_message = on_message
    client.loop_start()
