The source of the firmware is in firmware folder . 
Since the ESP32 should only download 5-10KB file at a time , the python code will automatic 
chopp any file to parts and locate it to folder Chopped .

f.write() only require a flash page size of memory , file can be large , but not so 
large that it wont compile
