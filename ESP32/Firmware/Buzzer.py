from machine import Pin 
from Blocky.Pin import getPin
from time import *
class Buzzer:
	def __init__(self,port):
		p = getPin(port)
		if p[0] == None : return 
		self.mode = None
		self.beeptime = 0
		self.beepgap = 0
		self.speed = 0
		self.buzzer = Pin(p[0],Pin.OUT)
		self.pwm  = None
	def _handler(self):
		self.beeptime -= 1
		if self.beeptime % 2 == 0:
			self.buzzer.value(0)
		else :
			self.buzzer.value(1)
		if self.beeptime == 0:
			return 
		#AddTask(mode='once',function=self._handler,time=self.speed)
		
	def beep(self,time=1,speed=200):
		self.beeptime = time*2
		self.speed = speed
		#self._handler()
		for x in range(self.beeptime):
			self.buzzer.value(not self.buzzer.value())
			sleep_ms(time)
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
	"""
	async def play(self,sequence):
		from machine import PWM 
		self.pwm = PWM(Pin(self.buzzer) , duty = 512)
		try :
			for x in range(len(sequence)):
				self.pwm.freq(sequence[x][0])
				await asyncio.sleep_ms(sequence[x][1])
			self.pwm = None 
		except Exception as err:
			print(err)
			pass
	"""


