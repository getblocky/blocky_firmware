sert resp[1] == pkt[2] and resp[2] == pkt[3]
				if resp[3] == 0x80:
					raise MQTTException(resp[3])
				return

	# Wait for a single incoming MQTT message and process it.
	# Subscribed messages are delivered to a callback previously
	# set by .set_callback() method. Other (internal) MQTT
	# messages processed internally.
	def wait_msg(self):
		res = self.sock.read(1)
		self.sock.setblocking(False)
		if res is None or len(res)==0:
			return None
		if res == b"\xd0":	# PINGRESP
			sz = self.sock.read(1)[0]
			assert sz == 0
			return None
		
		op = res[0]
		if op & 0xf0 != 0x30:
			return op
		sz = self._recv_len()
		topic_len = self.sock.read(2)
		topic_len = (topic_len[0] << 8) | topic_len[1]
		topic = self.sock.read(topic_len)
		sz -= topic_len + 2
		if op & 6:
			pid = self.sock.read(2)
			pid = pid[0] << 8 | pid[1]
			sz -= 2
		msg = self.sock.read(sz)
		core.mainthread.call_soon(self.cb(topic,msg))
		#self.cb(topic, msg)
		if op & 6 == 2:
			pkt = bytearray(b"\x40\x02\0\0")
			core.struct.pack_into("!H", pkt, 2, pid)
			self.sock.write(pkt)
		elif op & 6 == 4:
			assert 0

	# Checks whether a pending message from server is available.
	# If not, returns immediately with None. Otherwise, does
	# the same processing as wait_msg.
	def check_msg(self):
		self.sock.setblocking(False)
		return self.wait_msg()




