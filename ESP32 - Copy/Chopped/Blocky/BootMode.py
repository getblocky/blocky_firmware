#from Blocky.Indicator import indicator

import  sys
core = sys.modules['Blocky.Core']
class BootMode :
	
	def __init__ (self):
		self.wlan_ap =  core.Network.WLAN(core.Network.AP_IF)
		self.wlan_sta =  core.Network.WLAN(core.Network.STA_IF)
		self.status = 'start'
		self.content = ''
	
	async def connect(self, ssid, password):
		self.wlan_sta.active(True)
		self.wlan_sta.connect(ssid, password)
		
		print('Connecting to wifi')
		#indicator.animate('pulse',(100,50,0),10)
		while not self.wlan_sta.isconnected() | (a > 99) :
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
		content = []
		with open('Blocky/index.html') as f :
			while True :
				try :
					temp = f.read(100)
					if len(temp) == 0 : 
						break
					content.append(temp)
				except :
					print(len(content))
		print('Content = ' , len(content) , end = '')
		httpResponse.WriteResponseOk( headers = None,contentType= "text/html",	contentCharset = "UTF-8",	content = content) 
		print('Done')
		
		
	def _httpHandlerCheckStatus(self, httpClient, httpResponse):
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
			print('Reboo