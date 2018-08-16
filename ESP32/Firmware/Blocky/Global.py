
"""
	GLOBAL FLAG USED BY ALL FILES
	Note that this file is also to used as set non-volatile setup
"""

flag_UPCODE  = False 
flag_BOOT = False 
flag_ONLINE = False 
flag_BOOTBLOCK = False 
flag_INDICATOR = False

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