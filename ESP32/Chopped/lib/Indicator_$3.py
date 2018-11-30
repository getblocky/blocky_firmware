						self.rgb.fill((0,0,0))
						self.rgb[x] = (50,25,0)
						self.rgb[x-1 if x-1 >=0 else 11-x] = (0,20,10)
						self.rgb[x-2 if x-2 >=0 else 11-x] = (0,10,10)
						self.rgb[x-3 if x-3 >=0 else 11-x] = (0,5,5)
						self.rgb.write()
			await core.call_once('indicator',temp)
		if state == 'ota-success':
			@core.asyn.cancellable
			async def temp ():
				for x in range(5):
					self.rgb.fill((0,x*8,0))
					self.rgb.write()
					await asyncio.sleep_ms(10)
				for x in range(5,-1,-1):
					self.rgb.fill((0,x*8,0))
					self.rgb.write()
					await asyncio.sleep_ms(10)
			await core.call_once('indicator',temp)
		if state == None :
			await core.call_once('indicator',None)
indicator = Indicator()

	





