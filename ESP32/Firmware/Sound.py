import Blocky.uasyncio as asyncio
from Blocky.asyn import Cancellable , cancellable
from Blocky.Pin import getPin
from machine import ADC , Pin 
from time import ticks_ms

class Sound:
	def __init__(self,port,limit = 500, sensitive = 3):
		self.p = getPin(port)
		if self.p[2] == None :
			return 
		
		self.adc = ADC(Pin(self.p[2]))
		self.adc.atten(ADC.ATTN_11DB)
		self.count = 0
		self.limit = limit
		self.his = [0,0,0]
		self.curr = 0
		self.last = ticks_ms()
		self.cb = []
		self.callback = [None,None]
		loop = asyncio.get_event_loop()
		#loop.call_soon(self.handler())
		loop.create_task(Cancellable(self.handler)())
	@cancellable
	async def handler(self):
		while True :
			await asyncio.sleep_ms(10)
			self.curr = self.adc.read()
			self.his.pop(0)
			self.his.append(self.curr)
			if self.curr > self.limit:
				self.last = ticks_ms()
			if self.his[1] - self.his[0] > 0 and self.his[1] - self.his[2] > 0 and self.his[1] > self.limit :
				self.count += 1
				 
			if ticks_ms() - self.last > 500 and self.count > 0:
				for x in self.cb:
					if x[0] == 'clap' and x[1] == self.count:
						try :
							if x[3] == 'g':
								loop = asyncio.get_event_loop()
								loop.create_task(Cancellable(x[2])())
							if x[3] == 'f':
								x[2]()
						except Exception as err:
							print('sound-event->',err)
				if self.callback[0] != None :
					if self.callback[1] == 'g':
						loop = asyncio.get_event_loop()
						loop.create_task(Cancellable(self.callback[0])(self.count))
					if self.callback[1] == 'f':
						self.callback[0](self.count)
						
				self.count = 0
				self.prev = 0
	def event(self , type , time, function):
		if not callable(function):
			return 
		if time == 'all':
			self.callback = [function,'g' if str(function).find('generator') >0 else 'f']
		else :
			self.cb.append(['clap' ,time , function,'g' if str(function).find('generator') >0 else 'f'])
		
