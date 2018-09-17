self.client_id)
		if self.lw_topic:
			self._send_str(self.lw_topic)
			self._send_str(self.lw_msg)
		if self.user is not None:
			self._send_str(self.user)
			self._send_str(self.pswd)
		resp = self.sock.read(4)
		assert resp[0] == 0x20 and resp[1] == 0x02
		if resp[3] != 0:
			raise MQTTException(resp[3])
		return resp[2] & 1

	def disconnect(self):
		self.sock.write(b"\xe0\0")
		self.sock.close()

	def ping(self):
		self.sock.write(b"\xc0\0")

	async def publish(self, topic, msg, retain=False, qos=0):
		if core.Timer.runtime() - self.last < 20:
			core.time.sleep_ms(1)
		self.last = core.Timer.runtime()
		try :
			pkt = bytearray(b"\x30\0\0\0")
			pkt[0] |= qos << 1 | retain
			sz = 2 + len(topic) + len(msg)
			if qos > 0:
				sz += 2
			assert sz < 2097152
			i = 1
			while sz > 0x7f:
				pkt[i] = (sz & 0x7f) | 0x80
				sz >>= 7
				i += 1
			pkt[i] = sz
			#print(hex(len(pkt)), hexlify(pkt, ":"))
			self.sock.write(pkt, i + 1)
			self._send_str(topic)
			if qos > 0:
				self.pid += 1
				pid = self.pid
				core.struct.pack_into("!H", pkt, 0, pid)
				self.sock.write(pkt, 2)
			self.sock.write(msg)
			if qos == 1:
				while 1:
					op = self.wait_msg()
					if op == 0x40:
						sz = self.sock.read(1)
						assert sz == b"\x02"
						rcv_pid = self.sock.read(2)
						rcv_pid = rcv_pid[0] << 8 | rcv_pid[1]
						if pid == rcv_pid:
							return
			elif qos == 2:
				assert 0
		except Exception as err:
			print('mqtt-publish->',err)
			await core.network.connect()
			await self.publish(topic,msg,retain,qos)
	async def subscribe(self, topic, qos=0):
		assert self.cb is not None, "Subscribe callback is not set"
		pkt = bytearray(b"\x82\0\0\0")
		self.pid += 1
		core.struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, self.pid)
		#print(hex(len(pkt)), hexlify(pkt, ":"))
		self.sock.write(pkt)
		self._send_str(topic)
		self.sock.write(qos.to_bytes(1, "little"))
		while 1:
			op = self.wait_msg()
			if op == 0x90:
				resp = self.sock.read(4)
				#print(resp)
				as