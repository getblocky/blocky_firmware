ion(err)
			print('nw-handler->' , err)
		finally :
			core.gc.collect()
			self.topic = ''
			self.message = ''
	
	async def send(self,topic,data,echo=False,timout = 2):
		while core.flag.ONLINE == False and core.Timer.runtime() < start + timeout *1000 :
			await core.asyncio.sleep_ms(100)
			
		if self.state!=1 or not topic or not data:
			return 
		topic = self.config.get('auth_key') + '/user/' + topic
		if not echo and self.message_handlers.get(topic):
			self.echo.append(self.userPrefix+str(topic))
		try :
			core.indicator.animate('pulse' , (0,0,100))
			await self.mqtt.publish(topic = topic,msg = str(data))
		except Exception as err:
			print('nw-send->',err,topic,data)
	async def log(self,message,timeout = 2):
		start = core.Timer.runtime()
		while core.flag.ONLINE == False and core.Timer.runtime() < start + timeout *1000 :
			await core.asyncio.sleep_ms(100)
			
		if self.state != 1 or not message:
			return 
		prefix = self.config.get('auth_key') + '/sys/' + CHIP_ID + '/log'
		try :
			core.indicator.animate('pulse' , (0,50,50))
			await self.mqtt.publish(topic=prefix,msg=str(message))
		except Exception as err:
			print('nw-log->',err,message)
	async def subscribe(self,topic,callback):
		while core.flag.ONLINE == False :
			await core.asyncio.sleep_ms(100)
			
		if self.state != 1 or not topic:
			return 
		topic = self.config.get('auth_key') + '/user/' + topic
		await self.mqtt.subscribe(topic)
		self.message_handlers[topic] = callback

