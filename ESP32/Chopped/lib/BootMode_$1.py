orks'] = [{'ssid': request_json['ssid'], 'password': request_json['password']}]
			else:
				exist_ssid = None
				for n in config['known_networks']:
					if n['ssid'] == request_json['ssid']:
						exist_ssid = n
						break
				if exist_ssid:
					exist_ssid['password'] = request_json['password'] # update WIFI password
					print('Update wifi password')
				else:
					# add new WIFI network
					config['known_networks'].append({'ssid': request_json['ssid'], 'password': request_json['password']})
					print('Add new network')
			if len(request_json['token']):
				config['token'] = request_json['token']
			
			f = open('config.json', 'w')
			f.write(core.json.dumps(config))
			f.close()
			core.flag.wifi = True
			print('Get check status request ->',end = '')
			
			httpResponse.WriteResponseOk(headers = None,
				contentType	 = "text/html",
				contentCharset = "UTF-8",
				content = 'OK')
			if content == 'OK':
				print('completed')
				self.server.setup_success()
		else :
			core.flag.wifi = False
			print('.' , end = '')
			httpResponse.WriteResponseOk(headers = None,
				contentType	 = "text/html",
				contentCharset = "UTF-8",
				content = 'Failed')
		
		"""
		if self.wifi_status == 1:
			print('Wait for rebooting')
			time.sleep(5)
			print('Rebooting')
			machine.reset()
		"""

	def _httpHandlerSaveConfig(self, httpClient, httpResponse):
		request_json  = ''
		request_json = core.json.loads(httpClient.ReadRequestContent().decode('ascii'))
		self.wifi_status = 0
		httpResponse.WriteResponseOk(headers = None,contentType= "text/html",	contentCharset = "UTF-8",content = 'OK')
		self.wlan_sta.connect(request_json['ssid'], request_json['password'])
		
		#
		while not self.wlan_sta.isconnected() :
			core.time.sleep_ms(100)
			print('.',end = '')
		core.machine.reset()
		#
		
		print('client->saveconfig: Trying to connect to ' + str(request_json) , end = '')
		# we cant wait until the network to be connect here !
	def is_ascii(self, s):
		return all(ord(c) < 128 