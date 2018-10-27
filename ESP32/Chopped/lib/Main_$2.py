machine.reset()
			else :
				print("[LIB_PENDING]")
				return
			
		try :
			wdt_timer.init(mode=core.machine.Timer.PERIODIC,period=30000,callback = failsafe)
			#print("User's watchdog initialized")
		except :
			pass
		
		try :
			del core.sys.modules['user_code']
		except Exception as err:
			print('[OTA] Delete previous memory footprint failed',err)
			pass
		core.gc.collect()
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
		except ImportError :
			print("[IMPORT_ENOMEM]")
			core.machine.reset()
				
	except MemoryError:
		print('Blocky is now rebooting')
		import os , neopixel , time , machine 
		os.rename('user_code.py','temp_code.py')
		n = neopixel.NeoPixel(machine.Pin(5) , 1)
		for x in range(20):
			n[0] = (255,0,0);n.write();time.sleep_ms(50)
			n[0] = (0,0,0);n.write();time.sleep_ms(50)
		try :
			f = open('last_word.py' , 'w')
			f.write('Your code use too much memory,Blocky have to kill it')
			f.close()
		except:
			pass
		machine.reset()
					
async def send_last_word():
	if "last_word.py" in core.os.listdir():
		while not core.flag.wifi :
			await core.asyncio.sleep_ms(500)
		try :
			print("Last word = " , open('last_word.py').read())
			core.blynk.log(127,open('last_word.py').read(),http=True)
		except :
			pass
		try :
			print('removed last word')
			core.os.remove('last_word.py')
		except :
			print('cant remoce')
					
async def main(online=False):
	if not core.cfn_btn.value():
		time = core.time.ticks_ms()
		print('Configure:',end = '')
		while  not core.cfn_btn.value():
			print('#' , end = '')
			await core.asyncio.sleep_ms(500)
			temp = ( core.time.ticks_ms(