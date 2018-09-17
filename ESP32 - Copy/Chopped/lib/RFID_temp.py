# Adafruit PN532 breakout control library.
# Author: Tony DiCola
# Copyright (c) 2015 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import binascii
from Blocky.functools import reduce
import Blocky.logging
from Blocky.Pin import getPin
import time
from micropython import const

#import Adafruit_GPIO as GPIO
#import Adafruit_GPIO.SPI as SPI


PN532_PREAMBLE                      = const(0x00)
PN532_STARTCODE1                    = const(0x00)
PN532_STARTCODE2                    = const(0xFF)
PN532_POSTAMBLE                     = const(0x00)
PN532_HOSTTOPN532                   = const(0xD4)
PN532_PN532TOHOST                   = const(0xD5)
# PN532 Commands
PN532_COMMAND_DIAGNOSE              = const(0x00)
PN532_COMMAND_GETFIRMWAREVERSION    = const(0x02)
PN532_COMMAND_GETGENERALSTATUS      = const(0x04)
PN532_COMMAND_READREGISTER          = const(0x06)
PN532_COMMAND_WRITEREGISTER         = const(0x08)
PN532_COMMAND_READGPIO              = const(0x0C)
PN532_CO