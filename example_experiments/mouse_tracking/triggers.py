"""
Description: This file contains the code for sending triggers to the neuroimaging system.
"""
# -*- coding: utf-8 -*-
from psychopy import parallel
import platform

PLATFORM = platform.platform()
if 'Linux' in PLATFORM:
    port = parallel.ParallelPort(address='/dev/parport0')  # on MEG stim PC
else:  # on Win this will work, on Mac we catch error below
    port = parallel.ParallelPort(address=0xDFF8)  # on MEG stim PC

# NB problems getting parallel port working under conda env
# from psychopy.parallel._inpout32 import PParallelInpOut32
# port = PParallelInpOut32(address=0xDFF8)  # on MEG stim PC
# parallel.setPortAddress(address='0xDFF8')
# port = parallel

# Figure out whether to flip pins or fake it
try:
    port.setData(128)
except NotImplementedError:
    def setParallelData(code=1):
        if code > 0:
            # logging.exp('TRIG %d (Fake)' % code)
            print('TRIG %d (Fake)' % code)
            pass
else:
    port.setData(0)
    setParallelData = port.setData

