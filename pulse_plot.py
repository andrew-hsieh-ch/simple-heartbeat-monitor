import matplotlib.pyplot as plt
import numpy as np
import time
import time, random
import math
import serial
from collections import deque
from scipy import signal
import itertools



#Display loading 
class PlotData:
    def __init__(self, max_entries=30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)


#initial
fig, (ax,ax2,ax3) = plt.subplots(3,1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
line3, = ax3.plot(np.random.randn(100))
ax.set_title('Original Signal (w/o DC)')
ax2.set_title('Filtered Signal')
ax3.set_title('Magnitude Spectrum')
ax.set_xlabel('Time [s]')
ax.set_ylabel(r'Amplitude [uV]')
ax2.set_xlabel('Time [s]')
ax2.set_ylabel(r'Amplitude [uV]')
ax3.set_xlabel('Frequency [Hz]')
ax3.set_ylabel(r'Amplitude [uV]')
plt.show(block = False)
plt.setp(line2,color = 'r')
plt.setp(line3,color = 'g')
fig.tight_layout()


PData= PlotData(500)
ax.set_ylim(-5,5)
# ax2.set_ylim(0,500)
ax3.set_ylim(0,500)



# plot parameters
print ('plotting data...')
# open serial port
strPort='com4'
ser = serial.Serial(strPort, 115200)
ser.flush()

start = time.time()

while True:
    
    for ii in range(10):

        try:
            data = float(ser.readline())
            PData.add(time.time() - start, data)
        except:
            pass
    
    
    ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    fft_blue = np.fft.fft(PData.axis_y)
    fft_blue[0] = 0
    ifft_blue = np.fft.ifft(fft_blue)
    line.set_xdata(PData.axis_x)
    line.set_ydata(ifft_blue)
    
    # ax2 starting
    ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)



    def butter_lowpass(cutOff, fs, order=5):
        nyq = 0.6 * fs
        normalCutoff = cutOff / nyq
        b, a = signal.butter(order, normalCutoff, btype='low', analog = True)
        return b, a

    def butter_lowpass_filter(data, cutOff, fs, order=4):
        b, a = butter_lowpass(cutOff, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y

    cutOff = 23.1 #cutoff frequency in rad/s
    fs = 250 #sampling frequency in rad/s
    order = 20 #order of filter

        # print sticker_data.ps1_dxdt2

    filtered_y0 = butter_lowpass_filter(PData.axis_y, cutOff, fs, order)
    
    filtered_y = signal.lfilter([1/3, 1/3, 1/3], 1, filtered_y0)
    deque_slice = deque(itertools.islice(PData.axis_x, 9, len(PData.axis_x)))
    fft_y = np.fft.fft(filtered_y)
    fft_y[0] = 0
    ifft_y = np.fft.ifft(fft_y)
    newY = ifft_y[9:]
    ax2.set_ylim(min(newY), max(newY))
    line2.set_xdata(deque_slice)
    line2.set_ydata(newY)
    
    # ax3 starting
   
    ax3.set_xlim(0, 50)
    fsampling = 100
    t = np.arange(0, len(PData.axis_x)/fsampling, 1/fsampling)
    f = (t/10)*fsampling
    
    ax3.set_ylim(min(abs(fft_y)), max(abs(fft_y)))
    line3.set_xdata(f)
    line3.set_ydata(abs(fft_y))


    fig.canvas.draw()
    fig.canvas.flush_events()