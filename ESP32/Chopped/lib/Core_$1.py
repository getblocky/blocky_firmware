_running (name):
				await asyncio.sleep_ms(10)
	#mainthread.call_soon(asyn.NamedTask(name,function))
	if function != None :
		print('[CALLING] {} -> {}  DONE '.format(name,function))
		mainthread.call_soon( asyn.NamedTask(name,function) ())
		# Avoid pend throw for just stated-generator
		await asyncio.sleep_ms(0)
	else :
		print('[CANCEL] {}'.format(name))
	
	
	

def download(filename , path):
	response = None
	gc.collect()
	try :
		print('[Downloading]  File -> ' + str(filename), end = '')
		response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/{}'.format(filename))
		if response.status_code == 200 :
			f = open('temp.py','w')
			f.write(response.content)
			print('#',end = '')
			piece = 0
			while True :
				piece += 1
				response = None
				gc.collect()
				try :
					response = urequests.get('https://raw.githubusercontent.com/getblocky/blocky_firmware/master/ESP32/Chopped/lib/{}_${}.{}'.format(filename.split('.')[0] , piece , filename.split('.')[1]))   
					if response.status_code == 200 :
						f.write(response.content)
						print('#' , end = '')
					else :
						raise Exception
				except Exception :
					print('Pieces = ' , piece)
					f.close()
					os.rename('temp.py' , path)
					break 
		else :
			print('[Download] Failed . Library ' , filename , 'not found on server')
	except Exception as err:
		import sys
		sys.print_exception(err)
		print('Failed')
	
	del response
	gc.collect()
