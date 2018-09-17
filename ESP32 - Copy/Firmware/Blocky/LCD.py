import sys;core = sys.modules['Blocky.Core']

"""Implements a HD44780 character LCD connected via PCF8574 on I2C.
   This was tested with: https://www.wemos.cc/product/d1-mini.html"""
   
DEFAULT_I2C_ADDR = 56
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

LCD_CLR = 0x01			  # DB0: clear display
LCD_HOME = 0x02			 # DB1: return to home position
LCD_ENTRY_MODE = 0x04	   # DB2: set entry mode
LCD_ENTRY_INC = 0x02		# --DB1: increment
LCD_ENTRY_SHIFT = 0x01	  # --DB0: shift
LCD_ON_CTRL = 0x08		  # DB3: turn lcd/cursor on
LCD_ON_DISPLAY = 0x04	   # --DB2: turn display on
LCD_ON_CURSOR = 0x02		# --DB1: turn cursor on
LCD_ON_BLINK = 0x01		 # --DB0: blinking cursor
LCD_MOVE = 0x10			 # DB4: move cursor/display
LCD_MOVE_DISP = 0x08		# --DB3: move display (0-> move cursor)
LCD_MOVE_RIGHT = 0x04	   # --DB2: move right (0-> left)
LCD_FUNCTION = 0x20		 # DB5: function set
LCD_FUNCTION_8BIT = 0x10	# --DB4: set 8BIT mode (0->4BIT mode)
LCD_FUNCTION_2LINES = 0x08  # --DB3: two lines (0->one line)
LCD_FUNCTION_10DOTS = 0x04  # --DB2: 5x10 font (0->5x7 font)
LCD_FUNCTION_RESET = 0x30   # See "Initializing by Instruction" section
LCD_CGRAM = 0x40			# DB6: set CG RAM address
LCD_DDRAM = 0x80			# DB7: set DD RAM address
LCD_RS_CMD = 0
LCD_RS_DATA = 1
LCD_RW_WRITE = 0
LCD_RW_READ = 1


