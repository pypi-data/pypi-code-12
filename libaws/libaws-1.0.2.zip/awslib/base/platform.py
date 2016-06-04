import sys

WINDOWS_OS_SYSTEM = 1
LINUX_OS_SYSTEM = 2
OTHER_OS_SYSTEM = 3

CURRENT_OS_SYSTEM = OTHER_OS_SYSTEM

if sys.platform == "win32":
    CURRENT_OS_SYSTEM = WINDOWS_OS_SYSTEM
elif sys.platform.find('linux') != -1:
    CURRENT_OS_SYSTEM = LINUX_OS_SYSTEM
