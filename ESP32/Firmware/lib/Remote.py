#version=1.0
import sys
from machine import *
from time import *
from struct import *

"""
	Library made for ESP32 platform , AnataLAB . @Blocky platform
	How this works :
		This library can learn , send and receive IR signal asynchorously
		For learning process , this library will convert to the bytearray format
			By default , 100us = 1 
			bytearray( 10 , 50 ) = mark 1000 , space 5000
			
			If another gap :
			bytearray ( 0x00 , gap , 0x00 , 10 , 50 )
			The bytearray is fix with a length of 200
			0x00 mark EOS
			This allow a acurately enough that the sender can replicate
			
		For receiving process , the format	(bitarray,length)

			This allow for minimum latency and accuarate enough , not exactly though !
			
		For sending process , the sender will use bytearray
		
		Note :
			Do not allocate memory 
		

"""
def inside	( t , r ):
	# LMAO : How to recognise a bitarray is inside another bitarray ( in this case , number in number )
	if t[1] > r[1] :
		return False 
	for x in range(r[1]-t[1]+1):
		if (((((2**(r[1]-x-t[1])-1)|((2**x -1)<<(t[1]+(r[1]-x-t[1]))))^(2**r[1]-1))&r[0])>>(r[1]-x-t[1]))==t[0]:
			return True
	return False
		
class Remote :
	def __init__ (self) :
		self.pwm = PWM ( Pin(25,Pin.OUT) ,freq = 38000 , duty = 0)
		self.recv = Pin ( 26 , Pin.IN , Pin.PULL_UP)
		self.recv.irq ( trigger = Pin.IRQ_RISING|Pin.IRQ_FALLING , handler = self.handler)
		self.last = ticks_us()
		self.count = 0
		self.data = 0x00
		
		self.mark = 0
		self.space = 0
		self.packet = bytearray(500)
		self.handling = False
		self.prev = self.recv.value()
		self.sending = False
	def handler (self , source):
		if self.handling == True :
			print('Crap')
		self.handling = True
		if self.recv.value() == 1 and self.prev == 0 :
			self.mark = ticks_diff(ticks_us() , self.last)
			self.packet[self.count] = 127 + min(127 , self.mark // 2000) if self.mark >= 12700 else min(127,self.mark//100)
			self.last = ticks_us();self.prev = not self.prev
		if self.recv.value() == 0 and self.prev == 1 :
			self.space = ticks_diff(ticks_us() , self.last)
			self.packet[self.count] = 127 + min(127 , self.space // 2000) if self.mark >= 12700 else min(127,self.space//100)
			if self.mark > 2000 and self.space > 2000 :
				self.data = self.data | (1<<self.count)
			elif self.space-self.mark*2	> 0 :
				self.data = self.data | (1<<self.count)
			else :
				self.data = self.data&(~(1 << self.count))
			self.last = ticks_us()	
			self.count += 1
			self.prev = not self.prev
		self.handling = False
	def routine (self,source):
		if ticks_diff(ticks_us() , self.last) > 500000 :
			if self.count > 10 :
				#print(self.count , replicate(self.packet))
				print(self.count , hex(self.data))
				print(('{0:0' + str(self.count) + 'b}').format(self.data))
				#self.send(self.packet)
				self.p (self.packet)
				
				now = [self.data , self.count]
				if inside( listen , now ):
					print('Hello World')
				
			self.count = 0
			self.data = 0x00
			for x in self.packet :
				x = 0x00
	def p(self , packet):
		pass
	def send (self , packet ):
		self.recv = Pin(26 , Pin.OUT)
		self.recv.value(0)
		self.recv.irq(trigger = 0)
		
		self.sending = True
		"""
		for x in range( len(packet) // 6 ):
			for i in range(6):
				val = packet[x*6 +i]
				val = val * 100 if val <= 127 else val*2000
				print( val , end='\t')
			print()
		"""
		for x in range(0 , len(packet)):
			if packet[x] == 0x00 :
				self.sending = False
				break
			self.pwm.duty(512 if x%2==0 else 0)
			start = ticks_us()
			timing = packet[x]*100 if packet[x] <= 128 else packet[x]*2000 
			while ticks_diff(ticks_us(),start) < timing :
				machine.idle()
				pass
		self.sending = False
		
		self.recv = Pin(26 , Pin.IN , Pin.PULL_UP)
		self.recv.irq(trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING , handler = self.handler)
		
def get_bit(byteval,idx):
		return ((byteval&(1<<idx))!=0)



	
r = Remote ()
import Blocky.uasyncio as asyncio
async def loop ():
	while True :
		await asyncio.sleep_ms(500)
		r.routine(1)




l = asyncio.get_event_loop()

l.call_soon( loop () )

import _thread
#_thread.start_new_thread( l.run_forever , ())


l.run_forever()