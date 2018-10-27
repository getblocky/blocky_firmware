TA Message Received')
					core.gc.collect()
					ota_lock = core.eeprom.get('OTA_LOCK')
					
					if (ota_lock == True and core.cfn_btn.value() == 0) or ota_lock == False or ota_lock == None :
						if core.ota_file == None :
							core.ota_file = open('temp_code.py','w')
						if params[1] == "OTA":
							await core.asyn.Cancellable.cancel_all()
							await core.cleanup()
							core.ota_file.write("import sys\ncore=sys.modules['Blocky.Core']\n\n")
						else :
							print('PART' , params[1] ,len(params[0]) , end = '')
							total_part = int(params[1].split('/')[1])
							curr_part = int(params[1].split('/')[0])
							if total_part == curr_part :
								core.ota_file.write(params[0])
								core.ota_file.close()
								core.ota_file = None
								core.os.rename('temp_code.py','user_code.py')
								print('^^~')
								self.virtual_write(127,'[OTA_DONE]',http = True)
								print('User code saved')
								for x in range(7):
									core.indicator.rgb.fill((0,x*10,0))
									core.indicator.rgb.write()
									await core.asyncio.sleep_ms(20)
								for x in range(5,-1,-1):
									core.indicator.rgb.fill((0,x*10,0))
									core.indicator.rgb.write()
									await core.asyncio.sleep_ms(20)
								core.mainthread.call_soon(self.ota())
								
							if curr_part < total_part:
								core.ota_file.write(params[0])
								print('[PROBE] ' , params[0][0:min(10,len(params[0]))])
						
					else :
						print('Sorry , your code is lock , press config to unlock it')
						core.blynk.log("[ERROR] You have locked your code , to upload new code , you need to press CONFIG button onboard")
					# Run cleanup task here
					
				elif (pin in self._vr_pins_write or pin in self._vr_pins_read) :
					self.message = params
					for x in range(len(self.message)):
						try :
							self.message[x] = int(self.message[x])
						except :
							pass
					if len(self.message) == 1 :
						self.message = self.message[0]
						
					print("[Blynk] V{} | {} {}".f