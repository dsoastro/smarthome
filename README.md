# Smarthome (example of custom-made home monitoring solution)

A python telegram bot to monitor country house (_dacha_) temperature, movement inside, water leaks, etc. I use two raspberries to monitor the house: one with movement, sound and temperature sensors connected to it and the other listening to zigbee devices (aqara) via usb dongle.

## Sensors directly connected to raspberry (_base_ app variant)
The app provides for up to three movement sensors. Connection pins are set in gpio.py (`pin_back`, `pin_f1`, `pin_f2`). Sound sensor is connected to `pin_sound`.

Two temperature sensors are connected via 1-wire protocol. They appear in sysfs (/sys/bus/w1/devices/). The paths to them is set in config_base.py (ONE_WIRE_PATH1, ONE_WIRE_PATH2).

One sensor is used to measure the air temperature inside the house, the other is placed onto radiator connected to gas boiler via pipe to monitor its temperature and make sure that boiler is working (which is especially important during winter time to avoid pipe freezing if a boiler stops working). If a radiator temperature drops below certain point a warning is sent. This functionality has helped an author promptly react several times when the boiler mulfunctioned.

## Zigbee sensors (_zigbee_ app variant)
[Zigbee2mqtt project](https://www.zigbee2mqtt.io/) is used to flash cc2531 dongle and install required software on raspberry pi. The app assumes that a mosquitto server is running on localhost:1883 (the address could be changed in zig.py). Ids of sensors should be set in config_zig.py.

## Camera
The app takes a shot inside the house on request or when the movement is detected via web camera in the same local network. The http path to web camera is set in HTTP_IMAGE_URL variable (config_base.py).

## Telegram
Telegram bot tokens and chat ids are set in config_base.py and config_zig.py (there could be the own bot for each raspberry).

## Installation

```
git clone https://github.com/dsoastro/smarthome
cd smarhome
pip3 install -r requirements.txt
sudo apt install speedtest-cli


```

## Get Started

```
# for raspberry pi with directly connected sensors
python3 main.py DACHA_BASE

# for raspberry pi listening to zigbee sensors
python3 main.py DACHA_ZIG
```

## Commands
```
ptemp:    get cpu temperature  
temp:     get sensors temperature  
speed:    get network speed  
log:      get the last 20 lines of app log  
cpu:      get a list of processes sorted by cpu  
uptime:   get result of uptime linux command  
battery:  get available zigbee sensors and their charge  
last:     get the raw output from zigbee sensors  
moveon:   turn on monitoring via movement sensors  
moveoff:  turn off monitoring via movement sensors  
soundon:  turn on monitoring via sound sensor  
soundoff: turn off monitoring via sound sensor  
image:    get an image from web camera  
sdcard:   get sdcard statistics  
schedule: get a list of scheduled commands  
clearsc:  clear a list of scheduled commands  
```

Each command could be scheduled by adding `at time` to it, e.g.:  
```
temp at 53 - get temp at 53rd minute of the current hour  
temp at 16.53 - get temp at 16.53  
```

