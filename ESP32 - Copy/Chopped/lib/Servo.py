#version=1.0
from Blocky.Pin import *
from machine import Pin,PWM
class Servo:
	def __init__ (self , port , min=400 , max = 2600):
		self.p = getPin(port)
		if self.p[0] == None : return 
		self.pwm = PWM(Pin(self.p[0]),freq = 50)
		self.pwm.init()
		self.min = min
		self.max = max
		self.curr = 0
		
	def angle(self,value = None ):
		if value == None :
			return self.curr
		else :
			self.pwm.duty ( (value - 0) * (120 - 10) // (180 - 0) + 10 )
			self.curr = value
			
