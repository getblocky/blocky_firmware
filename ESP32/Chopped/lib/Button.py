#version=1.0

import sys 
core = sys.modules['Blocky.Core']


class Button:
	def __init__(self , port):
		self.p = core.getPort(port)
		if self.p[0] == None :
			return 
		self.last_time = core.Timer.runtime()
		self.last_state = 0
		self.number = 0
		self.ButtonTaskList = {}
		self.his = []
		self.button = core.machine.Pin(self.p[0] , core.machine.Pin.IN , core.machine.Pin.PULL_DOWN)
		self.button.irq(trigger = core.machine.Pin.IRQ_RISING|core.machine.Pin.IRQ_FALLING , handler = self._handler)
		core.mainthread.create_task(core.asyn.Cancellable(self._async_handler)())
	def event(self , type , time , function):
		function_name = str(type) + str(time)
		if not callable(function) :
			print('btn-event->Function cant be call')
			return 
		self.ButtonTaskList[function_name] = function
		
	def is_pressed(self):
		return True if self.button.value() else False
	def _handler(self,source):
		state = self.button.value()
		now = core.Timer.runtime()
		if state == self.last_state:
			return 
		self.last_state = state
		self.his.append(core.Timer.runtime())
		if len(self.his) < 2:
			return 
		if self.his[-1] - self.his[-2]  > 500:
			print('hold for ' , (self.his[-1] - self.his[-2] )// 1000 ,'seconds')
			self.execute('hold' ,  (self.his[-1] - self.his[-2] )// 1000 )
			self.his.clear()
	@core.asyn.cancellable		
	async def _async_handler (self):
		while True :
			await core.asyncio.sleep_ms(500)
			if self.button.value() == 0:
				if len(self.his) and (core.Timer.runtime() - self.his[-1]) > 500 :
					print('pressed ' , len(self.his)//2)
					core.mainthread.call_soon(self.execute('pressed' ,len(self.his)//2 ))
					self.his.clear()
					
	async def execute(self,type,time):
		try :
			function = self.ButtonTaskList.get( str(type) + str(time) )
			if function == None :
				raise Exception
				
			if core.flag.duplicate == False :
				await core.call_once('user_button_{}{}'.format(type,time) , function)
			else:
				core.mainthread.create_task(core.asyn.Cancellable(function)())
