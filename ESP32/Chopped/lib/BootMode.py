#version=1.0
import  sys
core = sys.modules['Blocky.Core']
class BootMode :
	
	def __init__ (self):
		self.wlan_ap =  core.network.WLAN(core.network.AP_IF)
		self.wlan_sta =  core.network.WLAN(core.network.STA_IF)
		self.wlan_sta.active(True)
		self.wlan_ap.active(True)
		self.status = 'start'
		self.content = ''
		self.success = False #dummy
		self.server = None
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
		httpResponse.WriteResponseOk(headers = None,contentType= "text/html",	contentCharset = "UTF-8",content = 'OK')
		print('checking')
		if self.wlan_sta.isconnected():
			self.wifi_status = 1
			print('Connected to ' , request_json['ssid'])
			config = {}
			try :
				config = core.json.loads(open('config.json').read())
			except :
				pass
			if not config.get('known_networks'):
				config['known_netw