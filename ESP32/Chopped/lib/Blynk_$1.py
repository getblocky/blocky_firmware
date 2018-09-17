implemented

STA_SUCCESS = const(200)

HB_PERIOD = const(10)
NON_BLK_SOCK = const(0)
MIN_SOCK_TO = const(1) # 1 second
MAX_SOCK_TO = const(5) # 5 seconds, must be < HB_PERIOD
RECONNECT_DELAY = const(1) # 1 second
TASK_PERIOD_RES = const(50) # 50 ms
IDLE_TIME_MS = const(5) # 5 ms

RE_TX_DELAY = const(2)
MAX_TX_RETRIES = const(3)

MAX_VIRTUAL_PINS = const(32)

DISCONNECTED = const(0)
CONNECTING = const(1)
AUTHENTICATING = const(2)
AUTHENTICATED = const(3)

EAGAIN = const(11)


def sleep_from_until (start, delay):
    while time.ticks_diff(start, time.ticks_ms()) < delay:
        idle_func()
    return start + delay

class VrPin:
    def __init__(self, read=None, write=None):
        self.read = read
        self.write = write

class Terminal:
    def __init__(self, blynk, pin):
        self._blynk = blynk
        self._pin = pin

    def write(self, data):
        self._blynk.virtual_write(self._pin, data)

    def read(self, size):
        return ''

    def virtual_read(self):
        pass

    def virtual_write(self, value):
        try:
            out = eval(value)
            if out != None:
                print(repr(out))
        except:
            try:
                exec(value)
            except Exception as e:
                print('Exception:\n  ' + repr(e))

class Blynk:
    def __init__(self, token, server='blynk-cloud.com', port=None, connect=True, ssl=False):
        self._vr_pins = {}
        self._do_connect = False
        self._on_connect = None
        self._task = None
        self._task_period = 0
        self._token = token
        if isinstance (self._token, str):
            self._token = token.encode('ascii')
        self._server = server
        if port is None:
            if ssl:
                port = 8441
            else:
                port = 80
        self._port = port
        self._do_connect = connect
        self._ssl = ssl
        self.state = DISCONNECTED

    def _format_msg(self, msg_type, *args):
        data = ('\0'.joi