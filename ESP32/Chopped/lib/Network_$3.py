e-1] = ''
							
							else :
								if len(self.ota) > piece : # new piece coming 
									if len(self.ota[piece-1]):
										self.file.write(self.ota[piece-1])
										self.ota[piece-1] = ''
										self.piece += 1
										
							"""
						elif piece == '$' : 
							print('EOF-> ' , len(self.ota) , ' pieces total')
							self.ota.append(self.message)
							f = open('user_code.py' , 'w')
							f.write('import sys\ncore=sys.modules["Blocky.Core"]\n')
							for x in self.ota :
								f.write(x)
							f.close()
							self.ota = []
						elif  piece == 'ota':
							f = open('user_code.py','w')
							f.write(self.message)
							f.close()
							
						if piece == 'ota' or piece == '$':
							self.piece = 0
							otaAckMsg = {'chipId': CHIP_ID, 'event': 'ota_ack'}
							self.mqtt.publish(topic=self.config['auth_key'] + '/sys/', msg=core.json.dumps(otaAckMsg))
							print('User Code Received !')
							print('Cancelling Previouse Task')
							await core.asyn.Cancellable.cancel_all()
							core.flag.UPCODE = True 
							print('Done Cancelling All Task ')
						
						#
						
					except MemoryError :
						self.ota = []
						print('Coode tooo big ')
						await core.network.log('Your code is too big !')
						
						
						
						# Clean up 
						"""
						from machine import Pin , Timer , PWM
						list = [ 4, 33 , 16, 32, 23, 22, 27 , 19 , 13, 17 , 14, 18 , 25, 26 ]
						for x in list:
							PWM(Pin(x)).deinit()
						for x in range(0 , 10): # Dont touch software timer
							Timer(x).deinit()
						from Blocky.Main import GLOBAL_CAPTURE
						for x in list(globals()):
							if x not in GLOBAL_CAPTURE:
								del globals()[x]
						"""
						
				
				elif self.topic == self.sysPrefix + 'run':
					print('['+str(core.Timer.runtime())+']' , 'RUN message' , len(self.message))
					exec(self.message , globals())
					# this will be used to handle upgrade firmwareVersion
				
				
					
		except Exception as err:
			core.sys.print_except