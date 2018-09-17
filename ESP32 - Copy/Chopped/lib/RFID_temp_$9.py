MIFARE_CMD_READ, block_number & 0xFF],
                                      response_length=17)
        # Check first response is 0x00 to show success.
        if response[0] != 0x00:
            return None
        # Return first 4 bytes since 16 bytes are always returned.
        return response[1:]

    def mifare_classic_write_block(self, block_number, data):
        """Write a block of data to the card.  Block number should be the block
        to write and data should be a byte array of length 16 with the data to
        write.  If the data is successfully written then True is returned,
        otherwise False is returned.
        """
        assert data is not None and len(data) == 16, 'Data must be an array of 16 bytes!'
        # Build parameters for InDataExchange command to do MiFare classic write.
        params = bytearray(19)
        params[0] = 0x01  # Max card numbers
        params[1] = MIFARE_CMD_WRITE
        params[2] = block_number & 0xFF
        params[3:] = data
        # Send InDataExchange request.
        response = self.call_function(PN532_COMMAND_INDATAEXCHANGE,
                                      params=params,
                                      response_length=1)
        return response[0] == 0x00