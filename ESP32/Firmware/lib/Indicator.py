from neopixel import NeoPixel
import sys
core = sys.modules['Blocky.Core']
class Indicator :
	def __init__ (self):
		self.animation = ''
		self.color = (0,0,0) # color that user set 
		self.fcolor = [0,0,0] # color that the handler use
		self.rgb = NeoPixel(core.machine.Pin(5) , 12 , timing = True )
		self.speed = 0
		self.rgb.write()
		self.gap = 1
		self.running = 0
	
	async def heartbeat(self,color , speed , exit , gap = 1):
		return
		self.color = color
		self.speed = speed
		self.gap = gap
		self.running=1
		while  self.running == 1:
			r,g,b = self.rgb[0]
			if (r,g,b) == (0,0,0):	self.fcolor = self.color
			if (r,g,b) == self.fcolor:self.fcolor = (0,0,0)
			d,e,f = self.fcolor
			if (r<d): r = min(r + self.gap,d)
			if (r>d): r = max(r-self.gap,0)
			if (g<e): g = min(g + self.gap,e)
			if (g>e): g = max(g-self.gap,0)
			if (b<f): b = min(b + self.gap,f)
			if (b>f): b = max(b-self.gap,0)
			self.rgb.fill(   (r,g,b) )
			self.rgb.write()
			await core.asyncio.sleep_ms(self.speed)
			if callable(exit):
				if exit() == True :
					break
			else :
				if exit == True :
					break 
		self.rgb.fill(  (0,0,0) )
		self.rgb.write()

	
	async def animate(self , name):
		await core.asyn.rgb.NamedTask('indicator-handler').cancel ()
		if name == 'ota-success':
			@core.asyn.rgb.cancellable
			async def handler (self):
				for x in range(255):
					self.rgb.fill((x,x,x));self.rgb.write()
					await core.asyncio.sleep_ms(1)
				for x in range(255,0,-1):
					self.rgb.fill((x,x,x));self.rgb.write()
					await core.asyncio.sleep_ms(1)
					
		elif name == 'blynk-connecting':
			@core.asyn.rgb.cancellable
			async def handler (self):
				while True :
					for x in range(255):
						self.rgb.fill((x,x,x));self.rgb.write()
						await core.asyncio.sleep_ms(1)
					for x in range(255,0,-1):
						self.rgb.fill((x,x,x));self.rgb.write()
						await core.asyncio.sleep_ms(1)
		elif name == 'blynk-authenticating':
			pass
		elif name == 'blynk-failed':
			pass
		elif name == 'blynk-success':
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
		async def temp():
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

	





