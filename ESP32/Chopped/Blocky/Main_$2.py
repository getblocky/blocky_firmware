ist_library):
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
	