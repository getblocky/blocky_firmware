 + str(x), end = '')
					response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/'+x+'.py')
					if response.status_code == 200 :
						f = open('Blocky/'+x+'.py','w')
						f.write(response.content)
						print('#',end = '')
						piece = 0
						while True :
							piece += 1
							response = None
							core.gc.collect()
							try :
								response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/'+x + '_$' + str(piece) +'.py')
								if response.status_code == 200 :
									f.write(response.content)
									print('#' , end = '')
								else :
									raise Exception
							except Exception :
								print('Pieces = ' , piece)
								f.close()
								break 
					else :
						print('Library ' , x , 'not found on server')
				except Exception as err:
					import sys
					sys.print_exception(err)
					print('Failed')
			
			del response
			core.gc.collect()
			
			
		try :
			#wdt_timer.init(mode=core.machine.Timer.PERIODIC,period=10000,callback = failsafe)
			print("User's watchdog initialized")
		except :
			pass
		
		try :
			del core.sys.modules['user_code']
		except :
			pass
			
		print('Starting Usercode with ' , core.gc.mem_free())
		try :
			core.user_code = __import__('user_code')
		except RuntimeError:
			print('User RuntimeError , will run after connected to Blynk')
			del core.sys.modules['user_code']
			while core.wifi.wlan_sta.isconnected() == False or core.flag.blynk == False :
				await core.asyncio.sleep_ms(500)
			print('Start user code')
			core.mainthread.create_task(run_user_code(True))
				
				
	except MemoryError:
		print('Blocky is now rebooting')
		import os , neopixel , time , machine 
		os.rename('user_code.py','temp_code.py')
		n = neopixel.NeoPixel(machine.Pin(5) , 1)
		for x in range(20):
			n[0] = (255,0,0);n.write();time.sleep_ms(50)
			n[0] = (0,0,0);n.write();time.sleep_ms(50)
		try :
			f = open('last_word.py' , 