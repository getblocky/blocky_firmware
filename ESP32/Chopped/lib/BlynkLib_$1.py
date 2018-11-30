 0
		self._token = token
		self.message = None
		if isinstance (self._token, str):
			self._token = token.encode('ascii')
		self._server = server
		if port is None:
			if ssl:
				port = 8441
			else:
				port = 80
		self._port = port
		self._do_connect = connect
		self._ssl = ssl
		self.state = DISCONNECTED
		self.conn = None
		self.last_call = core.Timer.runtime()
		self.ota = ota
		
	def _format_msg(self, msg_type, *args):
		data = ('\0'.join(map(str, args))).encode('ascii')
		return struct.pack(HDR_FMT, msg_type, self._new_msg_id(), len(data)) + data
	
	async def _handle_hw(self, data):
		try :
			params = list(map(lambda x: x.decode('ascii'), data.split(b'\0')))
			cmd = params.pop(0)
			if cmd == 'pm'or cmd == 'dr' or cmd == 'dw' or cmd == 'ar' or cmd == 'aw':
				pass
			# Handle Virtual Write operation
			elif cmd == 'vw': 
				pin = int(params.pop(0))
				
				if pin == 125 :
					print('[Blynk->Execute(125)]\t',end='') 
					ota_lock = core.eeprom.get('OTA_LOCK')
					if (ota_lock==True and core.cfn_btn.value()==0)or ota_lock==False or ota_lock==None:
						try :
							exec(params[0] , globals())
							print('OK')
						except Exception as err :
							print(err)
							self.log("Can't execute that -> {}".format(err))
					else :
						print('[FLAG_OTA_LOCKED]')
					
					
				if pin == 126 :
					print('['+str(core.Timer.runtime())+'] OTA Message Received')
					core.gc.collect()
					ota_lock = core.eeprom.get('OTA_LOCK')
					
					if (ota_lock == True and core.cfn_btn.value() == 0) or ota_lock == False or ota_lock == None :
						if core.ota_file == None :
							core.ota_file = open('temp_code.py','w')
						if params[1] == "OTA":
							await core.asyn.Cancellable.cancel_all()
							await core.cleanup()
							core.ota_file.write("import sys\ncore=sys.modules['Blocky.Core']\n")
						else :
							print('PART' , params[1] ,len(params[0]) , end = '')
							total_part = int(params[1].split('/')[1])
							curr_part = int(params[1].split('/')[0])
	