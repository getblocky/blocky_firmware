syn.NamedTask.is_running (name):
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
					response = urequests.get('https://raw.githubusercontent.com/getblocky/dot_firmware/master/ota/{}_${}.{}'.format(filename.split('.')[0] , piece , filename.split('.')[1]))   
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
	
def get_list_library(file):
	f = open(file)
	cell = ''
	while True :
		cell += f.read(1)
		if cell[-2:] == '\n\n':
			break
	cell = cell.split('\n')
	r = []
	for line in cell :
		library = ''
		version = 0.0
		#from Blocky.STH import * #version=1.0
		if line.startswith('from '):
			library = line.split('.')[1].split(' ')[0]
			if '#version' in line :
				version = float(line.split('=')[1])
			r.append([library,version])
	f.close()
	return r
	
def get_library_version(lib):
	if '{}.py'.format(lib) not in os.listdir('Block