#version=1.0

import sys 
core = sys.modules['Blocky.Core']


class Sound:
	def __init__(self , port):
		self.p = core.getPort(port)
		if self.p[1] == None :
			return 
		self.last_time = core.Timer.runtime()
		self.last_state = 0
		self.number = 0
		self.SoundTaskList = {}
		self.his = []
		self.button = core.machine.Pin(self.p[1] , core.machine.Pin.IN , core.machine.Pin.PULL_UP)
		self.button.irq(trigger = core.machine.Pin.IRQ_FALLING , handler = self._handler)
		core.mainthread.create_task(core.asyn.Cancellable(self._async_handler)())
		
	def event(self , type , time , function):
		function_name = str(type) + str(time)
		if not callable(function) :
			print('clap-event->Function cant be call')
			return 
		self.SoundTaskList[function_name] = function
		
	def _handler(self,source):
		now = core.Timer.runtime()
		if  (len(self.his) > 2 and state == 1 and now - self.his[-1] < 300):
			return 
		self.his.append(core.Timer.runtime())
			
	@core.asyn.cancellable		
	async def _async_handler (self):
		while True :
			await core.asyncio.sleep_ms(500)
			if self.button.value() == 1 and len(self.his) > 0 and core.Timer.runtime() - self.his[-1] > 500:
					print('clap ' , len(self.his))
					core.mainthread.call_soon(self.execute('clap' ,len(self.his) ))
					self.his.clear()
					
	async def execute(self,type,time):
		try :
			function = self.SoundTaskList.get( str(type) + str(time) )
			if function == None :
				raise Exception
				
			if core.flag.duplicate == False :
				await core.call_once('user_button_{}{}'.format(type,time) , function)
			else:
				core.mainthread.create_task(core.asyn.Cancellable(function)())
				
		except Exception as err:
			print('clap-exec->' , err)
			pass
			
