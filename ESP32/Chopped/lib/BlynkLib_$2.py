						if total_part == curr_part :
								core.ota_file.write(params[0])
								core.ota_file.close()
								core.ota_file = None
								core.os.rename('temp_code.py','user_code.py')
								print('^^~')
								#self.virtual_write(127,'[OTA_DONE]',http = True)
								self.log('[OTA_DONE]')
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
						self.log("[ERROR] You have locked your code , to upload new code , you need to press CONFIG button onboard")
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
						
					print("[Blynk] V{} | {} {}".format(pin,self.message,type(self.message) ) )
					if core.flag.duplicate == False :
						await core.call_once('user_blynk_{}'.format(pin) , self._vr_pins_write[pin])
					else :
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
				#raise ValueError("Unknown messag