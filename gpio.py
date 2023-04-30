import RPi.GPIO as GPIO
import datetime
import sys
import utils

event_last_time = 0


def add_sound_event():
    global event_last_time
    event_last_time = datetime.datetime.now().timestamp()


RECURRING_TIME_PERIOD = 120


def is_recurring_sound_event(timestamp):
    if timestamp - event_last_time < RECURRING_TIME_PERIOD:
        return True
    else:
        return False


last_image_time = datetime.datetime.now().timestamp()


def send_notification(message):
    global last_image_time
    dt = datetime.datetime.now()
    time_now = dt.timestamp()
    message = dt.strftime("%A, %d. %B %Y %I:%M:%S:%f%p") + " " + message
    if time_now - last_image_time > 2:
        utils.send_telegram(botHandler=botHandler, chat_id=chat_id, message=message, image=True)
        last_image_time = time_now


def add_to_log(message):
    dt = datetime.datetime.now()
    print(dt.strftime("%A, %d. %B %Y %I:%M:%S:%f%p") + " " + message + '\n', file=sys.stdout, flush=True)


sound_last_time = None


def sound_callback(pin):
    '''
    Send a warning if a sound is detected
    '''
    if not sound_on:
        return
    global sound_last_time
    if sound_last_time is None:
        sound_last_time = datetime.datetime.now().timestamp()
        message = "sound detected"
        add_to_log(message)
        # only send a warning if sound event is recurring
        is_notify = is_recurring_sound_event(sound_last_time)
        add_sound_event()
        if is_notify:
            send_notification(message)
    else:
        # only send a warning if at least two seconds have passed
        time_passed = datetime.datetime.now().timestamp() - sound_last_time
        if time_passed > 2:
            sound_last_time = None


def pir_callback(pin):
    '''
    Send a warning if movement is detected
    '''
    if not move_on:
        return
    message = pin_dict[pin] + ", movement detected"
    add_to_log(message)
    send_notification(message)


botHandler = None
chat_id = 0
# raspberry pins that movement and sound gauges are connected to
pin_back = 23
pin_f1 = 27
pin_f2 = 22
pin_any = 16
pin_sound = 17
pin_dict = {pin_f1: "forward 1 pir",
            pin_f2: "forward 2 pir",
            pin_back: "back pir",
            pin_any: "test pin"
            }


def start(bot, chatid):
    '''
    Activate movement and sound pins
    '''
    global botHandler
    global chat_id

    botHandler = bot

    GPIO.setmode(GPIO.BCM)
    chat_id = chatid

    for pin in [pin_f2, pin_back, pin_sound]:  # [pin_f2, pin_back, pin_sound]:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(pin, GPIO.BOTH)

    for pin in [pin_f2, pin_back]:
        GPIO.add_event_callback(pin, pir_callback)

    GPIO.add_event_callback(pin_sound, sound_callback)


move_on = True
sound_on = True


def set_move_detect(detect=True):
    '''
    Enable movement detection
    '''
    global move_on
    move_on = detect


def set_sound_detect(detect=True):
    '''
    Enable sound detection
    '''
    global sound_on
    sound_on = detect
