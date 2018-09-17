 but is done in the Arduino library and kept for consistency.
		self.ser.write( '\x55\x55\x00\x00\x00')
        self.get_firmware_version()
		

    def get_firmware_version(self):
        """Call PN532 GetFirmwareVersion function and return a tuple with the IC,
        Ver, Rev, and Support values.
        """
        response = self.call_function(PN532_COMMAND_GETFIRMWAREVERSION, 4)
        if response is None:
            raise RuntimeError('Failed to detect the PN532!  Make sure there is sufficient power (use a 1 amp or greater power supply), the PN532 is wired correctly to the device, and the solder joints on the PN532 headers are solidly connected.')
        return (response[0], response[1], response[2], response[3])

    def SAM_configuration(self):
        """Configure the PN532 to read MiFare cards."""
        # Send SAM configuration command with configuration for:
        # - 0x01, normal mode
        # - 0x14, timeout 50ms * 20 = 1 second
        # - 0x01, use IRQ pin
        # Note that no other verification is necessary as call_function will
        # check the command was executed as expected.
        self.call_function(PN532_COMMAND_SAMCONFIGURATION, params=[0x01, 0x14, 0x01])

    def read_passive_target(self, card_baud=PN532_MIFARE_ISO14443A, timeout_sec=1):
        """Wait for a MiFare card to be available and return its UID when found.
        Will wait up to timeout_sec seconds and return None if no card is found,
        otherwise a bytearray with the UID of the found card is returned.
        """
        # Send passive read command for 1 card.  Expect at most a 7 byte UUID.
        response = self.call_function(PN532_COMMAND_INLISTPASSIVETARGET,
                                      params=[0x01, card_baud],
                                      response_length=17)
        # If no response is available return None to indicate no card is present.
        if response is None:
            return None
        # Check only 1 card with up to a 7 byte