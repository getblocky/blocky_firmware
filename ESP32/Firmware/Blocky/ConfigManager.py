from Blocky.Indicator import indicator
import socket,time,random,binascii,machine,re,ustruct,gc,ujson
from json import dumps , loads
from os import stat
from _thread import start_new_thread
import socket
from time import sleep_ms
from Blocky.MicroWebSrv import *
import Blocky.uasyncio as asyncio 

"""
class config is called when esp boot and cant connect or the connection is dropped randomly 
therefore , when the network is restore  , this will reset ,
"""
# Update firmware version 
# Config Manager always run as cooperative thread ! 
# Problem with memory occur due to the length of index.html and MicroWebSrv file , hugh 

indicator.animate(type='heartbeat',color=(50,0,0),speed=10)

class ConfigManager:
	def __init__ (self,config = {}):
		import network as Network;self.config = config
		import socket,time,random,binascii,machine,re,ustruct,gc,ujson
		self.wlan_ap = Network.WLAN(Network.AP_IF)
		self.wlan_sta = Network.WLAN(Network.STA_IF)
		self.srv = None
		id = binascii.hexlify(machine.unique_id()).decode('ascii')
		uuid = [id[i:i+2] for i in range(0, len(id), 2)]

		max_index = 0 ; max_value = 0
		for x in range(6):
		  if int(uuid[x],16) > max_value:
			max_value = int(uuid[x],16)
			max_index = x
		color = []
		if max_index == 0 : color = ['red',(255,59,48)]
		if max_index == 1 : color = ['green',(76,217,100)]
		if max_index == 2 : color = ['blue',(0,122,255)]
		if max_index == 3 : color = ['pink',(255,45,85)]
		if max_index == 4 : color = ['purple',(88,86,214)]
		if max_index == 5 : color = ['yello',(255,204,0)]
			
		
		try :
			f = open('config.json')
			self.ap_name = loads(f.read()).get('device_name')
			if self.ap_name == None :
				raise Exception
		except Exception:
			self.ap_name = 'Blocky ' + color[0].upper() +' '+ binascii.hexlify(machine.unique_id()).decode('ascii')[0:4];print(self.ap_name)
		indicator.animate()
		indicator.rgb[0] = color[1]
		indicator.rgb.write()
		self.ap_password = ''
		self.wifi_status = 0
							 
	def start(self):		
		self.wlan_sta.active(True)
		self.wlan_ap.active(True)

		self.wlan_ap.config(essid=self.ap_name, password=self.ap_password)

		routeHandlers = [
			("/", "GET", self._httpHandlerIndexGet),
			("/aplist", "GET", self._httpHandlerScanNetworks),
			("/status", "GET", self._httpHandlerCheckStatus),
			("/save", "POST",	self._httpHandlerSaveConfig)
		]
		
		self.srv = MicroWebSrv(routeHandlers=routeHandlers)
		self.srv.Start(threaded=True)

		print('Now enter config mode')
		print('Connect to Wifi ssid :' + self.ap_name + ' , default pass: ' + self.ap_password)
		print('And connect to Blocky via at 192.168.4.1')
		
		gc.collect()
		print(gc.mem_free())

		return True
		
    
config_manager = ConfigManager()
config_manager.start()

sleep_ms(120000)
from machine import reset
reset()





