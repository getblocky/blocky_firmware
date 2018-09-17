#version=1.0

import sys
core = sys.modules['Blocky.Core']

class Buzzer:
	def __init__(self,port):
		p = core.getPort(port)
		if p[0] == None : return 
		self.mode = None
		self.beeptime = 0
		self.beepgap = 0
		self.speed = 0
		self.buzzer = core.machine.Pin(p[0],core.machine.Pin.OUT)
		self.pwm  = None
		self.timer = None
		self.sequence = []
		self.pos = 0
		self.playing = False
	def _handler(self):
		self.beeptime -= 1
		if self.beeptime % 2 == 0:
			self.buzzer.value(0)
		else :
			self.buzzer.value(1)
		if self.beeptime == 0:
			return 
		#AddTask(mode='once',function=self._handler,time=self.speed)
	@core.asyn.cancellable
	async def _handler (self):
		while self.beeptime > 0:
			await core.asyncio.sleep_ms(self.speed)
			self.beeptime -= 1
			self.buzzer.value(not self.buzzer.value())
			
	def beep(self,time=1,speed=200):
		self.beeptime = time*2
		self.speed = speed
		#self._handler()
		core.mainthread.create_task(core.asyn.Cancellable(self._handler)())
		
	def turn (self , value):
		if isinstance(value,int):
			self.buzzer.value( value )
		else :
			if value == 'on':
				self.buzzer.value(1)
			elif value == 'off':
				self.buzzer.value(0)
			elif value == 'flip':
				self.buzzer.value(not self.buzzer.value())
	
	
	
	def play(self,sequence):
		if self.playing == True :
			return 
		try :
			self.time.deinit()
		except :
			pass
		#core.deinit_list.append(self.timer)
		
		self.pwm = core.machine.PWM(self.buzzer , duty = 0)
		
		if not isinstance(sequence,list):
			return 
			
		self.sequence = sequence
		self.playing = True
		self.pos = 0
		try :
			self.timer.deinit()
		except :
			pass
			
		try :
			self.timer = None
			self.timer = core.machine.Timer(-1)
			self.timer.init(mode=core.machine.Timer.ONE_SHOT,period = 1,callback =self.isr_handler)
		except :
			pass
	def isr_handler(self , source):
		if self.sequence[self.pos][0] ==0:
			self.pwm.duty(0)
		else :
			self.pwm.duty(512)
			self.pwm.freq(self.sequence[self.pos][0])
		self.pos += 1
		if self.pos