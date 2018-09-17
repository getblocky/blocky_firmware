      offset = 1
        while response[offset] == 0x00:
            offset += 1
            if offset >= len(response):
                raise RuntimeError('Response frame preamble does not contain 0x00FF!')
        if response[offset] != 0xFF:
            raise RuntimeError('Response frame preamble does not contain 0x00FF!')
        offset += 1
        if offset >= len(response):
                raise RuntimeError('Response contains no data!')
        # Check length & length checksum match.
        frame_len = response[offset]
        if (frame_len + response[offset+1]) & 0xFF != 0:
            raise RuntimeError('Response length checksum did not match length!')
        # Check frame checksum value matches bytes.
        checksum = reduce(self._uint8_add, response[offset+2:offset+2+frame_len+1], 0)
        if checksum != 0:
            raise RuntimeError('Response checksum did not match expected value!')
        # Return frame data.
        return response[offset+2:offset+2+frame_len]
	@ note port problem
    def _wait_ready(self, timeout_sec=1):
        """Wait until the PN532 is ready to receive commands.  At most wait
        timeout_sec seconds for the PN532 to be ready.  If the PN532 is ready
        before the timeout is exceeded then True will be returned, otherwise
        False is returned when the timeout is exceeded.
        """
        start = time.time()
        # Send a SPI status read command and read response.
        sleep_ms(2) #self._busy_wait_ms(2)
		
        response = self.bus.transfer([PN532bus_STATREAD, 0x00])
        self._gpio.set_high(self._cs)
        # Loop until a ready response is received.
        while response[1] != PN532bus_READY:
            # Check if the timeout has been exceeded.
            if time.time() - start >= timeout_sec:
                return False
            # Wait a little while and try reading the status again.
            time.sleep(0.01)
            self._gpio.set_low(self._cs)
            self._busy_wait_ms(2)