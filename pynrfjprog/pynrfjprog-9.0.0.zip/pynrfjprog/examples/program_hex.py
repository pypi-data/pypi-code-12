""" 

    This file contains example code meant to be used in order to test the 
    pynrfjprog API and Hex. If multiple devices are connected, pop-up will appear.
    
    Sample program: program_hex.py
    Requires nrf51-DK or nrf52-DK for visual confirmation (LEDs).
    
    Run from command line:  
        python program_hex.py  
    or if imported as "from pynrfjprog import examples"
        examples.program_hex.run()
    
    Program flow:
        0. API is opened and checked to see if correct family type is used
        1. Memory is erased
        2. test_program_path is parsed and written to memory
        3. Device is reset and application is run

"""

from __future__ import division
from __future__ import print_function

from builtins import int

# Import pynrfjprog API module and HEX parser module
from pynrfjprog import API, Hex

import os   # Used to create path to .hex file

def run():
    print('# pynrfjprog program hex example started...  ')
    
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

    # Find path to test hex file
    module_dir, module_file = os.path.split(__file__)
    hex_file_path = os.path.join(os.path.abspath(module_dir), device_family.name + '_dk_blinky.hex')
    
    # Parse hex, program to device
    print('# Parsing hex file into segments  ')
    test_program = Hex.Hex(hex_file_path) # Parse .hex file into segments
    print('# Writing %s to device  ' % hex_file_path)
    for segment in test_program:
        api.write(segment.address, segment.data, True)
       
    # Reset device, run
    api.sys_reset()                         # Reset device
    api.go()                                # Run application
    print('# Application running  ')

    # Close API
    api.close()                             # Close the dll

    print('# Example done...  ')
    
 
if __name__ == '__main__':
    run()


