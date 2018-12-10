 True
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
						self._send(struct.pack(HDR_FMT, MSG_RSP, msg_id, STA_SUCCESS), True)
					elif msg_type == MSG_HW or msg_type == MSG_BRIDGE:
						data = self._recv(msg_len, MIN_SOCK_TO)
						if data:
							await self._handle_hw(data)
					elif msg_type == MSG_INTERNAL: # TODO: other message types?
						print('Internal')
						continue
					else:
						self._close('unknown message type %d' % msg_type)
						continue
				else:
					await core.asyncio.sleep_ms(1)
					#self._start_time = sleep_from_until(self._start_time, IDLE_TIME_MS)
				if not self._server_alive():
					self._close('Blynk server is offline')
					print('BlynkServer->DEAD')
					core.flag.blynk = False
					await core.indicator.show('blynk-authenticating')
					return
				else :
					core.flag.blynk = True
					
				
				await core.asyncio.sleep_ms(1)
				
			if not self._do_connect or not core.flag.blynk:
				self