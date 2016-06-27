""" 

    This file contains example code meant to program the nRF5x chip with multiple hex files.
    
    Sample program: program_multiple_hex_files.py
    
    Run from command line:  
        python program_multiple_hex_files.py <hex_file1> <hex_file2 --optional> <hexfile3 --optional> 
    	or if imported as "from pynrfjprog import examples" examples.program_multiple_hex_files.run(hexFile1.hex, ...)
    
    Program flow:
        0. API is opened and checked to see if correct family type is used
        1. Memory is erased
        2. Hex files that user passed to script as arguments are programmed to the device
        3. Device is reset and application is run

"""

from __future__ import division
from __future__ import print_function

from builtins import int

# Import pynrfjprog API module and HEX parser module
from pynrfjprog import API, Hex

# User may call this function directly from interpretor (where they pass in arguments to run()) or user may execute this file as a script (where __main__ passes arguments sys.argv).
def run(hexFile1 = None, hexFile2 = None, hexFile3 = None):

    # Check arguments. Hex module will check that these files are valid.
    if (hexFile1 == None): # Check that user supplied atleast one hex file to be programmed.
        print('# ERROR, no hex file supplied. Please call with python program_multiple_hex_files <hexFile1.hex> <hexFile2.hex> <--optional hexFile3.hex> or run(<hexFile1.hex>, ...)')
        return

    if (hexFile2 == None): # Warn user that only one hex file was supplied to be programmed.
        print('# WARNING, only one hex file programmed. ')
    
    print('# Pynrfjprog started...  ')

    device_family = API.DeviceFamily.NRF51  # Start out with nrf51, will be checked and changed if needed
    
    # Init API with NRF51, open, connect, then check if NRF51 is correct
    print('# Opening API with device %s, checking if correct  ' % device_family)
    api = API.API(device_family)            # Initializing API with correct NRF51 family type (will be checked later if correct)
    api.open()                              # Open the dll with the set family type
    api.connect_to_emu_without_snr()        # Connect to emulator, it multiple are connected - pop up will appear
    
    # Check if family used was correct or else change
    try:
        device_version = api.read_device_version()
    except API.APIError as e:
        if e.err_code == API.NrfjprogdllErr.WRONG_FAMILY_FOR_DEVICE:
            device_family = API.DeviceFamily.NRF52
            print('# Closing API and re-opening with device %s  ' % device_family)
            api.close()                         # Close API so that correct family can be used to open
        
            # Re-Init API, open, connect, and erase device
            api = API.API(device_family)        # Initializing API with correct family type [API.DeviceFamily.NRF51 or ...NRF52]
            api.open()                          # Open the dll with the set family type
            api.connect_to_emu_without_snr()    # Connect to emulator, it multiple are connected - pop up will appear# change
        else:
            raise e
            
    print('# Erasing all... ')
    api.erase_all()                         # Erase memory of device

    # Program device with all hex files supplied by user.
    hexFiles = [hexFile1, hexFile2, hexFile3]

    for hex_file_path in hexFiles: 
        if (hex_file_path == None): # Once we've programmed all .hex files supplied by user, break.
            break
        try:
            program = Hex.Hex(hex_file_path) # Parse .hex file into segments. Checks whether user passed a valid file path or not. 
        except Exception as e: # If hex_file_path not a valid file, print an error and raise an exception.
            api.close()
            print(' # One of the hex files provided was invalid... Please check that the path is correct. Closing api and exiting. ')
            raise e

        print('# Writing %s to device  ' % hex_file_path)
        for segment in program: # Program hex file to the device.
            api.write(segment.address, segment.data, True)

    # Reset device, run
    api.sys_reset()                         # Reset device
    print('# Device reset... ')
    api.go()                                # Run application
    print('# Application running...  ')

    # Close API
    api.close()                             # Close the dll

if __name__ == '__main__':

    tmpArg = [None] * 3 # Initialze all elements of an array of length 3 to None.
    i = 0

    for arg in sys.argv[1:]: # For each argument passed by user set the corresponding tmpArg element.
        tmpArg[i] = arg
        i += 1

    run(tmpArg[0], tmpArg[1], tmpArg[2])



