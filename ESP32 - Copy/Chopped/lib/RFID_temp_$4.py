ust be array of 1 to 255 bytes.'
        # Build frame to send as:
        # - SPI data write (0x01)
        # - Preamble (0x00)
        # - Start code  (0x00, 0xFF)
        # - Command length (1 byte)
        # - Command length checksum
        # - Command bytes
        # - Checksum
        # - Postamble (0x00)
        length = len(data)
        frame = bytearray(length+8)
        frame[0] = PN532bus_DATAWRITE
        frame[1] = PN532_PREAMBLE
        frame[2] = PN532_STARTCODE1
        frame[3] = PN532_STARTCODE2
        frame[4] = length & 0xFF
        frame[5] = self._uint8_add(~length, 1)
        frame[6:-2] = data
        checksum = reduce(self._uint8_add, data, 0xFF)
        frame[-2] = ~checksum & 0xFF
        frame[-1] = PN532_POSTAMBLE
        # Send frame.
        logger.debug('Write frame: 0x{0}'.format(binascii.hexlify(frame)))
		sleep_ms(2)
        self.bus.write(frame)
        

    def _read_data(self, count):
        """Read a specified count of bytes from the PN532."""
        # Build a read request frame.
        frame = bytearray(count)
        # Send the frame and return the response, ignoring the SPI header byte.
		sleep_ms(2)
		self.bus.readinto(frame)
        #~return response
        return frame

    def _read_frame(self, length):
        """Read a response frame from the PN532 of at most length bytes in size.
        Returns the data inside the frame if found, otherwise raises an exception
        if there is an error parsing the frame.  Note that less than length bytes
        might be returned!
        """
        # Read frame with expected length of data.
        response = self._read_data(length+8)
        logger.debug('Read frame: 0x{0}'.format(binascii.hexlify(response)))
        # Check frame starts with 0x01 and then has 0x00FF (preceeded by optional
        # zeros).
        if response[0] != 0x01:
            raise RuntimeError('Response frame does not start with 0x01!')
        # Swallow all the 0x00 values that preceed 0xFF.
  