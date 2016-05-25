""" 

    This file contains example code meant to be used in order to test the 
    pynrfjprog API. If multiple devices are connected, pop-up will appear.
    
    Sample program: memory_read_write.py
    
    Run from command line:  
        python memory_read_write.py  
    or if imported using "from pynrfjprog import examples"
        examples.memory_read_write.run()
    
    Program flow:
        0. API is opened and checked to see if correct family type is used
        1. Memory is erased
        2. 0xDEADBEEF is written to address 0x0
        3. 0xBAADF00D is written to address 0x10
        4. Memory 0x0 and 0x10 is read and printed to console

"""

from __future__ import division
from __future__ import print_function

from builtins import int

# Import pynrfjprog API module and HEX parser module
from pynrfjprog import API, Hex

def run():
    print('# pynrfjprog memory read and write example started...  ')
    
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
    
    api.erase_all()                         # Erase memory of device

    # Write to addresses
    print('# Writing 0xDEADBEEF to memory address 0x0, use NVMC  ')
    api.write_u32(0x0, 0xDEADBEEF, True)
    print('# Writing 0xBAADF00D to memory address 0x10, use NVMC  ')
    api.write_u32(0x10, 0xBAADF00D, True)

    # Read from addresses
    print('# Reading memory address 0x0 and 0x10, and print to console  ')
    print('Address 0x0 contains: ', hex(api.read_u32(0x0)))
    print('Address 0x10 contains: ', hex(api.read_u32(0x10)))

    # Close API
    api.close()                             # Close the dll

    print('# Example done...  ')
    
 
if __name__ == '__main__':
    run()


