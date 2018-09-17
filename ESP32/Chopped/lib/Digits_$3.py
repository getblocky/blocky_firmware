 colon:
			segments[1] |= 128
		self.write(segments[:4])

	def scroll(self, string, delay=250):
		segments = string if isinstance(string, list) else self.encode_string(string)
		data = [0] * 8
		data[4:0] = list(segments)
		for i in range(len(segments) + 5):
			self.write(data[0+i:4+i])
			sleep_ms(delay)


class TM1637Decimal(TM1637):
	"""Library for quad 7-segment LED modules based on the TM1637 LED driver.

	This class is meant to be used with decimal display modules (modules
	that have a decimal point after each 7-segment LED).
	"""

	def encode_string(self, string):
		"""Convert a string to LED segments.

		Convert an up to 4 character length string containing 0-9, a-z,
		space, dash, star and '.' to an array of segments, matching the length of
		the source string."""
		segments = bytearray(len(string.replace('.','')))
		j = 0
		for i in range(len(string)):
			if string[i] == '.' and j > 0:
				segments[j-1] |= TM1637_MSB
				continue
			segments[j] = self.encode_char(string[i])
			j += 1
		return segments
