
            response = self.bus.transfer([PN532bus_STATREAD, 0x00])
            self._gpio.set_high(self._cs)
        return True

    def call_function(self, command, response_length=0, params=[], timeout_sec=1):
        """Send specified command to the PN532 and expect up to response_length
        bytes back in a response.  Note that less than the expected bytes might
        be returned!  Params can optionally specify an array of bytes to send as
        parameters to the function call.  Will wait up to timeout_secs seconds
        for a response and return a bytearray of response bytes, or None if no
        response is available within the timeout.
        """
        # Build frame data with command and parameters.
        data = bytearray(2+len(params))
        data[0]  = PN532_HOSTTOPN532
        data[1]  = command & 0xFF
        data[2:] = params
        # Send frame and wait for response.
        self._write_frame(data)
        if not self._wait_ready(timeout_sec):
            return None
        # Verify ACK response and wait to be ready for function response.
        response = self._read_data(len(PN532_ACK))
        if response != PN532_ACK:
            raise RuntimeError('Did not receive expected ACK from PN532!')
        if not self._wait_ready(timeout_sec):
            return None
        # Read response bytes.
        response = self._read_frame(response_length+2)
        # Check that response is for the called function.
        if not (response[0] == PN532_PN532TOHOST and response[1] == (command+1)):
            raise RuntimeError('Received unexpected command response!')
        # Return response data.
        return response[2:]

    def begin(self):
        """Initialize communication with the PN532.  Must be called before any
        other calls are made against the PN532.
        """
        # Assert CS pin low for a second for PN532 to be ready.
        # Call GetFirmwareVersion to sync up with the PN532.  This might not be
        # required