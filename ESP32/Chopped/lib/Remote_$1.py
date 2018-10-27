= 1 :
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




l = asyncio.g