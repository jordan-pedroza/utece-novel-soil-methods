# -*- coding:utf-8 -*-

import sched
import time
import ADS1263
import RPi.GPIO as GPIO
import numpy as np

f1_buf = np.array([])
f2_buf = np.array([])

script_ADC = 0

def take_sample():
    global f1_buf, f2_buf, script_ADC
    f1_buf = np.append(f1_buf, script_ADC.ADS1263_GetChannelValue(1))
    f2_buf = np.append(f2_buf, script_ADC.ADS1263_GetChannelValue(3))

def collect(DURATION, ADC):
    global f1_buf, f2_buf, script_ADC
    script_ADC = ADC

    # MUST match processing script
    DURATION = 60
    REF = 5.08          # Modify according to actual voltage
                        # external AVDD and AVSS(Default), or internal 2.5V
    SAMPLE_RATE = 400.0 # Sample rate in Hz

    s = sched.scheduler(time.time, time.sleep)
    with open(f'/home/pi/git/utexas_lm_geophone_gis_data_fusion/scripts/collection/Geophone_Data1_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.csv','w') as f1, open(f'/home/pi/git/utexas_lm_geophone_gis_data_fusion/scripts/collection/Geophone_Data2_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.csv','w') as f2: 

        try:
            i = 0
            start = time.time()
            while(i < DURATION*SAMPLE_RATE):
                s.enterabs(start+float(i)/SAMPLE_RATE, 10, take_sample)
                i += 1
            print("Sampling scheduled...")
            s.run()

        except IOError as e:
            print(e)
        
        except KeyboardInterrupt:
            print("ctrl + c:")
            print("Program end")
            ADC.ADS1263_Exit()
            exit()

        for val in f1_buf:
            f1.write(str((val * REF / 0x7fffffff))+'\n')
        for val in f2_buf:
            f2.write(str((val * REF / 0x7fffffff))+'\n')

    print("Done.")    
