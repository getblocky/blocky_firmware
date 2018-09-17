import Blocky.Core as core
from Blocky.Indicator import indicator

core.indicator = indicator
core.mainthread = core.asyncio.get_event_loop()


if 'user_code.py' not in core.os.listdir():
	f = open('user_code.py','w')
	f.close()
if 'config.json' not in core.os.listdir():
	f = open('config.json','w')
	f.close()

# This timer will trigger a reset
# if user code use the mainthread too long 
try :
	wdt_timer = core.machine.Timer(1)
except :
	pass
	
def failsafe(source):
	try :
		if core.Timer.runtime() - core.blynk.last_call > 10000 :
			print('Usercode is so bad')
			import os , machine 
			try :
				os.rename('user_code.py' , 'temp_code.py')
				
			except :
				pass
				
			try :
				f = open('last_word.py' , 'w')
				f.write('Your code seem to block the mainthread,Blocky have to kill it')
				f.close()
			except:
				pass
			core.machine.reset()
	# Due to MemoryError or because reference has been deleted	
	except : 
		
		print('Blocky is now rebooting')
		import os , neopixel , time , machine 
		os.rename('user_code.py','temp_code.py')
		n = NeoPixel(Pin(5) , 1)
		for x in range(20):
			n[0] = (255,0,0);n.write();time.sleep_ms(50)
			n[0] = (0,0,0);n.write();time.sleep_ms(50)
		try :
			f = open('last_word.py' , 'w')
			f.write('Your code have some error,Blocky have to kill it')
			f.close()
		except:
			pass
		machine.reset()
		
		
async def run_user_code(direct = False):
	if direct == True :
		user_code = __import__('user_code')
		return 
		
	await core.asyn.Cancellable.cancel_all()
	print('Run User_code')
	try:
		wdt_timer.deinit()
	except :
		pass
	
	print('Checking library file')
	
	# Why am I doing this huh ?
	# We can use readlines() or readline() right
	# uPython user continuous memory region for readlines() -> MemoryError
	# uPython readline() use different newline syntax !
	# uPython's regex use recursive while max stack = 39
	# Damn right =))
	
	list_library = []
	try :
		f = open('user_code.py')
		eof = False
		while eof == False :
			line = ''
			while True :
				temp = f.read(1)
				if len(temp) == 0:
					eof = True
					break
				line += temp
				if temp == '\r' or temp == '\n':
					break 
				
				# Parse line by line :((
				
			if line.startswith('from '):
				library = line.split(' ')[1]
				if library.startswith('Blocky.'):
					library = line.split('.')[1].split(' ')[0]
					
					try :
						version = float(line.split('#version=')[1])
					except :
						if not library + '.py' in core.os.listdir('Blocky'):
							if library not in list_library:
								list_library.append(library)
							print('Library '+library+' need to be downloaded')
							continue
						print('Library '+library+' is kept')
						continue
						
					# Version is known
					try :
						l = open('Blocky/'+library+'.py')
						current_version = ''
						while True :
							
							temp = l.read(1)
							if temp == '\r' or temp == '\n':
								break
							current_version += temp
							print('CurrentVersion=' , current_version)
							try :
								current_version = float(current_version.split('=')[1])
							except:
								current_version = 0.0
								
							if current_version < version :
								print('Library',library,'is outdated',current_version)
								if library not in list_library:
									list_library.append(library)
						l.close()		
					except :
						if library not in list_library:
							list_library.append(library)
						print('Library' , library , 'is weird')
						
		f.close()		
		
		if len(list_library):
			print('Updating List -----')
			print(list_library , end = '\r\n')
			
			while not core.wifi.wlan_sta.isconnected():
				await core.asyncio.sleep_ms(500)
			
			print('Wifi Connected , Start downloading library')
			import urequests
			for x in list_library:
				response = None
				core.gc.collect()
				try :
					print('Updating Library -> ' + str(x), end = '')
					response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/'+x+'.py')
					if response.status_code == 200 :
						f = open('Blocky/'+x+'.py','w')
						f.write(response.content)
						print('#',end = '')
						piece = 0
						while True :
							piece += 1
							response = None
							core.gc.collect()
							try :
								response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/'+x + '_$' + str(piece) +'.py')
								if response.status_code == 200 :
									f.write(response.content)
									print('#' , end = '')
								else :
									raise Exception
							except Exception :
								print('Pieces = ' , piece)
								f.close()
								break 
					else :
						print('Library ' , x , 'not found on server')
				except Exception as err:
					import sys
					sys.print_exception(err)
					print('Failed')
			
			del response
			core.gc.collect()
			
			
		else :
			try :
				#wdt_timer.init(mode=core.machine.Timer.PERIODIC,period=10000,callback = failsafe)
				print("User's watchdog initialized")
			except :
				pass
			
			try :
				del core.sys.modules['user_code']
			except :
				pass
				
			print('Starting Usercode with ' , core.gc.mem_free())
			try :
				user_code = __import__('user_code')
			except RuntimeError:
				print('User RuntimeError , will run after connected to Blynk')
				del core.sys.modules['user_code']
				while core.wifi.wlan_sta.isconnected() == False or core.flag.blynk == False :
					await core.asyncio.sleep_ms(500)
				print('Start user code')
				core.mainthread.create_task(run_user_code(True))
				
				
	except MemoryError:
		print('Blocky is now rebooting')
		import os , neopixel , time , machine 
		os.rename('user_code.py','temp_code.py')
		n = neopixel.NeoPixel(machine.Pin(5) , 1)
		for x in range(20):
			n[0] = (255,0,0);n.write();time.sleep_ms(50)
			n[0] = (0,0,0);n.write();time.sleep_ms(50)
		try :
			f = open('last_word.py' , 'w')
			f.write('Your code use too much memory,Blocky have to kill it')
			f.close()
		except:
			pass
		machine.reset()
					
