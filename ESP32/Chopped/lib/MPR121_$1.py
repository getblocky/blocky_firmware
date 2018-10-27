ess, register, 2)
			return core.struct.unpack("<H", data)[0]
		self.i2c.writeto_mem(self.address, register, core.struct.pack("<H", value))

	def reset(self):
		try :
			# Soft reset of device.
			
			self._register8( 128, 0x63)
			core.time.sleep_ms(1)
			self._register8( 94, 0x00)
			# Check CDT, SFI, ESI configuration is at default values.
			c = self._register8( 93)
			if c != 0x24:
			   return False
			# Set threshold for touch and release to default values.
			self.set_thresholds(12, 6)
			# Configure baseline filtering control registers.
			self._register8( 43, 0x01)
			self._register8( 44, 0x01)
			self._register8( 45, 0x0E)
			self._register8( 46, 0x00)
			self._register8( 47, 0x01)
			self._register8( 48, 0x05)
			self._register8( 49, 0x01)
			self._register8( 50, 0x00)
			self._register8( 51, 0x00)
			self._register8( 52, 0x00)
			self._register8( 53, 0x00)
			# Set other configuration registers.
			self._register8( 91, 0)
			self._register8( 92, 0x10) # default, 16uA charge current
			self._register8( 93, 0x20) # 0.5uS encoding, 1ms period
			# Enable all electrodes.
			self._register8( 94, 0x8F) # start with first 5 bits of baseline tracking
			# All done, everything succeeded!
			print('[MPR121] -> Reset successful')
			self.error = False
		except Exception:
			pass 
		return True

	def set_thresholds(self, touch, release, electrode=None):
		"""Sets the touch and release thresholds (0-255) for a single electrode (0-11) or all electrodes"""
		if not 0 <= touch <= 255:
			raise ValueError('Touch must be in range 0-255.')
		if not 0 <= release <= 255:
			raise ValueError('Release must be in range 0-255.')
		f = 0 if electrode is None else electrode
		t = 12 if electrode is None else electrode + 1

		# you can only modify the thresholds when in stop mode
		config = self._register8(94)
		if config != 0:
			self._register8(94, 0)

		for i in range(f, t):
			self._register8(65 + i * 2, touch)
			self._register8(66 + i * 2, release)

		# return to previous mo