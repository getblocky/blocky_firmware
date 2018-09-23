#version=1.0
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
TimerInfo = [time.ticks_ms() , time.ticks_ms() , None , None]

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

def download(filename , path):
	response = None
	gc.collect()
	try :
		print('[Downloading]  File -> ' + str(filename), end = '')
		response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/{}'.format(filename))
		if response.status_code == 200 :
			f = open('temp.py','w')
			f.write(response.content)
			print('#',end = '')
			piece = 0
			while True :
				piece += 1
				response = None
				gc.collect()
				try :
					response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/{}_${}.{}'.format(filename.split('.')[0] , piece , filename.split('.')[1]))   
					if response.status_code == 200 :
						f.write(response.content)
						print('#' , end = '')
					else :
						raise Exception
				except Exception :
					print('Pieces = ' , piece)
					f.close()
					os.rename('temp.py' , path)
					break 
		else :
			print('[Download] Failed . Library ' , filename , 'not found on server')
	except Exception as err:
		import sys
		sys.print_exception(err)
		print('Failed')
	
	del response
	gc.collect()