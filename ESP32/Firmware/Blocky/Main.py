
"""
	Firmware Version 2 
	+ Add support for asynchorous programming 
	+ Add support for background boot mode 
	+ Add support for instant OTA , no reset 
	+ Start memory management 
	+ Add support for non-volatile setup
	+ Add support for LED indicator
	+ Add support for safe firmware update (TODO)
	# Add support for automatic lib update 
"""

import Blocky.Global
import Blocky.uasyncio as asyncio
from Blocky.Indicator import indicator 
from Blocky.Timer import runtime
from Blocky.Network import Network
loop = asyncio.get_event_loop()
from machine import idle , Timer 

wdt_timer = Timer(1)

def failsafe(source):
	try :
		if runtime() - network.last_call > 5000 :
			print('Yppppppppppppppppppppppppppppppppppppppppppppp')
			import os 
			try :
				f = open('user_code.py','w')
				f.close()
			except :
				pass
			from Blocky.Indicator import indicator
			for x in range(20):
				indicator.rgb[0] = (255,0,0)
				indicator.rgb.write()
				sleep_ms(50)
				indicator.rgb[0] = (0,0,0)
				indicator.rgb.write()
				sleep_ms(50)
			from machine import reset
			reset()
	except :
		print('Doooooooooooom')
		import os 
		try :
			f = open('user_code.py','w')
			f.close()
		except :
			pass
		from Blocky.Indicator import indicator
		from time import sleep_ms
		for x in range(20):
			indicator.rgb[0] = (255,0,0)
			indicator.rgb.write()
			sleep_ms(50)
			indicator.rgb[0] = (0,0,0)
			indicator.rgb.write()
			sleep_ms(50)
		from machine import reset
		reset()


network = None

#
#
#
# No matter what , start async routine 


from _thread import start_new_thread
def _master_routine():
	while True:
		try :
			loop.run_forever()
		except:
			pass

import micropython
import ssd1306
from machine import *
n = ssd1306.SSD1306_I2C(128,64,i)
adc = ADC( Pin(37))

adc.atten(ADC.ATTN_2_5DB)
from Blocky.Timer import runtime
import Blocky.Global
async def mem_watch():
	while True :
		gc.collect()
		n.fill(0)
		n.text('Heap:     ' + str(gc.mem_free()) , 0 , 0)
		n.text('Stack:    ' + str(micropython.stack_use()) , 0,10)
		n.text('Analog:    ' + str(adc.read()) , 0, 20)
		n.text('R : ' + str(runtime()),0,30)
		n.text('_' + Blocky.Global.error_mess,0,40)
		try :
			n.text('_' + network.last_call,0,50)
		except :
			pass
		n.show()
		await asyncio.sleep_ms(100)
loop.create_task(mem_watch())
  
print('uasyncio-> initialized>>>>>>>>>>>>>')
# ------------------------------------

async def service():
	while True :
		try :
			network.process()
			network.last_call = runtime()
			machine.idle()
		except :
			
			pass
		await asyncio.sleep_ms(200)
		if Blocky.Global.flag_UPCODE:
			Blocky.Global.flag_UPCODE = False
			loop.call_soon(run_user_code())
			
async def run_user_code():
	try :
		print('Run User Code')
		import ure
		lib_list = []
		regex = 'from Blocky\.\s*(\w*)\s*import\s*(\w*)\s*#\s*(\w*)'
		with open('user_code.py') as openfileobject:
			for line in openfileobject:
				matchObj = ure.match(regex , line)
				if matchObj:
					print( "Libray: ", matchObj.group(1))
					print( "Version : ", matchObj.group(3))
		
		del code
		wdt_timer.init(mode  = Timer.PERIODIC , period = 10000 , callback = failsafe)
		exec(open('./user_code.py').read(),globals())
	except MemoryError	:
		from Blocky.Indicator import indicator
		for x in range(10):
			indicator.rgb[0] = (255,0,0)
			indicator.rgb.write()
			sleep_ms(100)
			indicator.rgb[0] = (0,0,0)
			indicator.rgb.write()
			sleep_ms(100)
		print('Your code is dead , I kill it!')
		global network
		await network.log('Your code is dead , I kill it!')
		from machine import reset
		f = open('user_code.py','w')
		f.close()
		reset()


		
async def mainthread():
	
	try :	
		from ujson import loads
		config = loads(open('config.json').read())
		if not all(elem in list(config.keys()) for elem in ['auth_key','known_networks']):
			raise Exception
	except Exception:
		print('config->error . Start MainThread bootmode')
		from Blocky.BootMode import BootMode
		from Blocky.Indicator import indicator
		
		bootmode = BootMode()
		print('mainthread-> Booting')
		await bootmode.Start() 
		print('mainthread-> Boot Completed')
		error = True ; from machine import reset ; reset()
    
		
	global network
	network = Network()	
	loop.create_task(service())
	loop.create_task(network.connect())
	
	await asyncio.sleep_ms(200)
	loop.create_task(run_user_code())
	"""
	if Blocky.Global.flag_BOOTBLOCK :
		print('BAD CONFIG -> Start Boot mode')
		from Blocky.BootMode import bootmode
		from gc import collect , mem_free
		await bootmode.Start()
		loop.create_task(network.connect())
		loop.create_task(service() )
		#loop.create_task(thread_usercode())
		exec(open('user_code.py').read())
	else :
		print('Config -> OK')
		from Blocky.BootMode import bootmode
		loop.create_task(bootmode.Start() )
		loop.create_task(network.connect())
		loop.create_task(service() )
		
		exec(open('user_code.py').read())
	"""	

		
loop.create_task(mainthread())
#start_new_thread(loop.run_forever,())

while True :
	try :
		loop.run_forever()
	except Exception as err:
		print('mainloop->',err)
		
		import sys
		sys.print_exception(err)
		sleep_ms(3000)
		f = open('user_code.py','w')
		f.close()
		from Blocky.Indicator import indicator
		for x in range(20):
			indicator.rgb[0] = (255,0,0)
			indicator.rgb.write()
			sleep_ms(50)
			indicator.rgb[0] = (0,0,0)
			indicator.rgb.write()
			sleep_ms(50)
		from machine import reset
		reset()