class I2cLcd():
	"""Implements a HD44780 character LCD connected via PCF8574 on I2C."""

	def __init__(self, i2c, i2c_addr, num_lines, num_columns):
		self.i2c = i2c
		self.i2c_addr = i2c_addr
		self.i2c.writeto(self.i2c_addr, bytearray([0]))
		core.time.sleep_ms(20)   # Allow LCD time to powerup
		# Send reset 3 times
		self.hal_write_init_nibble(LCD_FUNCTION_RESET)
		core.time.sleep_ms(5)	# need to delay at least 4.1 msec
		self.hal_write_init_nibble(LCD_FUNCTION_RESET)
		core.time.sleep_ms(1)
		self.hal_write_init_nibble(LCD_FUNCTION_RESET)
		core.time.sleep_ms(1)
		# Put LCD into 4 bit mode
		self.hal_write_init_nibble(LCD_FUNCTION)
		core.time.sleep_ms(1)
		#LcdApi.__init__(self, num_lines, num_columns)
		self.num_lines = num_lines
		if self.num_lines > 4:
			self.num_lines = 4
		self.num_columns = num_columns
		if self.num_columns > 40:
			self.num_columns = 40
		self.cursor_x = 0
		self.cursor_y = 0
		self.backlight = True
		self.display_off()
		self.backlight_on()
		self.clear()
		self.hal_write_command(LCD_ENTRY_MODE | LCD_ENTRY_INC)
		self.hide_cursor()
		self.display_on()
		#
		cmd = LCD_FUNCTION
		if num_lines > 1:
			cmd |= LCD_FUNCTION_2LINES
		self.hal_write_command(cmd)
		
		

	def clear(self):
		"""Clears the LCD display and moves the cursor to the top left
		corner.
		"""
		self.hal_write_command(LCD_CLR)
		self.hal_write_command(LCD_HOME)
		self.cursor_x = 0
		self.cursor_y = 0

	def show_cursor(self):
		"""Causes the cursor to be made visible."""
		self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY |
							   LCD_ON_CURSOR)

	def hide_cursor(self):
		"""Causes the cursor to be hidden."""
		self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY)

	def blink_cursor_on(self):
		"""Turns on the cursor, and makes it blink."""
		self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY |
							   LCD_ON_CURSOR | LCD_ON_BLINK)

	def blink_cursor_off(self):
		"""Turns on the cursor, and makes it no blink (i.e. be solid)."""
		self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY |
							   LCD_ON_CURSOR)

	def display_on(self):
		"""Turns on (i.e. unblanks) the LCD."""
		self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY)

	def display_off(self):
		"""Turns off (i.e. blanks) the LCD."""
		self.hal_write_command(LCD_ON_CTRL)

	def backlight_on(self):
		"""Turns the backlight on.

		This isn't really an LCD command, but some modules have backlight
		controls, so this allows the hal to pass through the command.
		"""
		self.backlight = True
		self.hal_backlight_on()

	def backlight_off(self):
		"""Turns the backlight off.

		This isn't really an LCD command, but some modules have backlight
		controls, so this allows the hal to pass through the command.
		"""
		self.backlight = False
		self.hal_backlight_off()

	def move_to(self, cursor_x, cursor_y):
		"""Moves the cursor position to the indicated position. The cursor
		position is zero based (i.e. cursor_x == 0 indicates first column).
		"""
		self.cursor_x = cursor_x
		self.cursor_y = cursor_y
		addr = cursor_x & 0x3f
		if cursor_y & 1:
			addr += 0x40	# Lines 1 & 3 add 0x40
		if cursor_y & 2:
			addr += 0x14	# Lines 2 & 3 add 0x14
		self.hal_write_command(LCD_DDRAM | addr)

	def putchar(self, char):
		"""Writes the indicated character to the LCD at the current cursor
		position, and advances the cursor by one position.
		"""
		if char != '\n':
			self.hal_write_data(ord(char))
			self.cursor_x += 1
		if self.cursor_x >= self.num_columns or char == '\n':
			self.cursor_x = 0
			self.cursor_y += 1
			if self.cursor_y >= self.num_lines:
				self.cursor_y = 0
			self.move_to(self.cursor_x, self.cursor_y)

	def putstr(self, string):
		"""Write the indicated string to the LCD at the current cursor
		position and advances the cursor position appropriately.
		"""
		for char in string:
			self.putchar(char)

	def custom_char(self, location, charmap):
		"""Write a character to one of the 8 CGRAM locations, available
		as chr(0) through chr(7).
		"""
		location &= 0x7
		self.hal_write_command(LCD_CGRAM | (location << 3))
		core.time.sleep_us(40)
		for i in range(8):
			self.hal_write_data(charmap[i])
			core.time.sleep_us(40)
		self.move_to(self.cursor_x, self.cursor_y)

	def hal_backlight_on(self):
		"""Allows the hal layer to turn the backlight on.

		If desired, a derived HAL class will implement this function.
		"""
		pass

	def hal_backlight_off(self):
		"""Allows the hal layer to turn the backlight off.

		If desired, a derived HAL class will implement this function.
		"""
		pass

	def hal_write_command(self, cmd):
		"""Write a command to the LCD.

		It is expected that a derived HAL class will implement this
		function.
		"""
		raise NotImplementedError

	def hal_write_data(self, data):
		"""Write data to the LCD.

		It is expected that a derived HAL class will implement this
		function.
		"""
		raise NotImplementedError
		
	def hal_write_init_nibble(self, nibble):
		"""Writes an initialization nibble to the LCD.
		This particular function is only used during initialization.
		"""
		byte = ((nibble >> 4) & 0x0f) << SHIFT_DATA
		self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))

	def hal_backlight_on(self):
		"""Allows the hal layer to turn the backlight on."""
		self.i2c.writeto(self.i2c_addr, bytearray([1 << SHIFT_BACKLIGHT]))

	def hal_backlight_off(self):
		"""Allows the hal layer to turn the backlight off."""
		self.i2c.writeto(self.i2c_addr, bytearray([0]))

	def hal_write_command(self, cmd):
		"""Writes a command to the LCD.
		Data is latched on the falling edge of E.
		"""
		byte = ((self.backlight << SHIFT_BACKLIGHT) | (((cmd >> 4) & 0x0f) << SHIFT_DATA))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
		byte = ((self.backlight << SHIFT_BACKLIGHT) | ((cmd & 0x0f) << SHIFT_DATA))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
		if cmd <= 3:
			# The home and clear commands require a worst case delay of 4.1 msec
			core.time.sleep_ms(5)

	def hal_write_data(self, data):
		"""Write data to the LCD."""
		byte = (MASK_RS | (self.backlight << SHIFT_BACKLIGHT) | (((data >> 4) & 0x0f) << SHIFT_DATA))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
		byte = (MASK_RS | (self.backlight << SHIFT_BACKLIGHT) | ((data & 0x0f) << SHIFT_DATA))
		self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
		self.i2c.writeto(self.i2c_addr, bytearray([byte]))
		
class LCD ():
	def __init__(self , port , addr = 56 , line = 2 , column = 16):
		self.p = port
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
				string = left + ' '*(self.column-len(left))
			
			if len(string) > self.column :
				string = string[0:self.column]
			self.lcd.putstr(string)
			
	def backlight(self , state = 'on'):
		if state == 'on' :
			self.lcd.backlight_on()
		if state == 'off' :
			self.lcd.backlight_off()

