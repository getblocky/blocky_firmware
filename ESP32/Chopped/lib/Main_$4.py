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

