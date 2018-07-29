
#1.First step , check for json file
try :
	from ujson import loads
	f = open('config.json','r')
	config = loads(f.read())
	f.close()
	if not config.get('auth_key',False)\
	or not config.get('known_networks',False):
		raise KeyError('Missing key information')
except Exception:
	print('Missing required info in config. Enter config mode')
	import Blocky.ConfigManager#exec(open('Blocky/ConfigManager.py').read())
	
print('Finished loading config file' , config)




from Blocky.Timer import *
from Blocky.Network import network
from Blocky.Indicator import indicator
import Blocky.uasyncio as asyncio
from machine import Pin
if  Pin(12,Pin.IN,Pin.PULL_UP).value():
	import Blocky.ConfigManager#exec(open('Blocky/ConfigManager.py').read())

FLAG_UPCODE = False
import Blocky.Global
async def service():
	while True :
		await asyncio.sleep_ms(300)
		
		if Blocky.Global.flag_UPCODE == True:
			#perform clean up here 
			# ::Section1:: Coroutine -> Handle by Network 
			from Blocky.asyn import Cancellable
			
			await Cancellable.cancel_all()
			print(' ::Section2:: Variables ')
			global GLOBAL_CAPTURE
			print(GLOBAL_CAPTURE)
			for x in list(globals().keys()):
				if x not in GLOBAL_CAPTURE:
					
					print(x)
					del globals()[x]
			list_pin = [4,33,16,32,22,25,26,14,18,13,17,27,19]
			print(' ::Section3:: Pin IRQ , PWM ')
			from machine import Pin , PWM
			for x in list_pin:
				PWM(Pin(x)).deinit()
				Pin(x).irq(None)
			print(' ::Section4:: Network Topic')
			network.message_handlers = {}
			network.echo = []
			from json import loads
			network.config = loads(open('config.json','r').read())
			register_data = {'event': 'register', 
			'chipId': CHIP_ID, 
			'firmwareVersion': '1.0',
			'name': network.config.get('device_name', 'Blocky_' + CHIP_ID),
			'type': 'esp32'
			}
			network.mqtt.subscribe(network.config['auth_key'] + '/sys/' + CHIP_ID + '/ota/#')
			network.mqtt.subscribe(network.config['auth_key'] + '/sys/' + CHIP_ID + '/run/#')
			network.mqtt.subscribe(network.config['auth_key'] + '/sys/' + CHIP_ID + '/rename/#')
			network.mqtt.subscribe(network.config['auth_key'] + '/sys/' + CHIP_ID + '/reboot/#')
			network.mqtt.subscribe(network.config['auth_key'] + '/sys/' + CHIP_ID + '/upload/#')
			network.mqtt.subscribe(network.config['auth_key'] + '/sys/' + CHIP_ID + '/upgrade/#')
			network.mqtt.publish(topic=network.config['auth_key'] + '/sys/', msg=dumps(register_data))
		
			print('Ran by Flag')
			try :
				exec(open('user_code.py').read())
			except Exception as err:
				network.log('Your code crashed somehow -> ' + err)
			
			Blocky.Global.flag_UPCODE= False
		network.process()
		
def require_network():
	network.connect()
	loop = asyncio.get_event_loop()
	loop.call_soon(service())

try :
  network_required = open('user_code.py','r').read().find('network.') > 0
except :
  network_required = True
network_required = True
if network_required :
	require_network()
	
else :
	from Blocky.Button import *
	button  = Button(12)
	from Blocky.Network import network
	button.event('pressed' , 1 , require_network)
	




# network will do the wifi and broker
from Blocky.MQTT import *
from Blocky.Network import *
import _thread
loop = asyncio.get_event_loop()
GLOBAL_CAPTURE = list(globals().keys()) 
try :
	exec(open('user_code.py').read())
except Exception as err:
	network.log('Your code crashed because of "' + str(err) + '"')
	
# TODO :
"""
 If inside the setup block contains a blocking operation , the chip will be bricked
 
"""


def atte():
  while True :
    try :
      loop.run_forever()
    except Exception as e:
        import sys
        sys.print_exception(e)
      

_thread.start_new_thread(atte,())



