 through the command.
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
		raise NotImpleme