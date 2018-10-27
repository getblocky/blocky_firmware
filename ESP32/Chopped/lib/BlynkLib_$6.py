ed():
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
					await core.indicator.show('blynk-authenticating')
					self.state = AUTHENTICATING
					hdr = struct.pack(HDR_FMT, MSG_LOGIN, self._new_msg_id(), len(self._token))
					print('Blynk connection successful, authenticating...')
					self._send(hdr + self._token, True)
					data = self._recv(HDR_LEN, timeout=MAX_SOCK_TO)
					if not data:
						self._close('Blynk authentication timed out')
						core.indicator.animate('blynk-failed')
						continue

					msg_type, msg_id, status = struct.unpack(HDR_FMT, data)
					if status != STA_SUCCESS or msg_id == 0:
						self._close('Blynk authentication failed')
						core.indicator.animate('blynk-failed')
						continue
					await core.indicator.show('blynk-au