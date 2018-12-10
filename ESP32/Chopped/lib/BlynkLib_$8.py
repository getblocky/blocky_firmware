._close()
				print('Blynk disconnection requested by the user')
				break
			
			await core.asyncio.sleep_ms(1000)