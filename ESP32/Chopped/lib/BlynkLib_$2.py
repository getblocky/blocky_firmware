_lock = core.eeprom.get('OTA_LOCK')
					
					if (ota_lock == True and core.cfn_btn.value() == 0) or ota_lock == False or ota_lock == None :
						if core.ota_file == None :
							core.ota_file = open('user_code.py','w')
						if params[1] == "OTA":
							self.virtual_write(127,"[OTA_READY]",http = True)
							
							core.ota_file.write("import sys\ncore=sys.modules['Blocky.Core']\n")
						else :
							print('PART' , params[1] ,len(params[0]) , end = '')
							total_part = int(params[1].split('/')[1])
							curr_part = int(params[1].split('/')[0])
							
							if total_part == curr_part :
								core.ota_file.write(params[0])
								core.ota_file.close()
								core.ota_file = None
								self.virtual_write(127,"[OTA_DONE]",http = True)
								print('User code saved')
								core.mainthread.call_soon(self.ota())
							if curr_part < total_part:
								core.ota_file.write(params[0])
								self.virtual_write(127,"[OTA_READY]",http = True)
								print(curr_part ,'/' , total_part)
							
						
						
					else :
						print('Sorry , your code is lock , press config to unlock it')
						
					# Run cleanup task here
					
				elif (pin in self._vr_pins_write or pin in self._vr_pins_read) :
						core.mainthread.create_task(core.asyn.Cancellable(self._vr_pins_read[pin])(params[0]))
			# Handle Virtual Read operation
			elif cmd == 'vr':
				pin = int(params.pop(0))
				if pin in self._vr_pins and self._vr_pins[pin].read:
					self._vr_pins[pin].read()
			else:
				print('UNKNOWN' , params)
				return 
				#raise ValueError("Unknown message cmd: %s" % cmd)
		except Exception as err :
			import sys
			print('BlynkHandler ->')
			sys.print_exception(err)
	def _new_msg_id(self):
		self._msg_id += 1
		if (self._msg_id > 0xFFFF):
			self._msg_id = 1
		return self._msg_id

	def _settimeout(self, timeout):
		if timeout != self._timeout:
			self._timeout = timeout
			self.conn.settimeout(timeout)

	def _recv(self, length, timeout=0):
		self._settimeout (ti