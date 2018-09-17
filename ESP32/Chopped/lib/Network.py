import sys
core = sys.modules['Blocky.Core']

BROKER = 'broker.getblocky.com'
CHIP_ID = core.binascii.hexlify(core.machine.unique_id()).decode('ascii')
		
class Network:
	def __init__ (self):
		self.state = 0
		self.has_msg = False
		self.topic = ''
		self.msg = ''
		self.message_handlers = {}
		self.retry = 0
		self.echo = []
		self.config = {'known_networks':[] , 'device_name':'' , 'auth_key':''}
		self.server = None
		self.BootManager = None
		self.ota = []
		self.file = None
		try :
			self.config = core.json.loads(open('config.json','r').read())
		except Exception as err:
			print('network->init' , err)
			#from Blocky.BootMode import bootmode 
			#await bootmode.Start()
			self.config = core.json.loads(open('config.json','r').read())

		self.mqtt = core.mqtt.MQTTClient(CHIP_ID, BROKER, 0, CHIP_ID, self.config['auth_key'], 1883)
		self.sysPrefix = self.config.get('auth_key') + '/sys/' + CHIP_ID + '/'
		self.userPrefix = self.config.get('auth_key') + '/user/'
		self.mqtt_connected = False
		self.last_call = core.Timer.runtime()
		
	#---------------------------------------------------------
	async def isconnected(self):
		while True :
			if core.Network.WLAN(core.Network.STA_IF).isconnected() and \
				self.mqtt_connected == True :
				print('@')
				break 
			else :
				await core.asyncio.sleep_ms(1000)
	async def connect(self):
		wlan_sta = core.Network.WLAN(core.Network.STA_IF)
		wlan_sta.active(True)
		wifi_list = []
		core.indicator.animate('heartbeat' , (100,0,0))
		print('Scanning wifi')
		await core.asyncio.sleep_ms(50)
		try :
			for wifi in wlan_sta.scan(): #OSError Wifi Invalid Argument
				print(wifi)
				wifi_list.append(wifi[0].decode('utf-8'))
		except :
			core.machine.reset()
		for preference in [p for p in self.config.get('known_networks') if p['ssid'] in wifi_list]:
			core.indicator.animate('heartbeat' , (100,50,0))
			wlan_sta.connect(preference['ssid'],preference['password'])
			print('[',core.Timer.runtime(),'] Connecting to network {0}...'