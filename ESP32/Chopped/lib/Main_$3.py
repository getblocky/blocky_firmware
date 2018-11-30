leep_ms(500)
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
			
	
	
		
			
	