from Blocky.MQTT import *
from Blocky.Indicator import indicator
from machine import unique_id , reset
from binascii import hexlify 
import gc
from time import sleep_ms
from Blocky.Timer import *
from ujson import dumps , loads
#import uasyncio as asyncio
import Blocky.uasyncio as asyncio
from Blocky.asyn import cancellable , Cancellable
BROKER = 'broker.getblocky.com'
CHIP_ID = hexlify(unique_id()).decode('ascii')
from machine import Timer , Pin
from Blocky.Global import flag_UPCODE
class Network:
	def __init__ (self):
		self.state = 0
		self.has_msg = False
		self.topic = ''
		self.msg = ''
		self.message_handlers = {}
		self.retry = 0
		self.echo = []
		from json import loads
		self.config = loads(open('config.json','r').read())
		self.mqtt = MQTTClient(CHIP_ID, BROKER, 0, CHIP_ID, self.config['auth_key'], 1883)
		self.sysPrefix = self.config.get('auth_key') + '/sys/' + CHIP_ID + '/'
		self.userPrefix = self.config.get('auth_key') + '/user/'
		self.mqtt_connected = False
		self.last_call = runtime()
		Timer(-1).init(mode = Timer.PERIODIC , period = 3000 , callback = self.failsafe)
	def failsafe(self,source):
		if runtime() - self.last_call > 3000 :
			self.process()
			self.last_call = runtime()
	def connect(self):
		from network import WLAN , STA_IF
		wlan_sta = WLAN(STA_IF)
		wlan_sta.active(True)
		wifi_list = []
		indicator.animate('heartbeat' , (100,0,0))
		print('Scanning wifi')
		sleep_ms(50)
		try :
			for wifi in wlan_sta.scan(): #OSError Wifi Invalid Argument
				print(wifi)
				wifi_list.append(wifi[0].decode('utf-8'))
		except :
			from machine import reset
			reset()
		for preference in [p for p in self.config.get('known_networks') if p['ssid'] in wifi_list]:
			indicator.animate('heartbeat' , (100,50,0))
			wlan_sta.connect(preference['ssid'],preference['password'])
			print('[',runtime(),'] Connecting to network {0}...'.format(preference['ssid']))
			for check in range(0,5):
				if wlan_sta.isconnected():
					break
				print('.',end='')
				sleep_ms(1000)
			if wlan_sta.isconnected():
				print('Connected to ' , preference)
				self.mqtt_connected = False
				for i in range(5):
					indicator.animate('heartbeat' , (200,100,0))
					try :
						print('Retry..')
						self.mqtt.connect()
						self.mqtt_connected = True
						sleep_ms(2000)
						break
					except Exception:
						pass

		if not wlan_sta.isconnected() or not self.mqtt_connected :
			import Blocky.ConfigManager#exec(open('Blocky/ConfigManager.py').read())
		indicator.animate('pulse' , (10,50,100))	
		# At this poinrt , wifi and broker are connected
		self.mqtt.set_callback(self.handler)
		register_data = {'event': 'register', 
			'chipId': CHIP_ID, 
			'firmwareVersion': '1.0',
			'name': self.config.get('device_name', 'Blocky_' + CHIP_ID),
			'type': 'esp32'
		}
		
		
		self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/ota/#')
		self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/run/#')
		self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/rename/#')
		self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/reboot/#')
		self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/upload/#')
		self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/upgrade/#')
		self.mqtt.publish(topic=self.config['auth_key'] + '/sys/', msg=dumps(register_data))
    
		self.state = 1
		print('Connected to broker')
		indicator.animate()
		for x in range(0,250,1):
			indicator.rgb[0] = (0,x,x);indicator.rgb.write()
			sleep_ms(1)
		for x in range(250,0,-1):
			indicator.rgb[0] = (0,x,x);indicator.rgb.write()
			sleep_ms(1)	
		return True 
		
	def process(self): # Feed function , run as much as possible
		indicator.animate('heartbeat' , (100,0,0));self.last_call = runtime()
		if self.state != 1:
			return 
		try :
			self.mqtt.check_msg()
		except Exception as err:
			print('nw-mqtt-> ' , err)
	# Process will trigger mqtt.wait_msg -> selb.cb -> self.handler
	async def cancel (self):
		await Cancellable.cancel_all()
	def handler(self,topic,message):
		try :
			indicator.animate('pulse' , (0,100,0))
			print('handle',topic  , message)
			self.topic = topic.decode()
			self.message = message.decode()
			print(self.topic  , self.message,self.topic.startswith(self.userPrefix))
			if self.topic.startswith(self.userPrefix):
				if self.topic in self.echo:
					print('echo' , self.topic)
					self.echo.remove(self.topic)
					return 
					
				function = self.message_handlers.get(self.topic)
				print('func' , function)
				if function :
					print('init')
					loop = asyncio.get_event_loop()
					try :
						if not str(function(self.topic.split('/')[-1],self.message)).split("'")[1] in loop.tasks :
							loop.create_task(Cancellable(function(self.topic.split('/')[-1],self.message))(self.topic.split('/')[-1],self.message))
					except Exception as err:
						print('['+str(runtime())+']','nw-handler->' , err)
						
					
			elif self.topic.startswith(self.sysPrefix):
				if self.topic==self.sysPrefix+'ota':
					print('['+str(runtime())+']' , 'OTA Message' , len(self.message))
					f = open('user_code.py','w')
					#f.write('import Blocky.asyn as asyn\n'+self.message.replace('async def','@asyn.cancellable\nasync def'))
					f.write(self.message);f.close()
					otaAckMsg = {'chipId': CHIP_ID, 'event': 'ota_ack'}
					
					#global FLAG_UPCODE
					#FLAG_UPCODE = True
					print('Cancelling')
					try :
						loop = asyncio.get_event_loop()
						loop.call_soon(self.cancel())
					except :
						pass 
					#loop.call_soon(cancel())
					import Blocky.Global
					Blocky.Global.flag_UPCODE = True 
					
					print('Canceled')
					
					print('RUN')
					self.mqtt.publish(topic=self.config['auth_key'] + '/sys/', msg=dumps(otaAckMsg))
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
					
				
				elif self.topic == sysPrefix + 'run':
					print('['+str(runtime())+']' , 'RUN message' , len(self.message))
					exec(self.message , globals())
					# this will be used to handle upgrade firmwareVersion
				
				
					
		except Exception as err:
			print('nw-handler->' , err)
		finally :
			gc.collect()
			self.topic = ''
			self.message = ''
	
	def send(self,topic,data,echo=False):
		if self.state!=1 or not topic or not data:
			return 
		topic = self.config.get('auth_key') + '/user/' + topic
		if not echo and self.message_handlers.get(topic):
			self.echo.append(self.userPrefix+str(topic))
		try :
			indicator.animate('pulse' , (0,0,100))
			self.mqtt.publish(topic = topic,msg = str(data))
		except Exception as err:
			print('nw-send->',err,topic,data)
	def log(self,message):
	
		if self.state != 1 or not message:
			return 
		prefix = self.config.get('auth_key') + '/sys/' + CHIP_ID + '/log'
		try :
			indicator.animate('pulse' , (0,50,50))
			self.mqtt.publish(topic=prefix,msg=str(message))
		except Exception as err:
			print('nw-log->',err,message)
	def subscribe(self,topic,callback):
		if self.state != 1 or not topic:
			return 
		topic = self.config.get('auth_key') + '/user/' + topic
		self.mqtt.subscribe(topic)
		self.message_handlers[topic] = callback
		
network = Network()
		
			
			
		