async def send_last_word():
	if "last_word.py" in core.os.listdir():
		while not core.wifi.wlan_sta.isconnected() or not core.flag.blynk:
			await core.asyncio.sleep_ms(500)
		core.blynk.virtual_write(127,open('last_word.py').read())
		core.os.remove('last_word.py')
					
async def main(online=False):
	if not core.cfn_btn.value():
		time = core.time.ticks_ms()
		print('Configure:',end = '')
		while not core.cfn_btn.value():
			print('#' , end = '')
			core.time.sleep_ms(500)
		time = core.time.ticks_ms() - time
		time = time//1000
		if time > 0 and time < 5 :
			from Blocky.BootMode import BootMode
			bootmode = BootMode()
			await bootmode.Start()
		if time >= 5 and time < 10 :
			f = open('user_code.py','w')
			f.close()
			
	try :
		core.config = core.json.loads(open('config.json').read())
		if not all(elem in list(core.config.keys()) for elem in ['token','known_networks']):
			raise Exception
	except Exception as err :
		import sys
		sys.print_exception(err)
		print('Config->Error , Start Setup mode')
		bootmode = core.BootMode.BootMode()
		print('mainthread-> Booting')
		await bootmode.Start() 
		print('mainthread-> Boot Completed')
		core.machine.reset()
	
	if core.eeprom.get('OFFLINE') == True and core.eeprom.get('OTA_LOCK') == True:
		def clean_up (s):
			try :
				del core.sys.modules['Blocky/user_code']
			except :
				pass
			core.mainthread.call_soon(main(True))
			core.cfn_btn.irq(trigger=0)
		core.cfn_btn.irq(trigger=core.machine.Pin.IRQ_FALLING,handler = clean_up)
		user_code = __import__('user_code')
		return
		
	core.wifi = __import__('Blocky/wifi')
	from Blocky.BlynkLib import Blynk
	core.blynk = Blynk(core.config['token'],ota = run_user_code)		
	# There are some DeviceLog that cant be send
	core.mainthread.create_task(send_last_word())
	core.mainthread.create_task(run_user_code())
	#Routine check of connection to server
	while True :
		await core.asyncio.sleep_ms(500)
		# Recover from wifi jittering
		if not core.wifi.wlan_sta.isconnected():
			print('Oh Wow , wifi is disconnected , Connecting back')
			await core.wifi.connect(core.config['known_networks'])
			print('Wifi is on , connecting to Blynk')
			await core.asyncio.sleep_ms(500)
			core.mainthread.create_task(core.blynk.run())
			while not core.flag.blynk :
				await core.asyncio.sleep_ms(500)
			print('You are back online bro')
		# Recover from Blynk disconnect problem
		if core.flag.blynk == False  :
			print('Blynk disconnected somehow')
			core.mainthread.create_task(core.blynk.run())
			while not core.flag.blynk:
				await core.asyncio.sleep_ms(500)
			print('Blynk is back !')
			
		
#	To avoid random crash due to random error 
# 	This wrapper make sure that it keep running
def wrapper ():
	while True :
		try :
			core.mainthread.run_forever()
		except Exception as err:
			print('Wrapper->Error | ',end = '')
			import sys
			sys.print_exception(err)
			core.time.sleep_ms(1000)
			



core.blynk = None
core.mainthread.create_task(main())
core._thread.start_new_thread(wrapper,())

