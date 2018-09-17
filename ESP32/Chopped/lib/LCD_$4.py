	self.pin = core.getPort(self.p)
		self.line = line
		self.column = column
		self.addr = addr
		self.i2c = core.machine.I2C(scl=core.machine.Pin(self.pin[0]),\
			sda=core.machine.Pin(self.pin[1]) ,freq = 100000)
		self.lcd = I2cLcd(self.i2c,self.addr,self.line,self.column)
		self.lcd.clear()
		self.lcd.backlight_on()
		self.lcd.display_on()
		
	def clear(self,line=None): #line = 1 , line = 2 , 1 based
		if line == None :
			self.lcd.clear()
		elif isinstance(line , int):
			if line <= self.line :
				self.lcd.move_to(0,line-1)
				self.lcd.putstr(' '*self.column)
	def display(self,line = 0 , left = '' , right = ''):
		if line <= self.line :
			self.lcd.move_to(0,line-1)
			right = str(right)
			left = str(left)
			
			if len(right) > 0:
				left =left[0:self.column-len(right)-1]
				string = left +':' + ' '*(self.column-len(left)-len(right)-1)+ right
			else :
				string = left
			self.lcd.putstr(string)
			
	def backlight(self , state = 'on'):
		if state == 'on' :
			self.lcd.backlight_on()
		if state == 'off' :
			self.lcd.backlight_off()

