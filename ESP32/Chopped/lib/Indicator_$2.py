emp():
			target_color = list(self.rgb)
			option = [(10,0,0),(0,10,0),(0,0,10),(0,0,0)]
			for i in range(12) :
				target_color[i] = core.random.choice(option)
			while True :
				await core.asyncio.sleep_ms(speed)
				for i in range(12):
					if self.rgb[i] == target_color[i]:
						target_color[i] = core.random.choice(option)
					new = list(self.rgb[i])
					for x in range(3):
						if target_color[i][x] != self.rgb[i][x] :
							new[x] = self.rgb[i][x]-1 if self.rgb[i][x] > target_color[i][x] else self.rgb[i][x] + 1
					self.rgb[i] = new
				self.rgb.write()
		await core.call_once('indicator',temp)
					
					
					
					
	async def show (self , state):
		if state == 'blynk-authenticating':
			@core.asyn.cancellable
			async def temp ():
				while True :
					for x in range(12):
						await core.asyncio.sleep_ms( abs(6-x)*5 )
						self.rgb.fill((0,0,0))
						self.rgb[x] = (25,0,25)
						self.rgb[x-1 if x-1 >=0 else 11-x] = (10,0,10)
						self.rgb[x-2 if x-2 >=0 else 11-x] = (5,0,5)
						self.rgb.write()
			await core.call_once('indicator',temp)
		if state == 'wifi-connecting':
			@core.asyn.cancellable
			async def temp ():
				while True :
					for x in range(12):
						await core.asyncio.sleep_ms( abs(6-x)*5 )
						self.rgb.fill((0,0,0))
						self.rgb[x] = (50,25,0)
						self.rgb[x-1 if x-1 >=0 else 11-x] = (20,10,0)
						self.rgb[x-2 if x-2 >=0 else 11-x] = (5,5,0)
						self.rgb.write()
			await core.call_once('indicator',temp)
		if state == 'blynk-authenticated':
			@core.asyn.cancellable
			async def temp ():
				for x in range(12):
					await core.asyncio.sleep_ms(30)
					self.rgb.fill((0,x*5,0))
					self.rgb.write()
				for x in range(12,-1,-1):
					await core.asyncio.sleep_ms(30)
					self.rgb.fill((0,x*5,0))
					self.rgb.write()
			await core.call_once('indicator',temp)
		if state == 'ota-starting':
			@core.asyn.cancellable
			async def temp ():
				while True :
					for x in range(12):
						await core.asyncio.sleep_ms( abs(6-x)*5 )
