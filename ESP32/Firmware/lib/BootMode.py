#version=1.0
import  sys
core = sys.modules['Blocky.Core']
class BootMode :
	
	def __init__ (self):
		self.wlan_ap =  core.network.WLAN(core.network.AP_IF)
		self.wlan_sta =  core.network.WLAN(core.network.STA_IF)
		self.status = 'start'
		self.content = ''
	async def connect(self, ssid, password):
		self.wlan_sta.active(True)
		self.wlan_sta.connect(ssid, password)
		
		print('Connecting to wifi')
		#indicator.animate('pulse',(100,50,0),10)
		while not self.wlan_sta.isconnected()  :
			await core.asyncio.sleep_ms(100)
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
	def _httpHandlerIndexGet(self, httpClient, httpResponse):
		print('Get index request , memoryview' )
		# Heap fragmentation is our enemy
		f = open('Blocky/index.html')
		print('[bootmode] -> writing index request ',end='')
		content = []
		f = open('Blocky/index.html')
		while True:
			temp = f.read(500)
			if len(temp) == 0:
				break
			content.append(temp)
		f.close()
		httpResponse.WriteResponseOk( headers = None,contentType= "text/html",	contentCharset = "UTF-8",	content = content) 
		
		
	def _httpHandlerCheckStatus(self, httpClient, httpResponse):
		print('Get check status request')
		if core.flag.wifi == True:
			content = 'OK'
		elif core.flag.wifi == False:
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

	def _httpHandlerSaveConfig(self, httpClient, httpResponse):
		request_json  = ''
		request_json = core.json.loads(httpClient.ReadRequestContent().decode('ascii'))
		self.wifi_status = 0
		httpResponse.WriteResponseOk(headers = None,contentType= "text/html",	contentCharset = "UTF-8",content = 'OK')
		self.wlan_sta.connect(request_json['ssid'], request_json['password'])
		print('client->saveconfig: Trying to connect to ' + str(request_json) , end = '')
		for x in range(130):
			core.time.sleep_ms(100)
			if self.wlan_sta.isconnected():
				self.wifi_status = 1
				print('Connected to ' , request_json['ssid'])
				config = {}
				try :
					config = core.json.loads(open('config.json').read())
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
				if len(request_json['deviceName']):
					config['device_name'] = request_json['deviceName']
				if len(request_json['token']):
					config['token'] = request_json['token']
				
				f = open('config.json', 'w')
				f.write(core.json.dumps(config))
				f.close()
				core.flag.wifi = True
				break
			else :
				core.flag.wifi = False
				print('.' , end = '')
	def is_ascii(self, s):
		return all(ord(c) < 128 for c in s)
	
	def _httpHandlerScanNetworks(self, httpClient, httpResponse) :
		print('scanap->' , end = '')
		self.wlan_sta.active(True)
		
		networks = []
		raw = self.wlan_sta.scan()
		for nw in raw:
			networks.append({'ssid': nw[0].decode('ascii'), 'rssi': nw[3]})
		
		content = core.json.dumps(networks)
		print(len(networks) , 'networks detected')
		httpResponse.WriteResponseOk(headers = None,contentType= "application/json",contentCharset = "UTF-8",content = content)
		
	async def Start(self):
		
		#This function will run config boot mode in background ! 
		#As an replacement for ConfigManager.py
		#When a network call is erro , it will create this task in 
		#main thread as an async function 
		#As such , this won't block
		
		core.gc.collect()
		if core.gc.mem_free() < 20000 :
			core.machine.reset()
		
		server = None 
		id = core.binascii.hexlify(core.machine.unique_id()).decode('ascii')
		uuid = [id[i:i+2] for i in range(0, len(id), 2)]

		max_index = 0 ; max_value = 0
		for x in range(6):
		  if int(uuid[x],16) > max_value:
			max_value = int(uuid[x],16)
			max_index = x
			
		# Try to make an color indicator for which is which 
		# Blocky that shine red will be 'Blocky RED <uuid>'
		color = []
		n=5
		if max_index == 0 : color = ['red',(255//n,59//n,48//n)]
		if max_index == 1 : color = ['green',(76//n,217//n,100//n)]
		if max_index == 2 : color = ['blue',(0,122//n,255//n)]
		if max_index == 3 : color = ['pink',(255//n,45//n,85//n)]
		if max_index == 4 : color = ['purple',(88//n,86//n,214//n)]
		if max_index == 5 : color = ['yello',(255//n,204//n,0)]
		
		core.indicator.rgb.fill(color[1]);core.indicator.rgb.write()
		if core.eeprom.get('first_start') == 1:
			# when Blocky.Global.flag_ONLINE is True , it stop
			ap_name = "It's me , your " + color[0].upper() + ' Blocky'
		else :
			core.mainthread.create_task(core.indicator.heartbeat( color[1] , 1 ,core.flag.wifi , 5) )
			ap_name = 'Blocky ' + color[0].upper() +' '+ core.binascii.hexlify(core.machine.unique_id()).decode('ascii')[0:4]
		
		print(ap_name)
		
		
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
		from machine import reset
		reset()
	


