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

