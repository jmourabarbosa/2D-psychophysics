from psychopy import * #import all libraries from PsychoPy
import math
import scipy
import sys
from random import randrange,choice,shuffle
from numpy.linalg import norm
from pickle import dump
import os
import zmq
import numpy as np
from multiprocessing import Process, Value,Array,Queue
from time import sleep,time
import matplotlib.pyplot as plt

p_dir = "subjects"

# TIMES
FIXATION=1
PRESENTATION=1

colors=['green','blue','white']


#Pupil network setup
port = "5000"
localhost="tcp://127.0.0.1:"
genis="tcp://10.201.99.188:"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(localhost+port)
socket.setsockopt(zmq.SUBSCRIBE, '')

finish = Value('i',0)
detect = Value('i',0)


def get_vel(vels):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(localhost+port)
        socket.setsockopt(zmq.SUBSCRIBE, 'Gaze')

        while detect.value:
                n = 0
                times=[0,0]
                points = [0,0]
                while n<2:
                        msg = socket.recv()
                        items = msg.split("\n")
                        items.pop(0)
                        times[n]=float(items[-2].split(":")[1])
                        point = items[0].split(":")
                        x=point[1].split(",")[0][1:]
                        y=point[1].split(",")[1][:-1]
                        points[n]=(float(x),float(y))
                        n+=1

                (x1,y1) = points[0]
                (x2,y2) = points[1]
                v = np.sqrt((x2-x1)**2 + (y2-y1)**2)/(times[1]-times[0])
                #print v        
                vels.put(v)



vels = Queue()
#record=Process(target=read_pupil,args=(finish,))
detector=Process(target=get_vel,args=(vels,))

#create a window
mywin = visual.Window([1280, 1024],monitor="testMonitor", fullscr=True, units="cm") #create a window full screen
mouse=event.Mouse(win=mywin)
mouse.setVisible(False)

trialClock = core.Clock()

stim1 = visual.PatchStim(win=mywin, mask='gauss', size=0.5, pos=[0,0], sf=0, color='black')
stim2 = visual.PatchStim(win=mywin, mask='gauss', size=0.5, pos=[-20,0], sf=0, color='black') 
stim3 = visual.PatchStim(win=mywin, mask='gauss', size=0.5, pos=[0,10], sf=0, color='black') 
stim4 = visual.PatchStim(win=mywin, mask='gauss', size=0.5, pos=[20,0], sf=0, color='black') 
stim5 = visual.PatchStim(win=mywin, mask='gauss', size=0.5, pos=[0,-10], sf=0, color='black') 

stim = stim1
stims = [stim1,stim2,stim3,stim4]

n_stims = len(stims)
n_reps=10
detect.value=1
detector.start()
#for n in range(n_reps):
#	vel=[]
#	stim = stims[np.mod(n,n_stims)]
t = 0 
trialClock.reset()
while t < 3:
	stim.draw()
	mywin.flip()
	t=trialClock.getTime()
	
detect.value=0
detector.join()

v=[]
while not vels.empty():
	v.append(vels.get())

plt.hist(v)
plt.show(v)
