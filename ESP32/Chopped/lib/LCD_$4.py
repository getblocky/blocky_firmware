lf.p = port
		self.pin = core.getPort(self.p)
		self.line = line
		self.column = column
		self.addr = addr
		self.i2c = core.machine.I2C(scl=core.machine.Pin(self.pin[0]),\
			sda=core.machine.Pin(self.pin[1]) ,freq = 100000)
		try :
			self.lcd = I2cLcd(self.i2c,self.addr,self.line,self.column)
			self.lcd.clear()
			self.lcd.backlight_on()
			self.lcd.display_on()
		except Exception :
			pass
		
	def clear(self,line=None): #line = 1 , line = 2 , 1 based
		try :
			if line == None :
				self.lcd.clear()
			elif isinstance(line , int):
				if line <= self.line :
					self.lcd.move_to(0,line-1)
					self.lcd.putstr(' '*self.column)
		except Exception :
			pass
	def display(self,line = 0 , left = '' , right = ''):
		try :
			self.lcd.backlight_on()
			if line <= self.line :
				self.lcd.move_to(0,line-1)
				right = str(right)
				left = str(left)
				
				if len(right) > 0:
					left =left[0:self.column-len(right)-1]
					string = left +':' + ' '*(self.column-len(left)-len(right)-1)+ right
				else :
					string = left + ' '*(self.column-len(left))
				
				if len(string) > self.column :
					string = string[0:self.column]
				self.lcd.putstr(string)
		except Exception :
			pass
			
	def backlight(self , state = 'on'):
		try :
			if state == 'on' :
				self.lcd.backlight_on()
			if state == 'off' :
				self.lcd.backlight_off()
		except Exception:
			pass

