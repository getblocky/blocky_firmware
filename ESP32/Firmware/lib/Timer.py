

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


# Provide an non-ovf timer count 
def runtime():
	import Blocky.Core as core
	core.TimerInfo = [ core.time.ticks_ms() , core.time.ticks_ms()  , None , None ]

	now = core.time.ticks_ms()
	if now < core.TimerInfo[0]:offset =  (1073741823 - core.TimerInfo[1] + now)
	else :	offset =  (now - core.TimerInfo[0])
	core.TimerInfo[1] += offset;core.TimerInfo[0] = now
	return core.TimerInfo[1]
# This function should be call randomly every 10 minutes

	
