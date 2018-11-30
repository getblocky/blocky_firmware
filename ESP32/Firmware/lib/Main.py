#version=2.0
import Blocky.Core as core
from BLocky.Indicator import indicator
core.indicator = indicator
core.mainthread = core.asyncio.get_event_loop()
core.gc.threshold(90000)
if 'user_code.py' not in core.os.listdir():
	f = open('user_code.py','w')
	f.close()
if 'config.json' not in core.os.listdir():
	f = open('config.json','w')
	f.close()
try :
	wdt_timer = core.machine.Timer(1)
except :
	pass	

def _failsafe(source):
	if core.Timer.runtime() - core.blynk.last_call > 20000 :
		if not core.wifi.wlan_sta.isconnected():
			print('[failsafe] -> wifi is so bad')
			return
		else :
			import os , machine,time
			print('[failsafe] -> removing user code')
			try :
				os.rename('user_code.py','temp_code.py')
			except :
				pass
			f = open('last_word.py','w')
			f.write('[warning] -> your code has been deleted because it stucks somewhere')
			f.close()
			for x in range(20):
				core.indicator.rgb.fill((255,0,0));core.indicator.rgb.write();time.sleep_ms(50)
				core.indicator.rgb.fill((0,0,0));core.indicator.rgb.write();time.sleep_ms(50)
			core.machine.reset()

async def run_user_code(direct = False):
	"""
		Pending library that need to be download will be downloaded first , it will yield back
	"""
	if direct == False and core.eeprom.get('LIB') != None :
		return 
	if core.os.stat('user_code.py')[6] == 0 :
		while not core.flag.blynk :
			await core.asyncio.sleep_ms(500)
		await core.indicator.rainbow()
		return
	else :
		await core.indicator.show(None)
	try :
		wdt_timer.deinit()
	except :
		pass
	
	""" 
		By defaults , the system will run user code and connecting at the same time
		Sometimes , these two task yield RuntimeError 
		Which will kill user code , wait for the network to connect and then re-run user_code
	"""
	if direct == True :
		print('[user-code] -> run directly')
		try :
			wdt_timer.init(mode=core.machine.Timer.PERIODIC,period=20000,callback = _failsafe)
		except :
			pass
		core.user_code = __import__('user_code')
		return 
		
	list_library = core.get_list_library('user_code.py')
	list_library_update = []
	for x in list_library:
		print('[library] -> checking {}'.format(x) , end = '')
		current_version = core.get_library_version(x[0])
		if current_version == None or current_version < x[1] :
			list_library_update.append(x[0])
			print(False)
		else :
			print(True)
			
	if len(list_library_update):
		core.eeprom.set('LIB',list_library_update)
		core.machine.reset()
		
	try :
		wdt_timer.init(mode=core.machine.Timer.PERIODIC,period=20000,callback = _failsafe)
	except :
		pass
	try :
		del core.sys.modules['user_code']
	except :
		pass
	core.gc.collect()
	print('[user_code] -> started with {} heap'.format(core.gc.mem_free()))
	try :
		core.user_code = __import__('user_code')
	except RuntimeError:
		del core.sys.modules['user_code']
		while not core.wifi.wlan_sta.isconnected() or core.flag.blynk == False:
			await core.asyncio.sleep_ms(500)
		core.mainthread.create_task(run_user_code(True))
		return
	except MemoryError:
		del core.sys.modules['user_code']
		print('[memory] -> removing user code')
		try :
			os.rename('user_code.py','temp_code.py')
		except :
			pass
		f = open('last_word.py','w')
		f.write('[warning] -> your code has been deleted because it use so much memory')
		f.close()
		for x in range(20):
			core.indicator.rgb.fill((255,0,0));core.indicator.rgb.write();sleep_ms(50)
			core.indicator.rgb.fill((0,0,0));core.indicator.rgb.write();sleep_ms(50)
		core.machine.reset()
	
