', '0.1.3', 'buff-in', 4096, 'h-beat', HB_PERIOD, 'dev', sys.platform+'-py',open('Blocky/fuse.py').read()))
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