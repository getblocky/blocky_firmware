		try :
			self.mqtt.check_msg()
		except Exception as err:
			print('nw-mqtt-> ' , err)
			core.sys.print_exception(err)
			#await self.connect()
	# Process will trigger mqtt.wait_msg -> selb.cb -> self.handler
	async def cancel (self):
		await core.asyn.Cancellable.cancel_all()
		print('Canceled')
	async def handler(self,topic,message):
		print('%',end='')
		try :
			core.indicator.animate('pulse' , (0,100,0))
			print('handle->',topic  , len(message))
			self.topic = topic.decode()
			self.message = message.decode()
			if self.topic.startswith(self.userPrefix):
				if self.topic in self.echo:
					print('echo' , self.topic)
					self.echo.remove(self.topic)
					return 
					
				function = self.message_handlers.get(self.topic)
				print('func' , function)
				if function :
					print('init')
					try :
							#mainthread.create_task(Cancellable(function(self.topic.split('/')[-1],self.message))(self.topic.split('/')[-1],self.message))
						await function(self.topic.split('/')[-1],self.message)
					except Exception as err:
						print('['+str(runtime())+']','nw-handler->' , err)
						
					
			elif self.topic.startswith(self.sysPrefix):
				if self.topic.startswith(self.sysPrefix+'ota'):
					try :
						print('['+str(core.Timer.runtime())+']' , 'OTA Message' , len(self.message))
						piece = self.topic.split('/')[-1]
						if piece.isdigit():
							print('Receive piece # ' , piece , len(self.message))
							piece = int(piece)
							if piece > len(self.ota):
								for x in range(piece-len(self.ota)):
									self.ota.append('')
									
							self.ota[piece-1] = self.message
							"""
							if piece == 1:
								self.file = open('user_code.py' , 'w')
								self.file.write(self.ota[piece-1])
								self.piece += 1
								self.ota[piece-1] = ''
							
							else :
								if len(self.ota) > piece : # new piece coming 
									if len(self.ota[piece-1]):
										self.file.write(self.ota[piece-1])
										self.ota[piece-1] = ''
										self.