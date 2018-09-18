er
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

# Disable 2 _thread will save 16K RAM

