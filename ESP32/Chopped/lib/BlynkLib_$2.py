re.gc.collect()
					ota_lock = core.eeprom.get('OTA_LOCK')
					
					if (ota_lock == True and core.cfn_btn.value() == 0) or ota_lock == False or ota_lock == None :
						if core.ota_file == None :
							core.ota_file = open('user_code.py','w')
						if params[1] == "OTA":
							await core.asyn.Cancellable.cancel_all()
							core.cleanup()
							
							self.virtual_write(127,"[OTA_READY]",http = True)
							core.ota_file.write("import sys\ncore=sys.modules['Blocky.Core']\n\n")
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
						
					else :
						print('Sorry , your code is lock , press config to unlock it')
						core.blynk.log("[ERROR] You have locked your code , to upload new code , you need to press CONFIG button onboard")
					# Run cleanup task here
					
				elif (pin in self._vr_pins_write or pin in self._vr_pins_read) :
					self.message = params
					print('Task Handling on pin ', pin , 'with' , params)
					core.mainthread.call_soon(core.asyn.Cancellable(self._vr_pins_write[pin])())
					await core.asyncio.sleep_ms(50) #Asyncio will focus on the handling
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
	def _new