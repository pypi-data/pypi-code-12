import time  # import the time library

import pigpio  # import the GPIO library

pin = 18

# establish 2 pulse definitions to create a 1k hz tone
# the first entry sets pin 18 high for a duration of 1000 microseconds
# and the second entry set pin 18 low for a duration of 1000 microseconds
tone_1k = [pigpio.pulse(1 << pin, 0, 1000), pigpio.pulse(0, 1 << pin, 1000)]


# remember to execute "sudo pigpiod" on the Pi before executing

#instantiate pigpio
pi = pigpio.pi()

# set the buzzer pin to output
pi.set_mode(pin, pigpio.OUTPUT)

# clear any previous wave descriptions
pi.wave_clear()

# create a wave descriptor
pi.wave_add_generic(tone_1k)  # 100 ms flashes

# create the tone and save the id
tone = pi.wave_create()

# play tone continuously for one second
pi.wave_send_repeat(tone)
time.sleep(1)
pi.wave_tx_stop()  # stop waveform

#clean up
pi.wave_clear()  # clear all waveforms
pi.write(pin, 0)
