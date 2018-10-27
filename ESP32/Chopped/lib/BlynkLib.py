# The MIT License (MIT)
# 
# Copyright (c) 2015-2018 Volodymyr Shymanskyy
# Copyright (c) 2015 Daniel Campora
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
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

MSG_REDIRECT  = const(41)  # TODO