ormat(pin,self.message,type(self.message) ) )
					if core.flag.duplicate == False :
						await core.call_once('user_blynk_{}'.format(pin) , self._vr_pins_write[pin])
					else :
						core.mainthread.call_soon(core.asyn.Cancellable(self._vr_pins_write[pin])())
						
					await core.asyncio.sleep_ms(50) #Asyncio will focus on the handling
			# Handle Virtual Read operation
			elif cmd == 'vr':
				pin = int(params.pop(0))
				if pin in self._vr_pins and self._vr_pins[pin].read:
					self._vr_pins[pin].read()
			else:
				print('UNKNOWN' , params)
				return 
				#raise ValueError("Unknown message cmd: %s" % cmd)
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
						print('BlynkSend->EAGAIN')
						#raise Dont raise , flag instead
							
					else:
						time.sleep_ms(RE_TX_DELAY)
						retries += 1
	def _close(self, emsg=None):
		self.conn.close()
		self.state = DISCONNECTED
		time.sleep(RECONNECT_DELAY)
		if emsg:
			print('Error: 