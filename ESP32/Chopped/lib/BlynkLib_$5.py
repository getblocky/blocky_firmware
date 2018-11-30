end(self._format_msg(MSG_HW_SYNC, 'vr', pin))
	
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
				blynk._vr_pins[pin] = VrPin(func, None)
				#print(blynk, func, pin)
			def __call__(self):
				return self.func()
		return Decorator

	def VIRTUAL_WRITE(blynk, pin):
		class Decorator():
			def __init__(self, func):
				self.func = func
				blynk._vr_pins[pin] = VrPin(None, func)
			def __call__(self):
				return self.func()
		return Decorator

	def on_connect(self, func):
		self._on_connect = func

	def connect(self):
		self._do_connect = True

	def disconnect(self):
		self._do_connect = False
	def sending ( self , to , data ) :
		self._send(self._format_msg(MSG_HW, 'vw', pin, val))
	async def run(self):
		self._start_time = time.ticks_ms()
		self._task_millis = self._start_time
		self._hw_pins = {}
		self._rx_data = b''
		self._msg_id = 1
		self._timeout = None
		self._tx_count = 0
		self._m_time = 0
		self.state = DISCONNECTED
		while not core.wifi.wlan_sta.isconnected():
			self.last_call = core.Timer.runtime()
			await core.asyncio.sleep_ms(500)
		while True:
			self.last_call = core.Timer.runtime()
			while self.state != AUTHENTICATED:
				self.last_call = core.Timer.runtime()
				if self._do_connect:
					await core.asyncio.sleep_ms(100) # Delay in every retry
					core.gc.collect() 
					try:
						core.indicator.animate('blynk-connecting')
						self.state = CONNECTING
						if self._ssl:
							import ssl
							print('SSL: Connecting to %s:%d' % (self._server, self._port))
							ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SEC)
							self.conn = 