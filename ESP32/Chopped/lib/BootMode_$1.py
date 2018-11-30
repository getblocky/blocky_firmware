equest_json = core.json.loads(httpClient.ReadRequestContent().decode('ascii'))
		self.wifi_status = 0
		httpResponse.WriteResponseOk(headers = None,contentType= "text/html",	contentCharset = "UTF-8",content = 'OK')
		self.wlan_sta.connect(request_json['ssid'], request_json['password'])
		print('client->saveconfig: Trying to connect to ' + str(request_json) , end = '')
		for x in range(130):
			core.time.sleep_ms(100)
			if self.wlan_sta.isconnected():
				self.wifi_status = 1
				print('Connected to ' , request_json['ssid'])
				config = {}
				try :
					config = core.json.loads(open('config.json').read())
				except :
					pass
				if not config.get('known_networks'):
					config['known_networks'] = [{'ssid': request_json['ssid'], 'password': request_json['password']}]
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
				print('Devicename')
				if len(request_json['deviceName']):
					config['device_name'] = request_json['deviceName']
				if len(request_json['token']):
					config['token'] = request_json['token']
				
				f = open('config.json', 'w')
				f.write(core.json.dumps(config))
				f.close()
				core.flag.wifi = True
				break
			else :
				core.flag.wifi = False
				print('.' , end = '')
	def is_ascii(self, s):
		return all(ord(c) < 128 for c in s)
	
	def _httpHandlerScanNetworks(self, httpClient, httpResponse) :
		print('scanap->' , end = '')
		self.wlan_sta.active(True)
		
		networks = []
		raw = self.wlan_sta.scan()
		for nw in raw:
			networks.append({'ssid': nw[0].decode('ascii'), 'rssi': nw[3]})
		
		content = core.json.dumps(networks)
		p