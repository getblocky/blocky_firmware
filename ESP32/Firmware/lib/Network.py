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
			print('[',core.Timer.runtime(),'] Connecting to network {0}...'.format(preference['ssid']))
			for check in range(0,10):
				if wlan_sta.isconnected():
					break
				print('.',end='')
				await core.asyncio.sleep_ms(1000)
			if wlan_sta.isconnected():
				print('Connected to ' , preference)
				self.mqtt_connected = False
				for i in range(10):
					core.indicator.animate('heartbeat' , (200,100,0))
					try :
						print('Retry..')
						self.mqtt.connect()
						self.mqtt_connected = True
						await core.asyncio.sleep_ms(2000)
						break
					except Exception as err:
						print('mqtt-connect->' , err)
						pass

		if not wlan_sta.isconnected() or not self.mqtt_connected :
			bootmode = core.BootMode.BootMode()
			await bootmode.Start()
			del bootmode
		core.indicator.animate('pulse' , (10,50,100))	
		# At this poinrt , wifi and broker are connected
		self.mqtt.set_callback(self.handler)
		register_data = {'event': 'register', 
			'chipId': CHIP_ID, 
			'firmwareVersion': '1.0',
			'name': self.config.get('device_name', 'Blocky_' + CHIP_ID),
			'type': 'esp32'
		}
		
		
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/ota/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/run/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/rename/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/reboot/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/upload/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/upgrade/#')
		await self.mqtt.publish(topic=self.config['auth_key'] + '/sys/', msg=core.json.dumps(register_data))
	
		self.state = 1
		print('Connected to broker',core.json.dumps(register_data))
		core.flag.ONLINE = True
		core.indicator.animate()
		for x in range(0,250,1):
			core.indicator.rgb[0] = (0,x,x);core.indicator.rgb.write()
			core.time.sleep_ms(1)
		for x in range(250,0,-1):
			core.indicator.rgb[0] = (0,x,x);core.indicator.rgb.write()
			core.time.sleep_ms(1)	
		return True 
		
	def process(self): # Feed function , run as much as possible
		core.indicator.animate('heartbeat' , (255,0,0));self.last_call = core.Timer.runtime()
		if self.state != 1:
			return 
		try :
			self.mqtt.check_msg()
		except Exception as err:
			print('nw-mqtt-> ' , err)
			core.sys.print_exception(err)
			#await self.connect()
	# Process will trigger mqtt.wait_msg -> selb.cb -> self.handler
	async def cancel (self):
		await core.asyn.Cancellable.cancel_all()
		print('Canceled')
	async def handler(self,topic,message):
		print('%',end='')
		try :
			core.indicator.animate('pulse' , (0,100,0))
			print('handle->',topic  , len(message))
			self.topic = topic.decode()
			self.message = message.decode()
			if self.topic.startswith(self.userPrefix):
				if self.topic in self.echo:
					print('echo' , self.topic)
					self.echo.remove(self.topic)
					return 
					
				function = self.message_handlers.get(self.topic)
				print('func' , function)
				if function :
					print('init')
					try :
							#mainthread.create_task(Cancellable(function(self.topic.split('/')[-1],self.message))(self.topic.split('/')[-1],self.message))
						await function(self.topic.split('/')[-1],self.message)
					except Exception as err:
						print('['+str(runtime())+']','nw-handler->' , err)
						
					
			elif self.topic.startswith(self.sysPrefix):
				if self.topic.startswith(self.sysPrefix+'ota'):
					try :
						print('['+str(core.Timer.runtime())+']' , 'OTA Message' , len(self.message))
						piece = self.topic.split('/')[-1]
						if piece.isdigit():
							print('Receive piece # ' , piece , len(self.message))
							piece = int(piece)
							if piece > len(self.ota):
								for x in range(piece-len(self.ota)):
									self.ota.append('')
									
							self.ota[piece-1] = self.message
							"""
							if piece == 1:
								self.file = open('user_code.py' , 'w')
								self.file.write(self.ota[piece-1])
								self.piece += 1
								self.ota[piece-1] = ''
							
							else :
								if len(self.ota) > piece : # new piece coming 
									if len(self.ota[piece-1]):
										self.file.write(self.ota[piece-1])
										self.ota[piece-1] = ''
										self.piece += 1
										
							"""
						elif piece == '$' : 
							print('EOF-> ' , len(self.ota) , ' pieces total')
							self.ota.append(self.message)
							f = open('user_code.py' , 'w')
							f.write('import sys\ncore=sys.modules["Blocky.Core"]\n')
							for x in self.ota :
								f.write(x)
							f.close()
							self.ota = []
						elif  piece == 'ota':
							f = open('user_code.py','w')
							f.write(self.message)
							f.close()
							
						if piece == 'ota' or piece == '$':
							self.piece = 0
							otaAckMsg = {'chipId': CHIP_ID, 'event': 'ota_ack'}
							self.mqtt.publish(topic=self.config['auth_key'] + '/sys/', msg=core.json.dumps(otaAckMsg))
							print('User Code Received !')
							print('Cancelling Previouse Task')
							await core.asyn.Cancellable.cancel_all()
							core.flag.UPCODE = True 
							print('Done Cancelling All Task ')
						
						#
						
					except MemoryError :
						self.ota = []
						print('Coode tooo big ')
						await core.network.log('Your code is too big !')
						
						
						
						# Clean up 
						"""
						from machine import Pin , Timer , PWM
						list = [ 4, 33 , 16, 32, 23, 22, 27 , 19 , 13, 17 , 14, 18 , 25, 26 ]
						for x in list:
							PWM(Pin(x)).deinit()
						for x in range(0 , 10): # Dont touch software timer
							Timer(x).deinit()
						from Blocky.Main import GLOBAL_CAPTURE
						for x in list(globals()):
							if x not in GLOBAL_CAPTURE:
								del globals()[x]
						"""
						
				
				elif self.topic == self.sysPrefix + 'run':
					print('['+str(core.Timer.runtime())+']' , 'RUN message' , len(self.message))
					exec(self.message , globals())
					# this will be used to handle upgrade firmwareVersion
				
				
					
		except Exception as err:
			core.sys.print_exception(err)
			print('nw-handler->' , err)
		finally :
			core.gc.collect()
			self.topic = ''
			self.message = ''
	
	async def send(self,topic,data,echo=False,timout = 2):
		while core.flag.ONLINE == False and core.Timer.runtime() < start + timeout *1000 :
			await core.asyncio.sleep_ms(100)
			
		if self.state!=1 or not topic or not data:
			return 
		topic = self.config.get('auth_key') + '/user/' + topic
		if not echo and self.message_handlers.get(topic):
			self.echo.append(self.userPrefix+str(topic))
		try :
			core.indicator.animate('pulse' , (0,0,100))
			await self.mqtt.publish(topic = topic,msg = str(data))
		except Exception as err:
			print('nw-send->',err,topic,data)
	async def log(self,message,timeout = 2):
		start = core.Timer.runtime()
		while core.flag.ONLINE == False and core.Timer.runtime() < start + timeout *1000 :
			await core.asyncio.sleep_ms(100)
			
		if self.state != 1 or not message:
			return 
		prefix = self.config.get('auth_key') + '/sys/' + CHIP_ID + '/log'
		try :
			core.indicator.animate('pulse' , (0,50,50))
			await self.mqtt.publish(topic=prefix,msg=str(message))
		except Exception as err:
			print('nw-log->',err,message)
	async def subscribe(self,topic,callback):
		while core.flag.ONLINE == False :
			await core.asyncio.sleep_ms(100)
			
		if self.state != 1 or not topic:
			return 
		topic = self.config.get('auth_key') + '/user/' + topic
		await self.mqtt.subscribe(topic)
		self.message_handlers[topic] = callback

