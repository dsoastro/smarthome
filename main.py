import utils
import datetime
import time
import traceback
import sys
from common import Location, DeviceType
from config_base import MIN_RADIATOR_TEMP, AUTO_RADIATOR_MEASUREMENT_PERIOD
rpi_location = Location.HOME

if len(sys.argv) > 1:
    rpi_location = sys.argv[1]
    if rpi_location.upper() == "HOME":
        rpi_location = Location.HOME
    elif rpi_location.upper() == "DACHA_BASE":
        rpi_location = Location.DACHA_BASE
    elif rpi_location.upper() == "DACHA_ZIG":
        rpi_location = Location.DACHA_ZIG

if rpi_location == Location.HOME:
    from config_home import TOKEN, MYID, proxies

elif rpi_location == Location.DACHA_BASE:
    from config_base import TOKEN, MYID, proxies
    from gpio import start, set_move_detect, set_sound_detect

elif rpi_location == Location.DACHA_ZIG:
    from config_zig import TOKEN, MYID, proxies, TEMP1_ID, TEMP2_ID

if rpi_location == Location.HOME or rpi_location == Location.DACHA_ZIG:
    from zig import zig_start, get_temp, get_battery, get_last_messages, set_movement

if rpi_location == Location.HOME:
    from config_home import devices

if rpi_location == Location.DACHA_ZIG:
    from config_zig import devices

if rpi_location == Location.HOME or rpi_location == Location.DACHA_ZIG:
    zig_start(devices, TOKEN, MYID, proxies, rpi_location)

botHandler = utils.BotHandler(TOKEN, proxies)
if rpi_location == Location.DACHA_BASE:
    start(botHandler, MYID)


def ptemp(last_chat_id, location=None):
    '''
    Send raspberry pi cpu temperature
    '''
    temp = utils.read_cpu_temp()
    botHandler.send_message(last_chat_id, temp)


def temp(last_chat_id, location=None):
    '''
    Send sensor temperature
    '''
    # non-zigbee temp
    if location == Location.DACHA_BASE:
        out1 = utils.read_temp(1)
        out2 = utils.read_temp(2)
        log("out1=",out1)
        out1 = "" if out1 is None else out1
        out2 = "" if out2 is None else out2
        botHandler.send_message(last_chat_id, out1 + "\n" + out2)
    # zigbee temp
    elif location == Location.DACHA_ZIG:
        log("temp command")
        t1 = get_temp(TEMP1_ID)
        if t1 is None:
            t1 = ""
        else:
            t1 = str(t1)

        t2 = get_temp(TEMP2_ID)
        if t2 is None:
            t2 = ""
        else:
            t2 = str(t2)
        s = t1 + " " + t2
        botHandler.send_message(last_chat_id, s)


def sdcard(last_chat_id, location=None):
    '''
    Send sd card stats
    '''
    with open("/sys/block/mmcblk0/stat", "r") as f:
        text = f.read()
    a = text.split()
    read = int(a[2])
    written = int(a[6])
    log(read, written)
    s = "Uptime read: {:.2f}MiB written: {:.2f}MiB".format(read * 512 / 1048576, written * 512 / 1048576)
    botHandler.send_message(last_chat_id, s)


def speed(last_chat_id, location=None):
    '''
    Send internet speed
    '''
    text = utils.run_subprocess(["/usr/bin/speedtest-cli"])
    if text is not None:
        botHandler.send_message(last_chat_id, text)


def log1(last_chat_id, location=None):
    '''
    Send the last 20 lines of log
    '''
    text = utils.run_subprocess(['/usr/bin/tail', '-20', '/home/pi/log/main_home_log.txt'])
    if text is not None:
        botHandler.send_message(last_chat_id, text)


def cpu(last_chat_id, location=None):
    '''
    Send top 10 process sorted by cpu
    '''
    text = utils.run_subprocess('/bin/ps -eo pcpu,pid,user,args | sort -k 1 -r | head -10 ', shell=True)
    if text is not None:
        botHandler.send_message(last_chat_id, text)


def uptime(last_chat_id, location=None):
    '''
    Send the result of uptime command
    '''
    text = utils.run_subprocess(['/usr/bin/uptime'])
    if text is not None:
        botHandler.send_message(last_chat_id, text)


def battery(last_chat_id, location=None):
    '''
    Send info on battery charge of zigbee devices
    '''
    botHandler.send_message(last_chat_id, get_battery_status())


def last(last_chat_id, location=None):
    '''
    Send last events from zigbee devices
    '''
    botHandler.send_message(last_chat_id, get_last_messages(devices))


