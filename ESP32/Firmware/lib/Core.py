#version=1.0
# All public variable across the system to avoid duplicate import
rtc = False
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
alarm_list = []
user_namedtask = []

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

# This will run at OTA events 

async def cleanup():
	print('[CLEANER] -? START')
	pin = [25,26,27,14,13,15,4,16,32,17,33,18,23,19,22,21]
	# Clear all hardware that require to be deinit
	global deinit_list , alarm_list
	for x in deinit_list:
		try :
			x.deinit()
		except:
			pass
	deinit_list = []	#refresh the list 
	alarm_list = [] #delete all alarm stuff
	# Reset all hardware to it initial state
	# Timer must be deinit by deinit_list
	for x in pin:
		machine.PWM(machine.Pin(x)).deinit()
		machine.Pin(x,machine.Pin.IN)
	
	for x in asyn.NamedTask.instances :
		if x.startswith('user'):
			await asyn.NamedTask.cancel(x)
	
	a=False
	while a == False :
		a = True
		for x in asyn.NamedTask.instances:
			if x.startswith('user'):
				a = False
				break
		if a == True :
			break 
		await asyncio.sleep_ms(10)
	print('[CLEANER] -? DONE')
		
async def call_once(name,function):
	print('[CALLING] {} -> {}'.format(name,function))
	if name in asyn.NamedTask.instances:
		if asyn.NamedTask.is_running(name):
			await asyn.NamedTask.cancel ( name )
			while asyn.NamedTask.is_running (name):
				await asyncio.sleep_ms(10)
	#mainthread.call_soon(asyn.NamedTask(name,function))
	if function != None :
		print('[CALLING] {} -> {}  DONE '.format(name,function))
		mainthread.call_soon( asyn.NamedTask(name,function) ())
		# Avoid pend throw for just stated-generator
		await asyncio.sleep_ms(0)
	else :
		print('[CANCEL] {}'.format(name))
	
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
					response = urequests.get('https://raw.githubusercontent.com/getblocky/dot_firmware/master/ota/{}_${}.{}'.format(filename.split('.')[0] , piece , filename.split('.')[1]))   
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
	
def get_list_library(file):
	f = open(file)
	cell = ''
	while True :
		cell += f.read(1)
		if cell[-2:] == '\n\n':
			break
	cell = cell.split('\n')
	r = []
	for line in cell :
		library = ''
		version = 0.0
		#from Blocky.STH import * #version=1.0
		if line.startswith('from '):
			library = line.split('.')[1].split(' ')[0]
			if '#version' in line :
				version = float(line.split('=')[1])
			r.append([library,version])
	f.close()
	return r
	
def get_library_version(lib):
	if '{}.py'.format(lib) not in os.listdir('Blocky'):
		return None
	line = ''
	f = open('Blocky/{}.py'.format(lib))
	while True :
		temp = f.read(1)
		if len(temp) == 0 or temp == '\n' or temp == '\r':
			break
		line += temp
	# #version=1.0
	if not line.startswith('#version'):
		f.close()
		return 0.0
	f.close()
	return float(line.split('=')[1])
	
