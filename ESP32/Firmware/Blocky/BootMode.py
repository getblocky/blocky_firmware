#from Blocky.Indicator import indicator
from machine import unique_id , reset
from binascii import hexlify 
import gc
from ujson import dumps , loads
import Blocky.uasyncio as asyncio
from Blocky.asyn import cancellable , Cancellable
BROKER = 'broker.getblocky.com'
CHIP_ID = hexlify(unique_id()).decode('ascii')
from machine import Timer , Pin
import Blocky.Global 

class BootMode :	
	def __init__ (self):
		import network as Network
		self.wlan_ap =  Network.WLAN(Network.AP_IF)
		self.wlan_sta =  Network.WLAN(Network.STA_IF)
		self.status = 'start'
	
	async def connect(self, ssid, password):
		self.wlan_sta.active(True)
		self.wlan_sta.connect(ssid, password)
		
		print('Connecting to wifi')
		#indicator.animate('pulse',(100,50,0),10)
		while not self.wlan_sta.isconnected() | (a > 99) :
			await asyncio.sleep_ms(100)
			a+=1
			print('.', end='')
		
		if self.wlan_sta.isconnected():
			#indicator.animate('pulse',(0,100,50),10)
			print('\nConnected. Network config:', self.wlan_sta.ifconfig())
			self.wifi_status = 1
			return True
		else : 
			#indicator.animate('hearbeat',(0,100,50),10)
			print('\nProblem. Failed to connect to :' + ssid)
			self.wifi_status = 2
			self.wlan_sta.active(False)
			return False
	async def _httpHandlerIndexGet(self, httpClient, httpResponse):
		print('Get index request' )
		"""
		f = open('Blocky/index.html', 'r')
		a = f.readlines()
		f.close()
		content = ''
		for x in a:
			content += x
		"""
		f = open('Blocky/index.html', 'r')
		content = ''
		for line in f:
			content = content + line
			
		print('Content ------------>' , len(content) , end = '')
		print(httpResponse.WriteResponseOk( headers = None,contentType= "text/html",	contentCharset = "UTF-8",	content = content) , end = '')
		print('--> OK')
		
	async def _httpHandlerCheckStatus(self, httpClient, httpResponse):
		print('Get check status request')
		import Blocky.Global
		if Blocky.Global.flag_ONLINE == True:
			content = 'OK'
		elif Blocky.Global.flag_ONLINE == False:
			content = 'Failed'
		else:	
			content = ''
		
		httpResponse.WriteResponseOk(headers = None,
			contentType	 = "text/html",
			contentCharset = "UTF-8",
			content = content)
		
		"""
		if self.wifi_status == 1:
			print('Wait for rebooting')
			time.sleep(5)
			print('Rebooting')
			machine.reset()
		"""

	async def _httpHandlerSaveConfig(self, httpClient, httpResponse):
		from ujson import loads
		request_json  = ''
		request_json = loads(httpClient.ReadRequestContent().decode('ascii'))
		self.wifi_status = 0
		httpResponse.WriteResponseOk(headers = None,contentType= "text/html",	contentCharset = "UTF-8",content = 'OK')
		self.wlan_sta.connect(request_json['ssid'], request_json['password'])
		print('client->saveconfig: Trying to connect to ' + str(request_json) , end = '')
		for x in range(100):
			await asyncio.sleep_ms(100)
			
			if self.wlan_sta.isconnected():
				# save config
				
				self.wifi_status = 1
				print('Connected to ' , request_json['ssid'])
				
				config = {}
				try :
					config = loads(open('config.json').read())
				except :
					pass
				if not config.get('known_networks'):
					config['known_networks'] = [{'ssid': request_json['ssid'], 'password': request_json['password']}]
				else:
					exist_ssid = None
					for n in config['known_networks']:
						if n['ssid'] == request_json['ssid']:
							exist_ssid = n
							break
					if exist_ssid:
						exist_ssid['password'] = request_json['password'] # update WIFI password
						print('Update wifi password')
					else:
						# add new WIFI network
						config['known_networks'].append({'ssid': request_json['ssid'], 'password': request_json['password']})
						print('Add new network')
				print('Devicename')
				config['device_name'] = request_json['deviceName']
				config['auth_key'] = request_json['auth_key']
				
				
				
				f = open('config.json', 'w')
				f.write(dumps(config))
				f.close()
				import Blocky.Global
				Blocky.Global.flag_ONLINE = True
				print('Done' , config)
				break
			else :
				import Blocky.Global
				Blocky.Global.flag_ONLINE = False
				print('.' , end = '')
	def is_ascii(self, s):
		return all(ord(c) < 128 for c in s)
	
	async def _httpHandlerScanNetworks(self, httpClient, httpResponse) :
		print('scanap->' , end = '')
		self.wlan_sta.active(True)
		
		networks = []
		raw = self.wlan_sta.scan()
		for nw in raw:
			networks.append({'ssid': nw[0].decode('ascii'), 'rssi': nw[3]})
		
		content = dumps(networks)
		print(len(networks) , 'networks detected')
		httpResponse.WriteResponseOk(headers = None,contentType= "application/json",contentCharset = "UTF-8",content = content)
		
	async def Start(self):
		from Blocky.Indicator import indicator
		#This function will run config boot mode in background ! 
		#As an replacement for ConfigManager.py
		#When a network call is erro , it will create this task in 
		#main thread as an async function 
		#As such , this won't block
		
		gc.collect()
		if gc.mem_free() < 20000 :
			import machine 
			machine.reset()
		
		
		import network , socket , binascii , re , ustruct , ujson , machine
		
		server = None 
		id = binascii.hexlify(machine.unique_id()).decode('ascii')
		uuid = [id[i:i+2] for i in range(0, len(id), 2)]

		max_index = 0 ; max_value = 0
		for x in range(6):
		  if int(uuid[x],16) > max_value:
			max_value = int(uuid[x],16)
			max_index = x
			
		# Try to make an color indicator for which is which 
		# Blocky that shine red will be 'Blocky RED <uuid>'
		color = []
		if max_index == 0 : color = ['red',(255,59,48)]
		if max_index == 1 : color = ['green',(76,217,100)]
		if max_index == 2 : color = ['blue',(0,122,255)]
		if max_index == 3 : color = ['pink',(255,45,85)]
		if max_index == 4 : color = ['purple',(88,86,214)]
		if max_index == 5 : color = ['yello',(255,204,0)]
			
		
		ap_name = 'Blocky ' + color[0].upper() +' '+ binascii.hexlify(machine.unique_id()).decode('ascii')[0:4]
		print(ap_name)
		loop= asyncio.get_event_loop()
		loop.create_task(indicator.heartbeat( color[1] , 1 , Blocky.Global.flag_ONLINE , 5) )
		ap_password = ''
		wifi_status = 0
		
		
		#-------------------------------------------------
		
		#-------------------------------------------------
		self.wlan_sta.active(True)
		self.wlan_ap.active(True)
		
		self.wlan_ap.config(essid = ap_name , password = ap_password	)

		routeHandlers = [
			("/", "GET", self._httpHandlerIndexGet),
			("/aplist", "GET", self._httpHandlerScanNetworks),
			("/status", "GET", self._httpHandlerCheckStatus),
			("/save", "POST",	self._httpHandlerSaveConfig)
		]
		
		from Blocky.MicroWebSrv import MicroWebSrv
		server = MicroWebSrv(routeHandlers = routeHandlers)
		print('bootmode-> started')
		#loop = asyncio.get_event_loop()
		#loop.create_task(server.Start())
		
		await server.Start()
		print('bootmode-> completed')
	
