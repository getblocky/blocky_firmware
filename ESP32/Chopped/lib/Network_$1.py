.format(preference['ssid']))
			for check in range(0,10):
				if wlan_sta.isconnected():
					break
				print('.',end='')
				await core.asyncio.sleep_ms(1000)
			if wlan_sta.isconnected():
				print('Connected to ' , preference)
				self.mqtt_connected = False
				for i in range(10):
					core.indicator.animate('heartbeat' , (200,100,0))
					try :
						print('Retry..')
						self.mqtt.connect()
						self.mqtt_connected = True
						await core.asyncio.sleep_ms(2000)
						break
					except Exception as err:
						print('mqtt-connect->' , err)
						pass

		if not wlan_sta.isconnected() or not self.mqtt_connected :
			bootmode = core.BootMode.BootMode()
			await bootmode.Start()
			del bootmode
		core.indicator.animate('pulse' , (10,50,100))	
		# At this poinrt , wifi and broker are connected
		self.mqtt.set_callback(self.handler)
		register_data = {'event': 'register', 
			'chipId': CHIP_ID, 
			'firmwareVersion': '1.0',
			'name': self.config.get('device_name', 'Blocky_' + CHIP_ID),
			'type': 'esp32'
		}
		
		
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/ota/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/run/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/rename/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/reboot/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/upload/#')
		await self.mqtt.subscribe(self.config['auth_key'] + '/sys/' + CHIP_ID + '/upgrade/#')
		await self.mqtt.publish(topic=self.config['auth_key'] + '/sys/', msg=core.json.dumps(register_data))
	
		self.state = 1
		print('Connected to broker',core.json.dumps(register_data))
		core.flag.ONLINE = True
		core.indicator.animate()
		for x in range(0,250,1):
			core.indicator.rgb[0] = (0,x,x);core.indicator.rgb.write()
			core.time.sleep_ms(1)
		for x in range(250,0,-1):
			core.indicator.rgb[0] = (0,x,x);core.indicator.rgb.write()
			core.tim