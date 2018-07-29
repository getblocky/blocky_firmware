def getPin(port):
	if  isinstance(port,int):
		return [port,port,port]
	if isinstance(port,tuple):
		return port
	if isinstance(port , str):
		# Shield 
		if port == 'A1': return None,22,34;
		elif port == 'A2':return None ,23,35;
		elif port == 'A3':return 32 ,16,32;
		elif port == 'A4':return 33 ,4,33;
		elif port == 'D1':return 27 ,19,None;
		elif port == 'D2':return 13 ,17,None;
		elif port == 'D3':return 14 ,18,None;
		elif port == 'D4':return 25 ,26,None;
		# Cirle Board
		elif port == 'PORT1':return 25 ,26,36;
		elif port == 'PORT2':return 27 ,14,37;
		elif port == 'PORT3':return 13 ,15,38;
		elif port == 'PORT4':return 4  ,16,39;
		elif port == 'PORT5':return 32 ,17,32;
		elif port == 'PORT6':return 33 ,18,33;
		elif port == 'PORT7':return 23 ,19,34;
		elif port == 'PORT8':return 22 ,21,35;
		
	else :return None ,None,None;