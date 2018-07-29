import Blocky.uasyncio as asyncio
from Blocky.asyn import  cancellable , Cancellable
from machine import Pin
from Blocky.Pin import *
from Blocky.Timer import runtime

class Button:
	def __init__(self , port):
		self.p = getPin(port)
		if self.p[0] == None :
			return 
		self.last_time = runtime()
		self.last_state = 0
		self.number = 0
		self.ButtonTaskList = {}
		self.his = []
		self.button = Pin(self.p[0] , Pin.IN , Pin.PULL_DOWN)
		self.button.irq(trigger = Pin.IRQ_RISING|Pin.IRQ_FALLING , handler = self._handler)
		loop = asyncio.get_event_loop()
		loop.create_task(Cancellable(self._async_handler)())
	def event(self , type , time , function):
		function_name = str(type) + str(time)
		if not callable(function) :
			print('btn-event->Function cant be call')
			return 
		self.ButtonTaskList[function_name] = function
		
	
	def _handler(self,source):
		state = self.button.value()
		now = runtime()
		if state == self.last_state:
			return 
		self.last_state = state
		self.his.append(runtime())
		if len(self.his) < 2:
			return 
		if self.his[-1] - self.his[-2]  > 500:
			print('hold for ' , (self.his[-1] - self.his[-2] )// 1000 ,'seconds')
			self.execute('hold' ,  (self.his[-1] - self.his[-2] )// 1000 )
			self.his.clear()
	@cancellable		
	async def _async_handler (self):
		while True :
			await asyncio.sleep_ms(500)
			if self.button.value() == 0:
				if len(self.his) and (runtime() - self.his[-1]) > 500 :
					print('pressed ' , len(self.his)//2)
					self.execute('pressed' ,len(self.his)//2 )
					self.his.clear()
					
	def execute(self,type,time):
		try :
		
			function = self.ButtonTaskList.get( str(type) + str(time) )
			if function == None :
				raise Exception
			if str(function).find('generator'):
				loop = asyncio.get_event_loop()
				loop.create_task(Cancellable(function)())
			else :
				function()
				
		except Exception as err:
			print('btn-exec->' , err)
			pass
			
"""
b = Button('D3')
async def c():
	while True :
		print(runtime())
		await asyncio.sleep_ms(2000)
b.event('hold' , 1 , c )
loop = asyncio.get_event_loop()
loop.run_forever()
"""