async def send_last_word():
	if "last_word.py" in core.os.listdir():
		while not core.flag.wifi:
			await core.asyncio.sleep_ms(500)
		try :
			print('[lastword] -> {}'.format(open('last_word.py').read()))
			core.blynk.log(127,open('last_word.py').read(),http=True)
		except :
			pass
		core.os.remove('last_word.py')

async def main(online=False):
	if not core.cfn_btn.value():
		time = core.time.ticks_ms()
		print('Configure: ',end='')
		while not core.cfn_btn.value():
			core.time.sleep_ms(500)
			temp = ( core.time.ticks_ms() - time ) //1000
			if temp > 0 and temp < 5 :
				core.indicator.rgb.fill((0,25,0));core.indicator.rgb.write()
			if temp > 5 and temp < 10 :
				core.indicator.rgb.fill((25,0,0));core.indicator.rgb.write()
			if temp > 10:
				core.indicator.rgb.fill((255,0,0));core.indicator.rgb.write()
		time = core.time.ticks_ms() - time ; time = time//1000
		if time > 0 and time < 5 :
			from Blocky.BootMode import BootMode
			bootmode = BootMode()
			await bootmode.Start()
		if time > 5 and time < 10 :
			core.os.remove('user_code.py')
		if time > 10 and time < 15 :
			core.os.remove('user_code.py')
			core.os.remove('config.json')
			try :
				core.os.remove('Blocky/fuse.py')
			except:
				pass
		core.machine.reset()
	
	# 
	try :
		core.config = core.json.loads(open('config.json').read())
		if not all(elem in list(core.config.keys()) for elem in ['token','known_networks']):
			raise Exception
		if len(core.config['token']) == 0 or len(core.config['known_networks'])==0:
			raise Exception
			
	except Exception as err:
		core.sys.print_exception(err)
		print('[config] -> error , init bootmode')
		from Blocky.BootMode import BootMode
		bootmode = BootMode()
		await bootmode.Start()
		core.machine.reset()
		
	# Offline operation , press config to be back online
	if core.eeprom.get('OFFLINE') == True and core.eeprom.get('OTA_LOCK') == True :
		def back_online(s):
			core.mainthread.call_soon(main(True))
			core.cfn_btn.irq(trigger=0)
		core.cfn_btn.irq(trigger = core.machine.Pin.IRQ_FALLING , handler = back_online)
		print('running offline mode ! press config to be back online')
		core.user_code = __import__('user_code')
		return
		
	print('[wifi] -> connecting')
	core.wifi = __import__('Blocky/wifi')
	from BLocky.BlynkLib import Blynk
	core.blynk = Blynk(core.config['token'],ota = run_user_code)
	core.mainthread.create_task(send_last_word())
	core.mainthread.create_task(run_user_code())
	core.mainthread.create_task(core.Timer.alarm_service())
	while True :
		await core.asyncio.sleep_ms(500)
		if not core.wifi.wlan_sta.isconnected():
			print('[wifi] -> connecting back',end='')
			await core.wifi.connect(core.config['known_networks'])
			print('OK')
			if core.eeprom.get('LIB')!= None:
				print('[library] -> downloading list {}'.format(core.eeprom.get('LIB')))
				for x in core.eeprom.get('LIB'):
					core.download(x+'.py','Blocky/{}.py'.format(x))
				core.eeprom.set('LIB',None)
				core.mainthread.create_task(run_user_code(True))
			print('[blynk] -> connecting back')
			core.mainthread.create_task(core.blynk.run())
			while not core.flag.blynk:
				await core.asyncio.sleep_ms(500)
			print('You are back online :) Happy Blynking')
		if core.flag.blynk == False :
			print('[blynk] -> connecting back now')
			core.mainthread.create_task(core.blynk.run())
			while not core.flag.blynk:
				await core.asyncio.sleep_ms(500)
			print('[blynk] -> back online')

def wrapper():
	while True :
		try :
			core.mainthread.run_forever()
		except Exception as err :
			core.sys.print_exception(err)
			core.time.sleep_ms(1000)

core.blynk = None
core.mainthread.create_task(main())
wrapper()
#core._thread.start_new_thread(wrapper,())
			
	
	
		
			
	