#version = 1.0

import sys
core = sys.modules['Blocky.Core']

def alarm(day  = ['Monday'] , time = '7:00:00' ):
	"""
		Day is a list , 
		time is hh:mm:ss
	"""
	
	"""
		Note :
			This block is related to NTP and RTC
			At boot time , NTP will try to sync until success or synced with RTC 
			This block will wait until this process is done ! 
			This will only set a data at runtime 
			Another service will be run every 5 minutes and add a callback if it is almost there
			Since call_at_ is limited by 32bit-word , cant do long time !
			Remember the deinit list !
	"""
async def alarm_service():
	global alarm_list 
	while True :
		core.asyncio.sleep_ms(6000)
		
		
class Alarm :
	def __init__( self ):
		self.alarm_list = []
	def alarm ( date , time , function ):
	
	async def alarm_service(self):
	
	def deinit(self):
		
	
core.alarm( ["Monday","Tuesday"] , "7:00:00" , function = handler )
