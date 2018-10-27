%s, connection closed' % emsg)

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

	def notify(self, msg):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_NOTIFY, msg))

	def tweet(self, msg):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_TWEET, msg))

	def email(self, to, subject, body):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_EMAIL, to, subject, body))

	def virtual_write(self, pin, val , device = None,http=False):
		if http :
			try :
				#core.urequests.get('http://blynk.getblocky.com/' + self._token.decode() + '/update/V' + str(pin) + '?value=' + str(val))
				#core.urequests.get('http://blynk.getblocky.com/{}/update/V{}?value={}'.format(self._token.decode(),str(pin),str(val)))
				if not isinstance(val , list):
					val = str([val]).replace("'", '"')
				else :
					val = str(val).replace("'" , '"')
				print('[VW-HTTP]' , val)
				core.urequests.put('https://blynk.getblocky.com/{}/update/V{}'.format(self._token.decode(),str(pin)), data=val, headers={'Content-Type': 'application/json'})
			except Exception as err:
				print("VW using HTTP -> " , err)
		else :
			if self.state == AUTHENTICATED:
				if device == None :
					self._send(self._format_msg(MSG_HW, 'vw', pin, val))
				else :
					self._send(self._format_msg(MSG_BRIDGE ,100, 'i' , device)) # Set channel V100 of this node to point to that device
					self._send(self._format_msg(MSG_BRIDGE, 100,'vw',  pin ,