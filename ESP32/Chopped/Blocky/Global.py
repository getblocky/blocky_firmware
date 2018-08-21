
"""
	GLOBAL FLAG USED BY ALL FILES
"""
network = None
UPCODE  = False 					#this flag is set by OTA handler , then the mainthread will do the job
BOOTING = False 					#this flag means that the system is opening AP for setting up wifi
ONLINE = False 					#this flag means that the connection is established , both wifi and mqtt 
INDICATOR = False					#this flag means that the NeoPixel onboard will be used by user
										#critical system indicator will override user !
NETWORK_CONNECTING = False 		#this flag mean that the system is trying to connect in background , 
										#this should be used in case of weak wifi 
OFFLINE = False 					#in embedded mode , wifi wont be connected run user_code directly
										#double click CONFIG to connect to wifi , if fail it will start bootmode
										#this will exit after config

"""
	GLOBAL FLAG USED BY ALL FILES
	Note that this file is also to used as set non-volatile setup
"""

UPCODE  = False 
BOOT = False 
ONLINE = False 
BOOTBLOCK = False 
INDICATOR = False

"""
	if this flag is True , it means that the led ring is used by user 
	indicator when seing this flag wont pass any system indicator !
"""

fuse_OFFGRID = 'false'
fuse_BROKER = '' # Use another broker 

fuse_ULP = 'false' # Low power operation
fuse_PASSWORD = ''
fuse_BOARD = 'shield_v1'

status = 'offline'
# 'connected' , 'booting' , 'connecting' , 

error_mess  = ''


"""
	if this flag is True , it means that the led ring is used by user 
	indicator when seing this flag wont pass any system indicator !
"""

