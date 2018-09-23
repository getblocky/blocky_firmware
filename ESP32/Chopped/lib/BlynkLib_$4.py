f tweet(self, msg):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_TWEET, msg))

	def email(self, to, subject, body):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_EMAIL, to, subject, body))

	def virtual_write(self, pin, val,http=False):
		if http :
			try :
				#core.urequests.get('http://blynk.getblocky.com/' + self._token.decode() + '/update/V' + str(pin) + '?value=' + str(val))
				#core.urequests.get('http://blynk.getblocky.com/{}/update/V{}?value={}'.format(self._token.decode(),str(pin),str(val)))
				core.urequests.put('http://blynk.getblocky.com/{}/update/V{}'.format(self._token.decode(),str(pin)), data=str(val), headers={'Content-Type': 'application/json'})

			
			except Exception as err:
				print("VW using HTTP -> " , err)
		else :
			if self.state == AUTHENTICATED:
				self._send(self._format_msg(MSG_HW, 'vw', pin, val))
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
			self._send(self._format_msg(MSG_HW_SYNC, 'vr', pin))
	
	def add_virtual_pin(self, pin, read=None, write=None):
		if isinstance(pin, int) and pin in range(0, MAX_VIRTUAL_PINS):
			if read != None :
				self._vr_pins_read[pin] = read
			if write != None :
				self._vr_pins_write[pin] = write
		else:
			raise ValueError('the pin must be an integer between 0 and %d' % (MAX_VIRTUAL_PINS - 1))

	def VIRTUAL_READ(blynk, pin):
		class Decorator():
			def __init__(self, func):
				self.func = func
		