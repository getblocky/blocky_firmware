se NotImplementedError

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
		se