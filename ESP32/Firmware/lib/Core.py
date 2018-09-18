# All public variable across the system to avoid duplicate import

asyncio = None 
asyn = None 
flag = None 
eeprom = None
mqtt = None
BootMode = None
indicator = None
config = None
ota_file = None
deinit_list = []

import time
import machine
import neopixel
import binascii
import json
import ure
import gc
import network
import sys
import micropython
import socket
import struct
import _thread
import urequests
import random
import os
import Blocky.Global as flag
import Blocky.EEPROM as eeprom
import Blocky.uasyncio as asyncio
import Blocky.asyn as asyn
import Blocky.Timer as Timer
from Blocky.Indicator import indicator
from Blocky.Pin import getPort

cfn_btn = machine.Pin(12 , machine.Pin.IN , machine.Pin.PULL_UP)
mainthread = asyncio.get_event_loop()

wifi = None # Wifi class started in Main


def cleanup():
	pin = [25,26,27,14,13,15,4,16,32,17,33,18,23,19,22,21]
	# Clear all hardware that require to be deinit
	global deinit_list
	for x in deinit_list:
		try :
			x.deinit()
		except:
			pass
	deinit_list = []
	# Reset all hardware to it initial state
	# Timer must be deinit by deinit_list
	for x in pin:
		machine.PWM(machine.Pin(x)).deinit()
		machine.Pin(x,machine.Pin.IN)
	
	del sys.modules['user_code']