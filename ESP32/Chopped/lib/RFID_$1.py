age = rx_info
		else :
			self.message = ''
		return ack
	def _read_data(self , count):
		timeout = 1000
		rx_info = ''
		if self.message == '':
			self._ack_wait(1000)
		else :
			rx_info = self.message
		return rx_info
		
	def _read_frame(self,length):
		response = self._read_data(length+8)
		frame_len = 0
		offset = 0
		if not len(response):return None
		if response[0]!=0 : return None
		if PN532_ACK_FRAME == response : return None
		for i in range(0 , len(response)):
			if response[i] != 0 and response[i] != 255:
				frame_len = response[i]
				offset = i
				break
		if frame_len == 0:return None
		if frame_len+response[offset+1]&0xFF!=0:return None
		checksum = reduce(self._uint8_add, response[offset+2:offset+2+frame_len+1], 0)
		if checksum != 0: return None
		return response[offset+2:offset+2+frame_len] 
	def call_function(self,command,response_length=0,params=[],timeout_sec = 1):
		data = bytearray(2 + len(params))
		data[0] = 0xD4 #PN532_HOSTTOPN532
		data[1] = command & 0xFF
		for i in range(len(params)):data[2+i] = params[i]
		if not self._write_frame(data): return None
		response = self._read_frame(response_length+2)
		if not response == None : 
			if not (response[0] == 0xD5 and response[1] == (command+1)): return None#PN532_PN532TOHOST
			return response[2:]
		else :
			return response
	
	def fw(self):
		response = self.call_function(0x02,4) #PN532_COMMAND_GETFIRMWAREVERSION
		if response == None : return None
		else :
			return (response[0], response[1], response[2], response[3])
			
	def SAM_configuration(self):
		self.call_function(0x14, params=[0x01, 0x14, 0x01])#PN532_COMMAND_SAMCONFIGURATION
	def read_passive_target(self, card_baud=PN532_MIFARE_ISO14443A, timeout_sec=1):
		response = self.call_function(0x4A,params=[0x01, card_baud], response_length=17)#PN532_COMMAND_INLISTPASSIVETARGET
		if response == None : return None
		else :
			if response[0] != 0x01 or response[5] > 7:
				return None
			list = []
			for x in range(6,6+response[5]):
				lis