from machine import Pin , PWM
from Blocky.Pin import getPin
from ujson import dumps , loads
from time import sleep_us , ticks_us
import os
TIMEOUT = 5000000 #Max time to wait is 5 seconds
# During this time , no other tasks is running !
class Remote :
	def __init__ (self,port):
		self.p = getPin(port)
		if self.p[0] == None or self.p[1] == None:
			from Blocky.Network import network
			network.log('Wrong pin for ' , self.p)
			
		self.pwm = PWM(Pin(self.p[1]),freq = 38000,duty=0)
		self.pwm.duty(0)
		self.recv = Pin(self.p[0] , Pin.OUT)
		self.recv.value(1)
		self.now = 0
		self.last = 0
		
	def send(self,name):
		try :
			f = open('Remote/' + str(name) + '.json')
			data = loads(f.read())
			f.close()
			list = data['data']
			freq = data['freq']
			self.recv = Pin(self.p[0],Pin.OUT)
			self.recv.value(1)
			# Feedback , light indicate the chip has received
			# In this case , it is not , therefore , 1
			try :
				self.pwm.freq(freq)
			except :
				self.pwm.freq(38000)
			for x in range(len(list)):
				if x%2==0:
					self.pwm.duty(512)
					sleep_us(min(list[x],200000))
				else :
					self.pwm.duty(0)
					sleep_us(min(list[x],200000))
			self.pwm.duty(0)
			self.recv = Pin(self.p[0],Pin.IN)
			#enable_irq()
		except Exception as err:
			print('rm-send->' , err)
			pass
		finally:
			f.close()
			
	def learn(self,name,length = 500 , freq = 38000):
		self.recv = Pin(self.p[0],Pin.IN)
		self.pwm.duty(0)
		list = []
		timeout = ticks_us() + TIMEOUT
		while ticks_us() < timeout:
			self.now = self.recv.value()
			if self.now != self.last:
				if len(list) > length:
					break
				
				print('.',end='')
				self.last = self.now
				
				timeout = ticks_us() + TIMEOUT
				if len(list) == 0 and self.now == 1:
					continue 
				list.append(ticks_us())
				
		for x in range(len(list)-1):
			list[x] = list[x+1] - list[x]
			list[x] = min(list[x] , 200000)  # max pulse timeout
		#enable_irq()
		try:
			os.stat('Remote')
		except:
			os.mkdir('Remote')  
		f = open('Remote/' + str(name) + '.json','w')
		f.write(dumps({'data':list,'freq':freq}))
		f.close()
		# Feedback
		self.recv = Pin(self.p[0],Pin.OUT)
		for x in range(10):
			self.recv.value(0)
			sleep_us(30000)
			self.recv.value(1)
			sleep_us(30000)
		self.recv = Pin(self.p[0],Pin.IN)
		
	
		
