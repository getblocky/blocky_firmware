: not implemented
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
					print('['+str(core.Timer.runtime())+'] O