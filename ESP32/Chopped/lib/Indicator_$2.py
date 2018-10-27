				self.rgb.write()
					await asyncio.sleep_ms(10)
			await core.call_once('indicator',temp)
		if state == None :
			await core.call_once('indicator',None)
indicator = Indicator()

	





