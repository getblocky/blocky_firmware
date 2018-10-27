eadlines() or readline() right
	# uPython user continuous memory region for readlines() -> MemoryError
	# uPython readline() use different newline syntax !
	# uPython's regex use recursive while max stack = 39
	# Damn right =))
	
	list_library = []
	try :
		f = open('user_code.py')
		eof = False
		while eof == False :
			line = ''
			while True :
				temp = f.read(1)
				if len(temp) == 0:
					eof = True
					break
				line += temp
				if temp == '\r' or temp == '\n':
					break 
				
				# Parse line by line :((
				
			if line.startswith('from '):
				library = line.split(' ')[1]
				if library.startswith('Blocky.'):
					library = line.split('.')[1].split(' ')[0]
					
					try :
						version = float(line.split('#version=')[1])
					except :
						if not library + '.py' in core.os.listdir('Blocky'):
							if library not in list_library:
								list_library.append(library)
							print('Library '+library+' need to be downloaded')
							continue
						print('Library '+library+' is kept')
						continue
						
					# Version is known
					try :
						l = open('Blocky/'+library+'.py')
						current_version = ''
						while True :
							temp = l.read(1)
							
							if temp == '\r' or temp == '\n':
								try :
									current_version = float(current_version.split('=')[1])
								except:
									current_version = 0.0
								
								if current_version < version :
									print('Library',library,'is outdated',current_version)
									if library not in list_library:
										list_library.append(library)
									
									print('CurrentVersion=' , current_version)
								break
							else :
								current_version += temp
								
							
						l.close()		
					except :
						if library not in list_library:
							list_library.append(library)
						print('Library' , library , 'is weird')
						
		f.close()		
		
		if len(list_library):
			if core.eeprom.get('LIB') == None :
				core.eeprom.set('LIB' , list_library)
				print("[LIBRARY_UPDATE]")
				core.