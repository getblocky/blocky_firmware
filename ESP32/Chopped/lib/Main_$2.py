0
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
	