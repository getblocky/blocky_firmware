close()
			
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
		core.user_code = __import__('user_code')
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
