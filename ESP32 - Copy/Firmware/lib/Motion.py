import sys
core = sys.modules['Blocky.Core']

class Motion :
	def __init__(self , port):
		self.p = core.getPort(port)[0]
		if self.p == None :
			return 
		self.motion = core.machine.Pin(self.p,core.machine.Pin.IN,core.machine.Pin.PULL_DOWN)
		#self.motion.irq(trigger = core.machine.Pin.IRQ_RISING|core.machine.Pin.IRQ_FALLING,handler = self._handler)
		self.whendetect = None
		self.whennotdetect = None
		self.prev = self.motion.value()
		core.mainthread.create_task(core.asyn.Cancellable(self._handler)())
		
	@core.asyn.cancellable
	async def _handler(self):
		while True :
			if self.motion.value() != self.prev :
				if self.motion.value():
					if self.whendetect :
						await core.asyn.Cancellable(self.whendetect)()
				else :
					if self.whennotdetect :
						await core.asyn.Cancellable(self.whennotdetect)()
				self.prev = not self.prev
				
			await core.asyncio.sleep_ms(300)
						
	def event(self,type,function):
		if type == 'detect' :
			self.whendetect = function
		else :
			self.whennotdetect = function