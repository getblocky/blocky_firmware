e cmd: %s" % cmd)
		except Exception as err :
			import sys
			print('BlynkHandler ->')
			sys.print_exception(err)
	def _new_msg_id(self):
		self._msg_id += 1
		if (self._msg_id > 0xFFFF):
			self._msg_id = 1
		return self._msg_id

	def _settimeout(self, timeout):
		if timeout != self._timeout:
			self._timeout = timeout
			self.conn.settimeout(timeout)

	def _recv(self, length, timeout=0):
		self._settimeout (timeout)
		try:
			self._rx_data += self.conn.recv(length)
		except OSError as err:
			if err.args[0] == errno.ETIMEDOUT:
				return b''
			if err.args[0] ==  errno.EAGAIN:
				return b''
			else:
				core.flag.blynk  = False
				#raise
		if len(self._rx_data) >= length:
			data = self._rx_data[:length]
			self._rx_data = self._rx_data[length:]
			return data
		else:
			return b''

	def _send(self, data, send_anyway=False):
		if self._tx_count < MAX_MSG_PER_SEC or send_anyway:
			retries = 0
			while retries <= MAX_TX_RETRIES:
				try:
					self.conn.send(data)
					self._tx_count += 1
					break
				except OSError as er:
					
					if er.args[0] != errno.EAGAIN:
						core.flag.blynk = False
						#raise Dont raise , flag instead
							
					else:
						time.sleep_ms(RE_TX_DELAY)
					retries += 1
	def _close(self, emsg=None):
		self.conn.close()
		self.state = DISCONNECTED
		time.sleep(RECONNECT_DELAY)
		if emsg:
			print('Error: %s, connection closed' % emsg)

	def _server_alive(self):
		c_time = int(time.time())
		if self._m_time != c_time:
			self._m_time = c_time
			self._tx_count = 0
			if self._last_hb_id != 0 and c_time - self._hb_time >= MAX_SOCK_TO:
				return False
			if c_time - self._hb_time >= HB_PERIOD and self.state == AUTHENTICATED:
				self._hb_time = c_time
				self._last_hb_id = self._new_msg_id()
				self._send(struct.pack(HDR_FMT, MSG_PING, self._last_hb_id, 0), True)
		return True

	def repl(self, pin):
		repl = Terminal(self, pin)
		self.add_virtual_pin(pin, repl.virtual_read, repl.virtual_write)
		return repl

	def notify(self, msg)