y'):
		return None
	line = ''
	f = open('Blocky/{}.py'.format(lib))
	while True :
		temp = f.read(1)
		if len(temp) == 0 or temp == '\n' or temp == '\r':
			break
		line += temp
	# #version=1.0
	if not line.startswith('#version'):
		f.close()
		return 0.0
	f.close()
	return float(line.split('=')[1])
	
