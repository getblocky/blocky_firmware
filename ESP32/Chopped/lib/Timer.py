#version=1.0
import sys
core = sys.modules['Blocky.Core']

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

core.TimerInfo = [core.time.ticks_ms() , core.time.ticks_ms() , None , None]
# Provide an non-ovf timer count 
def runtime():
	now = core.time.ticks_ms()
	if now < core.TimerInfo[0]:offset =  (1073741823 - core.TimerInfo[1] + now)
	else :	offset =  (now - core.TimerInfo[0])
	core.TimerInfo[1] += offset;core.TimerInfo[0] = now
	return core.TimerInfo[1]
# This function should be call randomly every 10 minutes

	
def sync_ntp():
	if core.wifi.wlan_sta.isconnected():
		NTP_QUERY = bytearray(48)
		NTP_QUERY[0] = 0x1b
		addr = core.socket.getaddrinfo("pool.ntp.org", 123)[0][-1]
		s = core.socket.socket(core.socket.AF_INET, core.socket.SOCK_DGRAM)
		s.settimeout(1)
		res = s.sendto(NTP_QUERY, addr)
		msg = s.recv(48)
		s.close()
		val = core.struct.unpack("!I", msg[40:44])[0]
		t = val - 3155673600
		gmt = core.eeprom.get('GMT')
		if gmt != None :
			t += gmt * 3600
		tm = core.time.localtime(t)
		tm = tm[0:3] + (0,) + tm[3:6] + (0,)
		core.machine.RTC().datetime(tm)
		print('[NTP] Synced at {}'.format(core.time.localtime()))
		core.rtc = True
		
def current(field=None):
	if core.rtc == False :
		return 
	if field==None:
		return core.time.localtime()
	if field == "year":
		return core.time.localtime()[0]
	if field == "month":
		return core.time.localtime()[1]
	if field == "date":
		return core.time.localtime()[2]
	if field == "hour":
		return core.time.localtime()[3]
	if field == "minute":
		return core.time.localtime()[4]
	if field == "second":
		return core.time.localtime()[5]
	if field == "day":
		day = core.time.localtime()[6]
		if day == 0 :
			return "Monday"
		if day == 1 :
			retur