#!/usr/bin/python
# -*- coding:utf-8 -*-

import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import matplotlib.axes

# MUST match duration of data collection.
duration = 60

# Need to parameterize this...
f = open('../test_data/16sep2024/Geophone_Data1_15Hz.csv','r')
signal1 = f.readlines()
f.close()

f = open('../test_data/16sep2024/Geophone_Data2_15Hz.csv','r')
signal2 = f.readlines()
f.close()

sampling_rate = len(signal1)/duration

signal1 = list(map(float, signal1))
signal2 = list(map(float, signal2))

if(len(signal1) > len(signal2)):
    signal1 = signal1[0:len(signal2)]
else:
    signal2 = signal2[0:len(signal1)]

# Time axis
t = np.linspace(0, duration, len(signal1), endpoint=False)

# Remove DC component
b, a = scipy.signal.butter(5, 3, btype='highpass', fs=sampling_rate)
signal1 = scipy.signal.lfilter(b, a, signal1)
signal2 = scipy.signal.lfilter(b, a, signal2)

# Remove out of band noise
b, a = scipy.signal.butter(5, sampling_rate/2-1, btype='lowpass', fs=sampling_rate)
signal1 = scipy.signal.lfilter(b, a, signal1)
signal2 = scipy.signal.lfilter(b, a, signal2)

# Correlation Calculations
correlation = scipy.signal.correlate(signal1, signal2)

# FFT Calculations 
N = len(signal1)
T = 1/sampling_rate
fft_freq = np.fft.fftfreq(N, d=T)
fft_output1 = np.fft.fft(signal1)
fft_output2 = np.fft.fft(signal2)

# Plot signal
plt.figure(figsize=(14, 6))
plt.subplot(2, 2, 1)
plt.plot(t, signal1, linewidth=0.5)
plt.plot(t, signal2, linewidth=0.5)
plt.title('Input Signals')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')

# Plot the correlation
plt.subplot(2, 2, 2)
plt.stem(correlation, markerfmt=" ", basefmt="-b")
plt.title('Correlation')
plt.xlabel('Sample')
plt.ylabel('Magnitude')
plt.xlim(0, len(correlation))

# Plot signal zoomed in
zoom_factor = 10
plt.subplot(2, 2, 3)
plt.plot(t[0:len(t)//zoom_factor], signal1[0:len(t)//zoom_factor], linewidth=0.5)
plt.plot(t[0:len(t)//zoom_factor], signal2[0:len(t)//zoom_factor], linewidth=0.5)
plt.title(f'Input Signals ({zoom_factor}x Zoom)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')

# Plot FFTs
plt.subplot(2, 2, 4)
plt.stem(fft_freq, np.abs(fft_output1), 'b', markerfmt=" ")
plt.stem(fft_freq, np.abs(fft_output2), 'b', markerfmt=" ")
plt.title('Magnitude of FFT')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(0, sampling_rate/2)
plt.grid()

# Show and save whole plot
plt.tight_layout()
plt.show()
plt.savefig('plot_corr.png')