def movement_on(last_chat_id, location=Location.HOME):
    '''
    Enable movement sensors
    '''
    # global movement sensor
    if location == Location.DACHA_ZIG or rpi_location == Location.HOME:
        set_movement(True)
    else:
        set_move_detect(True)
    botHandler.send_message(last_chat_id, "movement on")


def sound_on(last_chat_id, location=Location.DACHA_BASE):
    '''
    Enable sound sensor
    '''
    set_sound_detect(True)
    botHandler.send_message(last_chat_id, "sound on")


def sound_off(last_chat_id, location=Location.DACHA_BASE):
    '''
    Disable sound sensor
    '''
    set_sound_detect(False)
    botHandler.send_message(last_chat_id, "sound off")


def movement_off(last_chat_id, location=Location.HOME):
    '''
    Disable movement sensor
    '''
    if location == Location.DACHA_ZIG or rpi_location == Location.HOME:
        set_movement(False)
    else:
        set_move_detect(False)
    botHandler.send_message(last_chat_id, "movement off")


def command_fun(last_chat_id, location=None):
    '''
    Send a list of commands
    '''
    a = []
    for k in commands.keys():
        a.append(k)
    a.sort()
    botHandler.send_message(last_chat_id, "\n".join(a))


def image(last_chat_id, location=None):
    '''
    Send an image from camera
    '''
    utils.send_telegram(botHandler=botHandler, chat_id=last_chat_id, image=True, send_message=False)


commands = {"ptemp": ptemp,
            "temp": temp,
            "speed": speed,
            "log": log1,
            "cpu": cpu,
            "uptime": uptime,
            "battery": battery,
            "commands": command_fun,
            "last": last,
            "moveon": movement_on,
            "moveoff": movement_off,
            "image": image,
            "soundon": sound_on,
            "soundoff": sound_off,
            "sdcard": sdcard
            }

commands_on_location = {"ptemp": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "temp": [Location.DACHA_BASE, Location.DACHA_ZIG],
                        "speed": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "log": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "cpu": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "uptime": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "battery": [Location.HOME, Location.DACHA_ZIG],
                        "commands": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "last": [Location.HOME, Location.DACHA_ZIG],
                        "moveon": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "moveoff": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "soundon": [Location.DACHA_BASE],
                        "soundoff": [Location.DACHA_BASE],
                        "image": [Location.DACHA_BASE, Location.DACHA_ZIG],
                        "sdcard": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "schedule": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        "clearsc": [Location.HOME, Location.DACHA_BASE, Location.DACHA_ZIG],
                        }


def parse_command(text):
    '''


    :param text: string to parse. May be either command or scheduled command,
    e.g. image at 14.53 - send an image at 14.53, image at 53 - send an image at the 53rd minute of the current hour
    :return: (text, None) if no scheduling
             (text, timestamp) with zeroes if the relevant pos is not provided
    '''
    text = text.lower()
    a = text.split()
    if len(a) > 2:
        if a[1] == "at":
            t = a[2].split(".")  # time
            tint = []
            try:
                for item in t:
                    tint.append(int(item))
            except:
                return (text, None)

            tint_out = [-1 for i in range(4)]  # [month, day, hour, min]

            k = 3
            for i in range(len(tint), 0, -1):  # fill tint_out starting from the end
                tint_out[k] = tint[i - 1]
                k -= 1

            now = datetime.datetime.now()

            if tint_out[0] == -1:
                tint_out[0] = now.month
            if tint_out[1] == -1:
                tint_out[1] = now.day
            if tint_out[2] == -1:
                tint_out[2] = now.hour
            if tint_out[3] == -1:
                tint_out[3] = now.minute

            now = now.replace(month=tint_out[0], day=tint_out[1], hour=tint_out[2], minute=tint_out[3])
            return (a[0], now.timestamp())
    return text, None


schedule = dict()  # { timestamp: command }


def add_to_schedule(timestamp, command):
    schedule[timestamp] = command


def timestamp_to_str(ts):
    d = datetime.datetime.fromtimestamp(ts)
    return "{}:{}:{}:{}".format(d.month, d.day, d.hour, d.minute)


def schedule_to_str():
    result = ""
    for t, command in schedule.items():
        result += timestamp_to_str(t) + " " + command + "\n"
    return result


def scheduled_command_to_execute():
    '''
    Check if there is a scheduled command to execute

    :return: one command for which the time has come and remove it from schedule, or None if there is no such command
             format - (command, timestamp)
    '''
    now = datetime.datetime.now()
    ts = now.timestamp()
    min_command = None
    min_t = None
    for t, command in schedule.items():
        if t < ts:  # the time has come
            if (min_command is None or min_t is None) or (t < min_t):
                min_command = command
                min_t = t

    if (min_command is not None) and (min_t is not None):
        schedule.pop(min_t, None)
        return min_command, min_t

    return None


