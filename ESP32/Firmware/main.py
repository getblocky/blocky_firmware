

from machine import Pin
from time import sleep_ms
from neopixel import NeoPixel
from os import urandom
from random import seed , choice
seed(int(urandom(1)[0]))
n = NeoPixel(Pin(5) , 12 , timing = True )
n.fill((0,0,0));n.write()
for x in range(12):
  n[x] = (choice((5,10,15,50)),choice((5,10,15,50)),choice((0,10,15,50)))
  n.write()
  sleep_ms(30)
sleep_ms(100)
for x in range(12):
  n[x] = (0,0,0)
  n.write()
  sleep_ms(30)
  
  

import Blocky.Main






