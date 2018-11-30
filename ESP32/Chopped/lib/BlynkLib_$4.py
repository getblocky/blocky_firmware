lf, msg):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_NOTIFY, msg))

	def tweet(self, msg):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_TWEET, msg))

	def email(self, email, subject, content):
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
					self._send(self._format_msg(MSG_BRIDGE, 100,'vw',  pin , val))
	def set_property(self, pin, prop, val):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_PROPERTY, pin, prop, val))

	def log_event(self, event, descr=None):
		if self.state == AUTHENTICATED:
			if descr==None:
				self._send(self._format_msg(MSG_EVENT_LOG, event))
			else:
				self._send(self._format_msg(MSG_EVENT_LOG, event, descr))
	def log(self,message , http = False):
		self.virtual_write(127,message,http=http)
		
	def sync_all(self):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_HW_SYNC))

	def sync_virtual(self, pin):
		if self.state == AUTHENTICATED:
			self._s