# The MIT License (MIT)
# 
# Copyright (c) 2015-2018 Volodymyr Shymanskyy
# Copyright (c) 2015 Daniel Campora
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import socket
import struct
import time
import sys
import errno
core = sys.modules['Blocky.Core']

try:
	import machine
	idle_func = machine.idle
except ImportError:
	const = lambda x: x
	idle_func = lambda: 0
	setattr(sys.modules['time'], 'sleep_ms', lambda ms: time.sleep(ms // 1000))
	setattr(sys.modules['time'], 'ticks_ms', lambda: int(time.time() * 1000))
	setattr(sys.modules['time'], 'ticks_diff', lambda s, e: e - s)

HDR_LEN = const(5)
HDR_FMT = "!BHH"

MAX_MSG_PER_SEC = const(20)

MSG_RSP = const(0)
MSG_LOGIN = const(2)
MSG_PING  = const(6)

MSG_TWEET = const(12)
MSG_EMAIL = const(13)
MSG_NOTIFY = const(14)
MSG_BRIDGE = const(15)
MSG_HW_SYNC = const(16)
MSG_INTERNAL = const(17)
MSG_PROPERTY = const(19)
MSG_HW = const(20)
MSG_EVENT_LOG = const(64)

MSG_REDIRECT  = const(41)  # TODO: not implemented
MSG_DBG_PRINT  = const(55) # TODO: not implemented

STA_SUCCESS = const(200)

HB_PERIOD = const(10)
NON_BLK_SOCK = const(0)
MIN_SOCK_TO = const(1) # 1 second
MAX_SOCK_TO = const(5) # 5 seconds, must be < HB_PERIOD
RECONNECT_DELAY = const(1) # 1 second
TASK_PERIOD_RES = const(50) # 50 ms
IDLE_TIME_MS = const(5) # 5 ms

RE_TX_DELAY = const(2)
MAX_TX_RETRIES = const(3)

MAX_VIRTUAL_PINS = const(125)

DISCONNECTED = const(0)
CONNECTING = const(1)
AUTHENTICATING = const(2)
AUTHENTICATED = const(3)

EAGAIN = const(11)

LOGO = "1"

def sleep_from_until (start, delay):
	while time.ticks_diff(start, time.ticks_ms()) < delay:
		idle_func()
	return start + delay

class VrPin:
	def __init__(self, read=None, write=None):
		self.read = read
		self.write = write


class Blynk:
	def __init__(self, token, server='blynk.getblocky.com', port=None, connect=True, ssl=False,ota=None):
		self._vr_pins = {}
		self._vr_pins_read = {}
		self._vr_pins_write = {}
		self._do_connect = False
		self._on_connect = None
		self._task = None
		self._task_period = 0
		self._token = token
		self.message = None
		if isinstance (self._token, str):
			self._token = token.encode('ascii')
		self._server = server
		if port is None:
			if ssl:
				port = 8441
			else:
				port = 80
		self._port = port
		self._do_connect = connect
		self._ssl = ssl
		self.state = DISCONNECTED
		self.conn = None
		self.last_call = core.Timer.runtime()
		self.ota = ota
		
	def _format_msg(self, msg_type, *args):
		data = ('\0'.join(map(str, args))).encode('ascii')
		return struct.pack(HDR_FMT, msg_type, self._new_msg_id(), len(data)) + data
		
	async def _handle_hw(self, data):
		try :
			params = list(map(lambda x: x.decode('ascii'), data.split(b'\0')))
			cmd = params.pop(0)
			if cmd == 'pm'or cmd == 'dr' or cmd == 'dw' or cmd == 'ar' or cmd == 'aw':
				pass
			# Handle Virtual Write operation
			elif cmd == 'vw': 
				pin = int(params.pop(0))
				if pin == 126 :
					print('['+str(core.Timer.runtime())+'] OTA Message Received')
					core.gc.collect()
					ota_lock = core.eeprom.get('OTA_LOCK')
					
					if (ota_lock == True and core.cfn_btn.value() == 0) or ota_lock == False or ota_lock == None :
						if core.ota_file == None :
							core.ota_file = open('user_code.py','w')
						if params[1] == "OTA":
							await core.asyn.Cancellable.cancel_all()
							core.cleanup()
							
							self.virtual_write(127,"[OTA_READY]",http = True)
							core.ota_file.write("import sys\ncore=sys.modules['Blocky.Core']\n\n")
						else :
							print('PART' , params[1] ,len(params[0]) , end = '')
							total_part = int(params[1].split('/')[1])
							curr_part = int(params[1].split('/')[0])
							if total_part == curr_part :
								core.ota_file.write(params[0])
								core.ota_file.close()
								core.ota_file = None
								self.virtual_write(127,"[OTA_DONE]",http = True)
								print('User code saved')
								core.mainthread.call_soon(self.ota())
							if curr_part < total_part:
								core.ota_file.write(params[0])
								self.virtual_write(127,"[OTA_READY]",http = True)
						
					else :
						print('Sorry , your code is lock , press config to unlock it')
						core.blynk.log("[ERROR] You have locked your code , to upload new code , you need to press CONFIG button onboard")
					# Run cleanup task here
					
				elif (pin in self._vr_pins_write or pin in self._vr_pins_read) :
					self.message = params
					print('Task Handling on pin ', pin , 'with' , params)
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

	def notify(self, msg):
		if self.state == AUTHENTICATED:
			self._send(self._format_msg(MSG_NOTIFY, msg))

	def tweet(self, msg):
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
					try:
						self.state = CONNECTING
						if self._ssl:
							import ssl
							print('SSL: Connecting to %s:%d' % (self._server, self._port))
							ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SEC)
							self.conn = ssl.wrap_socket(ss, cert_reqs=ssl.CERT_REQUIRED, ca_certs='/flash/cert/ca.pem')
						else:
							print('TCP: Connecting to %s:%d' % (self._server, self._port))
							self.conn = socket.socket()
							print('Socket')
						self.conn.settimeout(0.1)
						
						while True :
							await core.asyncio.sleep_ms(5000)
							try :
								b=socket.getaddrinfo(self._server, self._port)[0][4]
								self.conn.connect(b)
								break
							except OSError:
								print('>')
								continue
						print('Connected')
					except Exception as err:
						core.sys.print_exception(err)
						self._close('connection with the Blynk servers failed')
						continue

					self.state = AUTHENTICATING
					hdr = struct.pack(HDR_FMT, MSG_LOGIN, self._new_msg_id(), len(self._token))
					print('Blynk connection successful, authenticating...')
					self._send(hdr + self._token, True)
					data = self._recv(HDR_LEN, timeout=MAX_SOCK_TO)
					if not data:
						self._close('Blynk authentication timed out')
						continue

					msg_type, msg_id, status = struct.unpack(HDR_FMT, data)
					if status != STA_SUCCESS or msg_id == 0:
						self._close('Blynk authentication failed')
						continue

					self.state = AUTHENTICATED
					self._send(self._format_msg(MSG_INTERNAL, 'ver', '0.1.3', 'buff-in', 4096, 'h-beat', HB_PERIOD, 'dev', sys.platform+'-py',open('Blocky/fuse.py').read()))
					print('Access granted, happy Blynking!')
					if self._on_connect:
						self._on_connect()
				else:
					self._start_time = sleep_from_until(self._start_time, TASK_PERIOD_RES)
				
			# Connection established
			self._hb_time = 0
			self._last_hb_id = 0
			self._tx_count = 0
			core.flag.blynk = True
			while self._do_connect:
				self.last_call = core.Timer.runtime()
				try:
					data = self._recv(HDR_LEN, NON_BLK_SOCK)
				except:
					pass
				if data:
					msg_type, msg_id, msg_len = struct.unpack(HDR_FMT, data)
					if msg_id == 0:
						self._close('invalid msg id %d' % msg_id)
						break
					# TODO: check length
					
					if msg_type == MSG_RSP:
						if msg_id == self._last_hb_id:
							self._last_hb_id = 0
					elif msg_type == MSG_PING:
						self._send(struct.pack(HDR_FMT, MSG_RSP, msg_id, STA_SUCCESS), True)
					elif msg_type == MSG_HW or msg_type == MSG_BRIDGE:
						data = self._recv(msg_len, MIN_SOCK_TO)
						if data:
							await self._handle_hw(data)
					elif msg_type == MSG_INTERNAL: # TODO: other message types?
						print('Internal')
						break
					else:
						self._close('unknown message type %d' % msg_type)
						break
				else:
					await core.asyncio.sleep_ms(1)
					#self._start_time = sleep_from_until(self._start_time, IDLE_TIME_MS)
				if not self._server_alive():
					self._close('Blynk server is offline')
					print('BlynkServer->DEAD')
					core.flag.blynk = False
					break
				else :
					core.flag.blynk = True
					
				
				await core.asyncio.sleep_ms(1)
				
			if not self._do_connect or not core.flag.blynk:
				self._close()
				print('Blynk disconnection requested by the user')
				break
			
			await core.asyncio.sleep_ms(1000)