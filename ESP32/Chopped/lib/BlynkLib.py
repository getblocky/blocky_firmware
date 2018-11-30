# The MIT License (MIT)
# Copyright (c) 2015-2018 Volodymyr Shymanskyy
# Copyright (c) 2015 Daniel Campora

print('[BLYNK] Loading ...')

import socket
import struct
import time
import sys
import errno
core = sys.modules['Blocky.Core']

try:
	import machine
	idle_func = machine.idle
except ImportError:
	const = lambda x: x
	idle_func = lambda: 0
	setattr(sys.modules['time'], 'sleep_ms', lambda ms: time.sleep(ms // 1000))
	setattr(sys.modules['time'], 'ticks_ms', lambda: int(time.time() * 1000))
	setattr(sys.modules['time'], 'ticks_diff', lambda s, e: e - s)

HDR_LEN = const(5)
HDR_FMT = "!BHH"

MAX_MSG_PER_SEC = const(1000)

MSG_RSP = const(0)
MSG_LOGIN = const(2)
MSG_PING  = const(6)

MSG_TWEET = const(12)
MSG_EMAIL = const(13)
MSG_NOTIFY = const(14)
MSG_BRIDGE = const(15)
MSG_HW_SYNC = const(16)
MSG_INTERNAL = const(17)
MSG_PROPERTY = const(19)
MSG_HW = const(20)
MSG_EVENT_LOG = const(64)

MSG_REDIRECT  = const(41)  # TODO: not implemented
MSG_DBG_PRINT  = const(55) # TODO: not implemented

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

MAX_VIRTUAL_PINS = const(125)

DISCONNECTED = const(0)
CONNECTING = const(1)
AUTHENTICATING = const(2)
AUTHENTICATED = const(3)

EAGAIN = const(11)

LOGO = "1"

def sleep_from_until (start, delay):
	while time.ticks_diff(start, time.ticks_ms()) < delay:
		idle_func()
	return start + delay

class VrPin:
	def __init__(self, read=None, write=None):
		self.read = read
		self.write = write


class Blynk:
	def __init__(self, token, server='blynk.getblocky.com', port=None, connect=True, ssl=False,ota=None):
		self._vr_pins = {}
		self._vr_pins_read = {}
		self._vr_pins_write = {}
		self._do_connect = False
		self._on_connect = None
		self._task = None
		self._task_period =