battery_checked = False


def is_battery_check_time(time):
    '''
    Check battery charge of zigbee devices once a day
    :param time: should be datetime.datetime.now()
    :return:
    '''
    global battery_checked
    if time.hour == 15 and time.minute < 15:
        if not battery_checked:
            battery_checked = True
            return True
    if time.hour == 15 and time.minute > 16:
        battery_checked = False
    return False


def check_battery():
    '''
    Send a warning if an zigbee device is powered off
    '''
    for k, v in devices.items():
        battery = get_battery(k)
        log("battery=" + str(battery) + " id=" + k)
        if battery is None:
            type = DeviceType.name(v[0])
            location = v[1]
            botHandler.send_message(MYID, "device '{}' seems to be powered off".format(type + " " + location))


def get_battery_status():
    '''
    Return info on zigbee device battery charge
    '''
    a = []
    b = []
    for k, v in devices.items():
        battery = get_battery(k)
        type = DeviceType.name(v[0])
        location = v[1]
        if battery is not None:
            a.append(type + " " + location + " battery=" + str(battery))
        else:
            b.append("device '{}' seems to be powered off".format(type + " " + location))
    return "\n".join(a) + "\n" + "\n".join(b)


last_temp_measurement_time = 0


def check_radiator_temperature(nowtimestamp, location, last_chat_id):
    '''
    Regular temperature check of radiators on dacha to make sure that boiler is working.
    Send a warning if radiator temperature is below limit
    '''
    if location == Location.HOME:
        return

    global last_temp_measurement_time

    if nowtimestamp - last_temp_measurement_time > AUTO_RADIATOR_MEASUREMENT_PERIOD:

        if location == Location.DACHA_BASE:
            last_temp_measurement_time = nowtimestamp
            out2 = utils.read_temp(2)
            if out2 is not None:
                try:
                    temp = int(out2) / 1000
                    if temp < MIN_RADIATOR_TEMP:
                        botHandler.send_message(last_chat_id, "warning, battery temp=" + out2)
                except:
                    pass
        elif location == Location.DACHA_ZIG:
            last_temp_measurement_time = nowtimestamp
            temp = get_temp(TEMP1_ID)
            if temp is not None and temp < MIN_RADIATOR_TEMP:
                botHandler.send_message(last_chat_id, "warning, battery temp=" + str(temp))


def log(*args):
    now = datetime.datetime.now()
    print(now, *args, file=sys.stdout, flush=True)


def read_telegram():
    '''
    Main cycle. Reading commands from telegram
    '''
    new_offset = None
    while True:
        try:
            now = datetime.datetime.now()
            nowtimestamp = now.timestamp()
            if is_battery_check_time(now) and rpi_location in commands_on_location["battery"]:
                check_battery()

            check_radiator_temperature(nowtimestamp, rpi_location, MYID)

            scheduled_command = scheduled_command_to_execute()
            if scheduled_command is not None:
                command = scheduled_command[0]
                time_str = timestamp_to_str(scheduled_command[1])
                for key in commands.keys():
                    if key in command and rpi_location in commands_on_location[key]:
                        botHandler.send_message(MYID, "execute command scheduled at " + time_str)
                        commands[key](MYID, rpi_location)
                        break

                continue

            last_update = botHandler.get_last_update(new_offset)
            if last_update == []:
                continue
            if last_update is None:
                print(utils.get_time_now(), "last update None", file=sys.stdout, flush=True)
                time.sleep(10)
                continue
            user_id = last_update['message']['from']['id']
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text'].lower()
            last_chat_id = last_update['message']['chat']['id']
            new_offset = last_update_id + 1

            if user_id == MYID:

                command, ts = parse_command(last_chat_text.lower())
                log("main loop, command=", command)
                if ts is None:  # just command without scheduling
                    found = False  # first look for the exact coincidence
                    for key in commands.keys():
                        if key == last_chat_text.lower().strip() and rpi_location in commands_on_location[key]:
                            commands[key](last_chat_id, rpi_location)
                            log("main loop A, command executed", key)
                            found = True
                            break

                    if not found:
                        for key in commands.keys():
                            if key in last_chat_text.lower() and rpi_location in commands_on_location[key]:
                                commands[key](last_chat_id, rpi_location)
                                log("main loop B, command executed", key)
                                break

                else:  # scheduling
                    add_to_schedule(ts, command)
                    botHandler.send_message(last_chat_id, "command " + command + " scheduled at " + \
                                            timestamp_to_str(ts))

        except Exception:
            traceback.print_exc(file=sys.stdout)
            time.sleep(10)


read_telegram()
