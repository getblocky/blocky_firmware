nit__(self, num_lines, num_columns)
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
		controls, so this allows the hal to pass