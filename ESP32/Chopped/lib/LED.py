#version=1.0

import sys
core = sys.modules['Blocky.Core']

class LED:
	def __init__(self,port):
		p = core.getPort(port)
		if p[0] == None : return 
		self.mode = None
		self.beeptime = 0
		self.beepgap = 0
		self.speed = 0
		self.led = core.machine.Pin(p[0],core.machine.Pin.OUT)
		self.pwm  = None
	def _handler(self):
		self.beeptime -= 1
		if self.beeptime % 2 == 0:
			self.led.value(0)
		else :
			self.led.value(1)
		if self.beeptime == 0:
			return 
		#AddTask(mode='once',function=self._handler,time=self.speed)
	@core.asyn.cancellable
	async def _handler (self):
		while self.beeptime > 0:
			await core.asyncio.sleep_ms(self.speed)
			self.beeptime -= 1
			self.led.value(not self.led.value())
			
	def blink(self,time=1,speed=200):
		self.beeptime = time*2
		self.speed = speed
		#self._handler()
		core.mainthread.create_task(core.asyn.Cancellable(self._handler)())
		
	def turn (self , value):
		if isinstance(value,int):
			self.led.value( value )
		else :
			if value == 'on':
				self.led.value(1)
			elif value == 'off':
				self.led.value(0)
			elif value == 'flip':
				self.led.value(not self.led.value())
	"""
	async def play(self,sequence):
		from machine import PWM 
		self.pwm = PWM(Pin(self.led) , duty = 512)
		try :
			for x in range(len(sequence)):
				self.pwm.freq(sequence[x][0])
				await asyncio.sleep_ms(sequence[x][1])
			self.pwm = None 
		except Exception as err:
			print(err)
			pass
	"""


