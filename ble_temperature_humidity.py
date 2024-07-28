# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# BLE temperature and humidity sensor example.

import time
from hts221 import HTS221
from board import LED
from machine import Pin, I2C
from ubluepy import Service, Characteristic, UUID, Peripheral, constants


def event_handler(id, handle, data):
    global periph, service, notify_enabled

    if id == constants.EVT_GAP_CONNECTED:
        # indicated 'connected'
        LED(1).on()
    elif id == constants.EVT_GAP_DISCONNECTED:
        # indicate 'disconnected'
        LED(1).off()
        # restart advertisement
        periph.advertise(device_name="Temp Humidity Sensor", services=[service])
    elif id == constants.EVT_GATTS_WRITE:
        # write to this Characteristic is to CCCD
        print("data", data)
        print("---------------------")
        print("data0", int(data[0]))
        print("---------------------")
        print("data1", int(data[1]))
        print("---------------------")
        # Possibly need to make this if int data 0 or 1 then true
        # Or id data doesnt need to change then change to notify enabled temp
        # and notify enabled humid
        if int(data[0]) == 1:
            notify_enabled = True
        else:
            notify_enabled = False

LED(1).off()

notify_enabled = False
uuid_service = UUID("0x181A")  # Environmental Sensing service
uuid_temp = UUID("0x2A6E")  # Temperature characteristic
uuid_humidity = UUID("0x2A6E") # Humidity characteristic

service = Service(uuid_service)
temp_props = Characteristic.PROP_READ | Characteristic.PROP_NOTIFY
temp_attrs = Characteristic.ATTR_CCCD
temp_char = Characteristic(uuid_temp, props=temp_props, attrs=temp_attrs)
humidity_props = Characteristic.PROP_READ | Characteristic.PROP_NOTIFY
humidity_attrs = Characteristic.ATTR_CCCD
humidity_char = Characteristic(uuid_humidity, props=humidity_props, attrs=humidity_attrs)
service.addCharacteristic(temp_char)
service.addCharacteristic(humidity_char)

periph = Peripheral()
periph.addService(service)
periph.setConnectionHandler(event_handler)
periph.advertise(device_name="Temp Humidity Sensor", services=[service])

bus = I2C(1, scl=Pin(15), sda=Pin(14))
try:
    hts = HTS221(bus)
except OSError:
    from hs3003 import HS3003

    hts = HS3003(bus)
while True:
    if notify_enabled:
        #notify for only one service
        temp = int(hts.temperature()*100)
#        humidity = int(hts.humidity())
        temp_char.write(bytearray([temp & 0xFF, temp >> 8]))
#        humidity_char.write(bytearray([humidity & 0xFF, humidity >> 8]))
    time.sleep_ms(100)
