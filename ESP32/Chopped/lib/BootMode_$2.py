ks = []
		raw = self.wlan_sta.scan()
		for nw in raw:
			networks.append({'ssid': nw[0].decode('ascii'), 'rssi': nw[3]})
		
		content = core.json.dumps(networks)
		print(len(networks) , 'networks detected')
		httpResponse.WriteResponseOk(headers = None,contentType= "application/json",contentCharset = "UTF-8",content = content)
		
	async def Start(self):
		
		#This function will run config boot mode in background ! 
		#As an replacement for ConfigManager.py
		#When a network call is erro , it will create this task in 
		#main thread as an async function 
		#As such , this won't block
		
		core.gc.collect()
		if core.gc.mem_free() < 20000 :
			core.machine.reset()
		
		
		
		server = None 
		id = core.binascii.hexlify(core.machine.unique_id()).decode('ascii')
		uuid = [id[i:i+2] for i in range(0, len(id), 2)]

		max_index = 0 ; max_value = 0
		for x in range(6):
		  if int(uuid[x],16) > max_value:
			max_value = int(uuid[x],16)
			max_index = x
			
		# Try to make an color indicator for which is which 
		# Blocky that shine red will be 'Blocky RED <uuid>'
		color = []
		if max_index == 0 : color = ['red',(255,59,48)]
		if max_index == 1 : color = ['green',(76,217,100)]
		if max_index == 2 : color = ['blue',(0,122,255)]
		if max_index == 3 : color = ['pink',(255,45,85)]
		if max_index == 4 : color = ['purple',(88,86,214)]
		if max_index == 5 : color = ['yello',(255,204,0)]
			
		if core.eeprom.get('first_start') == 1:
			core.mainthread.create_task(core.indicator.rainbow(core.flag.ONLINE,100,1) )# when Blocky.Global.flag_ONLINE is True , it stop
			ap_name = "It's me , your " + color[0].upper() + ' Blocky'
		else :
			core.mainthread.create_task(core.indicator.heartbeat( color[1] , 1 ,core.flag.wifi , 5) )
			ap_name = 'Blocky ' + color[0].upper() +' '+ core.binascii.hexlify(core.machine.unique_id()).decode('ascii')[0:4]
		
		print(ap_name)
		
		
		ap_password = ''
		wifi_status = 0
		
		
		#-------------------------------------------------
		
		#----------------------