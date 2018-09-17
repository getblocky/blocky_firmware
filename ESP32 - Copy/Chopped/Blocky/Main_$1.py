================================================
print('uasyncio-> initialized>>>>>>>>>>>>>')
# ------------------------------------

async def service():
	while True :
		try :
			core.network.process()
			core.network.last_call = core.Timer.runtime()
			core.machine.idle()
		except Exception as err:
			print('service->', err)
		await core.asyncio.sleep_ms(200)
		if core.flag.UPCODE:
			core.flag.UPCODE = False
			core.mainthread.call_soon(run_user_code())
			
async def run_user_code():
	try :
		wdt_timer.deinit()
		print('Run User Code')
		lib_list = []
		"""
		with open('user_code.py') as openfileobject:
			for line in openfileobject:
				matchObj = ure.match(regex , line)
				if matchObj:
					print( "Libray: ", matchObj.group(1))
					print( "Version : ", matchObj.group(3))
		"""
		"""
		with open('user_code.py') as file :
			for line in file :
				if line.startswith('from '):
					library = line.split(' ')[1]
					version = ''
					pos = line.find('#')
					if pos != -1:
						version = line[pos:]
				print('Library ' ,library , version )
		"""
		list_library = []
		file = [] #line by line of the file , memory fragmentation !
		f = open('user_code.py','r')
		eof = False
		while eof == False :
			line = ''
			while True :
				temp = f.read(1)
				if len(temp) == 0 :
					eof = True ; break 
				line += temp 
				if temp == '\r':
					break
			file.append(line)
		print('UserCode #Line=',len(file))
		f.close()
		for x in range(len(file)):
			if file[x].find('from ')==0:
				print('Start')
				library = ''
				library = file[x].split(' ')[1]
				
				version = 0.0
				pos = file[x].find('#')
				if pos != -1:
					version = float(file[x][pos:])
				print('Library ' ,library , version )
				try :
					f = open('Blocky/'+library+'.py')
					a = ''
					a = f.readline()
					if not a.startswith('#version '):
						a = 0.0
					else :
						a = float(version.split('=')[1])
					
				except :
					a = 0.0
				if version > a :
					list_library.append(library)
		if len(l