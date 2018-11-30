-success':
			pass
		core.mainthread.create_task ( core.asyn.rgb.NamedTask('indicator-handler',self.handler) )
	
	async def loading(self,color,gap=10,cancel=None,reverse = False):
		# Cancel Condition either a flag or a function
		# if the confition function is reversed then set the reverse to True
		@core.asyn.cancellable
		async def temp ():
			while True :
				if (callable(cancel) == True and cancel() != reverse ) or (callable(cancel) == False and cancel != reverse):
					break
				
				for x in range(12):
					await core.asyncio.sleep_ms(gap)
					self.rgb.fill((0,0,0))
					for i in range(12) :
						self.rgb.fill((0,0,0))
						for fade in range(1,12):
							self.rgb[i-fade if x-fade >= 0 else 11-fade] = (color//fade,color//fade,color//fade)
							self.rgb[i] = color
							self.rgb[x-1 if x-1 >=0 else 11-x] = (color//2,color//2,color)
							self.rgb[x-2 if x-2 >=0 else 11-x] = (5,0,5)
							self.rgb.write()
							# do something here 
		await core.call_once('indicator',temp)
		
	def colour (self,start,stop,colour,update=True):
		if isinstance(colour,str):
			colour = colour.lstrip('#')
			colour = tuple(max(0,min(255,int(colour[i:i+2], 16))) for i in (0, 2 ,4))
		start = max(1,start)
		stop = min(12,stop)
		if start > stop :
			return
		for x in range(start,stop+1):
			self.rgb[x-1] = colour
		if update == True :
			self.rgb.write()
	async def pulse ( self , color , speed=10,gap = 1):
		@core.asyn.cancellable
		async def temp ():
			while color != self.rgb[0]:
				self.rgb.fill( ( min(color[0],self.rgb[0][0]+gap),min(color[1],self.rgb[0][1]+gap) ,min(color[2],self.rgb[0][2]+gap)  ) )
				self.rgb.write()
				await core.asyncio.sleep_ms(speed)
			while (0,0,0) != self.rgb[0]:
				self.rgb.fill( ( max(0,self.rgb[0][0]-gap),max(0,self.rgb[0][1]-gap) ,max(0,self.rgb[0][2]-gap)  ) )
				self.rgb.write()
				await core.asyncio.sleep_ms(speed)
		await core.call_once('indicator',temp)
	async def rainbow ( self , speed = 10):
		@core.asyn.cancellable
		async def t