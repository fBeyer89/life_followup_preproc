#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 11:22:05 2019

@author: fbeyer
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.io as sio


#/data/pt_life_restingstate_followup/physio/%s_resp.mat

resp=sio.loadmat('/data/pt_life_restingstate_followup/physio/LI0026893X_resp.mat')
resp_long=resp.get('r')[:]


# Number of samplepoints
y=resp_long.flatten()
N = resp_long.size
# sample spacing
T = 2
x = np.linspace(0.0, N*T, N)

#y=10 + np.sin(0.2 * 2.0*np.pi*x) + 0.5*np.sin(0.4 * 2.0*np.pi*x)
#y=10 + 3*np.sin(5 * 2.0*np.pi*x) + 0.5*np.sin(20 * 2.0*np.pi*x)

#y_pad=np.pad(y,(0,2**9-y.size),'constant')

plt.plot(x, y)


yf = scipy.fftpack.fft(y)
#yf_shift=scipy.fftpack.fftshift(yf)


#freq = np.fft.fftfreq(N, d=T)
xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

plt.plot(xf[1:], 2.0/N*np.abs(yf[0:N/2])[1:])

max(abs(yf[0:N/2]))