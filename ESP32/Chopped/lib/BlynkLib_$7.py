				
			if not self._do_connect or not core.flag.blynk:
				self._close()
				print('Blynk disconnection requested by the user')
				break
			
			await core.asyncio.sleep_ms(1000)