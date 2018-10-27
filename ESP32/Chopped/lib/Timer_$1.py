n "Tuesday"
		if day == 2 :
			return "Wednesday"
		if day == 3 :
			return "Thursday"
		if day == 4 :
			return "Friday"
		if day == 5 :
			return "Saturday"
		if day == 6 :
			return "Sunday"
async def alarm_service():
	while not core.rtc :
		await core.asyncio.sleep_ms(1000)
	while True :
		for x in core.alarm_list:
			day , time , function  =  x 
			if core.time.localtime()[6] == day and core.time.localtime()[3] == time[0] \
				and core.time.localtime()[4] == time[1] :
				print("[DINGDONG] {} {}".format(core.time.localtime() , x))
				core.mainthread.call_soon( core.asyn.Cancellable( function ) () )
				
		
		await core.asyncio.sleep_ms( 60000 - core.time.localtime()[5]*1000)
			
		
def alarm ( day , time , function ):
	day_list = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	day = day_list.index(day)
	if day < 0 : 
		return 
	if isinstance(time , str) :
		time = time.split(":")
		time = [int(time[0]) , int(time[1]) ]
	
	print("[ALARM] -> {} {} ".format(day , time) )
	core.alarm_list.append([day , time , function])
	