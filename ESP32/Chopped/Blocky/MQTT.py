class MQTTException(Exception):
	pass
import sys
core = sys.modules['Blocky.Core']
class MQTTClient:
	
	def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0,ssl=False, ssl_params={}):
		if port == 0:
			port = 8883 if ssl else 1883
		self.client_id = client_id
		self.sock = None
		self.addr = None
		self.ssl = ssl
		self.ssl_params = ssl_params
		self.pid = 0
		self.cb = None
		self.user = user
		self.pswd = password
		self.keepalive = keepalive
		self.lw_topic = None
		self.lw_msg = None
		self.lw_qos = 0
		self.lw_retain = False
		self.server = server
		self.port = port
		self.last = core.Timer.runtime()
	def _send_str(self, s):
		self.sock.write(core.struct.pack("!H", len(s)))
		self.sock.write(s)

	def _recv_len(self):
		n = 0
		sh = 0
		while 1:
			b = self.sock.read(1)[0]
			n |= (b & 0x7f) << sh
			if not b & 0x80:
				return n
			sh += 7

	def set_callback(self, f):
		self.cb = f

	def set_last_will(self, topic, msg, retain=False, qos=0):
		assert 0 <= qos <= 2
		assert topic
		self.lw_topic = topic
		self.lw_msg = msg
		self.lw_qos = qos
		self.lw_retain = retain

	def connect(self, clean_session=True):
		self.addr = core.socket.getaddrinfo(self.server, self.port)[0][-1]
		self.sock = core.socket.socket()
		self.sock.connect(self.addr)
		if self.ssl:
			import ussl
			self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)
		msg = bytearray(b"\x10\0\0\x04MQTT\x04\x02\0\0")
		msg[1] = 10 + 2 + len(self.client_id)
		msg[9] = clean_session << 1
		if self.user is not None:
			msg[1] += 2 + len(self.user) + 2 + len(self.pswd)
			msg[9] |= 0xC0
		if self.keepalive:
			assert self.keepalive < 65536
			msg[10] |= self.keepalive >> 8
			msg[11] |= self.keepalive & 0x00FF
		if self.lw_topic:
			msg[1] += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
			msg[9] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
			msg[9] |= self.lw_retain << 5
		self.sock.write(msg)
		#print(hex(len(msg)), hexlify(msg, ":"))
		self._send_str(