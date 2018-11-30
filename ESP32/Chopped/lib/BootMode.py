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
		r