= const(0x23)
PN532_GPIO_VALIDATIONBIT            = const(0x80)
PN532_GPIO_P30                      = const(0)
PN532_GPIO_P31                      = const(1)
PN532_GPIO_P32                      = const(2)
PN532_GPIO_P33                      = const(3)
PN532_GPIO_P34                      = const(4)
PN532_GPIO_P35                      = const(5)

PN532_ACK                           = bytearray([0x01, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00])
PN532_FRAME_START                   = bytearray([0x01, 0x00, 0x00, 0xFF])

logger = logging.getLogger(__name__)


class PN532(object):
    """PN532 breakout board representation.  Requires a SPI connection to the
    breakout board.  A software SPI connection is recommended as the hardware
    SPI on the Raspberry Pi has some issues with the LSB first mode used by the
    PN532 (see: http://www.raspberrypi.org/forums/viewtopic.php?f=32&t=98070&p=720659#p720659)
    """

    #~def __init__(self, cs, sclk=None, mosi=None, miso=None, gpio=None,spi=None):
    def __init__(self, port ):
        """Create an instance of the PN532 class using either software SPI (if
        the sclk, mosi, and miso pins are specified) or hardware SPI if a
        spi parameter is passed.  The cs pin must be a digital GPIO pin.
        Optionally specify a GPIO controller to override the default that uses
        the board's GPIO pins.
        """
		self.bus = UART( 1 , tx = self.pin[0] , rx = self.pin[1] , baudrate = 115200)
		
        

    def _uint8_add(self, a, b):
        """Add add two values as unsigned 8-bit values."""
        return ((a & 0xFF) + (b & 0xFF)) & 0xFF

    def _busy_wait_ms(self, ms):
        """Busy wait for the specified number of milliseconds."""
        start = time.time()
        delta = ms/1000.0
        while (time.time() - start) <= delta:
            pass

    def _write_frame(self, data):
        """Write a frame to the PN532 with the specified data bytearray."""
        assert data is not None and 0 < len(data) < 255, 'Data m