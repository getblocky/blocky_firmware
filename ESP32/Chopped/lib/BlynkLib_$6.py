ssl.wrap_socket(ss, cert_reqs=ssl.CERT_REQUIRED, ca_certs='/flash/cert/ca.pem')
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
					await core.indicator.show('blynk-authenticated')
					self.state = AUTHENTICATED
					self._send(self._format_msg(MSG_INTERNAL, 'ver', '0.1.3', 'buff-in', 4096, 'h-beat', HB_PERIOD, 'dev', sys.platform+'-py',open('Blocky/fuse.py').read()))
					print("[BLYNK] Happy Blynking ! ")
					for x in range(5):
						core.indicator.rgb.fill((0,x*8,0))
						core.indicator.rgb.write()
						await core.asyncio.sleep_ms(10)
					for x in range(5,-1,-1):
						core.indicator.rgb.fill((0,x*8,0))
						core.indicator.rgb.write()
						await core.asyncio.sleep_ms(10)
					core.flag.blynk = True
					#self.log( {"id":core.binascii.hexlify(core.machine.unique_id()) , "co