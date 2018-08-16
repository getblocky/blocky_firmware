

from time import *

"""
Main Timer Variable 
[0] :	[Low] Time before feeding
[1]	:	[Important] Timer after feeding ( real time )
[3]	:	NTP at the last sync
[4]	:	Runtime at that sync

Timer Usage :;
	1 . provide runtime function 
	2 . Alarm task using ntp 
	3 . Do not handler any task !
	4 . No task will be execute here , leave it to asyncio
	
"""

TimerInfo = [ ticks_ms() , ticks_ms()  , None , None ]

# Provide an non-ovf timer count 
def runtime():
	global TimerInfo
	now = ticks_ms()
	if now < TimerInfo[0]:offset =  (1073741823 - TimerInfo[1] + now)
	else :	offset =  (now - TimerInfo[0])
	TimerInfo[1] += offset;TimerInfo[0] = now
	return TimerInfo[1]
# This function should be call randomly every 10 minutes


	
def sync_time():
	pass
	
	
