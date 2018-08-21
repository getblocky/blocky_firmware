
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

import Blocky.Core as core

core.mainthread = core.asyncio.get_event_loop()
from Blocky.Indicator import indicator
core.indicator = indicator
wdt_timer = core.machine.Timer(1)

def failsafe(source):
	try :
		if core.Timer.runtime() - core.network.last_call > 5000 :
			print('Yppppppppppppppppppppppppppppppppppppppppppppp')
			try :
				f = open('user_code.py','w')
				f.close()
			except :
				pass
			
			core.machine.reset()
	except :
		print('Doooooooooooom')
		try :
			f = open('user_code.py','w')
			f.close()
		except :
			pass
		for x in range(20):
			core.indicator.rgb[0] = (255,0,0)
			core.indicator.rgb.write()
			core.time.sleep_ms(50)
			core.indicator.rgb[0] = (0,0,0)
			core.indicator.rgb.write()
			core.time.sleep_ms(50)
		core.machine.reset()




# developer sector , delete afterfinish\
#=================================================================
import ssd1306
n = ssd1306.SSD1306_I2C(128,64,core.machine.I2C (scl = core.machine.Pin(26,core.machine.Pin.IN,\
core.machine.Pin.PULL_UP) , sda = core.machine.Pin(25,core.machine.Pin.IN,core.machine.Pin.PULL_UP)))
adc = core.machine.ADC( core.machine.Pin(37))
adc.atten(core.machine.ADC.ATTN_2_5DB)
async def mem_watch():
	while True :
		core.gc.collect()
		n.fill(0)
		n.text('Heap:     ' + str(core.gc.mem_free()) , 0 , 0)
		n.text('Stack:    ' + str(core.micropython.stack_use()) , 0,10)
		n.text('Analog:    ' + str(adc.read()) , 0, 20)
		n.text('R : ' + str(core.Timer.runtime()),0,30)
		try :
			n.text('_' + core.network.last_call,0,50)
		except :
			pass
		n.show()
		await core.asyncio.sleep_ms(100)
core.mainthread.create_task(mem_watch())
#========================