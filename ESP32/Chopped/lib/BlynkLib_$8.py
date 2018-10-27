						self._close('unknown message type %d' % msg_type)
						continue
				else:
					await core.asyncio.sleep_ms(1)
					#self._start_time = sleep_from_until(self._start_time, IDLE_TIME_MS)
				if not self._server_alive():
					self._close('Blynk server is offline')
					print('BlynkServer->DEAD')
					core.flag.blynk = False
					await core.indicator.show('blynk-authenticating')
					return
				else :
					core.flag.blynk = True
					
				
				await core.asyncio.sleep_ms(1)
				
			if not self._do_connect or not core.flag.blynk:
				self._close()
				print('Blynk disconnection requested by the user')
				break
			
			await core.asyncio.sleep_ms(1000)