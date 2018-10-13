 servers failed')
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
					print("[BLYNK] Sending system information")
					#self.log( {"id":core.binascii.hexlify(core.machine.unique_id()) , "config" : core.config , "ssid" : core.wifi.wlan_sta.config('essid') , "wifi_list" : core.wifi.wifi_list} , http = True)
					#self.virtual_write(128 ,  {"id":core.binascii.hexlify(core.machine.unique_id()) , "config" : core.config , "ssid" : core.wifi.wlan_sta.config('essid') , "wifi_list" : core.wifi.wifi_list} , http = True)
					core.wifi.wifi_list  = None
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
						self._send(struct.pack(HDR_FMT, MSG_RSP,