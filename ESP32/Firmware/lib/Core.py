# All public variable across the system to avoid duplicate import
asyncio = None 
asyn = None 
flag = None 
eeprom = None
mqtt = None
BootMode = None
indicator = None
config = None
ota_file = None

import time
import machine
import neopixel

import binascii
import json
import ure
import gc
import network

import sys
import micropython
import socket
import struct

import _thread
import urequests
import random
import os
import Blocky.Global as flag
import Blocky.EEPROM as eeprom
import Blocky.uasyncio as asyncio
import Blocky.asyn as asyn
import Blocky.Timer as Timer
from Blocky.Indicator import indicator
from Blocky.Pin import getPort

cfn_btn = machine.Pin(12 , machine.Pin.IN , machine.Pin.PULL_UP)
mainthread = asyncio.get_event_loop()
TimerInfo =  None

wifi = None # Wifi class started in Main


