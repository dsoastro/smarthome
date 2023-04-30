import datetime
import os
import sys
import requests
import subprocess
from config_base import ONE_WIRE_PATH1,ONE_WIRE_PATH2,HTTP_IMAGE_URL


def add_to_log(message, path):
    dt = datetime.datetime.now()
    with open(path, 'a') as f:
        f.write(dt.strftime("%A, %d. %B %Y %I:%M:%S:%f%p") + " " + message + '\n')


def run_subprocess(params=[], shell=False):
    '''
    Run subprocess and catch errors

    :param params: e.g. (["/usr/bin/gammu", "getallsms"]
    '''
    try:
        text = subprocess.check_output(params, shell=shell).decode("utf-8")
        return text
    except Exception as e:
        print(e, file=sys.stdout, flush=True)
        return None


def read_temp(num):
    '''
    Return temperature from 1-wire temperature sensors
    '''
    path = ONE_WIRE_PATH1
    if num == 2:
        path = ONE_WIRE_PATH2
    try:
        with open(path, "r") as f:
            line = next(f)
            line = next(f)

            pos = line.find("t=")
            if pos != -1:
                return line[pos + 2:].replace("\n", "")
            return None
    except:
        return None


def read_cpu_temp():
    '''
    Return raspberry cpu temperature
    '''
    PATH = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(PATH, "r") as f:
            return f.read()
    except:
        return ""


def send_telegram(botHandler, chat_id, message="", image=False, send_message=True):
    dt = datetime.datetime.now()
    time_now = dt.timestamp()
    message = dt.strftime("%A, %d. %B %Y %I:%M:%S:%f%p") + " " + message
    if image:
        command = '(cd; rm jpeg.cgi; rm image.jpg; wget {} --user=admin --password=""'.format(HTTP_IMAGE_URL) + '; mv jpeg.cgi image.jpg)'
        os.system(command)
        if send_message:
            botHandler.send_message(chat_id, message)
        botHandler.send_image("/home/pi/image.jpg", chat_id)
    elif send_message:
        botHandler.send_message(chat_id, message)


def get_time_now():
    dt = datetime.datetime.now()
    time_now = dt.timestamp()
    return dt.strftime("%A, %d. %B %Y %I:%M:%S:%f%p")


class BotHandler:

    def __init__(self, token, proxies):
        self.token = token
        self.proxies = proxies
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        try:
            resp = requests.get(self.api_url + method, params, proxies=self.proxies, timeout=60)
            result_json = resp.json()['result']
        except Exception as e:
            return None

        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': str(chat_id), 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params, proxies=self.proxies)
        return resp

    def send_image(self, imagefile, chat_id):
        command = 'curl -s -X POST https://api.telegram.org/bot' + self.token + '/sendPhoto -F chat_id=' + str(
            chat_id) + " -F photo=@" + imagefile
        os.system(command)
        return

    def get_last_update(self, offset):
        get_result = self.get_updates(offset)
        if get_result is None:
            return None
        if len(get_result) > 0:
            get_result = get_result[-1]
        return get_result
