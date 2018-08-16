from Blocky.Timer import AddTask , runtime
import Blocky.uasyncio as asyncio

NTP_PAIR = []

def sync_ntp():
	try :
		import usocket , ustruct
		NTP_QUERY = bytearray(48)
		NTP_QUERY[0] = 0x1b
		s = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM)
		s.settimeout(2)
		res = s.sendto(NTP_QUERY,usocket.getaddrinfo("pool.ntp.org",123)[0][-1])
		msg = s.recv(48)
		s.close()
		ntp = ustruct.unpack("!I",msg[40:44])[0]
		ntp -= 3155673600
		if ntp > 0: # Correct time 
			from time import localtime
			ntp += gmt*3600 #GMT time
			global NTP_PAIR
			NTP_PAIR = [runtime() , ntp]
			print('Synced ' , localtime(ntp))
			
	except Exception as err:
		
		print('ntp-sync->' , err)
		return 
		
def Alarm(date,time,function):
	if not isinstance(date,tuple):
		raise TypeError('Date should be a tuple')
	if not isinstance(date,tuple):
		raise TypeError('Date should be a string')
	if not callable(function):
		raise TypeError('Function cant be call')
	
	