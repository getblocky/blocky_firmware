.get_list_library('user_code.py')
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
			temp = ( core.time.ticks_ms() 