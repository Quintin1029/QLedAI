import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
from scipy.fftpack import fft
import numpy as np

path = input("Enter WAV path: ")
sample_rate, samples = wavfile.read('/home/qharter/demo.wav')

plt.subplot(2, 1, 1)
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (sec)')
plt.plot(samples)

plt.subplot(2, 1, 2)

samples = samples / (2.**15)
length = len(samples)
p = fft(samples)
nUniquePoints = int(np.ceil((length+1)/2.0))
p = p[0:nUniquePoints]
p = abs(p)

p = p / float(length)
p = p**2

if length % 2 > 0:
    p[1:len(p)] = p[1:len(p)] * 2
else:
    p[1:len(p) - 1] = p[1:len(p) - 1] * 2

freqArray = np.arange(0, nUniquePoints, 1.0) * (sample_rate / length)

plt.plot(freqArray / 1000, 10000 * np.log10(p), color='k')

plt.show()
