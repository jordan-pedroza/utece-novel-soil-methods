#!/usr/bin/python
import RPi.GPIO as GPIO
import ADS1263
import collect

ADC = ADS1263.ADS1263()

# Anything higher pushes the limits of the Pi's software scheduler...

# The faster the rate, the worse the stability
# and the need to choose a suitable digital filter(REG_MODE1)
if (ADC.ADS1263_init_ADC1('ADS1263_2400SPS') == -1):
    exit()
ADC.ADS1263_SetMode(0) # 0 is singleChannel, 1 is diffChannel

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    try:
        print("Collecting Started")
        collect.collect(60, ADC)
    except KeyboardInterrupt:
            print("ctrl + c:")
            print("Program end")
            ADC.ADS1263_Exit()
            exit()
