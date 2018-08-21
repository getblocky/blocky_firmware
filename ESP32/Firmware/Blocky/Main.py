
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
#========================================================================
print('uasyncio-> initialized>>>>>>>>>>>>>')
# ------------------------------------

async def service():
	while True :
		try :
			core.network.process()
			core.network.last_call = core.Timer.runtime()
			core.machine.idle()
		except Exception as err:
			print('service->', err)
		await core.asyncio.sleep_ms(200)
		if core.flag.UPCODE:
			core.flag.UPCODE = False
			core.mainthread.call_soon(run_user_code())
			
async def run_user_code():
	try :
		wdt_timer.deinit()
		print('Run User Code')
		lib_list = []
		"""
		with open('user_code.py') as openfileobject:
			for line in openfileobject:
				matchObj = ure.match(regex , line)
				if matchObj:
					print( "Libray: ", matchObj.group(1))
					print( "Version : ", matchObj.group(3))
		"""
		"""
		with open('user_code.py') as file :
			for line in file :
				if line.startswith('from '):
					library = line.split(' ')[1]
					version = ''
					pos = line.find('#')
					if pos != -1:
						version = line[pos:]
				print('Library ' ,library , version )
		"""
		list_library = []
		file = [] #line by line of the file , memory fragmentation !
		f = open('user_code.py','r')
		eof = False
		while eof == False :
			line = ''
			while True :
				temp = f.read(1)
				if len(temp) == 0 :
					eof = True ; break 
				line += temp 
				if temp == '\r':
					break
			file.append(line)
		print('UserCode #Line=',len(file))
		f.close()
		for x in range(len(file)):
			if file[x].find('from ')==0:
				print('Start')
				library = ''
				library = file[x].split(' ')[1]
				
				version = 0.0
				pos = file[x].find('#')
				if pos != -1:
					version = float(file[x][pos:])
				print('Library ' ,library , version )
				try :
					f = open('Blocky/'+library+'.py')
					a = ''
					a = f.readline()
					if not a.startswith('#version '):
						a = 0.0
					else :
						a = float(version.split('=')[1])
					
				except :
					a = 0.0
				if version > a :
					list_library.append(library)
		if len(list_library):
			for x in list_library:
				core.gc.collect()
				print('Libray ' , x , 'Required -> Updating ')
				c = core.urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Firmware/lib/' + x + '.py')
				if c.status_code == 200 :
					f = open('Blocky/'+x,'w')
					f.write(c.content)
					f.close()
					
			
					
		try :
			wdt_timer.init(mode  = core.machine.Timer.PERIODIC , period = 20000 , callback = failsafe)
		except :
			pass
		#exec(open('./user_code.py').read(),globals())
		# Memory fragmentation !
		try :
			del core.sys.modules['user_code']
		except:
			pass
		usercode  = __import__('user_code')
	except MemoryError	:
		from Blocky.Indicator import indicator
		for x in range(10):
			core.indicator.rgb[0] = (255,0,0)
			core.indicator.rgb.write()
			core.time.sleep_ms(100)
			core.indicator.rgb[0] = (0,0,0)
			core.indicator.rgb.write()
			core.time.sleep_ms(100)
		print('Your code is dead , I kill it!')
		await core.network.log('Your code is dead , I kill it!')
		f = open('user_code.py','w')
		f.close()
		core.machine.reset()


		
async def mainthread():
	
	try :	
		config = core.json.loads(open('config.json').read())
		if not all(elem in list(config.keys()) for elem in ['auth_key','known_networks']):
			raise Exception
	except Exception:
		print('config->error . Start MainThread bootmode')
			
		bootmode = core.BootMode.BootMode()
		print('mainthread-> Booting')
		await bootmode.Start() 
		print('mainthread-> Boot Completed')
		error = True 
		core.machine.reset()
	from Blocky.Network import Network
	core.network = Network()	
	core.mainthread.create_task(service())
	core.mainthread.create_task(core.network.connect())
	
	await core.asyncio.sleep_ms(200)
	core.mainthread.create_task(run_user_code())
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

		
core.mainthread.create_task(mainthread())


if THREADED :
	core._thread.start_new_thread(core.mainthread.run_forever,())
else :
	while True :
		try :
			core.mainthread.run_forever()
		except Exception as err:
			print('mainloop->',err)
			await core.network.log('Your code just crashed ! ' + str(err))
			core.sys.print_exception(err)
			core.time.sleep_ms(3000)
			f = open('user_code.py','w')
			f.close()
			for x in range(20):
				core.indicator.rgb[0] = (255,0,0)
				core.indicator.rgb.write()
				core.time.sleep_ms(50)
				core.indicator.rgb[0] = (0,0,0)
				core.indicator.rgb.write()
				core.time.sleep_ms(50)
			core.machine.reset()

