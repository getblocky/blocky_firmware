) - time ) //1000
			if temp > 0 and temp < 5 :
				core.mainthread.call_soon(core.indicator.heartbeat( (0,100,0) , 1 , core.cfn_btn.value() ))
			if temp > 5 and temp < 10 :
				core.mainthread.call_soon(core.indicator.heartbeat( (100,0,0) , 1 , core.cfn_btn.value() ))
				
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
		core.BootMode = __import__('Blocky/BootMode')
		bootmode = core.BootMode.BootMode()
		print('mainthread-> Booting')
		await bootmode.Start() 
		print('mainthread-> Boot Completed')
		core.machine.reset()
	print('[CONFIG] -> Loaded')
	if core.eeprom.get('OFFLINE') == True and core.eeprom.get('OTA_LOCK') == True:
		def clean_up (s):
			try :
				del core.sys.modules['Blocky/user_code']
			except :
				pass
			core.mainthread.call_soon(main(True))
			core.cfn_btn.irq(trigger=0)
		core.cfn_btn.irq(trigger=core.machine.Pin.IRQ_FALLING,handler = clean_up)
		print('[MAIN] -> Running offline mode')
		core.user_code = __import__('user_code')
		return
	print('[WIFI] -> Loaded')
	core.wifi = __import__('Blocky/wifi')
	from Blocky.BlynkLib import Blynk
	print('[BLYNK] -> Loaded')
	core.blynk = Blynk(core.config['token'],ota = run_user_code)		
	# There are some DeviceLog that cant be send
	core.mainthread.create_task(send_last_word())
	core.mainthread.create_task(run_user_code())
	core.mainthread.create_task(core.Timer.alarm_service())
	#Routine check of connection to server
	while True :
		await core.asyncio.sleep_ms(500)
		# Recover from wifi jittering
		if not core.wifi.wl